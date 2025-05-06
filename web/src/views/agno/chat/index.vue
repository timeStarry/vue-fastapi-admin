<template>
  <CommonPage>
    <template #header>
      <div flex items-center justify-between w-full>
        <h2 text-22 font-normal text-hex-333 dark:text-hex-ccc>AI助手</h2>
        <n-space>
          <n-button @click="$router.back()">
            <template #icon>
              <TheIcon icon="material-symbols:arrow-back" :size="16" />
            </template>
            返回
          </n-button>
        </n-space>
      </div>
    </template>
    
    <div v-if="noAssistant" class="no-assistant-container">
      <div class="no-assistant-content">
        <TheIcon icon="material-symbols:smart-toy-outline" :size="64" />
        <h2>未找到助手</h2>
        <p>请先创建或选择一个助手来开始对话</p>
        <div class="no-assistant-actions">
          <NButton @click="goToCreateAssistant" type="primary">
            <template #icon>
              <TheIcon icon="material-symbols:add" :size="16" />
            </template>
            创建新助手
          </NButton>
        </div>
      </div>
    </div>
    
    <div v-else class="agno-chat-container">
      <div class="chat-sidebar">
        <div class="assistant-info" v-if="assistant">
          <div class="assistant-header">
            <h3>{{ assistant.name }}</h3>
            <n-tag size="small">{{ assistant.model_id }}</n-tag>
          </div>
          <p class="assistant-description">{{ assistant.description }}</p>
        </div>
        
        <div class="conversation-list">
          <div class="conversation-header">
            <h4>对话列表</h4>
            <n-button text @click="createNewConversation">
              <template #icon>
                <TheIcon icon="material-symbols:add" :size="16" />
              </template>
              新建对话
            </n-button>
          </div>
          
          <n-input
            placeholder="搜索对话"
            v-model:value="searchText"
            clearable
          >
            <template #prefix>
              <TheIcon icon="material-symbols:search" :size="16" />
            </template>
          </n-input>
          
          <div v-if="conversationsLoading" class="conversation-items">
            <n-spin size="medium" />
          </div>
          <div v-else class="conversation-items">
            <div
              v-for="conv in filteredConversations"
              :key="conv.id"
              class="conversation-item"
              :class="{ active: currentConversationId === conv.id }"
              @click="selectConversation(conv.id)"
            >
              <div class="conversation-title">{{ conv.title || '无标题对话' }}</div>
              <div class="conversation-time">{{ formatTime(conv.created_at) }}</div>
              <div class="conversation-actions">
                <n-dropdown :options="dropdownOptions" @select="handleConvAction($event, conv.id)">
                  <TheIcon icon="material-symbols:more-horiz" :size="16" />
                </n-dropdown>
              </div>
            </div>
            
            <div v-if="filteredConversations.length === 0" class="empty-list">
              <TheIcon icon="material-symbols:chat" :size="36" />
              <p>{{ conversationsLoading ? '加载中...' : '没有对话记录' }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chat-main">
        <div v-if="!currentConversationId" class="chat-empty-state">
          <TheIcon icon="material-symbols:chat-bubble-outline" :size="64" />
          <h3>开始一个新对话</h3>
          <p>选择已有对话或创建一个新的对话开始</p>
          <n-button type="primary" @click="createNewConversation">新建对话</n-button>
        </div>
        
        <template v-else>
          <div ref="messageContainer" class="message-container">
            <n-spin v-if="messagesLoading" size="large" />
            
            <div v-else-if="messages.length === 0" class="no-messages">
              <p>没有消息记录，开始发送消息吧！</p>
            </div>
            
            <template v-else>
              <div
                v-for="(message, index) in messages"
                :key="message.id || index"
                :class="['message', message.role]"
              >
                <div class="message-avatar">
                  <TheIcon v-if="message.role === 'user'" icon="material-symbols:person" :size="18" />
                  <TheIcon v-else icon="material-symbols:smart-toy" :size="18" />
                </div>
                <div class="message-content">
                  <div v-if="message.role === 'assistant'" v-html="message.isPending ? message.content : formatMarkdown(message.content)"></div>
                  <div v-else>{{ message.content }}</div>
                </div>
              </div>
            </template>
          </div>
          
          <div class="message-input">
            <n-input
              type="textarea"
              :rows="2"
              placeholder="输入消息..."
              v-model:value="userInput"
              :disabled="sending"
              @keydown.ctrl.enter="sendMessage"
              :autosize="{ minRows: 2, maxRows: 4 }"
            />
            <div class="input-actions">
              <span class="hint">Ctrl + Enter 发送</span>
              <n-button
                type="primary"
                :loading="sending"
                @click="sendMessage"
                :disabled="!userInput.trim()"
              >
                <template #icon>
                  <TheIcon icon="material-symbols:send" :size="16" />
                </template>
                发送
              </n-button>
            </div>
          </div>
        </template>
      </div>
      
      <div class="chat-knowledge" v-if="assistant">
        <div class="knowledge-header">
          <h4>知识库</h4>
          <n-button text @click="manageKnowledgeBases">管理</n-button>
        </div>
        
        <div class="knowledge-list">
          <n-spin v-if="knowledgeBasesLoading" size="medium" />
          
          <template v-else>
            <div
              v-for="kb in knowledgeBases"
              :key="kb.id"
              class="knowledge-item"
            >
              <div class="knowledge-title">{{ kb.name }}</div>
              <div class="knowledge-description">{{ kb.description || '无描述' }}</div>
            </div>
            
            <div v-if="knowledgeBases.length === 0" class="empty-list">
              <TheIcon icon="material-symbols:article" :size="36" />
              <p>{{ knowledgeBasesLoading ? '加载中...' : '没有关联知识库' }}</p>
            </div>
          </template>
        </div>
      </div>
    </div>
    
    <!-- 重命名对话弹窗 -->
    <n-modal v-model:show="renameDialogVisible" preset="dialog" title="重命名对话">
      <n-form>
        <n-form-item label="对话标题">
          <n-input v-model:value="renameTitle" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space justify="end">
          <n-button @click="renameDialogVisible = false">取消</n-button>
          <n-button type="primary" @click="handleRenameConfirm">确定</n-button>
        </n-space>
      </template>
    </n-modal>
    
    <!-- 知识库管理弹窗 -->
    <n-modal v-model:show="knowledgeDialogVisible" preset="dialog" title="管理知识库" style="width: 600px">
      <n-transfer
        v-model:value="selectedKnowledgeBases"
        :options="allKnowledgeBases"
        source-title="可选知识库"
        target-title="已选知识库"
        @update:value="handleKnowledgeChange"
      />
      <template #action>
        <n-button @click="knowledgeDialogVisible = false">关闭</n-button>
      </template>
    </n-modal>
  </CommonPage>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted, onBeforeUnmount, h, watchEffect } from 'vue'
