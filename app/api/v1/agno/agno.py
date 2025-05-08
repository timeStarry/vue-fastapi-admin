from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import logging

from app.controllers.agno import (
    knowledge_base_controller, 
    document_controller,
    assistant_controller, 
    tool_controller,
    conversation_controller,
    AgnoController
)
from app.models.agno_agent import (
    KnowledgeBase_Pydantic, 
    Document_Pydantic,
    Assistant_Pydantic, 
    Tool_Pydantic,
    Conversation_Pydantic,
    Message_Pydantic
)
from app.schemas.base import Success, Fail, SuccessExtra

router = APIRouter()

# 请求/响应模型
class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None

class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class DocumentCreate(BaseModel):
    title: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AssistantCreate(BaseModel):
    name: str
    description: str
    model_id: str
    model_host: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None

class AssistantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    model_id: Optional[str] = None
    model_host: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None

class ToolCreate(BaseModel):
    name: str
    description: str
    tool_type: str
    configuration: Optional[Dict[str, Any]] = None

class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tool_type: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None

class ConversationCreate(BaseModel):
    assistant_id: int
    title: Optional[str] = None

class ConversationUpdate(BaseModel):
    title: str

class MessageCreate(BaseModel):
    content: str

class ChatResponse(BaseModel):
    response: str
    thinking: Optional[str] = None
    tools_used: List[str] = []

# 系统报告相关模型
class SystemReportRequest(BaseModel):
    system_info: Dict[str, Any]
    ticket_info: Dict[str, Any]
    service_status: List[Dict[str, Any]] = []
    recent_alerts: List[Dict[str, Any]] = []
    recent_logs: List[Dict[str, Any]] = []
    assistants: List[Dict[str, Any]] = []

class SystemReportResponse(BaseModel):
    title: str
    content: str
    created_at: Optional[str] = None

# 知识库管理路由
@router.post("/knowledge-bases", summary="创建知识库")
async def create_knowledge_base(kb: KnowledgeBaseCreate):
    """创建知识库"""
    result = await knowledge_base_controller.create_knowledge_base(name=kb.name, description=kb.description)
    return Success(data=KnowledgeBase_Pydantic.model_validate(result).model_dump())

@router.get("/knowledge-bases", summary="列出所有知识库")
async def list_knowledge_bases():
    """列出所有知识库"""
    result = await knowledge_base_controller.list_knowledge_bases()
    return Success(data=[KnowledgeBase_Pydantic.model_validate(kb).model_dump() for kb in result])

@router.get("/knowledge-bases/{kb_id}", summary="获取知识库详情")
async def get_knowledge_base(kb_id: int):
    """获取知识库详情"""
    kb = await knowledge_base_controller.get_knowledge_base(kb_id)
    if not kb:
        return Fail(code=404, msg="知识库不存在")
    return Success(data=KnowledgeBase_Pydantic.model_validate(kb).model_dump())

@router.put("/knowledge-bases/{kb_id}", summary="更新知识库")
async def update_knowledge_base(kb_id: int, kb_update: KnowledgeBaseUpdate):
    """更新知识库"""
    kb = await knowledge_base_controller.update_knowledge_base(
        kb_id=kb_id, 
        name=kb_update.name, 
        description=kb_update.description
    )
    if not kb:
        return Fail(code=404, msg="知识库不存在")
    return Success(data=KnowledgeBase_Pydantic.model_validate(kb).model_dump())

@router.delete("/knowledge-bases/{kb_id}", summary="删除知识库")
async def delete_knowledge_base(kb_id: int):
    """删除知识库"""
    result = await knowledge_base_controller.delete_knowledge_base(kb_id)
    if not result:
        return Fail(code=404, msg="知识库不存在")
    return Success(msg="删除成功")

# 文档管理路由
@router.post("/knowledge-bases/{kb_id}/documents", summary="添加文档到知识库")
async def add_document(kb_id: int, document: DocumentCreate):
    """添加文档到知识库"""
    doc = await document_controller.add_document(
        knowledge_base_id=kb_id,
        title=document.title,
        content=document.content,
        metadata=document.metadata
    )
    if not doc:
        return Fail(code=404, msg="知识库不存在")
    return Success(data=Document_Pydantic.model_validate(doc).model_dump())

@router.get("/knowledge-bases/{kb_id}/documents", summary="列出知识库中的所有文档")
async def list_documents(kb_id: int):
    """列出知识库中的所有文档"""
    docs = await document_controller.list_documents(knowledge_base_id=kb_id)
    return Success(data=[Document_Pydantic.model_validate(doc).model_dump() for doc in docs])

