import os
import time
import uuid
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

from tortoise.expressions import Q
from tortoise.transactions import atomic

from app.models.ticket import Ticket, TicketRecord, TicketAttachment
from app.models.admin import User
from app.core.exceptions import CustomException


class TicketController:
    """工单控制器"""
    
    async def list(
        self, 
        page: int = 1, 
        page_size: int = 10, 
        search: Q = None,
        order: List[str] = None
    ) -> Tuple[int, List[Ticket]]:
        """获取工单列表"""
        query = Ticket.all()
        if search:
            query = query.filter(search)
            
        # 计算总数
        total = await query.count()
        
        # 排序和分页
        if order:
            query = query.order_by(*order)
        else:
            query = query.order_by("-created_at")
            
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # 预加载关联数据
        ticket_objs = await query.prefetch_related("creator", "assignee")
        
        return total, ticket_objs
    
    async def get(self, id: int) -> Ticket:
        """获取工单详情"""
        ticket_obj = await Ticket.filter(id=id).prefetch_related("creator", "assignee").first()
        if not ticket_obj:
            raise CustomException("工单不存在")
        return ticket_obj
    
    async def get_by_ticket_no(self, ticket_no: str) -> Ticket:
        """根据工单编号获取工单"""
        ticket_obj = await Ticket.filter(ticket_no=ticket_no).first()
        if not ticket_obj:
            raise CustomException("工单不存在")
        return ticket_obj
    
    @atomic()
    async def create(
        self, 
        title: str,
        description: str,
        type: str,
        priority: str,
        creator_id: int,
        assignee_id: Optional[int] = None,
        expected_time: Optional[datetime] = None,
        attachments: Optional[List[int]] = None,
    ) -> Ticket:
        """创建工单"""
        # 检查创建人
        creator = await User.filter(id=creator_id).first()
        if not creator:
            raise CustomException("创建人不存在")
        
        # 检查处理人
        assignee = None
        if assignee_id:
            assignee = await User.filter(id=assignee_id).first()
            if not assignee:
                raise CustomException("处理人不存在")
        
        # 生成工单编号 格式：TK + 年月日 + 3位序号
        date_str = datetime.now().strftime("%Y%m%d")
        # 查询当天最大序号
        max_ticket = await Ticket.filter(ticket_no__startswith=f"TK{date_str}").order_by("-ticket_no").first()
        if max_ticket:
            # 提取序号并加1
            try:
                seq = int(max_ticket.ticket_no[-3:]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        
        ticket_no = f"TK{date_str}{seq:03d}"
        
        # 创建工单
        ticket_obj = await Ticket.create(
            ticket_no=ticket_no,
            title=title,
            description=description,
            type=type,
            status="pending",  # 初始状态为待接单
            priority=priority,
            creator_id=creator_id,
            assignee_id=assignee_id,
            expected_time=expected_time,
        )
        
        # 创建处理记录
        record_obj = await TicketRecord.create(
            ticket_id=ticket_obj.id,
            action="create",
            content=f"创建了工单: {title}",
            operator_id=creator_id,
        )
        
        # 关联附件
        if attachments:
            await TicketAttachment.filter(id__in=attachments).update(ticket_id=ticket_obj.id, record_id=record_obj.id)
        
        return ticket_obj
    
    @atomic()
    async def update(
        self,
        id: int,
        operator_id: int,
        data: Dict[str, Any],
    ) -> Ticket:
        """更新工单基本信息"""
        ticket_obj = await self.get(id)
        
        # 只有创建人和管理员可以更新
        operator = await User.filter(id=operator_id).first()
        if not operator:
            raise CustomException("操作人不存在")
        
        if operator_id != ticket_obj.creator_id and not operator.is_superuser:
            raise CustomException("无权限更新此工单")
        
        # 已完成或已关闭的工单不能更新
        if ticket_obj.status in ["completed", "closed"]:
            raise CustomException("已完成或已关闭的工单不能更新")
        
        # 更新工单信息
        update_fields = {}
        for key, value in data.items():
            if key in ["title", "description", "type", "priority", "expected_time"]:
                update_fields[key] = value
                
        if "assignee_id" in data and data["assignee_id"]:
            assignee = await User.filter(id=data["assignee_id"]).first()
            if not assignee:
                raise CustomException("处理人不存在")
            update_fields["assignee_id"] = data["assignee_id"]
        
        if update_fields:
            for key, value in update_fields.items():
                setattr(ticket_obj, key, value)
            await ticket_obj.save()
        
        # 创建更新记录
        await TicketRecord.create(
            ticket_id=ticket_obj.id,
            action="update",
            content=f"更新了工单信息",
            operator_id=operator_id,
        )
        
        return ticket_obj
    
    @atomic()
    async def process(
        self,
        ticket_id: int,
        operator_id: int,
        action: str,
        content: str,
        assignee_id: Optional[int] = None,
        attachments: Optional[List[int]] = None,
    ) -> Ticket:
        """处理工单"""
        ticket_obj = await self.get(ticket_id)
        
        # 检查操作人
        operator = await User.filter(id=operator_id).first()
        if not operator:
            raise CustomException("操作人不存在")
        
        # 检查权限和有效性
        await self._validate_process_action(ticket_obj, operator, action, assignee_id)
        
        # 执行操作
        if action == "accept":
            # 接单: 待接单 -> 处理中
            if ticket_obj.status != "pending":
                raise CustomException("只有待接单状态的工单可以接单")
            ticket_obj.status = "processing"
            # 如果未分配处理人，则设置为当前操作人
            if not ticket_obj.assignee_id:
                ticket_obj.assignee_id = operator_id
                
        elif action == "process":
            # 处理: 仅更新处理记录，不改变状态
            if ticket_obj.status != "processing":
                raise CustomException("只有处理中状态的工单可以进行处理")
                
        elif action == "complete":
            # 完成: 处理中 -> 待确认
            if ticket_obj.status != "processing":
                raise CustomException("只有处理中状态的工单可以完成")
            ticket_obj.status = "confirming"
                
        elif action == "confirm":
            # 确认: 待确认 -> 已完成
            if ticket_obj.status != "confirming":
                raise CustomException("只有待确认状态的工单可以确认")
            # 只有创建人可以确认
            if operator_id != ticket_obj.creator_id and not operator.is_superuser:
                raise CustomException("只有创建人或管理员可以确认工单")
            ticket_obj.status = "completed"
            ticket_obj.finished_time = datetime.now()
                
        elif action == "reject":
            # 退回: 待确认 -> 处理中
            if ticket_obj.status != "confirming":
                raise CustomException("只有待确认状态的工单可以退回")
            # 只有创建人可以退回
            if operator_id != ticket_obj.creator_id and not operator.is_superuser:
                raise CustomException("只有创建人或管理员可以退回工单")
            ticket_obj.status = "processing"
                
        elif action == "transfer":
            # 转派: 不改变状态，只改变处理人
            if ticket_obj.status not in ["pending", "processing"]:
                raise CustomException("只有待接单或处理中状态的工单可以转派")
            # 检查转派目标
            if not assignee_id:
                raise CustomException("转派时必须指定处理人")
            assignee = await User.filter(id=assignee_id).first()
            if not assignee:
                raise CustomException("转派的处理人不存在")
            ticket_obj.assignee_id = assignee_id
                
        elif action == "close":
            # 关闭: 任何状态 -> 已关闭
            ticket_obj.status = "closed"
                
        elif action == "reopen":
            # 重新打开: 已完成/已关闭 -> 处理中
            if ticket_obj.status not in ["completed", "closed"]:
                raise CustomException("只有已完成或已关闭状态的工单可以重新打开")
            ticket_obj.status = "processing"
                
        else:
            raise CustomException(f"不支持的操作类型: {action}")
        
        # 保存工单状态
        await ticket_obj.save()
        
        # 创建处理记录
        record_obj = await TicketRecord.create(
            ticket_id=ticket_obj.id,
            action=action,
            content=content,
            operator_id=operator_id,
        )
        
        # 关联附件
        if attachments:
            await TicketAttachment.filter(id__in=attachments).update(record_id=record_obj.id)
        
        return ticket_obj
    
    async def _validate_process_action(
        self,
        ticket: Ticket,
        operator: User,
        action: str,
        assignee_id: Optional[int] = None,
    ) -> None:
        """验证处理操作的有效性"""
        # 管理员可以执行任何操作
        if operator.is_superuser:
            return
        
        # 验证各类操作权限
        if action in ["accept", "process", "complete"]:
            # 处理人或未分配处理人时的任何人都可以接单和处理
            if ticket.assignee_id and ticket.assignee_id != operator.id:
                raise CustomException("只有指定的处理人可以执行此操作")
                
        elif action in ["confirm", "reject"]:
            # 只有创建人可以确认或退回
            if operator.id != ticket.creator_id:
                raise CustomException("只有创建人可以执行此操作")
                
        elif action == "transfer":
            # 处理人或管理员可以转派
            if operator.id != ticket.assignee_id and not operator.is_superuser:
                raise CustomException("只有当前处理人可以转派工单")
            # 不能转派给自己
            if assignee_id and assignee_id == operator.id:
                raise CustomException("不能转派给自己")
    
    @atomic()
    async def delete(self, id: int, operator_id: int) -> None:
        """删除工单"""
        ticket_obj = await self.get(id)
        
        # 检查操作人
        operator = await User.filter(id=operator_id).first()
        if not operator:
            raise CustomException("操作人不存在")
        
        # 只有创建人和管理员可以删除
        if operator_id != ticket_obj.creator_id and not operator.is_superuser:
            raise CustomException("无权限删除此工单")
        
        # 删除关联数据
        await TicketRecord.filter(ticket_id=id).delete()
        await TicketAttachment.filter(ticket_id=id).delete()
        
        # 删除工单
        await ticket_obj.delete()
    
    async def upload_attachment(
        self,
        file_name: str,
        file_path: str,
        file_size: int,
        file_type: str,
        uploader_id: int,
    ) -> TicketAttachment:
        """上传附件"""
        # 检查上传人
        uploader = await User.filter(id=uploader_id).first()
        if not uploader:
            raise CustomException("上传人不存在")
        
        # 创建附件记录
        attachment = await TicketAttachment.create(
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            uploader_id=uploader_id,
        )
        
        return attachment
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取工单统计数据"""
        import logging
        logger = logging.getLogger(__name__)
        
        # 工单总数
        total_count = await Ticket.all().count()
        logger.debug(f"总工单数: {total_count}")
        
        # 待处理工单数量
        pending_count = await Ticket.filter(status__in=["pending", "processing"]).count()
        
        # 已完成工单数量
        completed_count = await Ticket.filter(status="completed").count()
        
        # 平均处理时间(小时)
        completed_tickets = await Ticket.filter(status="completed").all()
        if completed_tickets:
            total_hours = 0
            count = 0
            for ticket in completed_tickets:
                if ticket.finished_time and ticket.created_at:
                    # 计算工单完成时间与创建时间的差值（小时）
                    delta = ticket.finished_time - ticket.created_at
                    hours = delta.total_seconds() / 3600
                    total_hours += hours
                    count += 1
            avg_process_time = round(total_hours / count, 1) if count > 0 else 0
        else:
            avg_process_time = 0
        
        # 工单类型分布
        type_distribution = []
        for type_value in ["fault", "resource", "config", "maintenance", "emergency"]:
            count = await Ticket.filter(type=type_value).count()
            if count > 0:
                type_distribution.append({"type": type_value, "count": count})
        
        # 工单状态分布
        status_distribution = []
        for status_value in ["pending", "processing", "confirming", "completed", "closed"]:
            count = await Ticket.filter(status=status_value).count()
            if count > 0:
                status_distribution.append({"status": status_value, "count": count})
                
        # 工单优先级分布
        priority_distribution = []
        for priority_value in ["low", "medium", "high", "urgent"]:
            count = await Ticket.filter(priority=priority_value).count()
            if count > 0:
                priority_distribution.append({"priority": priority_value, "count": count})
        
        # 工单数量趋势(最近7天)
        import datetime
        
        trend_data = []
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(6, -1, -1):
            date = today - datetime.timedelta(days=i)
            next_date = date + datetime.timedelta(days=1)
            
            # 获取当天创建的工单数量
            created_count = await Ticket.filter(
                created_at__gte=date,
                created_at__lt=next_date
            ).count()
            
            # 获取当天完成的工单数量
            completed_count = await Ticket.filter(
                finished_time__gte=date,
                finished_time__lt=next_date
            ).count()
            
            trend_data.append({
                "date": date.strftime("%m-%d"),  # 修改为更兼容的格式
                "created": created_count,
                "completed": completed_count
            })
        
        # 平均处理时间(按工单类型)
        process_time = []
        
        for type_value, type_name in [
            ("fault", "故障报修"), 
            ("resource", "资源申请"), 
            ("config", "配置变更"), 
            ("maintenance", "日常维护"), 
            ("emergency", "紧急处理")
        ]:
            # 获取已完成的该类型工单
            type_tickets = await Ticket.filter(
                type=type_value, 
                status="completed"
            ).all()
            
            if type_tickets:
                total_hours = 0
                count = 0
                for ticket in type_tickets:
                    if ticket.finished_time and ticket.created_at:
                        delta = ticket.finished_time - ticket.created_at
                        hours = delta.total_seconds() / 3600
                        total_hours += hours
                        count += 1
                
                if count > 0:
                    avg_time = round(total_hours / count, 1)
                    process_time.append({
                        "type": type_value,
                        "type_name": type_name,
                        "avg_time": avg_time
                    })
                    logger.debug(f"工单类型 {type_name} 的平均处理时间: {avg_time}小时 (基于{count}条记录)")
                else:
                    # 即使没有数据也添加0值记录，确保图表显示
                    process_time.append({
                        "type": type_value,
                        "type_name": type_name,
                        "avg_time": 0
                    })
                    logger.debug(f"工单类型 {type_name} 无有效处理时间记录")
            else:
                # 即使没有数据也添加0值记录，确保图表显示
                process_time.append({
                    "type": type_value,
                    "type_name": type_name,
                    "avg_time": 0
                })
                logger.debug(f"工单类型 {type_name} 无已完成工单")
        
        logger.debug(f"处理时间数据: {process_time}")
        
        # 处理人工作量
        assignee_workload = []
        
        # 获取所有处理过工单的用户
        assignees = await User.filter(
            id__in=await Ticket.all().distinct().values_list("assignee_id", flat=True)
        ).all()
        
        for assignee in assignees:
            if not assignee:
                continue
                
            # 已完成的工单数量
            completed = await Ticket.filter(
                assignee_id=assignee.id,
                status="completed"
            ).count()
            
            # 处理中的工单数量
            processing = await Ticket.filter(
                assignee_id=assignee.id,
                status__in=["pending", "processing", "confirming"]
            ).count()
            
            if completed > 0 or processing > 0:
                assignee_workload.append({
                    "assignee_name": assignee.alias or assignee.username,
                    "completed": completed,
                    "processing": processing
                })
        
        # 按总工单数排序
        assignee_workload.sort(key=lambda x: x["completed"] + x["processing"], reverse=True)
        
        # 最多显示前5个
        assignee_workload = assignee_workload[:5]
        
        # 获取待处理的工单(按优先级排序)
        pending_tickets_query = await Ticket.filter(
            status__in=["pending", "processing"]
        ).order_by(
            # 紧急 > 高 > 中 > 低
            # 同优先级按创建时间排序
            "-priority", "created_at"
        ).limit(5).prefetch_related("creator")
        
        pending_tickets = []
        for ticket in pending_tickets_query:
            pending_tickets.append({
                "id": ticket.id,
                "ticket_no": ticket.ticket_no,
                "title": ticket.title,
                "priority": ticket.priority,
                "created_at": ticket.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
        
        return {
            "overview": {
                "total": total_count,
                "pending": pending_count,
                "completed": completed_count,
                "avg_process_time": avg_process_time,
            },
            "type_distribution": type_distribution,
            "status_distribution": status_distribution,
            "priority_distribution": priority_distribution,
            "trend_data": trend_data,
            "process_time": process_time,
            "assignee_workload": assignee_workload,
            "pending_tickets": pending_tickets,
        }


ticket_controller = TicketController() 