import {
  NButton,
  NInput,
  NTag,
  NSpin,
  NSpace,
  NModal,
  NForm,
  NFormItem,
  NTransfer,
  NDropdown
} from 'naive-ui'
import {
  getAssistant,
  getConversations,
  createConversation,
  getConversationMessages,
  sendMessage as apiSendMessage,
  getAssistantKnowledgeBases,
  getKnowledgeBases,
  addKnowledgeBaseToAssistant,
  removeKnowledgeBaseFromAssistant,
  updateConversation,
  deleteConversation
} from '@/api/agno'
import * as marked from 'marked'
import DOMPurify from 'dompurify'
import { useUserStore } from '@/store'
import TheIcon from '@/components/icon/TheIcon.vue'
import CommonPage from '@/components/page/CommonPage.vue'
import { useRouter, useRoute } from 'vue-router'

defineOptions({ name: 'AgnoChat' })

const props = defineProps({
  id: {
    type: [String, Number],
    default: null
  }
})

// 获取路由参数
const route = useRoute()
const router = useRouter()

// 页面状态
const assistantId = ref(null);
const noAssistant = ref(false);

// 从query参数获取ID
const getIdFromQuery = () => {
  // 优先从query参数获取
  if (route.query && route.query.id) {
    const parsedId = parseInt(route.query.id, 10);
    if (!isNaN(parsedId)) {
      console.log('从query参数获取到ID:', parsedId);
      return parsedId;
    }
  }
  
  // 其次从props中获取
  if (props.id) {
    const parsedId = parseInt(props.id, 10);
    if (!isNaN(parsedId)) {
      console.log('从props获取到ID:', parsedId);
      return parsedId;
    }
  }
  
  // 最后从路由params获取
  if (route.params && route.params.id) {
    const parsedId = parseInt(route.params.id, 10);
    if (!isNaN(parsedId)) {
      console.log('从params参数获取到ID:', parsedId);
      return parsedId;
    }
  }
  
  console.log('未找到有效的ID参数');
  return null;
};