@router.get("/documents/{doc_id}", summary="获取文档详情")
async def get_document(doc_id: int):
    """获取文档详情"""
    doc = await document_controller.get_document(doc_id)
    if not doc:
        return Fail(code=404, msg="文档不存在")
    return Success(data=Document_Pydantic.model_validate(doc).model_dump())

@router.put("/documents/{doc_id}", summary="更新文档")
async def update_document(doc_id: int, document: DocumentUpdate):
    """更新文档"""
    doc = await document_controller.update_document(
        doc_id=doc_id,
        title=document.title,
        content=document.content,
        metadata=document.metadata
    )
    if not doc:
        return Fail(code=404, msg="文档不存在")
    return Success(data=Document_Pydantic.model_validate(doc).model_dump())

@router.delete("/documents/{doc_id}", summary="删除文档")
async def delete_document(doc_id: int):
    """删除文档"""
    result = await document_controller.delete_document(doc_id)
    if not result:
        return Fail(code=404, msg="文档不存在")
    return Success(msg="删除成功")

# 助手管理路由
@router.post("/assistants", summary="创建助手")
async def create_assistant(assistant: AssistantCreate):
    """创建助手"""
    result = await assistant_controller.create_assistant(
        name=assistant.name,
        description=assistant.description,
        model_id=assistant.model_id,
        model_host=assistant.model_host,
        configuration=assistant.configuration
    )
    return Success(data=Assistant_Pydantic.model_validate(result).model_dump())

@router.get("/assistants", summary="列出所有助手")
async def list_assistants():
    """列出所有助手"""
    assistants = await assistant_controller.list_assistants()
    return Success(data=[Assistant_Pydantic.model_validate(assistant).model_dump() for assistant in assistants])

@router.get("/assistants/{assistant_id}", summary="获取助手详情")
async def get_assistant(assistant_id: int):
    """获取助手详情"""
    assistant = await assistant_controller.get_assistant(assistant_id)
    if not assistant:
        return Fail(code=404, msg="助手不存在")
    return Success(data=Assistant_Pydantic.model_validate(assistant).model_dump())

@router.put("/assistants/{assistant_id}", summary="更新助手")
async def update_assistant(assistant_id: int, assistant_update: AssistantUpdate):
    """更新助手"""
    assistant = await assistant_controller.update_assistant(
        assistant_id=assistant_id,
        name=assistant_update.name,
        description=assistant_update.description,
        model_id=assistant_update.model_id,
        model_host=assistant_update.model_host,
        configuration=assistant_update.configuration
    )
    if not assistant:
        return Fail(code=404, msg="助手不存在")
    return Success(data=Assistant_Pydantic.model_validate(assistant).model_dump())

@router.delete("/assistants/{assistant_id}", summary="删除助手")
async def delete_assistant(assistant_id: int):
    """删除助手"""
    result = await assistant_controller.delete_assistant(assistant_id)
    if not result:
        return Fail(code=404, msg="助手不存在")
    return Success(msg="删除成功")

@router.post("/assistants/{assistant_id}/knowledge-bases/{kb_id}", summary="为助手添加知识库")
async def add_knowledge_base_to_assistant(assistant_id: int, kb_id: int):
    """为助手添加知识库"""
    result = await assistant_controller.add_knowledge_base(assistant_id, kb_id)
    if not result:
        return Fail(code=404, msg="助手或知识库不存在")
    return Success(msg="添加成功")

@router.delete("/assistants/{assistant_id}/knowledge-bases/{kb_id}", summary="为助手移除知识库")
async def remove_knowledge_base_from_assistant(assistant_id: int, kb_id: int):
    """为助手移除知识库"""
    result = await assistant_controller.remove_knowledge_base(assistant_id, kb_id)
    if not result:
        return Fail(code=404, msg="助手或知识库不存在或未关联")
    return Success(msg="移除成功")

@router.get("/assistants/{assistant_id}/knowledge-bases", summary="获取助手的所有知识库")
async def list_assistant_knowledge_bases(assistant_id: int):
    """获取助手的所有知识库"""
    assistant = await assistant_controller.get_assistant(assistant_id)
    if not assistant:
        return Fail(code=404, msg="助手不存在")
    kb_list = await assistant_controller.list_knowledge_bases(assistant_id)
    return Success(data=[KnowledgeBase_Pydantic.model_validate(kb).model_dump() for kb in kb_list])

