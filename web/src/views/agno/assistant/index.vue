<template>
  <CommonPage>
    <div class="assistant-container">
      <!-- 操作栏 -->
      <div class="action-bar">
        <NSpace>
          <NButton type="primary" @click="handleAdd">
            <template #icon>
              <NIcon>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6z" />
                </svg>
              </NIcon>
            </template>
            新建助手
          </NButton>
          <NButton @click="loadAssistants">
            <template #icon>
              <NIcon>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M17.65 6.35A7.958 7.958 0 0 0 12 4a8 8 0 0 0-8 8a8 8 0 0 0 8 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0 1 12 18a6 6 0 0 1-6-6a6 6 0 0 1 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4z" />
                </svg>
              </NIcon>
            </template>
            刷新
          </NButton>
        </NSpace>
      </div>

      <!-- 数据表格 -->
      <NDataTable
        :columns="columns"
        :data="assistantList"
        :loading="loading"
        :pagination="pagination"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
        :bordered="false"
        striped
        size="medium"
      />

      <!-- 模态框 -->
      <NModal
        v-model:show="modalVisible"
        preset="card"
        :title="modalTitle"
        :style="{ width: '600px' }"
      >
        <NForm
          ref="modalFormRef"
          :model="modalForm"
          :rules="rules"
          label-placement="left"
          label-width="100"
          require-mark-placement="right-hanging"
        >
          <NFormItem label="名称" path="name">
            <NInput v-model:value="modalForm.name" placeholder="请输入助手名称" />
          </NFormItem>
          
          <NFormItem label="描述" path="description">
            <NInput
              v-model:value="modalForm.description"
              placeholder="请输入助手描述"
              type="textarea"
              :autosize="{ minRows: 3, maxRows: 5 }"
            />
          </NFormItem>
          
          <NFormItem label="模型" path="model_id">
            <NSelect
              v-model:value="modalForm.model_id"
              :options="modelOptions"
              placeholder="请选择模型"
            />
          </NFormItem>
          
          <NFormItem label="模型主机" path="model_host">
            <NInput
              v-model:value="modalForm.model_host"
              placeholder="可选，例如 http://localhost:11434"
            />
          </NFormItem>
          
          <NFormItem label="ChatAnywhere">
            <NSwitch v-model:value="modalForm.configuration.use_chatanywhere" />
          </NFormItem>
          
          <NFormItem label="API密钥" v-if="modalForm.configuration.use_chatanywhere">
            <NInput
              v-model:value="modalForm.configuration.api_key"
              type="password"
              placeholder="输入ChatAnywhere API密钥"
              show-password-on="click"
            />
          </NFormItem>
          
          <NFormItem label="状态">
            <NSwitch v-model:value="modalForm.is_active" />
          </NFormItem>
        </NForm>
        <template #footer>
          <NSpace justify="end">
            <NButton @click="modalVisible = false">取消</NButton>
            <NButton type="primary" :loading="modalLoading" @click="handleSave">确定</NButton>
          </NSpace>
        </template>
      </NModal>
    </div>
  </CommonPage>
</template>