// 直接获取ID，不使用watchEffect
onMounted(() => {
  const id = getIdFromQuery();
  console.log('组件挂载后获取ID:', id);
  
  if (id) {
    assistantId.value = id;
    noAssistant.value = false;
    fetchAssistant();
    fetchConversations();
    fetchKnowledgeBases();
  } else {
    console.warn('未找到有效的助手ID');
    noAssistant.value = true;
  }
});

// 监听路由变化
watch(
  () => route.query.id,
  (newId) => {
    console.log('路由ID变化:', newId);
    if (newId) {
      const parsedId = parseInt(newId, 10);
      if (!isNaN(parsedId) && parsedId !== assistantId.value) {
        assistantId.value = parsedId;
        noAssistant.value = false;
        fetchAssistant();
        fetchConversations();
        fetchKnowledgeBases();
      }
    } else {
      noAssistant.value = true;
    }
  }
);

// 状态
const assistant = ref(null)
const conversations = ref([])
const currentConversationId = ref(null)
const messages = ref([])
const userInput = ref('')
const sending = ref(false)
const conversationsLoading = ref(false)
const messagesLoading = ref(false)
const searchText = ref('')

// 知识库相关
const knowledgeBases = ref([])
const allKnowledgeBases = ref([])
const selectedKnowledgeBases = ref([])
const knowledgeBasesLoading = ref(false)
const knowledgeDialogVisible = ref(false)

// 对话重命名
const renameDialogVisible = ref(false)
const renameTitle = ref('')
const renameConversationId = ref(null)

// DOM引用
const messageContainer = ref(null)

// 用户信息
const userStore = useUserStore()

// 下拉菜单选项
const dropdownOptions = [
  {
    label: '重命名',
    key: 'rename',
    icon: () => h(TheIcon, { icon: 'material-symbols:edit', size: 16 })
  },
  {
    label: '删除',
    key: 'delete',
    icon: () => h(TheIcon, { icon: 'material-symbols:delete', size: 16 })
  }
]

// 计算属性
const filteredConversations = computed(() => {
  if (!searchText.value) return conversations.value
  
  const searchLower = searchText.value.toLowerCase()
  return conversations.value.filter(conv => {
    return (conv.title || '').toLowerCase().includes(searchLower)
  })
})

// 方法
function cleanup() {
  // 清理函数，用于组件卸载时
}

async function fetchAssistant() {
  if (!assistantId.value) {
    console.error('fetchAssistant: 助手ID为空');
    window.$message?.error('助手ID不能为空');
    noAssistant.value = true;
    return;
  }
  
  console.log('开始获取助手信息，ID:', assistantId.value);
  try {
    const response = await getAssistant(assistantId.value);
    console.log('获取助手信息成功，响应数据:', response);
    
    // 验证响应数据结构
    if (!response) {
      console.error('获取助手信息失败: 响应为空');
      window.$message?.error('获取助手信息失败: 服务器没有返回数据');
      noAssistant.value = true;
      return;
    }
    
    // 验证响应状态码
    if (response.code !== 200 && response.code !== undefined) {
      console.error('获取助手信息失败: 错误码', response.code, response.msg || '未知错误');
      window.$message?.error(`获取助手信息失败: ${response.msg || '未知错误'}`);
      noAssistant.value = true;
      return;
    }
    
    // 验证数据是否存在
    if (!response.data) {
      console.warn('助手数据返回为空:', response);
      window.$message?.warning('未找到助手数据');
      noAssistant.value = true;
      return;
    }
    
    // 成功获取数据
    assistant.value = response.data;
    noAssistant.value = false;
    console.log('助手数据已更新:', assistant.value);
  } catch (error) {
    console.error('获取助手信息失败:', error);
    window.$message?.error('获取助手信息失败: ' + (error.message || '未知错误'));
    noAssistant.value = true;
  }
}

async function fetchConversations() {
  conversationsLoading.value = true
  try {
    const response = await getConversations(assistantId.value)
    conversations.value = response.data
    // 默认选择第一个对话
    if (conversations.value.length > 0 && !currentConversationId.value) {
      selectConversation(conversations.value[0].id)
    }
  } catch (error) {
    window.$message?.error('获取对话列表失败')
  } finally {
    conversationsLoading.value = false
  }
}