# 工具管理路由
@router.post("/tools", summary="创建工具")
async def create_tool(tool: ToolCreate):
    """创建工具"""
    result = await tool_controller.create_tool(
        name=tool.name,
        description=tool.description,
        tool_type=tool.tool_type,
        configuration=tool.configuration
    )
    return Success(data=Tool_Pydantic.model_validate(result).model_dump())

@router.get("/tools", summary="列出所有工具")
async def list_tools():
    """列出所有工具"""
    tools = await tool_controller.list_tools()
    return Success(data=[Tool_Pydantic.model_validate(tool).model_dump() for tool in tools])

@router.get("/tools/{tool_id}", summary="获取工具详情")
async def get_tool(tool_id: int):
    """获取工具详情"""
    tool = await tool_controller.get_tool(tool_id)
    if not tool:
        return Fail(code=404, msg="工具不存在")
    return Success(data=Tool_Pydantic.model_validate(tool).model_dump())

@router.put("/tools/{tool_id}", summary="更新工具")
async def update_tool(tool_id: int, tool_update: ToolUpdate):
    """更新工具"""
    tool = await tool_controller.update_tool(
        tool_id=tool_id,
        name=tool_update.name,
        description=tool_update.description,
        tool_type=tool_update.tool_type,
        configuration=tool_update.configuration
    )
    if not tool:
        return Fail(code=404, msg="工具不存在")
    return Success(data=Tool_Pydantic.model_validate(tool).model_dump())

@router.delete("/tools/{tool_id}", summary="删除工具")
async def delete_tool(tool_id: int):
    """删除工具"""
    result = await tool_controller.delete_tool(tool_id)
    if not result:
        return Fail(code=404, msg="工具不存在")
    return Success(msg="删除成功")

@router.post("/assistants/{assistant_id}/tools/{tool_id}", summary="为助手添加工具")
async def add_tool_to_assistant(assistant_id: int, tool_id: int):
    """为助手添加工具"""
    result = await tool_controller.add_tool_to_assistant(assistant_id, tool_id)
    if not result:
        return Fail(code=404, msg="助手或工具不存在")
    return Success(msg="添加成功")

@router.delete("/assistants/{assistant_id}/tools/{tool_id}", summary="为助手移除工具")
async def remove_tool_from_assistant(assistant_id: int, tool_id: int):
    """为助手移除工具"""
    result = await tool_controller.remove_tool_from_assistant(assistant_id, tool_id)
    if not result:
        return Fail(code=404, msg="助手或工具不存在或未关联")
    return Success(msg="移除成功")

@router.get("/assistants/{assistant_id}/tools", summary="获取助手的所有工具")
async def list_assistant_tools(assistant_id: int):
    """获取助手的所有工具"""
    assistant = await assistant_controller.get_assistant(assistant_id)
    if not assistant:
        return Fail(code=404, msg="助手不存在")
    tools = await tool_controller.list_assistant_tools(assistant_id)
    return Success(data=[Tool_Pydantic.model_validate(tool).model_dump() for tool in tools])

# 对话管理路由
@router.post("/conversations", summary="创建对话")
async def create_conversation(conversation: ConversationCreate):
    """创建对话"""
    conv = await conversation_controller.create_conversation(
        assistant_id=conversation.assistant_id,
        title=conversation.title
    )
    if not conv:
        return Fail(code=404, msg="助手不存在")
    return Success(data=Conversation_Pydantic.model_validate(conv).model_dump())