<script setup>
import { h, onMounted, ref, resolveDirective, withDirectives } from 'vue'
import {
  NButton,
  NForm,
  NFormItem,
  NInput,
  NSpace,
  NPopconfirm,
  NLayout,
  NModal,
  NCard,
  NTag,
  NDataTable,
  NPagination,
  NIcon,
  NSwitch,
  NSelect
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import { formatDate, renderIcon } from '@/utils'
import { getAssistants, createAssistant, updateAssistant, deleteAssistant } from '@/api/agno'
import { useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'

defineOptions({ name: 'AI助手管理' })

const message = useMessage()
const router = useRouter()
const vPermission = resolveDirective('permission')

// 助手列表相关
const assistantList = ref([])
const loading = ref(false)
const pagination = ref({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 50],
  showSizePicker: true,
  prefix: ({ itemCount }) => `共 ${itemCount} 条`
})

// 模态框相关
const modalVisible = ref(false)
const modalTitle = ref('')
const modalLoading = ref(false)
const modalAction = ref('create') // 'create' 或 'update'
const modalForm = ref({
  id: undefined,
  name: '',
  description: '',
  model_id: '',
  model_host: '',
  is_active: true,
  configuration: {
    use_chatanywhere: false,
    api_key: '',
    markdown: true
  }
})
const modalFormRef = ref(null)
const rules = {
  name: [{ required: true, message: '名称必填', trigger: 'blur' }],
  model_id: [{ required: true, message: '模型必选', trigger: 'change' }]
}

// 模型选项
const modelOptions = [
  { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
  { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
  { value: 'gpt-4o', label: 'GPT-4o' },
  { value: 'llama2', label: 'Llama 2' },
  { value: 'deepseek-r1:14b', label: 'DeepSeek R1 14B' }
]

// 表格列定义
const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 80,
    align: 'center'
  },
  {
    title: '名称',
    key: 'name',
    align: 'left',
    ellipsis: { tooltip: true },
    width: 200
  },
  {
    title: '描述',
    key: 'description',
    align: 'left',
    ellipsis: { tooltip: true }
  },
  {
    title: '模型',
    key: 'model_id',
    width: 150,
    align: 'center',
    render(row) {
      return h(NTag, { type: 'info' }, { default: () => row.model_id })
    }
  },
  {
    title: '状态',
    key: 'is_active',
    width: 100,
    align: 'center',
    render(row) {
      return h(NTag, { type: row.is_active ? 'success' : 'error' }, { 
        default: () => row.is_active ? '活跃' : '禁用' 
      })
    }
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    align: 'center',
    render(row) {
      return h('span', {}, formatDate(row.created_at))
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 250,
    align: 'center',
    fixed: 'right',
    render(row) {
      return [
        h(
          NButton,
          {
            size: 'small',
            type: 'primary',
            style: 'margin-right: 8px;',
            onClick: () => handleChat(row)
          },
          {
            default: () => '对话',
            icon: renderIcon('material-symbols:chat', { size: 16 })
          }
        ),
        h(
          NButton,
          {
            size: 'small',
            type: 'info',
            style: 'margin-right: 8px;',
            onClick: () => handleEdit(row)
          },
          {
            default: () => '编辑',
            icon: renderIcon('material-symbols:edit', { size: 16 })
          }
        ),
        h(
          NPopconfirm,
          {
            onPositiveClick: () => handleDelete(row),
            onNegativeClick: () => {}
          },
          {
            trigger: () =>
              h(
                NButton,
                {
                  size: 'small',
                  type: 'error'
                },
                {
                  default: () => '删除',
                  icon: renderIcon('material-symbols:delete-outline', { size: 16 })
                }
              ),
            default: () => h('div', {}, '确定删除该助手吗？')
          }
        )
      ]
    }
  }
]

// 生命周期钩子
onMounted(() => {
  loadAssistants()
})

// 加载助手列表
async function loadAssistants() {
  loading.value = true
  try {
    const response = await getAssistants()
    if (response.code === 200) {
      assistantList.value = response.data
      pagination.value.itemCount = response.data.length
    } else {
      message.error('获取助手列表失败')
    }
  } catch (error) {
    message.error('获取助手列表出错: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 处理页码变化
function handlePageChange(page) {
  pagination.value.page = page
}

// 处理每页条数变化
function handlePageSizeChange(pageSize) {
  pagination.value.pageSize = pageSize
  pagination.value.page = 1
}

// 重置表单
function resetModalForm() {
  modalForm.value = {
    id: undefined,
    name: '',
    description: '',
    model_id: '',
    model_host: '',
    is_active: true,
    configuration: {
      use_chatanywhere: false,
      api_key: '',
      markdown: true
    }
  }
  if (modalFormRef.value) {
    modalFormRef.value.restoreValidation()
  }
}

// 添加助手
function handleAdd() {
  resetModalForm()
  modalAction.value = 'create'
  modalTitle.value = '创建助手'
  modalVisible.value = true
}

// 编辑助手
function handleEdit(row) {
  resetModalForm()
  modalAction.value = 'update'
  modalTitle.value = '编辑助手'
  
  // 深拷贝行数据
  const rowData = JSON.parse(JSON.stringify(row))
  
  // 确保配置对象存在
  if (!rowData.configuration) {
    rowData.configuration = {
      use_chatanywhere: false,
      api_key: '',
      markdown: true
    }
  }
  
  modalForm.value = rowData
  modalVisible.value = true
}

// 保存助手（新增或更新）
async function handleSave() {
  if (!modalFormRef.value) return
  
  await modalFormRef.value.validate()
  modalLoading.value = true
  
  try {
    if (modalAction.value === 'create') {
      // 创建助手
      const response = await createAssistant(modalForm.value)
      if (response.code === 200) {
        message.success('创建助手成功')
        modalVisible.value = false
        loadAssistants()
      } else {
        message.error('创建助手失败: ' + response.msg)
      }
    } else {
      // 更新助手
      const response = await updateAssistant(modalForm.value.id, modalForm.value)
      if (response.code === 200) {
        message.success('更新助手成功')
        modalVisible.value = false
        loadAssistants()
      } else {
        message.error('更新助手失败: ' + response.msg)
      }
    }
  } catch (error) {
    message.error('操作失败: ' + error.message)
  } finally {
    modalLoading.value = false
  }
}

// 删除助手
async function handleDelete(row) {
  try {
    const response = await deleteAssistant(row.id)
    if (response.code === 200) {
      message.success('删除助手成功')
      loadAssistants()
    } else {
      message.error('删除助手失败: ' + response.msg)
    }
  } catch (error) {
    message.error('删除失败: ' + error.message)
  }
}

// 跳转到聊天页面
function handleChat(row) {
  if (!row || !row.id) {
    message.error('无效的助手ID');
    return;
  }
  
  try {
    // 确保ID是正确的格式
    const assistantId = parseInt(row.id, 10);
    if (isNaN(assistantId)) {
      message.error('助手ID格式错误');
      return;
    }
    
    console.log('准备跳转到聊天页面，助手ID:', assistantId);
    
    // 使用正确的URL字符串形式，确保使用query参数
    router.push(`/ai/chat?id=${assistantId}`);
    
    // 添加调试日志
    console.log('导航完成，跳转到URL:', `/ai/chat?id=${assistantId}`);
  } catch (error) {
    console.error('导航出错:', error);
    message.error('导航失败: ' + (error.message || '未知错误'));
  }
}
</script>

<style scoped>
.assistant-container {
  width: 100%;
}

.action-bar {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
}
</style> 