async function fetchMessages() {
  if (!currentConversationId.value) return
  
  messagesLoading.value = true
  try {
    const response = await getConversationMessages(currentConversationId.value)
    messages.value = response.data
    scrollToBottom()
  } catch (error) {
    window.$message?.error('获取消息记录失败')
  } finally {
    messagesLoading.value = false
  }
}

async function fetchKnowledgeBases() {
  knowledgeBasesLoading.value = true
  try {
    const response = await getAssistantKnowledgeBases(assistantId.value)
    knowledgeBases.value = response.data
  } catch (error) {
    console.error('获取知识库失败', error)
  } finally {
    knowledgeBasesLoading.value = false
  }
}

async function fetchAllKnowledgeBases() {
  try {
    const response = await getKnowledgeBases()
    allKnowledgeBases.value = response.data.map(kb => ({
      label: kb.name,
      value: kb.id,
      disabled: false
    }))
    
    // 设置已选择的知识库
    selectedKnowledgeBases.value = knowledgeBases.value.map(kb => kb.id)
  } catch (error) {
    window.$message?.error('获取知识库列表失败')
  }
}

async function createNewConversation() {
  try {
    const title = '新对话'
    console.log('创建新对话，助手ID:', assistantId.value);
    
    if (!assistantId.value) {
      console.error('创建对话失败: 助手ID为空');
      window.$message?.error('助手ID不能为空');
      return;
    }
    
    // 确保assistant_id是数字类型
    const intId = parseInt(assistantId.value, 10);
    if (isNaN(intId)) {
      console.error('创建对话失败: 无效的助手ID格式');
      window.$message?.error('无效的助手ID格式');
      return;
    }
    
    const response = await createConversation({
      assistant_id: intId,
      title: title
    });
    
    console.log('创建对话成功，响应数据:', response);
    
    if (!response || !response.data) {
      console.error('创建对话失败: 响应数据异常', response);
      window.$message?.error('创建对话失败: 响应数据异常');
      return;
    }
    
    conversations.value.unshift(response.data)
    selectConversation(response.data.id)
    window.$message?.success('创建对话成功');
  } catch (error) {
    console.error('创建对话失败:', error);
    window.$message?.error('创建对话失败: ' + (error.message || '未知错误'));
  }
}

function selectConversation(id) {
  currentConversationId.value = id
  fetchMessages()
}

// 发送消息
async function sendMessage() {
  // 验证输入不为空
  if (!userInput.value.trim() || sending.value) return
  
  // 如果没有选中对话，先创建一个
  if (!currentConversationId.value) {
    try {
      await createNewConversation()
      if (!currentConversationId.value) {
        console.error('创建对话失败: 未能获取对话ID');
        window.$message?.error('创建对话失败，请重试');
        return;
      }
    } catch (error) {
      console.error('创建对话失败:', error);
      window.$message?.error('创建对话失败: ' + (error.message || '未知错误'));
      return;
    }
  }
  
  const userMessage = userInput.value.trim()
  userInput.value = ''
  sending.value = true
  
  // 立即添加用户消息到界面
  messages.value.push({
    role: 'user',
    content: userMessage,
    created_at: new Date().toISOString()
  })
  
  scrollToBottom()
  
  // 添加一个临时的"正在输入"消息
  const pendingMessageId = Date.now()
  messages.value.push({
    id: pendingMessageId,
    role: 'assistant',
    content: '<div class="typing-indicator">AI助手正在思考<span>.</span><span>.</span><span>.</span></div>',
    created_at: new Date().toISOString(),
    isPending: true
  })
  
  scrollToBottom()
  
  try {
    console.log(`开始聊天请求，对话ID: ${currentConversationId.value}, 内容: ${userMessage.substring(0, 50)}${userMessage.length > 50 ? '...' : ''}`);
    
    // 使用非流式API，不使用流式API
    const response = await apiSendMessage(currentConversationId.value, userMessage)
    
    // 移除临时消息
    messages.value = messages.value.filter(msg => !msg.isPending);
    
    if (response && response.code === 200) {
      // 添加助手回复到消息列表
      messages.value.push({
        role: 'assistant',
        content: response.data.response || response.data,
        created_at: new Date().toISOString()
      })
      
      // 滚动到底部
      scrollToBottom()
    } else {
      const errorMsg = response?.msg || '未知错误';
      console.error('接收回复失败:', errorMsg);
      window.$message?.error('接收回复失败: ' + errorMsg);
    }
  } catch (error) {
    // 移除临时消息
    messages.value = messages.value.filter(msg => !msg.isPending);
    
    console.error('发送消息失败:', error);
    window.$message?.error('发送消息失败: ' + (error.message || '未知错误'));
  } finally {
    sending.value = false;
  }
}

