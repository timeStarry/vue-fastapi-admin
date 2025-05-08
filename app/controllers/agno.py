from typing import List, Optional, Dict, Any
import json
import io
import sys
import logging
from datetime import datetime
from contextlib import redirect_stdout
from fastapi import HTTPException
import random

from tortoise.transactions import in_transaction

from app.models.agno_agent import (
    KnowledgeBase, Document, Assistant, Tool, 
    Conversation, Message, AssistantTool,
    KnowledgeBase_Pydantic, Document_Pydantic,
    Assistant_Pydantic, Tool_Pydantic
)
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools


class KnowledgeBaseController:
    """知识库控制器"""
    model = KnowledgeBase

    async def create_knowledge_base(self, name: str, description: Optional[str] = None) -> KnowledgeBase:
        """创建知识库"""
        return await self.model.create(
            name=name,
            description=description
        )

    async def get_knowledge_base(self, kb_id: int) -> Optional[KnowledgeBase]:
        """获取知识库"""
        return await self.model.get_or_none(id=kb_id)

    async def list_knowledge_bases(self) -> List[KnowledgeBase]:
        """列出所有知识库"""
        return await self.model.all()

    async def update_knowledge_base(self, kb_id: int, name: str = None, description: str = None) -> Optional[KnowledgeBase]:
        """更新知识库"""
        kb = await self.get_knowledge_base(kb_id)
        if not kb:
            return None
        
        if name:
            kb.name = name
        if description is not None:
            kb.description = description
        
        await kb.save()
        return kb

    async def delete_knowledge_base(self, kb_id: int) -> bool:
        """删除知识库"""
        kb = await self.get_knowledge_base(kb_id)
        if not kb:
            return False
        
        await kb.delete()
        return True


class DocumentController:
    """文档控制器"""
    model = Document

    async def add_document(self, knowledge_base_id: int, title: str, content: str, metadata: Dict = None) -> Optional[Document]:
        """添加文档到知识库"""
        kb = await KnowledgeBase.get_or_none(id=knowledge_base_id)
        if not kb:
            return None
        
        return await self.model.create(
            knowledge_base=kb,
            title=title,
            content=content,
            metadata=metadata or {}
        )

    async def get_document(self, doc_id: int) -> Optional[Document]:
        """获取文档"""
        return await self.model.get_or_none(id=doc_id)

    async def list_documents(self, knowledge_base_id: int) -> List[Document]:
        """列出知识库中的所有文档"""
        return await self.model.filter(knowledge_base_id=knowledge_base_id)

    async def update_document(self, doc_id: int, title: str = None, content: str = None, metadata: Dict = None) -> Optional[Document]:
        """更新文档"""
        doc = await self.get_document(doc_id)
        if not doc:
            return None
        
        if title:
            doc.title = title
        if content:
            doc.content = content
        if metadata:
            doc.metadata = metadata
        
        await doc.save()
        return doc

    async def delete_document(self, doc_id: int) -> bool:
        """删除文档"""
        doc = await self.get_document(doc_id)
        if not doc:
            return False
        
        await doc.delete()
        return True


class AssistantController:
    """助手控制器"""
    model = Assistant

    async def create_assistant(
        self, 
        name: str, 
        description: str, 
        model_id: str, 
        model_host: str = None, 
        configuration: Dict = None
    ) -> Assistant:
        """创建助手"""
        return await self.model.create(
            name=name,
            description=description,
            model_id=model_id,
            model_host=model_host,
            configuration=configuration or {}
        )

    async def get_assistant(self, assistant_id: int) -> Optional[Assistant]:
        """获取助手"""
        return await self.model.get_or_none(id=assistant_id)

    async def list_assistants(self) -> List[Assistant]:
        """列出所有助手"""
        return await self.model.all()

    async def update_assistant(
        self, 
        assistant_id: int, 
        name: str = None, 
        description: str = None,
        model_id: str = None,
        model_host: str = None,
        configuration: Dict = None
    ) -> Optional[Assistant]:
        """更新助手"""
        assistant = await self.get_assistant(assistant_id)
        if not assistant:
            return None
        
        if name:
            assistant.name = name
        if description is not None:
            assistant.description = description
        if model_id:
            assistant.model_id = model_id
        if model_host is not None:
            assistant.model_host = model_host
        if configuration:
            assistant.configuration = configuration
        
        await assistant.save()
        return assistant

    async def delete_assistant(self, assistant_id: int) -> bool:
        """删除助手"""
        assistant = await self.get_assistant(assistant_id)
        if not assistant:
            return False
        
        await assistant.delete()
        return True

    async def add_knowledge_base(self, assistant_id: int, kb_id: int) -> bool:
        """为助手添加知识库"""
        assistant = await self.get_assistant(assistant_id)
        kb = await KnowledgeBase.get_or_none(id=kb_id)
        
        if not assistant or not kb:
            return False
            
        await assistant.knowledge_bases.add(kb)
        return True

    async def remove_knowledge_base(self, assistant_id: int, kb_id: int) -> bool:
        """为助手移除知识库"""
        assistant = await self.get_assistant(assistant_id)
        kb = await KnowledgeBase.get_or_none(id=kb_id)
        
        if not assistant or not kb:
            return False
            
        await assistant.knowledge_bases.remove(kb)
        return True

    async def list_knowledge_bases(self, assistant_id: int) -> List[KnowledgeBase]:
        """获取助手的所有知识库"""
        assistant = await self.get_assistant(assistant_id)
        if not assistant:
            return []
            
        return await assistant.knowledge_bases.all()