@router.get("/conversations", summary="列出所有对话")
async def list_conversations(
    assistant_id: Optional[int] = Query(None, description="助手ID"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量")
):
    """列出所有对话"""
    conversations = await conversation_controller.list_conversations(assistant_id)
    
    # 简单分页
    start = (page - 1) * page_size
    end = start + page_size
    paginated_conversations = conversations[start:end]
    
    return SuccessExtra(
        data=[Conversation_Pydantic.model_validate(conv).model_dump() for conv in paginated_conversations],
        total=len(conversations),
        page=page,
        page_size=page_size
    )

@router.get("/conversations/{conversation_id}", summary="获取对话详情")
async def get_conversation(conversation_id: int):
    """获取对话详情"""
    conversation = await conversation_controller.get_conversation(conversation_id)
    if not conversation:
        return Fail(code=404, msg="对话不存在")
    return Success(data=Conversation_Pydantic.model_validate(conversation).model_dump())

@router.put("/conversations/{conversation_id}", summary="更新对话")
async def update_conversation(conversation_id: int, conversation_update: ConversationUpdate):
    """更新对话"""
    conversation = await conversation_controller.update_conversation(
        conversation_id=conversation_id,
        title=conversation_update.title
    )
    if not conversation:
        return Fail(code=404, msg="对话不存在")
    return Success(data=Conversation_Pydantic.model_validate(conversation).model_dump())

@router.delete("/conversations/{conversation_id}", summary="删除对话")
async def delete_conversation(conversation_id: int):
    """删除对话"""
    result = await conversation_controller.delete_conversation(conversation_id)
    if not result:
        return Fail(code=404, msg="对话不存在")
    return Success(msg="删除成功")

@router.get("/conversations/{conversation_id}/messages", summary="获取对话的所有消息")
async def list_messages(conversation_id: int):
    """获取对话的所有消息"""
    messages = await conversation_controller.list_messages(conversation_id)
    return Success(data=[Message_Pydantic.model_validate(msg).model_dump() for msg in messages])

@router.post("/conversations/{conversation_id}/chat", summary="与助手对话")
async def chat_with_assistant(conversation_id: int, message: MessageCreate):
    """与助手对话（非流式）"""
    response = await conversation_controller.chat(conversation_id, message.content)
    if not response:
        return Fail(code=404, msg="对话不存在")
    return Success(data=response)

async def stream_generator(conversation_id: int, message_content: str):
    """流式聊天生成器"""
    import io
    from contextlib import redirect_stdout
    import re
    
    try:
        # 验证输入参数
        if not conversation_id:
            yield json.dumps({"code": 400, "msg": "对话ID不能为空", "data": None}) + "\n"
            return
            
        # 确保消息内容不为空
        if message_content is None or message_content.strip() == '':
            yield json.dumps({"code": 400, "msg": "聊天内容不能为空", "data": None}) + "\n"
            return
            
        # 获取对话
        conversation = await conversation_controller.get_conversation(conversation_id)
        if not conversation:
            yield json.dumps({"code": 404, "msg": "对话不存在", "data": None}) + "\n"
            return
            
        # 获取助手信息
        assistant = await conversation.assistant
        if not assistant:
            yield json.dumps({"code": 404, "msg": "助手不存在", "data": None}) + "\n"
            return
            
        # 保存用户消息
        await conversation_controller.add_message(conversation_id, "user", message_content)
        
        # 获取会话历史
        history = await conversation_controller.get_chat_history(conversation_id)
        
        try:
            # 创建Agno Agent实例
            agent = conversation_controller._create_agent(assistant)
        except Exception as e:
            yield json.dumps({
                "code": 500,
                "msg": f"创建Agent失败: {str(e)}",
                "data": None
            }) + "\n"
            return
        
        # 获取助手的知识库列表
        kb_list = await assistant.knowledge_bases.all()
        
        # 获取RAG上下文
        rag_context = ""
        if kb_list:
            try:
                rag_context = await conversation_controller._get_rag_context(kb_list, message_content)
            except Exception as e:
                print(f"获取RAG上下文失败: {str(e)}")
                # 继续执行，但不使用RAG上下文
        
        # 准备消息内容
        message = message_content
        if rag_context:
            message = f"RAG上下文: {rag_context}\n\n用户问题: {message_content}"
        
        # 发送开始标识
        yield json.dumps({
            "code": 200,
            "msg": "开始响应",
            "data": {
                "content": "",
                "done": False
            }
        }) + "\n"
        
        # 使用官方推荐的方法2：获取响应迭代器
        run_response = agent.run(message, history=history, stream=True)
        full_response = ""
        
        for chunk in run_response:
            content = chunk.content if hasattr(chunk, 'content') else chunk
            if content:
                full_response += content
                data = {
                    "code": 200,
                    "msg": "OK",
                    "data": {
                        "content": content,
                        "done": False
                    }
                }
                yield json.dumps(data) + "\n"
                await asyncio.sleep(0.01)  # 小延迟，避免过快响应
        
        # 保存完整响应到数据库
        await conversation_controller.add_message(conversation_id, "assistant", full_response)
        
        # 发送完成标识
        yield json.dumps({
            "code": 200,
            "msg": "完成",
            "data": {
                "content": "",
                "done": True
            }
        }) + "\n"
            
    except Exception as e:
        error_message = f"流式输出错误: {str(e)}"
        yield json.dumps({
            "code": 500,
            "msg": error_message,
            "data": {
                "content": "抱歉，处理您的请求时出现错误。",
                "done": True
            }
        }) + "\n"
        # 记录异常信息
        print(f"流式聊天生成器错误: {str(e)}")

@router.post("/conversations/{conversation_id}/chat/stream", summary="与助手流式对话(POST)")
async def stream_chat_with_assistant(conversation_id: int, message: MessageCreate, background_tasks: BackgroundTasks):
    """与助手流式对话（POST方法）"""
    # 使用SSE(Server-Sent Events)格式返回流式数据
    return StreamingResponse(
        stream_generator(conversation_id, message.content),
        media_type="text/event-stream"
    )

@router.get("/conversations/{conversation_id}/chat/stream", summary="与助手流式对话(GET)")
async def stream_chat_with_assistant_get(
    conversation_id: int, 
    content: Optional[str] = Query(None, description="聊天内容"),
    background_tasks: BackgroundTasks = None
):
    """与助手流式对话（GET方法）
    
    通过查询参数传递聊天内容，用于前端EventSource请求
    """
    print(f"收到GET流式聊天请求: conversation_id={conversation_id}, content={content}")
    
    # 确保内容不为空或空字符串
    if content is None or content.strip() == '':
        # 在流式响应中返回错误信息
        async def error_generator():
            yield json.dumps({
                "code": 400,
                "msg": "聊天内容不能为空",
                "data": {
                    "content": "请提供有效的聊天内容",
                    "done": True
                }
            }) + "\n"
        
        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream"
        )
    
    # 使用SSE(Server-Sent Events)格式返回流式数据
    return StreamingResponse(
        stream_generator(conversation_id, content),
        media_type="text/event-stream"
    )