function handleConvAction(key, convId) {
  if (key === 'rename') {
    const conv = conversations.value.find(c => c.id === convId)
    renameTitle.value = conv.title || ''
    renameConversationId.value = convId
    renameDialogVisible.value = true
  } else if (key === 'delete') {
    window.$dialog?.warning({
      title: '确认删除',
      content: '确定要删除此对话吗？',
      positiveText: '确定',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          await deleteConversation(convId)
          
          // 更新UI状态
          conversations.value = conversations.value.filter(c => c.id !== convId)
          if (currentConversationId.value === convId) {
            currentConversationId.value = conversations.value[0]?.id || null
            messages.value = []
            
            if (currentConversationId.value) {
              fetchMessages()
            }
          }
          
          window.$message?.success('删除成功')
        } catch (error) {
          window.$message?.error('删除失败')
        }
      }
    })
  }
}

async function handleRenameConfirm() {
  if (!renameTitle.value.trim()) {
    window.$message?.warning('标题不能为空')
    return
  }
  
  try {
    await updateConversation(renameConversationId.value, { title: renameTitle.value })
    
    // 更新UI状态
    const index = conversations.value.findIndex(c => c.id === renameConversationId.value)
    if (index !== -1) {
      conversations.value[index].title = renameTitle.value
    }
    
    renameDialogVisible.value = false
    window.$message?.success('重命名成功')
  } catch (error) {
    window.$message?.error('重命名失败')
  }
}

async function manageKnowledgeBases() {
  await fetchAllKnowledgeBases()
  knowledgeDialogVisible.value = true
}

async function handleKnowledgeChange(value, movedKeys = []) {
  const currentKeys = new Set(selectedKnowledgeBases.value)
  const addedKeys = []
  const removedKeys = []
  
  // 检查新增的keys
  for (const key of value) {
    if (!knowledgeBases.value.some(kb => kb.id === key)) {
      addedKeys.push(key)
    }
  }
  
  // 检查移除的keys
  for (const kb of knowledgeBases.value) {
    if (!value.includes(kb.id)) {
      removedKeys.push(kb.id)
    }
  }
  
  // 执行添加和移除操作
  for (const key of addedKeys) {
    try {
      await addKnowledgeBaseToAssistant(assistantId.value, key)
    } catch (error) {
      window.$message?.error('添加知识库失败')
    }
  }
  
  for (const key of removedKeys) {
    try {
      await removeKnowledgeBaseFromAssistant(assistantId.value, key)
    } catch (error) {
      window.$message?.error('移除知识库失败')
    }
  }
  
  // 更新知识库列表
  await fetchKnowledgeBases()
}

function scrollToBottom() {
  nextTick(() => {
    const container = messageContainer.value
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString()
}

function formatMarkdown(text) {
  if (!text) return ''
  // 使用DOMPurify清理HTML，防止XSS攻击
  return DOMPurify.sanitize(marked.parse(text))
}

// 导航函数 - 直接跳转
function goToCreateAssistant() {
  console.log('跳转到创建助手页面');
  try {
    router.push('/ai/assistant');
    console.log('已跳转到创建助手页面');
  } catch (error) {
    console.error('导航失败:', error);
    window.$message?.error('导航失败: ' + (error.message || '未知错误'));
  }
}

// 监听属性变化
watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
})

// 生命周期钩子
onMounted(() => {
  window.addEventListener('beforeunload', cleanup)
})

onBeforeUnmount(() => {
  cleanup()
  window.removeEventListener('beforeunload', cleanup)
})
</script>

<style scoped>
.agno-chat-container {
  display: grid;
  grid-template-columns: 280px 1fr 280px;
  grid-template-rows: 100%;
  grid-template-areas: "sidebar main knowledge";
  height: calc(100vh - 120px);
  overflow: hidden;
}

.chat-sidebar {
  grid-area: sidebar;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  background-color: var(--card-color);
}