class ToolController:
    """工具控制器"""
    model = Tool

    async def create_tool(self, name: str, description: str, tool_type: str, configuration: Dict = None) -> Tool:
        """创建工具"""
        return await self.model.create(
            name=name,
            description=description,
            tool_type=tool_type,
            configuration=configuration or {}
        )

    async def get_tool(self, tool_id: int) -> Optional[Tool]:
        """获取工具"""
        return await self.model.get_or_none(id=tool_id)

    async def list_tools(self) -> List[Tool]:
        """列出所有工具"""
        return await self.model.all()

    async def update_tool(
        self, 
        tool_id: int, 
        name: str = None, 
        description: str = None,
        tool_type: str = None,
        configuration: Dict = None
    ) -> Optional[Tool]:
        """更新工具"""
        tool = await self.get_tool(tool_id)
        if not tool:
            return None
        
        if name:
            tool.name = name
        if description is not None:
            tool.description = description
        if tool_type:
            tool.tool_type = tool_type
        if configuration:
            tool.configuration = configuration
        
        await tool.save()
        return tool

    async def delete_tool(self, tool_id: int) -> bool:
        """删除工具"""
        tool = await self.get_tool(tool_id)
        if not tool:
            return False
        
        await tool.delete()
        return True

    async def add_tool_to_assistant(self, assistant_id: int, tool_id: int) -> bool:
        """将工具添加到助手"""
        assistant = await Assistant.get_or_none(id=assistant_id)
        tool = await self.get_tool(tool_id)
        
        if not assistant or not tool:
            return False
            
        # 检查是否已经关联
        exist = await AssistantTool.exists(assistant_id=assistant_id, tool_id=tool_id)
        if exist:
            return True
            
        await AssistantTool.create(assistant=assistant, tool=tool)
        return True

    async def remove_tool_from_assistant(self, assistant_id: int, tool_id: int) -> bool:
        """从助手中移除工具"""
        link = await AssistantTool.get_or_none(assistant_id=assistant_id, tool_id=tool_id)
        if not link:
            return False
            
        await link.delete()
        return True

    async def list_assistant_tools(self, assistant_id: int) -> List[Tool]:
        """获取助手的所有工具"""
        assistant = await Assistant.get_or_none(id=assistant_id)
        if not assistant:
            return []
            
        links = await AssistantTool.filter(assistant_id=assistant_id).prefetch_related('tool')
        return [link.tool for link in links]


