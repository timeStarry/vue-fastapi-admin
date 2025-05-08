import { request } from '@/utils/http'

// API基础路径前缀 - 由于request已经配置了baseURL为/api/v1，这里只需要使用相对路径
const API_PREFIX = '/agno';

// 助手相关API
export function getAssistants() {
  return request({
    url: `${API_PREFIX}/assistants`,
    method: 'get'
  })
}

export function getAssistant(id) {
  return request({
    url: `${API_PREFIX}/assistants/${id}`,
    method: 'get'
  })
}

export function createAssistant(data) {
  return request({
    url: `${API_PREFIX}/assistants`,
    method: 'post',
    data
  })
}

export function updateAssistant(id, data) {
  return request({
    url: `${API_PREFIX}/assistants/${id}`,
    method: 'put',
    data
  })
}

export function deleteAssistant(id) {
  return request({
    url: `${API_PREFIX}/assistants/${id}`,
    method: 'delete'
  })
}

// 知识库相关API
export function getKnowledgeBases() {
  return request({
    url: `${API_PREFIX}/knowledge-bases`,
    method: 'get'
  })
}

export function getKnowledgeBase(id) {
  return request({
    url: `${API_PREFIX}/knowledge-bases/${id}`,
    method: 'get'
  })
}

export function createKnowledgeBase(data) {
  return request({
    url: `${API_PREFIX}/knowledge-bases`,
    method: 'post',
    data
  })
}

export function updateKnowledgeBase(id, data) {
  return request({
    url: `${API_PREFIX}/knowledge-bases/${id}`,
    method: 'put',
    data
  })
}

export function deleteKnowledgeBase(id) {
  return request({
    url: `${API_PREFIX}/knowledge-bases/${id}`,
    method: 'delete'
  })
}

// 知识库文档相关API
export function getDocuments(knowledgeBaseId) {
  return request({
    url: `${API_PREFIX}/knowledge-bases/${knowledgeBaseId}/documents`,
    method: 'get'
  })
}

export function getDocument(id) {
  return request({
    url: `${API_PREFIX}/documents/${id}`,
    method: 'get'
  })
}

export function createDocument(knowledgeBaseId, data) {
  return request({
    url: `${API_PREFIX}/knowledge-bases/${knowledgeBaseId}/documents`,
    method: 'post',
    data
  })
}

export function updateDocument(id, data) {
  return request({
    url: `${API_PREFIX}/documents/${id}`,
    method: 'put',
    data
  })
}

export function deleteDocument(id) {
  return request({
    url: `${API_PREFIX}/documents/${id}`,
    method: 'delete'
  })
}

export function getAssistantKnowledgeBases(assistantId) {
  return request({
    url: `${API_PREFIX}/assistants/${assistantId}/knowledge-bases`,
    method: 'get'
  })
}

export function addKnowledgeBaseToAssistant(assistantId, kbId) {
  return request({
    url: `${API_PREFIX}/assistants/${assistantId}/knowledge-bases/${kbId}`,
    method: 'post'
  })
}

export function removeKnowledgeBaseFromAssistant(assistantId, kbId) {
  return request({
    url: `${API_PREFIX}/assistants/${assistantId}/knowledge-bases/${kbId}`,
    method: 'delete'
  })
}

// 对话相关API
export function getConversations(assistantId, page = 1, pageSize = 10) {
  return request({
    url: `${API_PREFIX}/conversations`,
    method: 'get',
    params: {
      assistant_id: assistantId,
      page,
      page_size: pageSize
    }
  })
}

export function createConversation(data) {
  // 确保assistant_id是数字类型，解决整数验证错误
  const assistantId = parseInt(data.assistant_id, 10);
  
  if (isNaN(assistantId)) {
    console.error('创建对话失败: assistant_id 不是有效的整数', data);
    return Promise.reject(new Error('assistant_id 必须是有效的整数'));
  }
  
  // 创建一个新的数据对象，确保 assistant_id 为数字类型
  const newData = {
    ...data,
    assistant_id: assistantId
  };
  
  console.log('API请求数据:', newData);
  
  return request({
    url: `${API_PREFIX}/conversations`,
    method: 'post',
    data: newData
  });
}

export function updateConversation(id, data) {
  return request({
    url: `${API_PREFIX}/conversations/${id}`,
    method: 'put',
    data
  })
}

export function deleteConversation(id) {
  return request({
    url: `${API_PREFIX}/conversations/${id}`,
    method: 'delete'
  })
}

