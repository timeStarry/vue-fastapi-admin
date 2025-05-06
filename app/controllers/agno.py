from typing import List, Optional, Dict, Any
import json
import io
import sys
from contextlib import redirect_stdout

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


# 实例化控制器
knowledge_base_controller = KnowledgeBaseController()
document_controller = DocumentController()
assistant_controller = AssistantController()
tool_controller = ToolController()
conversation_controller = ConversationController() 