class ConversationController:
    """对话控制器"""
    model = Conversation

    async def create_conversation(self, assistant_id: int, title: str = None) -> Optional[Conversation]:
        """创建对话"""
        assistant = await Assistant.get_or_none(id=assistant_id)
        if not assistant:
            return None
            
        return await self.model.create(
            assistant=assistant,
            title=title
        )

    async def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """获取对话"""
        return await self.model.get_or_none(id=conversation_id)

    async def list_conversations(self, assistant_id: int = None) -> List[Conversation]:
        """列出对话"""
        if assistant_id:
            return await self.model.filter(assistant_id=assistant_id)
        return await self.model.all()

    async def update_conversation(self, conversation_id: int, title: str) -> Optional[Conversation]:
        """更新对话"""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None
            
        conversation.title = title
        await conversation.save()
        return conversation

    async def delete_conversation(self, conversation_id: int) -> bool:
        """删除对话"""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return False
            
        await conversation.delete()
        return True

    async def add_message(self, conversation_id: int, role: str, content: str) -> Optional[Message]:
        """添加消息到对话"""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None
            
        return await Message.create(
            conversation=conversation,
            role=role,
            content=content
        )

    async def list_messages(self, conversation_id: int) -> List[Message]:
        """获取对话的所有消息"""
        return await Message.filter(conversation_id=conversation_id).order_by('created_at')

    async def get_chat_history(self, conversation_id: int) -> List[Dict[str, str]]:
        """获取格式化的对话历史"""
        messages = await self.list_messages(conversation_id)
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    async def chat(self, conversation_id: int, message: str) -> Optional[Dict[str, Any]]:
        """与助手对话"""
        import io
        from contextlib import redirect_stdout
        
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None
            
        # 获取助手信息
        assistant = await conversation.assistant
        
        # 保存用户消息
        await self.add_message(conversation_id, "user", message)
        
        # 获取会话历史
        history = await self.get_chat_history(conversation_id)
        
        # 创建Agno Agent实例
        agent = self._create_agent(assistant)
        
        # 获取助手的知识库列表
        kb_list = await assistant.knowledge_bases.all()
        
        # 获取助手配置的工具
        tools = await ToolController().list_assistant_tools(assistant.id)
        
        # 处理工具 (如果有)
        mcp_tools = []
        for tool in tools:
            if tool.configuration:
                mcp_tools.append(self._configure_tool(tool))
        
        # 执行对话
        if mcp_tools:
            agent.tools = mcp_tools
        
        # 包含RAG知识库 (如果有)
        rag_context = ""
        if kb_list:
            rag_context = await self._get_rag_context(kb_list, message)
        
        # 使用run方法获取响应
        response_text = ""
        thinking = ""
        
        try:
            # 准备提示词
            prompt = message
            if rag_context:
                prompt = f"RAG上下文: {rag_context}\n\n用户问题: {message}"
            
            # 使用官方推荐的方法获取响应
            response = agent.run(prompt, history=history)
            response_text = response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            thinking = f"错误: {str(e)}"
            response_text = "抱歉，处理您的请求时出现错误。"
        
        # 保存助手回复
        await self.add_message(conversation_id, "assistant", response_text)
        
        # 返回结果
        return {
            "response": response_text,
            "thinking": thinking,
            "tools_used": [t.name for t in mcp_tools] if mcp_tools else []
        }
    
    def _create_agent(self, assistant: Assistant) -> Agent:
        """根据助手配置创建Agno Agent"""
        # 获取配置
        config = assistant.configuration or {}
        
        # 检查是否使用ChatAnywhere API
        use_chatanywhere = config.get('use_chatanywhere', False)
        
        if use_chatanywhere:
            # 使用ChatAnywhere API
            api_key = config.get('api_key', '')
            model_id = assistant.model_id  # 如 "deepseek", "gpt-3.5-turbo", "gpt-4o-mini"
            
            model = OpenAIChat(
                id=model_id,
                api_key=api_key,
                base_url="https://api.chatanywhere.tech/v1"
            )
        else:
            # 回退到原来的Ollama
            from agno.models.ollama import Ollama
            model_kwargs = {}
            if assistant.model_host:
                model_kwargs["host"] = assistant.model_host
                
            model = Ollama(id=assistant.model_id, **model_kwargs)
        
        return Agent(
            model=model,
            markdown=config.get("markdown", True)
        )
    
    def _configure_tool(self, tool: Tool):
        """根据工具配置创建MCP工具"""
        try:
            # Agno 1.4.4版本的工具实现可能与文档不同
            # 暂时不实现工具功能，返回None
            return None
        except Exception as e:
            # 记录错误并返回None
            print(f"工具配置错误: {str(e)}")
            return None
    
    async def _get_rag_context(self, kb_list: List[KnowledgeBase], query: str) -> str:
        """获取RAG知识库上下文"""
        # 简单实现：获取所有知识库中的文档内容
        # 在实际应用中，这里应该使用向量数据库进行相似度查询
        contexts = []
        for kb in kb_list:
            docs = await Document.filter(knowledge_base=kb)
            for doc in docs:
                contexts.append(f"标题: {doc.title}\n内容: {doc.content}")
        
        # 返回拼接的上下文
        return "\n\n".join(contexts)


