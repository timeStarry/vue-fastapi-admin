from typing import List, Optional, Dict, Any
import json
import io
import sys
import logging
from datetime import datetime
from contextlib import redirect_stdout
from fastapi import HTTPException

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
                    assistant=assistant
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
    async def _call_llm(system_prompt: str, user_prompt: str, assistant: Assistant) -> str:
        """调用LLM模型获取响应"""
        # 使用uvicorn的日志器，确保日志格式一致
        logger = logging.getLogger("uvicorn")
        
        try:
            # 创建Agent实例（使用和ConversationController._create_agent相同的逻辑）
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
            
            # 根据Agno官方文档，正确创建Agent
            # 使用description和instructions来构建系统消息
            
            # 从系统提示词中提取基本描述
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
            
            # 使用简单的run调用，不传递history
            logger.debug(f"开始调用AI助手生成工单，输入: {user_prompt[:100]}...")
            response = agent.run(formatted_user_prompt)
            
            # 获取响应内容
            response_text = response.content if hasattr(response, 'content') else str(response)
            logger.debug(f"AI助手返回原始响应: {response_text[:200]}...")
            
            # 清理响应文本，确保是有效的JSON
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
                
                logger.info(f"成功生成工单核心数据: {result}")
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
                        
                        logger.info(f"通过正则提取成功获取工单核心数据: {result}")
                        return json.dumps(result, ensure_ascii=False)
                    except (json.JSONDecodeError, Exception) as e:
                        logger.error(f"提取的JSON数据无效: {str(e)}")
                        raise
                else:
                    raise  # 如果找不到JSON部分，重新抛出异常
                
        except json.JSONDecodeError as e:
            # 如果不是有效的JSON，直接构建JSON格式
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
            
            logger.info(f"使用回退机制生成工单核心数据")
            return json.dumps(ticket_json, ensure_ascii=False)
        except Exception as e:
            logger.error(f"LLM调用错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI服务调用失败: {str(e)}")


# 实例化控制器
knowledge_base_controller = KnowledgeBaseController()
document_controller = DocumentController()
assistant_controller = AssistantController()
tool_controller = ToolController()
conversation_controller = ConversationController() 