# 智能工单生成功能后端实现方案

## 功能概述

实现一个API端点，接收用户的简短描述，调用AI助手生成完整工单信息，并返回生成的JSON数据，以便前端自动填充工单表单。

## API设计

### 端点

```
POST /api/v1/ticket/generate
```

### 请求参数

```json
{
  "description": "用户输入的简短工单描述"
}
```

### 响应数据

```json
{
  "code": 200,
  "data": {
    "ticket_no": "T2025050801",
    "title": "工单标题",
    "description": "工单详细描述",
    "type": "fault",
    "status": "pending",
    "priority": "high",
    "expected_time": "2025-05-09T12:00:00",
    "assignee_id": 1
  },
  "msg": "成功"
}
```

## 后端实现步骤

### 1. 创建API控制器

在`app/api/v1/ticket`目录下，编辑或创建文件`ticket.py`，添加工单生成端点。

```python
@router.post("/generate", summary="智能生成工单")
async def generate_ticket(
    request: GenerateTicketRequest,
    current_user = Depends(AuthControl.is_authed)
) -> dict:
    """智能生成工单信息"""
    ticket_data = await TicketController.generate_ticket(request.description, current_user.id)
    return Success(data=ticket_data)
```

### 2. 创建请求模型

在`app/schemas/ticket.py`中添加请求模型：

```python
class GenerateTicketRequest(BaseModel):
    """智能生成工单请求"""
    description: str = Field(..., description="工单描述", example="主服务器CPU使用率过高")
```

### 3. 创建控制器方法

在`app/controllers/ticket.py`中添加生成方法：

```python
@staticmethod
async def generate_ticket(description: str, user_id: int) -> Dict[str, Any]:
    """智能生成工单信息"""
    # 调用AI助手生成工单信息
    ticket_data = await AgnoController.generate_ticket_data(description)
    
    # 生成工单号（T + 年月日 + 两位序号）
    today = datetime.date.today()
    today_str = today.strftime("%Y%m%d")
    
    # 查询今天已有的工单数量
    count = await Ticket.filter(ticket_no__startswith=f"T{today_str}").count()
    ticket_no = f"T{today_str}{(count+1):02d}"
    
    # 更新工单号
    ticket_data["ticket_no"] = ticket_no
    
    # 设置默认状态为pending
    ticket_data["status"] = "pending"
    
    # 设置创建者ID
    ticket_data["creator_id"] = user_id
    
    return ticket_data
```

### 4. 创建AI助手调用方法

在`app/controllers/agno.py`中添加工单生成调用方法：

```python
@staticmethod
async def generate_ticket_data(description: str) -> Dict[str, Any]:
    """调用AI助手生成工单数据"""
    # 读取提示词模板
    with open("ticket_prompt.md", "r", encoding="utf-8") as f:
        prompt_template = f.read()
    
    # 构建系统提示词和用户输入
    system_prompt = prompt_template
    user_input = description
    
    # 与AI助手对话
    assistant = await AgnoAssistant.filter(is_active=True).first()
    if not assistant:
        raise HTTPException(status_code=400, detail="未找到可用的AI助手")
    
    # 调用AI接口
    completion = await AgnoController._call_llm(
        system_prompt=system_prompt,
        user_prompt=user_input,
        assistant=assistant
    )
    
    try:
        # 解析JSON响应
        ticket_data = json.loads(completion)
        return ticket_data
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="AI生成的工单数据格式错误")
```

## 前端实现思路

1. 在工单创建页面添加"智能生成"按钮
2. 点击按钮后弹出对话框，要求用户输入简短描述
3. 发送请求到后端API
4. 接收返回的工单JSON数据
5. 自动填充工单表单各字段
6. 用户确认后保存工单

## 测试计划

1. 使用不同类型的工单描述测试生成功能
2. 验证生成的工单号格式是否正确
3. 验证字段验证与默认值处理
4. 测试错误处理（如AI服务不可用）
5. 测试长描述和极短描述的处理能力

## 部署注意事项

1. 确保`ticket_prompt.md`文件存在于应用根目录
2. 确保AI助手配置正确且可用
3. 考虑添加请求超时处理
4. 添加适当的日志记录
5. 考虑添加缓存机制，减少频繁调用AI服务 