export function getConversationMessages(conversationId) {
  return request({
    url: `${API_PREFIX}/conversations/${conversationId}/messages`,
    method: 'get'
  })
}

export function sendMessage(conversationId, content) {
  return request({
    url: `${API_PREFIX}/conversations/${conversationId}/chat`,
    method: 'post',
    data: { content }
  })
}

// 流式聊天API
export function createStreamChat(conversationId, content, onMessage, onComplete, onError) {
  // 验证参数
  if (!conversationId) {
    console.error('无效的对话ID');
    onError && onError(new Error('无效的对话ID'));
    return { close: () => {} };
  }
  
  // 确保content是字符串且不为undefined
  const safeContent = content || '';
  
  // 判断内容长度，如果超过100字符，使用POST方式发送
  if (safeContent.length > 100) {
    return createStreamChatPost(conversationId, safeContent, onMessage, onComplete, onError);
  }
  
  // 获取当前环境的基础URL
  // EventSource不会自动添加baseURL，需要手动添加完整路径
  const baseUrl = import.meta.env.VITE_BASE_API || '/api/v1';
  
  // 使用完整的API路径，确保不会重复/api/v1前缀
  const apiUrl = `${baseUrl}${API_PREFIX}/conversations/${conversationId}/chat/stream?content=${encodeURIComponent(safeContent)}`;
  console.log('SSE连接URL (GET):', apiUrl);
  
  try {
    const eventSource = new EventSource(apiUrl);
    
    eventSource.onmessage = (event) => {
      try {
        console.log('SSE消息:', event.data);
        const data = JSON.parse(event.data);
        onMessage && onMessage(data);
        
        if (data.data && data.data.done) {
          eventSource.close();
          onComplete && onComplete();
        }
      } catch (error) {
        console.error('SSE消息处理错误:', error);
        onError && onError(error);
      }
    };
    
    eventSource.onerror = (error) => {
      console.error('SSE连接错误:', error);
      eventSource.close();
      onError && onError(error);
    };
    
    return {
      close: () => {
        console.log('手动关闭SSE连接');
        eventSource.close();
      }
    };
  } catch (error) {
    console.error('创建SSE连接失败:', error);
    onError && onError(error);
    return { close: () => {} };
  }
}

// 使用POST方式的流式聊天API
export function createStreamChatPost(conversationId, content, onMessage, onComplete, onError) {
  // 验证参数
  if (!conversationId) {
    console.error('无效的对话ID');
    onError && onError(new Error('无效的对话ID'));
    return { close: () => {} };
  }
  
  // 确保content是字符串且不为undefined
  const safeContent = content || '';
  
  // 获取当前环境的基础URL
  const baseUrl = import.meta.env.VITE_BASE_API || '/api/v1';
  
  // 使用fetch API模拟SSE行为
  console.log('使用POST方式发送内容');
  
  let aborted = false;
  let reader = null;
  
  // 创建一个AbortController用于取消请求
  const controller = new AbortController();
  
  // 发起POST请求（使用完整URL）
  fetch(`${baseUrl}${API_PREFIX}/conversations/${conversationId}/chat/stream`, {
    method: 'POST',
    body: JSON.stringify({ content: safeContent }),
    headers: {
      'Content-Type': 'application/json'
    },
    signal: controller.signal
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    function readStream() {
      if (aborted) return;
      
      reader.read().then(({ done, value }) => {
        if (done) {
          onComplete && onComplete();
          return;
        }
        
        // 解码并处理数据
        const text = decoder.decode(value, { stream: true });
        
        // 按行分割数据
        const lines = text.split('\n').filter(line => line.trim());
        
        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            onMessage && onMessage(data);
            
            if (data.data && data.data.done) {
              onComplete && onComplete();
              return;
            }
          } catch (error) {
            console.error('SSE数据解析错误:', error, 'Raw data:', line);
          }
        }
        
        // 继续读取
        readStream();
      }).catch(error => {
        if (!aborted) {
          console.error('读取流数据错误:', error);
          onError && onError(error);
        }
      });
    }
    
    readStream();
  })
  .catch(error => {
    if (!aborted) {
      console.error('流式聊天请求错误:', error);
      onError && onError(error);
    }
  });
  
  // 返回控制对象
  return {
    close: () => {
      console.log('手动中断流式请求');
      aborted = true;
      controller.abort();
      if (reader) {
        // Reader不能直接取消，但我们可以标记已取消
        console.log('标记reader已取消');
      }
    }
  };
} 