import asyncio
import datetime
import jinja2
from typing import Dict, List, Optional, Any, Union
from tortoise.transactions import atomic

from app.models.notification import (
    NotificationQueue, NotificationChannel, NotificationTemplate,
    NotificationLog, NotificationSetting, QueueStatus, NotificationPriority,
    NotificationChannel as ChannelEnum
)
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, ChannelCreate, ChannelUpdate,
    TemplateCreate, TemplateUpdate, SettingCreate, SettingUpdate,
    NotificationFromTemplate
)
from app.core.bgtask import BgTasks
from app.log import logger


class NotificationController:
    """通知控制器"""
    
    # 队列相关方法
    @staticmethod
    async def get_queue_list(
        page: int = 1, 
        page_size: int = 10, 
        source: Optional[str] = None,
        status: Optional[QueueStatus] = None,
        priority: Optional[NotificationPriority] = None,
    ) -> Dict[str, Any]:
        """获取通知队列列表"""
        # 构建查询条件
        query = {}
        if source:
            query["source"] = source
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
            
        # 查询总数
        total = await NotificationQueue.filter(**query).count()
        
        # 分页查询
        queue_items = await NotificationQueue.filter(**query).order_by("-created_at", "-priority").offset((page - 1) * page_size).limit(page_size)
        
        # 转换为字典
        item_list = [await item.to_dict() for item in queue_items]
        
        return {
            "items": item_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    @atomic()
    async def create_notification(notification_data: NotificationCreate) -> Dict[str, Any]:
        """创建通知"""
        queue_item = await NotificationQueue.create(
            source=notification_data.source,
            source_id=notification_data.source_id,
            title=notification_data.title,
            content=notification_data.content,
            priority=notification_data.priority,
            status=QueueStatus.PENDING,
            scheduled_at=notification_data.scheduled_at,
            max_retries=notification_data.max_retries,
            data=notification_data.data
        )
        
        # 将消息添加到后台任务队列
        await BgTasks.add_task(NotificationController.process_notification_queue)
        
        return await queue_item.to_dict()
    
    @staticmethod
    async def create_notification_from_template(data: NotificationFromTemplate) -> Dict[str, Any]:
        """根据模板创建通知"""
        # 获取模板
        template = await NotificationTemplate.get_or_none(template_key=data.template_key, is_active=True)
        if not template:
            raise ValueError(f"找不到模板: {data.template_key}")
        
        # 渲染模板
        env = jinja2.Environment()
        
        # 渲染标题
        title_template = env.from_string(template.title_template)
        title = title_template.render(**data.template_data)
        
        # 渲染内容
        content_template = env.from_string(template.content_template)
        content = content_template.render(**data.template_data)
        
        # 创建通知
        notification_data = NotificationCreate(
            source=data.source,
            source_id=data.source_id,
            title=title,
            content=content,
            priority=data.priority,
            scheduled_at=data.scheduled_at,
            max_retries=data.max_retries,
            data=data.additional_data
        )
        
        return await NotificationController.create_notification(notification_data)
    
    @staticmethod
    async def get_notification(notification_id: int) -> Optional[Dict[str, Any]]:
        """获取通知详情"""
        queue_item = await NotificationQueue.get_or_none(id=notification_id)
        if not queue_item:
            return None
        
        notification_dict = await queue_item.to_dict()
        
        # 获取通知日志
        logs = await NotificationLog.filter(queue_id=notification_id).order_by("-created_at")
        notification_dict["logs"] = [await log.to_dict() for log in logs]
        
        return notification_dict
    
    @staticmethod
    async def update_notification(notification_id: int, notification_data: NotificationUpdate) -> Optional[Dict[str, Any]]:
        """更新通知"""
        queue_item = await NotificationQueue.get_or_none(id=notification_id)
        if not queue_item:
            return None
        
        # 更新字段
        update_data = notification_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(queue_item, key, value)
        
        await queue_item.save()
        return await queue_item.to_dict()
    
    @staticmethod
    async def delete_notification(notification_id: int) -> bool:
        """删除通知"""
        queue_item = await NotificationQueue.get_or_none(id=notification_id)
        if not queue_item:
            return False
        
        # 删除日志
        await NotificationLog.filter(queue_id=notification_id).delete()
        
        # 删除通知
        await queue_item.delete()
        return True
    
    # 渠道相关方法
    @staticmethod
    async def get_channel_list(
        page: int = 1, 
        page_size: int = 10, 
        channel_type: Optional[ChannelEnum] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """获取通知渠道列表"""
        # 构建查询条件
        query = {}
        if channel_type:
            query["channel_type"] = channel_type
        if is_active is not None:
            query["is_active"] = is_active
            
        # 查询总数
        total = await NotificationChannel.filter(**query).count()
        
        # 分页查询
        channels = await NotificationChannel.filter(**query).order_by("name").offset((page - 1) * page_size).limit(page_size)
        
        # 转换为字典
        channel_list = [await channel.to_dict() for channel in channels]
        
        return {
            "items": channel_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def create_channel(channel_data: ChannelCreate) -> Dict[str, Any]:
        """创建通知渠道"""
        channel = await NotificationChannel.create(
            name=channel_data.name,
            channel_type=channel_data.channel_type,
            config=channel_data.config,
            is_active=channel_data.is_active
        )
        
        return await channel.to_dict()
    
    @staticmethod
    async def get_channel(channel_id: int) -> Optional[Dict[str, Any]]:
        """获取通知渠道详情"""
        channel = await NotificationChannel.get_or_none(id=channel_id)
        if not channel:
            return None
        
        return await channel.to_dict()
    
    @staticmethod
    async def update_channel(channel_id: int, channel_data: ChannelUpdate) -> Optional[Dict[str, Any]]:
        """更新通知渠道"""
        channel = await NotificationChannel.get_or_none(id=channel_id)
        if not channel:
            return None
        
        # 更新字段
        update_data = channel_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(channel, key, value)
        
        await channel.save()
        return await channel.to_dict()
    
    @staticmethod
    async def delete_channel(channel_id: int) -> bool:
        """删除通知渠道"""
        channel = await NotificationChannel.get_or_none(id=channel_id)
        if not channel:
            return False
        
        await channel.delete()
        return True
    
    @staticmethod
    async def test_channel(channel_data: ChannelCreate) -> Dict[str, Any]:
        """测试通知渠道连接"""
        try:
            # 创建一个临时渠道对象，但不保存到数据库
            channel = NotificationChannel(
                name="测试渠道",
                channel_type=channel_data.channel_type,
                config=channel_data.config,
                is_active=True
            )
            
            # 根据渠道类型执行不同的测试逻辑
            if channel.channel_type == ChannelEnum.EMAIL:
                # 测试邮件服务器连接
                await NotificationController._test_email_channel(channel)
            elif channel.channel_type == ChannelEnum.SMS:
                # 测试短信服务连接
                await NotificationController._test_sms_channel(channel)
            elif channel.channel_type in [ChannelEnum.DINGTALK, ChannelEnum.WECOM, ChannelEnum.FEISHU]:
                # 测试webhook连接
                await NotificationController._test_webhook_channel(channel)
            else:
                # 其他渠道类型
                return {"status": "skipped", "message": f"暂不支持测试渠道类型: {channel.channel_type}"}
            
            return {"status": "success", "message": "连接测试成功"}
        except Exception as e:
            logger.error(f"测试渠道连接失败: {str(e)}")
            raise ValueError(f"连接测试失败: {str(e)}")
    
    @staticmethod
    async def _test_email_channel(channel: NotificationChannel) -> None:
        """测试邮件渠道"""
        # 这里应该实现实际的SMTP连接测试逻辑
        # 由于实际逻辑依赖于具体的邮件服务配置，这里仅做简单的配置检查
        config = channel.config
        required_fields = ["host", "port", "username", "from_email"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                raise ValueError(f"邮件配置缺少必要字段: {field}")
        
        # 在实际项目中，这里应该尝试连接SMTP服务器
        # 出于演示目的，我们仅做简单校验
        logger.info(f"测试邮件渠道连接 - 配置检查通过: {config['host']}:{config['port']}")
    
    @staticmethod
    async def _test_sms_channel(channel: NotificationChannel) -> None:
        """测试短信渠道"""
        # 这里应该实现实际的短信API连接测试逻辑
        config = channel.config
        required_fields = ["platform", "access_key", "secret_key"]
        
        for field in required_fields:
            if field not in config or not config[field]:
                raise ValueError(f"短信配置缺少必要字段: {field}")
        
        # 在实际项目中，这里应该尝试调用短信服务API
        logger.info(f"测试短信渠道连接 - 配置检查通过: 平台={config['platform']}")
    
    @staticmethod
    async def _test_webhook_channel(channel: NotificationChannel) -> None:
        """测试Webhook渠道"""
        config = channel.config
        
        if "webhook_url" not in config or not config["webhook_url"]:
            raise ValueError("Webhook配置缺少必要字段: webhook_url")
        
        # 在实际项目中，这里应该尝试发送请求到webhook地址
        logger.info(f"测试Webhook渠道连接 - 配置检查通过: {config['webhook_url']}")
    
    # 模板相关方法
    @staticmethod
    async def get_template_list(
        page: int = 1, 
        page_size: int = 10, 
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """获取通知模板列表"""
        # 构建查询条件
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
            
        # 查询总数
        total = await NotificationTemplate.filter(**query).count()
        
        # 分页查询
        templates = await NotificationTemplate.filter(**query).order_by("name").offset((page - 1) * page_size).limit(page_size)
        
        # 转换为字典
        template_list = [await template.to_dict() for template in templates]
        
        return {
            "items": template_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    async def create_template(template_data: TemplateCreate) -> Dict[str, Any]:
        """创建通知模板"""
        # 检查是否存在相同的template_key
        existing = await NotificationTemplate.get_or_none(template_key=template_data.template_key)
        if existing:
            raise ValueError(f"模板键名已存在: {template_data.template_key}")
        
        template = await NotificationTemplate.create(
            name=template_data.name,
            template_key=template_data.template_key,
            title_template=template_data.title_template,
            content_template=template_data.content_template,
            applicable_channels=template_data.applicable_channels,
            is_active=template_data.is_active
        )
        
        return await template.to_dict()
    
    @staticmethod
    async def get_template(template_id: int) -> Optional[Dict[str, Any]]:
        """获取通知模板详情"""
        template = await NotificationTemplate.get_or_none(id=template_id)
        if not template:
            return None
        
        return await template.to_dict()
    
    @staticmethod
    async def get_template_by_key(template_key: str) -> Optional[Dict[str, Any]]:
        """根据键名获取通知模板"""
        template = await NotificationTemplate.get_or_none(template_key=template_key)
        if not template:
            return None
        
        return await template.to_dict()
    
    @staticmethod
    async def update_template(template_id: int, template_data: TemplateUpdate) -> Optional[Dict[str, Any]]:
        """更新通知模板"""
        template = await NotificationTemplate.get_or_none(id=template_id)
        if not template:
            return None
        
        # 更新字段
        update_data = template_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(template, key, value)
        
        await template.save()
        return await template.to_dict()
    
    @staticmethod
    async def delete_template(template_id: int) -> bool:
        """删除通知模板"""
        template = await NotificationTemplate.get_or_none(id=template_id)
        if not template:
            return False
        
        # 删除模板
        await template.delete()
        return True
    
    # 设置相关方法
    @staticmethod
    async def get_user_settings(user_id: int) -> List[Dict[str, Any]]:
        """获取用户通知设置"""
        settings = await NotificationSetting.filter(user_id=user_id)
        return [await setting.to_dict() for setting in settings]
    
    @staticmethod
    async def get_user_source_setting(user_id: int, source: str) -> Optional[Dict[str, Any]]:
        """获取用户特定来源的通知设置"""
        setting = await NotificationSetting.get_or_none(user_id=user_id, source=source)
        if not setting:
            return None
        
        return await setting.to_dict()
    
    @staticmethod
    async def create_or_update_setting(setting_data: SettingCreate) -> Dict[str, Any]:
        """创建或更新通知设置"""
        # 查找是否存在
        setting = await NotificationSetting.get_or_none(user_id=setting_data.user_id, source=setting_data.source)
        
        if setting:
            # 更新
            setting.enabled_channels = setting_data.enabled_channels
            setting.is_enabled = setting_data.is_enabled
            await setting.save()
        else:
            # 创建
            setting = await NotificationSetting.create(
                user_id=setting_data.user_id,
                source=setting_data.source,
                enabled_channels=setting_data.enabled_channels,
                is_enabled=setting_data.is_enabled
            )
        
        return await setting.to_dict()
    
    @staticmethod
    async def delete_setting(setting_id: int) -> bool:
        """删除通知设置"""
        setting = await NotificationSetting.get_or_none(id=setting_id)
        if not setting:
            return False
        
        # 删除设置
        await setting.delete()
        return True
    
    # 通知处理方法
    @staticmethod
    async def process_notification_queue():
        """处理通知队列"""
        # 查找需要处理的通知
        query = {
            "status": QueueStatus.PENDING,
            "scheduled_at__lte": datetime.datetime.now(),  # 只处理已经到了计划时间的通知
        }
        
        # 设置一个处理上限
        limit = 10
        
        # 获取待处理通知
        notifications = await NotificationQueue.filter(**query).order_by("priority", "created_at").limit(limit)
        
        logger.info(f"开始处理通知队列，找到 {len(notifications)} 条待处理通知")
        
        for notification in notifications:
            try:
                # 标记为处理中
                notification.status = QueueStatus.PROCESSING
                await notification.save()
                
                # 处理通知
                success = await NotificationController._send_notification(notification)
                
                if success:
                    # 标记为处理完成
                    notification.status = QueueStatus.COMPLETED
                    notification.processed_at = datetime.datetime.now()
                    await notification.save()
                else:
                    # 增加重试次数
                    notification.retry_count += 1
                    
                    # 检查是否超过最大重试次数
                    if notification.retry_count >= notification.max_retries:
                        notification.status = QueueStatus.FAILED
                    else:
                        notification.status = QueueStatus.PENDING
                    
                    await notification.save()
            
            except Exception as e:
                logger.error(f"处理通知 {notification.id} 失败: {str(e)}")
                # 发生异常时增加重试次数
                notification.retry_count += 1
                
                # 检查是否超过最大重试次数
                if notification.retry_count >= notification.max_retries:
                    notification.status = QueueStatus.FAILED
                else:
                    notification.status = QueueStatus.PENDING
                
                await notification.save()
    
    @staticmethod
    async def _send_notification(notification: NotificationQueue) -> bool:
        """发送通知"""
        # 获取有效的通知渠道
        channels = await NotificationChannel.filter(is_active=True)
        
        if not channels:
            logger.warning(f"没有有效的通知渠道，通知 {notification.id} 发送失败")
            return False
        
        # 发送成功标记
        success = False
        
        # 遍历所有渠道进行发送
        for channel in channels:
            try:
                result = await NotificationController._send_via_channel(notification, channel)
                
                # 记录发送日志
                await NotificationLog.create(
                    queue=notification,
                    channel=channel,
                    channel_name=channel.name,
                    channel_type=channel.channel_type,
                    recipients=[],  # 这里应该根据实际情况设置接收者
                    status="success" if result["success"] else "failed",
                    error_message=result.get("error"),
                    response_data=result.get("response")
                )
                
                # 只要有一个渠道发送成功，就标记为成功
                if result["success"]:
                    success = True
            
            except Exception as e:
                logger.error(f"通过渠道 {channel.name} 发送通知 {notification.id} 时发生异常: {str(e)}")
                
                # 记录发送日志
                await NotificationLog.create(
                    queue=notification,
                    channel=channel,
                    channel_name=channel.name,
                    channel_type=channel.channel_type,
                    recipients=[],
                    status="failed",
                    error_message=str(e)
                )
        
        return success
    
    @staticmethod
    async def _send_via_channel(notification: NotificationQueue, channel: NotificationChannel) -> Dict[str, Any]:
        """通过特定渠道发送通知"""
        # 默认结果
        result = {
            "success": False,
            "error": None,
            "response": None
        }
        
        try:
            # 根据渠道类型分别处理
            if channel.channel_type == ChannelEnum.EMAIL:
                # 此处应该实现邮件发送逻辑
                logger.info(f"模拟通过邮件发送通知: {notification.title}")
                result["success"] = True
                result["response"] = {"message": "邮件发送成功"}
            
            elif channel.channel_type == ChannelEnum.SMS:
                # 此处应该实现短信发送逻辑
                logger.info(f"模拟通过短信发送通知: {notification.title}")
                result["success"] = True
                result["response"] = {"message": "短信发送成功"}
            
            elif channel.channel_type == ChannelEnum.WECHAT:
                # 此处应该实现微信发送逻辑
                logger.info(f"模拟通过微信发送通知: {notification.title}")
                result["success"] = True
                result["response"] = {"message": "微信发送成功"}
            
            elif channel.channel_type == ChannelEnum.WEBHOOK:
                # 此处应该实现Webhook发送逻辑
                logger.info(f"模拟通过Webhook发送通知: {notification.title}")
                result["success"] = True
                result["response"] = {"message": "Webhook发送成功"}
            
            elif channel.channel_type == ChannelEnum.SYSTEM:
                # 系统内部通知
                logger.info(f"系统内部通知: {notification.title}")
                result["success"] = True
                result["response"] = {"message": "系统内部通知已发送"}
            
            else:
                result["error"] = f"不支持的渠道类型: {channel.channel_type}"
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    # 实用方法：将监控告警添加到通知队列
    @staticmethod
    async def add_monitor_alert_to_queue(alert_id: int) -> Dict[str, Any]:
        """将监控告警添加到通知队列"""
        from app.models.monitor import MonitorAlert
        
        # 获取告警信息
        alert = await MonitorAlert.get_or_none(id=alert_id)
        if not alert:
            raise ValueError(f"找不到告警: {alert_id}")
        
        # 构建通知内容
        alert_dict = await alert.to_dict()
        
        # 创建通知
        notification_data = NotificationCreate(
            source="monitor",
            source_id=alert_id,
            title=f"监控告警: {alert.alert_type}",
            content=alert.content,
            priority=NotificationPriority.HIGH if alert.level == "error" else NotificationPriority.NORMAL,
            data=alert_dict
        )
        
        return await NotificationController.create_notification(notification_data)
    
    # 实用方法：将工单状态变更添加到通知队列
    @staticmethod
    async def add_ticket_status_change_to_queue(ticket_id: int, old_status: str, new_status: str) -> Dict[str, Any]:
        """将工单状态变更添加到通知队列"""
        from app.models.ticket import Ticket
        
        # 获取工单信息
        ticket = await Ticket.get_or_none(id=ticket_id)
        if not ticket:
            raise ValueError(f"找不到工单: {ticket_id}")
        
        # 构建通知内容
        ticket_dict = {
            "id": ticket.id,
            "ticket_no": ticket.ticket_no,
            "title": ticket.title,
            "old_status": old_status,
            "new_status": new_status
        }
        
        # 创建通知
        notification_data = NotificationCreate(
            source="ticket",
            source_id=ticket_id,
            title=f"工单状态变更: {ticket.ticket_no}",
            content=f"工单 {ticket.title} 状态从 {old_status} 变更为 {new_status}",
            priority=NotificationPriority.NORMAL,
            data=ticket_dict
        )
        
        return await NotificationController.create_notification(notification_data)