class AgnoController:
    """AI助手总控制器"""
    kb_controller = KnowledgeBaseController()
    doc_controller = DocumentController()
    assistant_controller = AssistantController()
    tool_controller = ToolController()
    conversation_controller = ConversationController()

    # 添加生成系统报告方法
    @staticmethod
    async def generate_system_report(system_data: Dict[str, Any]) -> Dict[str, Any]:
        """调用AI助手生成系统智能报告"""
        logger = logging.getLogger("uvicorn")
        logger.info(f"AgnoController.generate_system_report方法开始执行, 输入数据类型: {type(system_data)}")
        
        if not isinstance(system_data, dict):
            logger.error(f"输入数据不是字典: {system_data}")
            return {
                "title": "网络运行状况智能分析报告",
                "content": "# 网络运行状况智能分析报告\n\n生成报告失败: 输入数据格式错误。",
                "created_at": datetime.now().isoformat()
            }
        
        # 检查必要的系统数据
        logger.info(f"系统数据键: {list(system_data.keys())}")
        if "system_info" not in system_data or "ticket_info" not in system_data:
            logger.error("系统数据缺少必要的键: system_info或ticket_info")
            return {
                "title": "网络运行状况智能分析报告",
                "content": "# 网络运行状况智能分析报告\n\n生成报告失败: 缺少必要的系统数据。",
                "created_at": datetime.now().isoformat()
            }
        
        # 准备系统数据
        try:
            logger.info("准备系统数据JSON")
            
            # 精简系统数据，只保留必要的字段以减少token使用
            simplified_data = {
                "system_summary": {
                    "hosts": system_data.get("system_info", {}).get("host_count", 0),
                    "services": system_data.get("system_info", {}).get("service_count", 0),
                    "users": system_data.get("system_info", {}).get("user_count", 0),
                    "alerts": system_data.get("system_info", {}).get("alert_count", 0)
                },
                "tickets": {
                    "total": system_data.get("ticket_info", {}).get("total_count", 0),
                    "pending": system_data.get("ticket_info", {}).get("pending_count", 0),
                    "completed": system_data.get("ticket_info", {}).get("completed_count", 0),
                    "distribution": system_data.get("ticket_info", {}).get("type_distribution", [])[:5]  # 只取前5种类型
                },
                "service_status": system_data.get("service_status", [])[:10],  # 只取前10条服务状态
                "recent_alerts": system_data.get("recent_alerts", [])[:5],     # 只取前5条告警
                "recent_logs": system_data.get("recent_logs", [])[:5],         # 只取前5条日志
                "assistants": system_data.get("assistants", [])[:3]            # 只取前3个助手
            }
            
            system_data_json = json.dumps(simplified_data, ensure_ascii=False, indent=2)
            logger.info(f"精简后的系统数据JSON长度: {len(system_data_json)}")
            
            # 简化提示词模板，减少token使用
            short_prompt_template = """你是专业系统分析师，请根据以下数据生成运行报告：
            
1. 系统概览：主机、服务、用户、告警数据分析
2. 工单处理：工单数量、分布和完成率
3. 告警分析：告警严重程度和分布
4. 服务状态：运行状态分析和建议

格式：Markdown，标题使用#，突出关键数据和结论。

系统数据："""
            
            # 使用简化的提示词模板，避免使用格式占用过多token
            report_prompt = short_prompt_template + "\n" + system_data_json + "\n\n请生成标题为\"网络运行状况智能分析报告\"的完整分析报告。"
            logger.info(f"简化后的提示词长度: {len(report_prompt)}")
            
            # 估算token数量（粗略估计，英文约1.3字符/token，中文约2字符/token）
            est_tokens = len(report_prompt) / 1.5  # 混合中英文的粗略估计
            logger.info(f"估计token数量: {int(est_tokens)}")
            
            # 如果预估token数量仍然很大，再次缩减数据
            if est_tokens > 3500:  # 留出一些余量，确保不超过4096限制
                logger.warning("预估token数量过大，无法调用AI生成报告")
                # 返回特殊标识，通知前端使用纯前端报告方案
                return {
                    "title": "网络运行状况智能分析报告",
                    "content": "USE_FRONTEND_REPORT",
                    "created_at": datetime.now().isoformat(),
                    "status": "frontend_fallback"  # 特殊状态标识
                }
                
                # 注释掉原来的本地生成报告和极简提示词部分
                '''
                # 数据极度精简的情况下，使用本地生成的高质量报告模板
                hosts = simplified_data["system_summary"]["hosts"]
                services = simplified_data["system_summary"]["services"]
                users = simplified_data["system_summary"]["users"]
                alerts = simplified_data["system_summary"]["alerts"]
                total_tickets = simplified_data["tickets"]["total"]
                pending_tickets = simplified_data["tickets"]["pending"]
                completed_tickets = simplified_data["tickets"]["completed"]
                
                # 计算一些有用的派生指标
                online_ratio = round(0.9, 2)  # 模拟90%的主机在线
                online_hosts = int(hosts * online_ratio)
                completion_rate = round((completed_tickets / total_tickets * 100) if total_tickets > 0 else 0, 1)
                system_health = "良好" if alerts < 5 else "需要关注" if alerts < 10 else "警告"
                estimated_uptime = random.randint(180, 365)  # 模拟180-365天的运行时间
                
                # 生成自定义高质量报告
                custom_report = f"""# 网络运行状况智能分析报告

## 1. 系统概览

当前系统共有 **{hosts}** 台主机，**{services}** 个服务，**{users}** 个用户账户。系统整体健康状态为**{system_health}**，已连续运行 **{estimated_uptime}** 天。

- 主机在线率: **{online_ratio*100}%** ({online_hosts}/{hosts})
- 服务可用性: **{random.randint(97, 100)}%**
- 系统负载: **{random.randint(20, 60)}%**

## 2. 工单处理情况

系统当前共有 **{total_tickets}** 个工单，其中 **{pending_tickets}** 个待处理，**{completed_tickets}** 个已完成。工单完成率为 **{completion_rate}%**。

工单类型分布:
- 故障报修: **{random.randint(20, 40)}%**
- 资源申请: **{random.randint(20, 40)}%**
- 配置变更: **{random.randint(10, 20)}%**
- 其他类型: **{random.randint(5, 20)}%**

平均工单处理时间: **{random.randint(6, 24)}** 小时

## 3. 告警情况

当前系统共有 **{alerts}** 个告警，其中:
- 严重级别: **{random.randint(0, 2)}** 个
- 高级别: **{random.randint(0, 3)}** 个
- 中级别: **{random.randint(1, 5)}** 个
- 低级别: **{random.randint(2, 10)}** 个

主要告警来源为网络设备和应用服务器，建议关注网络连接稳定性和应用服务性能。

## 4. 优化建议

1. **系统维护**: 建议对已运行 {estimated_uptime} 天的系统进行例行维护检查
2. **工单处理**: 提高工单响应速度，特别是针对当前 {pending_tickets} 个待处理工单
3. **告警管理**: 建立更完善的告警分级响应机制，优先处理高优先级告警
4. **资源规划**: 基于当前 {hosts} 台主机的使用情况，评估是否需要扩容

## 5. 总结

系统整体运行{system_health}，主要关注点应放在工单响应时间和告警处理上。建议定期进行系统巡检和性能优化，确保系统持续稳定运行。
"""
                
                logger.info("使用本地生成的高质量报告模板替代极简AI生成内容")
                return {
                    "title": "网络运行状况智能分析报告",
                    "content": custom_report,
                    "created_at": datetime.now().isoformat()
                }
                
                # 极简提示词
                minimal_prompt = """作为系统分析师，根据以下数据生成简短的运行报告：

数据：""" + system_data_json + "\n\n请用Markdown格式生成标题为\"网络运行状况智能分析报告\"的简明分析报告。"
                
                report_prompt = minimal_prompt
                est_tokens = len(report_prompt) / 1.5
                logger.info(f"极简提示词长度: {len(report_prompt)}, 估计token: {int(est_tokens)}")
                '''
            
        except Exception as e:
            logger.error(f"准备系统数据时出错: {str(e)}", exc_info=True)
            return {
                "title": "网络运行状况智能分析报告",
                "content": f"# 网络运行状况智能分析报告\n\n生成报告时发生错误: 数据格式化失败: {str(e)}",
                "created_at": datetime.now().isoformat()
            }
        
        try:
            # 获取助手
            logger.info("尝试获取活跃的AI助手")
            assistant = await Assistant.filter(is_active=True).first()
            if not assistant:
                logger.warning("未找到可用的AI助手，无法生成系统报告")
                return {
                    "title": "网络运行状况智能分析报告",
                    "content": "# 网络运行状况智能分析报告\n\n无法连接AI助手生成报告，请检查系统配置。",
                    "created_at": datetime.now().isoformat()
                }
            
            logger.info(f"找到活跃的AI助手: id={assistant.id}, name={assistant.name}, model_id={assistant.model_id}")
                
            # 调用AI生成报告
            logger.info("开始调用AI生成系统报告")
            try:
                logger.info("调用_call_llm方法")
                report_content = await AgnoController._call_llm(
                    system_prompt="您是一个专业的系统分析师，擅长数据分析和可视化。请生成详细的系统运行分析报告。",
                    user_prompt=report_prompt,
                    assistant=assistant,
                    output_format="text"  # 明确指定输出格式为文本
                )
                
                logger.info(f"AI生成的报告内容类型: {type(report_content)}, 长度: {len(report_content) if isinstance(report_content, str) else 'N/A'}")
                
                if not report_content or not isinstance(report_content, str):
                    logger.error(f"AI生成的报告内容无效: {report_content}")
                    # 返回特殊标识，通知前端使用纯前端报告方案
                    return {
                        "title": "网络运行状况智能分析报告",
                        "content": "USE_FRONTEND_REPORT",
                        "created_at": datetime.now().isoformat(),
                        "status": "frontend_fallback",  # 特殊状态标识
                        "error": str(report_content)  # 添加错误信息，便于调试
                    }
                    
                # 限制内容长度，避免过大的响应
                if len(report_content) > 100000:  # 限制为约100KB
                    logger.warning(f"报告内容过长({len(report_content)}字符)，进行截断")
                    report_content = report_content[:100000] + "\n\n...(报告过长，已截断)"
                
            except Exception as e:
                logger.error(f"调用AI生成报告失败: {str(e)}", exc_info=True)
                # 返回特殊标识，通知前端使用纯前端报告方案
                return {
                    "title": "网络运行状况智能分析报告",
                    "content": "USE_FRONTEND_REPORT",
                    "created_at": datetime.now().isoformat(),
                    "status": "frontend_fallback",  # 特殊状态标识
                    "error": str(e)  # 添加错误信息，便于调试
                }
            
            logger.info("系统报告内容生成完成")
            
            # 构建返回数据
            logger.info("构建返回数据")
            result = {
                "title": "网络运行状况智能分析报告",
                "content": report_content,
                "created_at": datetime.now().isoformat()
            }
            
            # 检查结果数据
            logger.info(f"返回数据: title={result['title']}, content长度={len(result['content'])}, created_at={result['created_at']}")
            
            # 返回报告数据
            return result
                
        except Exception as e:
            logger.error(f"生成系统报告失败: {str(e)}", exc_info=True)
            error_report = {
                "title": "网络运行状况智能分析报告",
                "content": f"# 网络运行状况智能分析报告\n\n生成报告时发生错误: {str(e)}",
                "created_at": datetime.now().isoformat()
            }
            logger.info("返回错误报告")
            return error_report

    # 添加工单生成方法
    @staticmethod
    async def generate_ticket_data(description: str) -> Dict[str, Any]:
        """调用AI助手生成工单数据"""
        logger = logging.getLogger("uvicorn")
        
        # 读取提示词模板
        try:
            with open("ticket_prompt.md", "r", encoding="utf-8") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            # 如果找不到文件，使用内置的简化提示词
            logger.warning("ticket_prompt.md not found, using simplified prompt")
            prompt_template = """
            你是一个IT运维助手，根据描述生成工单信息。返回JSON格式，包含以下字段：
            title, description, type (fault/task/request), 
            status (pending), priority (critical/high/medium/low), 
            expected_time (ISO格式), assignee_id (可选)
            
            重要：只返回JSON对象，不要包含任何其他文本或解释。
            """
        
        # 构建系统提示词和用户输入
        system_prompt = prompt_template
        user_input = description
        
        # 与AI助手对话
        assistant = await Assistant.filter(is_active=True).first()
        if not assistant:
            # 如果没有激活的助手，使用回退方案生成基本工单
            logger.warning("未找到可用的AI助手，使用默认工单数据")
            return {
                "title": f"工单请求: {description[:30]}...",
                "description": description,
                "type": "task",
                "status": "pending",
                "priority": "medium",
                "expected_time": datetime.now().isoformat()
            }
        
        try:
            # 调用AI接口
            try:
                completion = await AgnoController._call_llm(
                    system_prompt=system_prompt,
                    user_prompt=user_input,
                    assistant=assistant,
                    output_format="json"  # 明确指定输出格式为JSON
                )
                
                logger.debug(f"AI生成的原始响应: {completion}")
                
                # _call_llm方法现在已经确保返回有效的JSON字符串
                ticket_data = json.loads(completion)
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"AI响应处理错误: {str(e)}")
                # 使用基本工单数据作为回退方案
                return {
                    "title": f"工单请求: {description[:30]}..." if len(description) > 30 else description,
                    "description": description,
                    "type": "task",
                    "status": "pending",
                    "priority": "medium",
                    "expected_time": datetime.now().isoformat()
                }
            
            # 验证必要字段
            required_fields = ["title", "description", "type", "priority"]
            for field in required_fields:
                if field not in ticket_data:
                    logger.warning(f"AI生成的工单数据缺少必要字段: {field}，将使用默认值")
                    # 设置默认值
                    if field == "title":
                        ticket_data["title"] = f"工单请求: {description[:30]}..." if len(description) > 30 else description
                    elif field == "description":
                        ticket_data["description"] = description
                    elif field == "type":
                        ticket_data["type"] = "task"
                    elif field == "priority":
                        ticket_data["priority"] = "medium"
            
            # 确保字段类型正确
            if ticket_data.get("expected_time") and not isinstance(ticket_data["expected_time"], str):
                ticket_data["expected_time"] = datetime.now().isoformat()
            elif not ticket_data.get("expected_time"):
                # 如果没有expected_time字段，添加一个默认值
                ticket_data["expected_time"] = datetime.now().isoformat()
            
            # 移除AI可能添加的工单号，由系统生成
            if "ticket_no" in ticket_data:
                del ticket_data["ticket_no"]
                
            # 确保状态为pending
            ticket_data["status"] = "pending"
            
            # 验证工单类型是否合法
            valid_types = ["fault", "task", "request", "resource", "config", "maintenance", "emergency"]
            if ticket_data.get("type") not in valid_types:
                ticket_data["type"] = "task"  # 默认为task类型
                
            # 验证优先级是否合法
            valid_priorities = ["critical", "high", "medium", "low", "urgent"]
            if ticket_data.get("priority") not in valid_priorities:
                ticket_data["priority"] = "medium"  # 默认为medium优先级
            
            # 限制标题长度
            if len(ticket_data.get("title", "")) > 100:
                ticket_data["title"] = ticket_data["title"][:97] + "..."
                
            # 确保description不为空
            if not ticket_data.get("description"):
                ticket_data["description"] = description
                
            return ticket_data
        except Exception as e:
            logger.error(f"生成工单数据错误: {str(e)}")
            # 返回基本工单数据而不是抛出异常
            return {
                "title": f"工单请求: {description[:30]}..." if len(description) > 30 else description,
                "description": description,
                "type": "task",
                "status": "pending",
                "priority": "medium",
                "expected_time": datetime.now().isoformat()
            }
    
    @staticmethod
    async def _call_llm(system_prompt: str, user_prompt: str, assistant: Assistant, output_format: str = "text") -> str:
        """调用LLM模型获取响应
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            assistant: 助手对象
            output_format: 输出格式，可以是 "text" 或 "json"
            
        Returns:
            str: 如果 output_format 为 "text"，则返回文本内容；如果为 "json"，则返回 JSON 字符串
        """
        # 使用uvicorn的日志器，确保日志格式一致
        logger = logging.getLogger("uvicorn")
        
        try:
            # 创建Agent实例
            # 获取配置
            config = assistant.configuration or {}
            
            # 检查是否使用ChatAnywhere API
            use_chatanywhere = config.get('use_chatanywhere', False)
            
            if use_chatanywhere:
                # 使用ChatAnywhere API
                api_key = config.get('api_key', '')
                model_id = assistant.model_id  # 如 "deepseek", "gpt-3.5-turbo", "gpt-4o-mini"
                
                model = OpenAIChat(
                    id=model_id,
                    api_key=api_key,
                    base_url="https://api.chatanywhere.tech/v1"
                )
            else:
                # 回退到原来的Ollama
                from agno.models.ollama import Ollama
                model_kwargs = {}
                if assistant.model_host:
                    model_kwargs["host"] = assistant.model_host
                    
                model = Ollama(id=assistant.model_id, **model_kwargs)
            
            # 创建Agent
            # 根据输出格式配置不同的说明
            if output_format == "json":
                # 为JSON输出配置
                description = "你是一个专业的IT运维助手，负责根据用户的简短描述生成工单基本信息。"
                
                # 定义明确的指令列表，只关注核心字段
                instructions = [
                    "你需要生成一个JSON格式的对象，仅包含以下四个核心字段：title、description、type、priority",
                    "title: 简短明确的工单标题，20字以内",
                    "description: 详细的工单描述，包含问题的具体表现、影响范围等信息",
                    "type: 工单类型，必须是以下值之一：fault(故障报修), resource(资源申请), config(配置变更), maintenance(日常维护), emergency(紧急处理)",
                    "priority: 工单优先级，必须是以下值之一: low(低), medium(中), high(高), urgent(紧急)",
                    "不要生成其他字段，如expected_time、assignee_id等，这些将由系统自动生成",
                    "不要包含任何代码块标记或额外文本，仅返回JSON数据"
                ]
                
                # 添加精简的提示词内容作为额外上下文
                additional_context = """
根据描述判断工单类型：
- 含有"故障"、"错误"、"无法访问"、"失败"等词汇，判断为 fault
- 含有"申请"、"请求"、"需要"、"资源"等词汇，判断为 resource
- 含有"更新"、"维护"、"检查"等词汇，判断为 maintenance
- 含有"配置"、"设置"、"修改"等词汇，判断为 config
- 含有"紧急"、"立即"、"严重"等词汇，判断为 emergency

根据描述判断优先级：
- 含有"紧急"、"严重"、"立即"、"无法工作"等词汇，判断为 urgent
- 含有"重要"、"尽快"、"影响使用"等词汇，判断为 high
- 含有"优化"、"改进"等词汇，判断为 medium
- 默认为 low
"""
                # 创建Agent，禁用markdown避免格式化干扰
                agent = Agent(
                    model=model,
                    description=description,
                    instructions=instructions,
                    additional_context=additional_context,
                    markdown=False
                )
                
                # 增强用户提示，明确要求生成四个核心字段
                formatted_user_prompt = f"根据以下描述，生成一个包含title、description、type、priority四个字段的工单：{user_prompt}"
            else:
                # 为文本输出配置
                description = system_prompt
                # 对于文本输出，我们希望保持原始的格式化
                agent = Agent(
                    model=model,
                    description=description,
                    markdown=True
                )
                formatted_user_prompt = user_prompt
            
            # 使用简单的run调用，不传递history
            logger.debug(f"开始调用AI助手，输入: {formatted_user_prompt[:100]}...")
            response = agent.run(formatted_user_prompt)
            
            # 获取响应内容
            response_text = response.content if hasattr(response, 'content') else str(response)
            logger.debug(f"AI助手返回原始响应: {response_text[:200]}...")
            
            # 根据输出格式处理响应
            if output_format == "json":
                # 处理JSON格式输出
                response_text = response_text.strip()
                
                # 移除可能的Markdown JSON代码块标记
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                elif response_text.startswith("```"):
                    response_text = response_text[3:]
                
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                    
                response_text = response_text.strip()
                
                # 尝试解析JSON来验证格式是否正确
                try:
                    json_data = json.loads(response_text)
                    # 确保只包含需要的四个字段，移除多余字段
                    result = {
                        "title": json_data.get("title", ""),
                        "description": json_data.get("description", ""),
                        "type": json_data.get("type", "task"),
                        "priority": json_data.get("priority", "medium")
                    }
                    
                    # 验证字段值是否有效
                    valid_types = ["fault", "resource", "config", "maintenance", "emergency"]
                    if result["type"] not in valid_types:
                        result["type"] = "task"
                    
                    valid_priorities = ["low", "medium", "high", "urgent"]
                    if result["priority"] not in valid_priorities:
                        result["priority"] = "medium"
                    
                    logger.info("成功生成JSON数据")
                    return json.dumps(result, ensure_ascii=False)
                    
                except json.JSONDecodeError:
                    # 尝试查找文本中的JSON部分
                    import re
                    json_pattern = r'(\{[\s\S]*\})'
                    match = re.search(json_pattern, response_text)
                    if match:
                        try:
                            json_part = match.group(1)
                            # 检验找到的JSON是否有效
                            json_data = json.loads(json_part)
                            # 同样确保只包含需要的四个字段
                            result = {
                                "title": json_data.get("title", ""),
                                "description": json_data.get("description", ""),
                                "type": json_data.get("type", "task"),
                                "priority": json_data.get("priority", "medium")
                            }
                            
                            # 验证字段值是否有效
                            valid_types = ["fault", "resource", "config", "maintenance", "emergency"]
                            if result["type"] not in valid_types:
                                result["type"] = "task"
                            
                            valid_priorities = ["low", "medium", "high", "urgent"]
                            if result["priority"] not in valid_priorities:
                                result["priority"] = "medium"
                            
                            logger.info("通过正则提取成功获取JSON数据")
                            return json.dumps(result, ensure_ascii=False)
                        except (json.JSONDecodeError, Exception) as e:
                            logger.error(f"提取的JSON数据无效: {str(e)}")
                            raise
                    else:
                        # 如果找不到JSON部分，生成一个简单的JSON
                        title = user_prompt[:20] + "..." if len(user_prompt) > 20 else user_prompt
                        
                        # 只包含四个核心字段
                        ticket_json = {
                            "title": f"工单: {title}",
                            "description": user_prompt,
                            "type": "fault" if any(kw in user_prompt.lower() for kw in ["故障", "错误", "问题", "无法"]) else "task",
                            "priority": "medium"
                        }
                        
                        logger.info("使用回退机制生成JSON数据")
                        return json.dumps(ticket_json, ensure_ascii=False)
            else:
                # 对于文本输出，直接返回响应内容
                return response_text
                
        except json.JSONDecodeError as e:
            # 如果不是有效的JSON，但我们需要JSON格式
            if output_format == "json":
                logger.error(f"AI返回的不是有效JSON: {str(e)}, 原始内容: {response_text[:200]}...")
                
                # 构建简单的工单数据，确保响应格式始终是有效的JSON
                title = user_prompt[:20] + "..." if len(user_prompt) > 20 else user_prompt
                
                # 只包含四个核心字段
                ticket_json = {
                    "title": f"工单: {title}",
                    "description": user_prompt,
                    "type": "fault" if any(kw in user_prompt.lower() for kw in ["故障", "错误", "问题", "无法"]) else "task",
                    "priority": "medium"
                }
                
                logger.info("使用回退机制生成JSON数据")
                return json.dumps(ticket_json, ensure_ascii=False)
            else:
                # 对于文本输出，返回错误消息
                error_message = f"AI服务返回的内容格式有误: {str(e)}"
                logger.error(error_message)
                return f"生成内容时发生错误: {error_message}"
        except Exception as e:
            logger.error(f"LLM调用错误: {str(e)}")
            error_message = f"AI服务调用失败: {str(e)}"
            
            if output_format == "json":
                # 对于JSON输出，返回一个有效的JSON
                error_json = {
                    "title": "错误",
                    "description": error_message,
                    "type": "fault",
                    "priority": "high"
                }
                return json.dumps(error_json, ensure_ascii=False)
            else:
                # 对于文本输出，返回错误消息
                return f"生成内容时发生错误: {error_message}"


# 实例化控制器
knowledge_base_controller = KnowledgeBaseController()
document_controller = DocumentController()
assistant_controller = AssistantController()
tool_controller = ToolController()
conversation_controller = ConversationController() 