# 添加系统报告API端点
@router.post("/report", summary="生成系统智能报告")
async def generate_system_report(data: SystemReportRequest):
    """调用AI助手生成系统智能报告"""
    try:
        # 记录日志
        logger = logging.getLogger("uvicorn")
        logger.info("开始处理系统报告生成请求")
        
        # 记录请求数据结构
        logger.info(f"请求数据结构: system_info类型: {type(data.system_info)}, ticket_info类型: {type(data.ticket_info)}")
        logger.info(f"请求数据项数: system_info={len(data.system_info) if isinstance(data.system_info, dict) else 'not dict'}, "
                  f"ticket_info={len(data.ticket_info) if isinstance(data.ticket_info, dict) else 'not dict'}, "
                  f"service_status={len(data.service_status)}, "
                  f"recent_alerts={len(data.recent_alerts)}, "
                  f"recent_logs={len(data.recent_logs)}, "
                  f"assistants={len(data.assistants)}")
        
        # 将请求数据转换为字典
        request_data = data.model_dump()
        logger.info(f"转换后的请求数据类型: {type(request_data)}")
        
        # 将请求数据传递给控制器
        logger.info("开始调用 AgnoController.generate_system_report")
        try:
            report = await AgnoController.generate_system_report(request_data)
            logger.info(f"报告生成结果类型: {type(report)}")
            if isinstance(report, dict):
                logger.info(f"报告包含的键: {list(report.keys())}")
                # 检查每个值的类型
                for key, value in report.items():
                    logger.info(f"键 '{key}' 的值类型: {type(value)}")
            else:
                logger.error(f"报告不是字典类型: {report}")
        except Exception as e:
            logger.error(f"调用 generate_system_report 时发生异常: {str(e)}", exc_info=True)
            raise
        
        # 验证返回的报告数据格式是否正确
        if not isinstance(report, dict):
            logger.error(f"报告数据格式错误: {type(report)}")
            return Fail(code=500, msg="报告生成失败: 返回数据格式错误")
            
        # 确保所有字段都存在
        if "title" not in report:
            logger.error("报告数据缺少title字段")
            report["title"] = "网络运行状况智能分析报告"
            
        if "content" not in report:
            logger.error("报告数据缺少content字段")
            report["content"] = "# 网络运行状况智能分析报告\n\n生成报告时发生错误: 内容缺失。"
            
        if "created_at" not in report:
            logger.error("报告数据缺少created_at字段")
            from datetime import datetime
            report["created_at"] = datetime.now().isoformat()
        
        logger.info("系统报告生成成功")
        logger.info(f"返回前的报告数据: title={report['title'][:20]}..., content长度={len(report['content'])}, created_at={report['created_at']}")
        return Success(data=report)
    except Exception as e:
        # 记录详细错误信息
        logger = logging.getLogger("uvicorn")
        logger.error(f"生成系统报告失败: {str(e)}", exc_info=True)
        
        # 返回错误响应，携带默认报告数据
        from datetime import datetime
        default_report = {
            "title": "网络运行状况智能分析报告",
            "content": f"# 网络运行状况智能分析报告\n\n生成报告时发生错误: {str(e)}",
            "created_at": datetime.now().isoformat()
        }
        logger.info("返回默认报告数据")
        return Success(data=default_report) 