.assistant-info {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.assistant-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.assistant-header h3 {
  margin: 0;
  font-size: 16px;
}

.assistant-description {
  font-size: 13px;
  color: var(--text-color-3);
  margin: 0;
}

.conversation-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0 12px;
}

.conversation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
}

.conversation-header h4 {
  margin: 0;
  font-size: 14px;
}

.conversation-items {
  flex: 1;
  overflow-y: auto;
  margin-top: 12px;
}

.conversation-item {
  position: relative;
  padding: 10px 16px;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.conversation-item:hover {
  background-color: var(--hover-color);
}

.conversation-item.active {
  background-color: var(--primary-color-hover);
}

.conversation-title {
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: 24px;
}

.conversation-time {
  font-size: 12px;
  color: var(--text-color-3);
  margin-top: 4px;
}

.conversation-actions {
  position: absolute;
  right: 8px;
  top: 10px;
  display: none;
}

.conversation-item:hover .conversation-actions {
  display: block;
}

.chat-main {
  grid-area: main;
  display: flex;
  flex-direction: column;
  background-color: var(--body-color);
  overflow: hidden;
}

.chat-empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-color-3);
}

.chat-empty-state h3 {
  font-size: 24px;
  font-weight: normal;
  margin: 16px 0 10px;
}

.chat-empty-state p {
  margin-bottom: 20px;
}

.message-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.no-messages {
  display: flex;
  justify-content: center;
  padding: 20px;
  color: var(--text-color-3);
}

.message {
  display: flex;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message.user .message-avatar {
  margin-left: 12px;
  margin-right: 0;
  background-color: var(--primary-color);
  color: white;
}

.message.user .message-content {
  background-color: var(--primary-color-hover);
  border-radius: 8px 0 8px 8px;
}

.message.assistant .message-content {
  background-color: var(--card-color);
  border-radius: 0 8px 8px 8px;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  background-color: var(--card-color);
  color: var(--text-color);
}

.message-content {
  max-width: 80%;
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.6;
}

.message-content :deep(pre) {
  background-color: #f8f8f8;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.message-content :deep(code) {
  font-family: Consolas, Monaco, monospace;
}

.message-content :deep(p) {
  margin: 0 0 10px;
}

.message-content :deep(p:last-child) {
  margin-bottom: 0;
}

.message-content :deep(ul), .message-content :deep(ol) {
  margin: 0 0 10px;
  padding-left: 20px;
}

.thinking-indicator {
  display: flex;
  margin-top: 8px;
}

.thinking-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--text-color-3);
  margin-right: 4px;
  animation: pulse 1.5s infinite;
}

.thinking-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.thinking-indicator span:nth-child(3) {
  animation-delay: 0.4s;
  margin-right: 0;
}

/* 打字指示器样式 */
.typing-indicator {
  background-color: transparent;
  padding: 4px 8px;
  border-radius: 6px;
  display: inline-block;
  color: var(--text-color-3);
}

.typing-indicator span {
  animation: typing 1s infinite;
  display: inline-block;
  opacity: 0.7;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.3s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes typing {
  0%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  50% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  50% {
    transform: scale(1);
    opacity: 1;
  }
}

.message-input {
  padding: 16px;
  border-top: 1px solid var(--border-color);
}

.input-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}

.hint {
  font-size: 12px;
  color: var(--text-color-3);
}

.chat-knowledge {
  grid-area: knowledge;
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  background-color: var(--card-color);
}

.knowledge-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.knowledge-header h4 {
  margin: 0;
  font-size: 14px;
}

.knowledge-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.knowledge-item {
  padding: 12px;
  background-color: var(--body-color);
  border-radius: 4px;
  margin-bottom: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.knowledge-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.knowledge-description {
  font-size: 13px;
  color: var(--text-color-3);
}

.empty-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: var(--text-color-3);
}

.empty-list i {
  font-size: 36px;
  margin-bottom: 10px;
}

.empty-list p {
  font-size: 13px;
}

/* 添加无助手状态的样式 */
.no-assistant-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 120px);
  width: 100%;
}

.no-assistant-content {
  text-align: center;
  padding: 2rem;
  background-color: var(--card-color);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  max-width: 480px;
}

.no-assistant-content h2 {
  font-size: 24px;
  margin: 16px 0;
  font-weight: normal;
}

.no-assistant-content p {
  color: var(--text-color-3);
  margin-bottom: 24px;
}

.no-assistant-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style> 