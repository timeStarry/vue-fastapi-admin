<template>
  <CommonPage>
    <template #header>
      <div flex items-center justify-between w-full>
        <h2 text-22 font-normal text-hex-333 dark:text-hex-ccc>智能助手</h2>
        <div flex items-center>
          <n-input-group>
            <n-input v-model:value="directAccessId" placeholder="输入助手ID直接访问" style="width: 150px" />
            <n-button type="primary" @click="handleDirectAccess">访问</n-button>
          </n-input-group>
        </div>
      </div>
    </template>

    <n-card>
      <n-spin :show="loading">
        <div class="assistant-list">
          <n-grid :cols="3" :x-gap="16" :y-gap="16">
            <n-grid-item v-for="assistant in assistants" :key="assistant.id">
              <n-card hoverable @click="handleSelectAssistant(assistant.id)">
                <template #header>
                  <div class="assistant-header">
                    <h3 class="assistant-name">{{ assistant.name }}</h3>
                    <n-tag size="small">{{ assistant.model_id }}</n-tag>
                  </div>
                </template>
                <div class="assistant-content">
                  <p class="assistant-description">{{ assistant.description }}</p>
                </div>
                <template #footer>
                  <div class="assistant-footer">
                    <n-button tertiary size="small" type="primary" @click.stop="handleManage(assistant.id)">
                      <template #icon>
                        <TheIcon icon="material-symbols:settings-outline" :size="16" />
                      </template>
                      管理
                    </n-button>
                    <n-button type="primary" @click.stop="handleChat(assistant.id)">
                      <template #icon>
                        <TheIcon icon="material-symbols:chat-outline" :size="16" />
                      </template>
                      开始对话
                    </n-button>
                  </div>
                </template>
              </n-card>
            </n-grid-item>
            
            <n-grid-item>
              <n-card hoverable class="create-card" @click="handleCreateAssistant">
                <div class="create-content">
                  <TheIcon icon="material-symbols:add-circle-outline" :size="64" />
                  <p>创建新助手</p>
                </div>
              </n-card>
            </n-grid-item>
          </n-grid>
          
          <div v-if="assistants.length === 0 && !loading" class="empty-list">
            <TheIcon icon="material-symbols:smart-toy-outline" :size="64" />
            <p>您还没有创建任何助手</p>
            <n-button type="primary" @click="handleCreateAssistant">创建助手</n-button>
          </div>
        </div>
      </n-spin>
    </n-card>
  </CommonPage>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NCard, NGrid, NGridItem, NSpin, NTag, NInput, NInputGroup } from 'naive-ui'
import { getAssistants } from '@/api/agno'
import TheIcon from '@/components/icon/TheIcon.vue'
import CommonPage from '@/components/page/CommonPage.vue'

defineOptions({ name: 'AgnoAssistantList' })

const router = useRouter()
const loading = ref(false)
const assistants = ref([])
const directAccessId = ref('')

onMounted(() => {
  fetchAssistants()
})

async function fetchAssistants() {
  console.log('开始获取助手列表...');
  loading.value = true;
  try {
    console.log('API请求：getAssistants()');
    const response = await getAssistants();
    console.log('获取助手列表成功，响应数据:', response);
    
    if (response && response.data) {
      assistants.value = response.data;
      console.log('助手列表数据已更新:', assistants.value);
    } else {
      console.warn('返回数据结构异常:', response);
      window.$message?.warning('获取助手列表成功，但数据结构异常');
      assistants.value = [];
    }
  } catch (error) {
    console.error('获取助手列表失败，详细错误:', error);
    window.$message?.error('获取助手列表失败');
  } finally {
    loading.value = false;
  }
}

function handleSelectAssistant(id) {
  if (!id) {
    window.$message?.error('无效的助手ID');
    return;
  }
  
  // 确保ID是正确的格式
  const assistantId = parseInt(id, 10);
  if (isNaN(assistantId)) {
    window.$message?.error('助手ID格式错误');
    return;
  }
  
  console.log('选择助手，ID:', assistantId);
  try {
    // 使用完整URL字符串形式
    router.push(`/ai/chat?id=${assistantId}`);
    console.log('已跳转到聊天页面，URL:', `/ai/chat?id=${assistantId}`);
  } catch (error) {
    console.error('导航失败:', error);
    window.$message?.error('导航失败: ' + (error.message || '未知错误'));
  }
}

function handleChat(id) {
  if (!id) {
    window.$message?.error('无效的助手ID');
    return;
  }
  
  // 确保ID是正确的格式
  const assistantId = parseInt(id, 10);
  if (isNaN(assistantId)) {
    window.$message?.error('助手ID格式错误');
    return;
  }
  
  console.log('开始对话，ID:', assistantId);
  try {
    // 使用完整URL字符串形式
    router.push(`/ai/chat?id=${assistantId}`);
    console.log('已跳转到聊天页面，URL:', `/ai/chat?id=${assistantId}`);
  } catch (error) {
    console.error('导航失败:', error);
    window.$message?.error('导航失败: ' + (error.message || '未知错误'));
  }
}

function handleManage(id) {
  try {
    router.push(`/ai/assistant?id=${id}`);
    console.log('已跳转到助手管理页面，URL:', `/ai/assistant?id=${id}`);
  } catch (error) {
    console.error('导航失败:', error);
    window.$message?.error('导航失败: ' + (error.message || '未知错误'));
  }
}

function handleCreateAssistant() {
  try {
    router.push('/ai/assistant');
    console.log('已跳转到创建助手页面');
  } catch (error) {
    console.error('导航失败:', error);
    window.$message?.error('导航失败: ' + (error.message || '未知错误'));
  }
}

function handleDirectAccess() {
  if (!directAccessId.value) {
    window.$message?.error('请输入有效的助手ID');
    return;
  }
  
  // 确保ID是正确的格式
  const assistantId = parseInt(directAccessId.value, 10);
  if (isNaN(assistantId)) {
    window.$message?.error('助手ID格式错误');
    return;
  }
  
  console.log('直接访问助手，ID:', assistantId);
  try {
    // 使用完整URL字符串形式
    router.push(`/ai/chat?id=${assistantId}`);
    console.log('已跳转到聊天页面，URL:', `/ai/chat?id=${assistantId}`);
  } catch (error) {
    console.error('导航失败:', error);
    window.$message?.error('导航失败: ' + (error.message || '未知错误'));
  }
}
</script>

<style scoped>
.assistant-list {
  min-height: 300px;
}

.assistant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.assistant-name {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.assistant-content {
  min-height: 80px;
}

.assistant-description {
  margin: 0;
  color: var(--text-color-3);
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.assistant-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.create-card {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.create-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-color-3);
  height: 180px;
}

.create-content p {
  margin-top: 12px;
}

.empty-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: var(--text-color-3);
}

.empty-list p {
  margin: 16px 0;
}
</style> 