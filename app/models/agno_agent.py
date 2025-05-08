from tortoise import fields
from pydantic import BaseModel as PydanticBaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from .base import BaseModel, TimestampMixin


class KnowledgeBase(BaseModel, TimestampMixin):
    """知识库模型"""
    name = fields.CharField(max_length=100, description="知识库名称")
    description = fields.TextField(description="知识库描述", null=True)

    class Meta:
        table = "agno_knowledge_base"


class Document(BaseModel, TimestampMixin):
    """知识库文档模型"""
    knowledge_base = fields.ForeignKeyField(
        "models.KnowledgeBase", related_name="documents", description="所属知识库"
    )
    title = fields.CharField(max_length=200, description="文档标题")
    content = fields.TextField(description="文档内容")
    metadata = fields.JSONField(description="文档元数据", default={})

    class Meta:
        table = "agno_document"


class Assistant(BaseModel, TimestampMixin):
    """智能助手模型"""
    name = fields.CharField(max_length=100, description="助手名称")
    description = fields.TextField(description="助手描述", null=True)
    model_id = fields.CharField(max_length=100, description="使用的模型标识")
    model_host = fields.CharField(max_length=200, description="模型主机地址", null=True)
    configuration = fields.JSONField(description="助手配置", default={})
    knowledge_bases = fields.ManyToManyField(
        "models.KnowledgeBase", related_name="assistants", description="关联的知识库"
    )
    is_active = fields.BooleanField(default=True, description="是否激活")

    class Meta:
        table = "agno_assistant"


class Tool(BaseModel, TimestampMixin):
    """MCP工具模型"""
    name = fields.CharField(max_length=100, description="工具名称")
    description = fields.TextField(description="工具描述")
    tool_type = fields.CharField(max_length=50, description="工具类型")
    configuration = fields.JSONField(description="工具配置", default={})

    class Meta:
        table = "agno_tool"


class AssistantTool(BaseModel):
    """助手工具关联模型"""
    assistant = fields.ForeignKeyField(
        "models.Assistant", related_name="assistant_tools", description="关联的助手"
    )
    tool = fields.ForeignKeyField(
        "models.Tool", related_name="assistant_tools", description="关联的工具"
    )
    
    class Meta:
        table = "agno_assistant_tool"
        unique_together = (("assistant", "tool"),)


class Conversation(BaseModel, TimestampMixin):
    """对话模型"""
    assistant = fields.ForeignKeyField(
        "models.Assistant", related_name="conversations", description="关联的助手"
    )
    title = fields.CharField(max_length=200, description="对话标题", null=True)

    class Meta:
        table = "agno_conversation"


class Message(BaseModel):
    """消息模型"""
    conversation = fields.ForeignKeyField(
        "models.Conversation", related_name="messages", description="关联的对话"
    )
    role = fields.CharField(max_length=20, description="角色(user 或 assistant)")
    content = fields.TextField(description="消息内容")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "agno_message"


# 创建Pydantic模型用于API响应
class KnowledgeBase_Pydantic(PydanticBaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
    def model_dump(self, **kwargs):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class Document_Pydantic(PydanticBaseModel):
    id: int
    title: str
    content: str
    metadata: Dict[str, Any] = {}
    knowledge_base_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
    def model_dump(self, **kwargs):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "knowledge_base_id": self.knowledge_base_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class Assistant_Pydantic(PydanticBaseModel):
    id: int
    name: str
    description: Optional[str] = None
    model_id: str
    model_host: Optional[str] = None
    configuration: Dict[str, Any] = {}
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
    def model_dump(self, **kwargs):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "model_id": self.model_id,
            "model_host": self.model_host,
            "configuration": self.configuration,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class Tool_Pydantic(PydanticBaseModel):
    id: int
    name: str
    description: str
    tool_type: str
    configuration: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
    def model_dump(self, **kwargs):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tool_type": self.tool_type,
            "configuration": self.configuration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class Conversation_Pydantic(PydanticBaseModel):
    id: int
    title: Optional[str] = None
    assistant_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
    def model_dump(self, **kwargs):
        return {
            "id": self.id,
            "title": self.title,
            "assistant_id": self.assistant_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class Message_Pydantic(PydanticBaseModel):
    id: int
    role: str
    content: str
    conversation_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
        
    def model_dump(self, **kwargs):
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "conversation_id": self.conversation_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        } 