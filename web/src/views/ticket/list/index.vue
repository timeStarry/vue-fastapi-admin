<template>
  <!-- 业务页面 -->
  <CommonPage show-footer title="工单列表">
    <template #action>
      <div>
        <NButton
          v-permission="'post/api/v1/ticket/create'"
          class="float-right mr-15"
          type="primary"
          @click="handleAdd"
        >
          <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />新建工单
        </NButton>
      </div>
    </template>
    <!-- 表格 -->
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getTicketList"
      :scroll-x="1500"
    >
      <template #queryBar>
        <QueryBarItem label="工单编号" :label-width="70">
          <NInput
            v-model:value="queryItems.ticket_no"
            clearable
            placeholder="请输入工单编号"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="工单标题" :label-width="70">
          <NInput
            v-model:value="queryItems.title"
            clearable
            placeholder="请输入工单标题"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="工单类型" :label-width="70">
          <NSelect
            v-model:value="queryItems.type"
            clearable
            :options="typeOptions"
            placeholder="请选择工单类型"
            style="width: 180px"
          />
        </QueryBarItem>
        <QueryBarItem label="工单状态" :label-width="70">
          <NSelect
            v-model:value="queryItems.status"
            clearable
            :options="statusOptions"
            placeholder="请选择工单状态"
            style="width: 180px"
          />
        </QueryBarItem>
        <QueryBarItem label="优先级" :label-width="70">
          <NSelect
            v-model:value="queryItems.priority"
            clearable
            :options="priorityOptions"
            placeholder="请选择优先级"
            style="width: 180px"
          />
        </QueryBarItem>
        <QueryBarItem label="创建时间" :label-width="70">
          <NDatePicker
            v-model:value="queryItems.date_range"
            clearable
            type="daterange"
            placeholder="请选择时间范围"
          />
        </QueryBarItem>
        <QueryBarItem label="处理人" :label-width="70">
          <NSelect
            v-model:value="queryItems.assignee_id"
            clearable
            :options="userOptions"
            placeholder="请选择处理人"
            style="width: 180px"
          />
        </QueryBarItem>
      </template>
      <template #action>
        <NButton type="primary" @click="handleAdd">
          <template #icon>
            <TheIcon icon="material-symbols:add-circle-outline-rounded" />
          </template>
          新建工单
        </NButton>
      </template>
    </CrudTable>

    <CrudModal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      width="800px"
      @save="customHandleSave"
    >
      <n-form
        ref="modalFormRef"
        :model="modalForm"
        :rules="rules"
        label-placement="left"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <n-grid :cols="24" :x-gap="24">
          <n-grid-item :span="24">
            <div class="flex items-center justify-between mb-2">
              <n-form-item label="工单标题" path="title" style="flex: 1; margin-bottom: 0;">
                <n-input 
                  v-model:value="modalForm.title" 
                  placeholder="请输入工单标题"
                  :style="getFieldStyle('title')"
                  @input="() => console.log('标题输入:', modalForm.title)"
                />
              </n-form-item>
              <n-button 
                type="primary" 
                secondary 
                class="ml-2" 
                :loading="aiGenerating"
                @click="showAIGenerateModal = true"
              >
                <template #icon>
                  <TheIcon icon="mdi:robot" />
                </template>
                智能生成
              </n-button>
            </div>
          </n-grid-item>
          <n-grid-item :span="12">
            <n-form-item label="工单类型" path="type">
              <n-select
                v-model:value="modalForm.type"
                clearable
                :options="typeOptions"
                :style="getFieldStyle('type')"
                placeholder="请选择工单类型"
                @update:value="(val) => console.log('类型选择:', val)"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item :span="12">
            <n-form-item label="优先级" path="priority">
              <n-select
                v-model:value="modalForm.priority"
                clearable
                :options="priorityOptions"
                :style="getFieldStyle('priority')"
                placeholder="请选择优先级"
                @update:value="(val) => console.log('优先级选择:', val)"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item :span="12">
            <n-form-item label="处理人" path="assignee_id">
              <n-select
                v-model:value="modalForm.assignee_id"
                clearable
                :options="userOptions"
                placeholder="请选择处理人"
                @update:value="(val) => console.log('处理人选择:', val)"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item :span="12">
            <n-form-item label="期望完成时间" path="expected_time">
              <n-date-picker
                v-model:value="modalForm.expected_time"
                type="datetime"
                clearable
                placeholder="请选择期望完成时间"
                @update:value="(val) => console.log('日期选择:', val)"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item :span="24">
            <n-form-item label="工单描述" path="description">
              <n-input
                v-model:value="modalForm.description"
                type="textarea"
                :style="getFieldStyle('description')"
                :autosize="{
                  minRows: 3,
                  maxRows: 6,
                }"
                placeholder="请输入工单详细描述"
                @input="() => console.log('描述输入:', modalForm.description)"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item :span="24">
            <n-form-item label="附件" path="attachments">
              <n-upload
                v-model:file-list="modalForm.attachments"
                :action="uploadUrl"
                :headers="{
                  Authorization: `Bearer ${token}`,
                }"
                :max="5"
                list-type="image-card"
              >
                上传附件
              </n-upload>
            </n-form-item>
          </n-grid-item>
        </n-grid>
      </n-form>
    </CrudModal>

    <!-- 添加AI生成对话框 -->
    <n-modal 
      v-model:show="showAIGenerateModal" 
      preset="dialog" 
      title="智能生成工单" 
      positive-text="生成" 
      negative-text="取消" 
      @positive-click="handleAIGenerate" 
      @negative-click="cancelAIGenerate"
      style="width: 60%;"
    >
      <n-input
        v-model:value="aiDescription"
        type="textarea"
        placeholder="请简要描述您的问题或需求，AI将为您智能生成工单..."
        :autosize="{ minRows: 4, maxRows: 8 }"
      />
      <div v-if="aiGenerating" class="mt-2 text-gray-500">
        <n-spin size="small" />
        <span class="ml-2">正在生成，请稍候...</span>
      </div>
    </n-modal>
  </CommonPage>
</template>

<script setup>
import { h, onMounted, ref, resolveDirective, withDirectives, nextTick, watch } from 'vue'
import {
  NButton,
  NGrid,
  NGridItem,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NDatePicker,
  NUpload,
  NTag,
  NPopconfirm,
  NSpace,
  NModal,
  NSpin,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

import { formatDate, renderIcon } from '@/utils'
import { useCRUD } from '@/composables'
import api from '@/api'
import { getToken } from '@/utils/auth/token'
import { useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'

defineOptions({ name: '工单列表' })

const $table = ref(null)
const queryItems = ref({})
const vPermission = resolveDirective('permission')
const token = getToken()
const uploadUrl = `${import.meta.env.VITE_API_BASE_URL}/api/v1/tickets/upload`
const message = useMessage()
const router = useRouter()

// 工单类型选项
const typeOptions = [
  { label: '故障报修', value: 'fault' },
  { label: '资源申请', value: 'resource' },
  { label: '配置变更', value: 'config' },
  { label: '日常维护', value: 'maintenance' },
  { label: '紧急处理', value: 'emergency' },
]

// 工单状态选项
const statusOptions = [
  { label: '待接单', value: 'pending', type: 'warning' },
  { label: '处理中', value: 'processing', type: 'info' },
  { label: '待确认', value: 'confirming', type: 'success' },
  { label: '已完成', value: 'completed', type: 'success' },
  { label: '已关闭', value: 'closed', type: 'error' },
]

// 工单优先级选项
const priorityOptions = [
  { label: '低', value: 'low', type: 'default' },
  { label: '中', value: 'medium', type: 'info' },
  { label: '高', value: 'high', type: 'warning' },
  { label: '紧急', value: 'urgent', type: 'error' },
]

// 用户选项，在mounted中获取
const userOptions = ref([])

// 表单验证规则
const rules = {
  title: { required: true, message: '请输入工单标题', trigger: ['blur', 'input'] },
  type: { required: true, message: '请选择工单类型', trigger: ['blur', 'change'] },
  priority: { required: true, message: '请选择优先级', trigger: ['blur', 'change'] },
  description: { required: true, message: '请输入工单描述', trigger: ['blur', 'input'] },
}

// API 调用处理
const {
  modalVisible,
  modalTitle,
  modalAction,
  modalLoading,
  handleSave,
  modalForm,
  modalFormRef,
  handleEdit,
  handleDelete,
  handleAdd,
} = useCRUD({
  name: '工单',
  initForm: {
    title: '',
    type: '',
    priority: 'medium',
    assignee_id: null,
    expected_time: null,
    description: '',
    attachments: [],
  },
  doCreate: (formData) => {
    // 创建一个新对象用于提交，保持原始表单数据不变
    const submitData = {
      title: formData.title || '未命名工单',
      description: formData.description || '无描述',
      type: formData.type || 'task',
      priority: formData.priority || 'medium'
    }
    
    // 可选字段需要特殊处理
    if (formData.assignee_id) {
      submitData.assignee_id = Number(formData.assignee_id)
    }
    
    // 日期格式转换
    if (formData.expected_time) {
      // 如果是Date对象，转为ISO字符串
      if (formData.expected_time instanceof Date) {
        submitData.expected_time = formData.expected_time.toISOString()
      } else if (typeof formData.expected_time === 'string') {
        // 尝试将字符串解析为日期
        try {
          const date = new Date(formData.expected_time)
          submitData.expected_time = date.toISOString()
        } catch (e) {
          console.error('日期格式转换失败', e)
        }
      }
    }
    
    console.log('提交至API的工单数据:', submitData)
    return api.createTicket(submitData)
  },
  doUpdate: (data) => {
    // 调用实际的API更新工单
    return api.updateTicket(data)
  },
  doDelete: (params) => {
    // 调用实际的API删除工单
    return api.deleteTicket(params)
  },
  refresh: () => $table.value?.handleSearch(),
})

// AI智能生成相关
const showAIGenerateModal = ref(false)
const aiDescription = ref('')
const aiGenerating = ref(false)

// 添加高亮状态控制
const highlightFields = ref({
  title: false,
  description: false,
  type: false,
  priority: false
})

// 设置高亮效果函数
function setHighlight(duration = 3000) {
  // 所有字段设置为高亮
  Object.keys(highlightFields.value).forEach(key => {
    highlightFields.value[key] = true
  })
  
  // 3秒后取消高亮
  setTimeout(() => {
    Object.keys(highlightFields.value).forEach(key => {
      highlightFields.value[key] = false
    })
  }, duration)
}

// 取消AI生成
function cancelAIGenerate() {
  showAIGenerateModal.value = false
  aiDescription.value = ''
}

// 智能生成工单
async function handleAIGenerate() {
  if (!aiDescription.value) {
    message.warning('请输入问题或需求描述')
    return
  }
  
  aiGenerating.value = true
  let aiGeneratedData = null
  
  try {
    // 1. 调用API获取AI生成的工单数据
    console.log('正在调用AI生成工单API...')
    const res = await api.generateTicket({ description: aiDescription.value })
    console.log('AI生成工单返回数据:', res)
    
    if (res && res.data) {
      // 存储AI生成的数据以备后用
      aiGeneratedData = res.data
      console.log('成功获取AI工单数据:', aiGeneratedData)
      
      // 先关闭AI生成对话框
      showAIGenerateModal.value = false
      aiDescription.value = '' // 清空描述，以便下次使用
    } else {
      message.error('工单生成失败: 服务器返回数据异常')
      return
    }
  } catch (error) {
    console.error('AI工单生成错误:', error)
    message.error('工单生成失败: ' + (error.message || '未知错误'))
    aiGenerating.value = false
    return
  }
  
  try {
    // 2. 打开新建工单模态框
    console.log('打开新建工单对话框...')
    // 查看handleAdd函数的实现
    console.log('handleAdd函数:', handleAdd)
    // 检查当前modalForm的状态
    console.log('modalForm修改前:', modalForm.value)
    
    // 打开模态框
    handleAdd()
    console.log('modalVisible设置为:', modalVisible.value)
    console.log('modalForm在handleAdd后:', modalForm.value)
    
    // 等待模态框完全打开和表单初始化
    await nextTick()
    console.log('nextTick后modalForm:', modalForm.value)
    
    // 3. 确保模态框已成功显示
    if (!modalVisible.value) {
      console.error('模态框未能成功打开')
      message.error('打开工单表单失败，请重试')
      aiGenerating.value = false
      return
    }
    
    // 4. 填充表单数据
    console.log('开始填充表单...')
    
    // 重要: 创建一个完整的新对象，而不是更新原有对象的属性
    const newFormData = {
      // 默认值
      title: '',
      description: '',
      type: 'task',
      priority: 'medium',
      expected_time: null,
      assignee_id: null,
      attachments: [],
    }
    
    // 使用AI生成的数据覆盖默认值
    if (aiGeneratedData.title) newFormData.title = aiGeneratedData.title
    if (aiGeneratedData.description) newFormData.description = aiGeneratedData.description
    
    // 类型处理
    if (aiGeneratedData.type && ['fault', 'resource', 'config', 'maintenance', 'emergency', 'task', 'request'].includes(aiGeneratedData.type)) {
      newFormData.type = aiGeneratedData.type
    }
    
    // 优先级处理
    if (aiGeneratedData.priority && ['low', 'medium', 'high', 'urgent', 'critical'].includes(aiGeneratedData.priority)) {
      newFormData.priority = aiGeneratedData.priority
    }
    
    // 日期处理
    if (aiGeneratedData.expected_time) {
      try {
        newFormData.expected_time = new Date(aiGeneratedData.expected_time)
      } catch (e) {
        console.error('日期解析错误:', e)
      }
    }
    
    // 处理人ID处理
    if (aiGeneratedData.assignee_id && Number.isInteger(Number(aiGeneratedData.assignee_id))) {
      newFormData.assignee_id = Number(aiGeneratedData.assignee_id)
    }
    
    // 5. 使用完全新的对象替换表单数据，确保触发响应式更新
    console.log('即将填充表单数据:', newFormData)
    
    // 注意：我们发现直接替换整个对象可能不会触发更新，
    // 所以改为逐个属性赋值，确保Vue的响应式系统能够检测到更改
    for (const key in newFormData) {
      console.log(`设置属性 ${key}:`, newFormData[key])
      modalForm.value[key] = newFormData[key]
    }
    
    // 确保数据赋值后表单显示正确
    console.log('填充后的表单数据:', modalForm.value)
    
    // 等待DOM更新
    await nextTick()
    console.log('nextTick后的表单数据:', modalForm.value)
    
    // 6. 检查表单是否成功填充
    if (modalForm.value.title !== newFormData.title || 
        modalForm.value.description !== newFormData.description) {
      console.error('表单填充异常，设置值与实际值不匹配')
      console.log('期望值:', newFormData)
      console.log('实际值:', modalForm.value)
    } else {
      console.log('表单填充成功，当前表单数据:', modalForm.value)
      message.success('工单已智能生成，请检查并提交')
      
      // 设置高亮效果，引导用户注意
      setHighlight()
    }
  } catch (error) {
    console.error('表单填充过程中出错:', error)
    message.error('填充表单失败: ' + (error.message || '未知错误'))
  } finally {
    aiGenerating.value = false
  }
}

// 监听表单数据变化，用于调试
watch(() => modalForm.value, (newValue, oldValue) => {
  console.log('表单数据变化:', newValue)
}, { deep: true })

// 监听模态框状态变化
watch(() => modalVisible.value, (isVisible) => {
  if (isVisible) {
    console.log('模态框已打开，当前表单数据:', modalForm.value)
  }
})

// 状态标签渲染函数
function renderStatusTag(row) {
  const statusInfo = statusOptions.find(item => item.value === row.status) || { label: '未知', type: 'default' }
  return h(NTag, { type: statusInfo.type, style: { marginRight: '5px' } }, {
    default: () => statusInfo.label
  })
}

// 优先级标签渲染函数
function renderPriorityTag(row) {
  const priorityInfo = priorityOptions.find(item => item.value === row.priority) || { label: '未知', type: 'default' }
  return h(NTag, { type: priorityInfo.type, style: { marginRight: '5px' } }, {
    default: () => priorityInfo.label
  })
}

// 表格列配置
const columns = [
  {
    title: '工单编号',
    key: 'ticket_no',
    width: 120,
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '标题',
    key: 'title',
    width: 200,
    align: 'left',
    ellipsis: { tooltip: true },
  },
  {
    title: '类型',
    key: 'type',
    width: 100,
    align: 'center',
    render(row) {
      const typeInfo = typeOptions.find(item => item.value === row.type) || { label: '未知' }
      return h('span', typeInfo.label)
    }
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    align: 'center',
    render: renderStatusTag
  },
  {
    title: '优先级',
    key: 'priority',
    width: 80,
    align: 'center',
    render: renderPriorityTag
  },
  {
    title: '创建人',
    key: 'creator_name',
    width: 100,
    align: 'center',
  },
  {
    title: '处理人',
    key: 'assignee_name',
    width: 100,
    align: 'center',
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 160,
    align: 'center',
    render(row) {
      return h('span', formatDate(row.created_at))
    }
  },
  {
    title: '期望完成时间',
    key: 'expected_time',
    width: 160,
    align: 'center',
    render(row) {
      return h('span', row.expected_time ? formatDate(row.expected_time) : '-')
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 220,
    align: 'center',
    fixed: 'right',
    render(row) {
      return h(NSpace, { justify: 'center' }, {
        default: () => [
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              onClick: () => {
                window.open(`/ticket/process?id=${row.id}`, '_blank')
              },
            },
            {
              default: () => '详情',
              icon: renderIcon('material-symbols:visibility-outline', { size: 16 }),
            }
          ),
          withDirectives(
            h(
              NButton,
              {
                size: 'small',
                type: 'info',
                onClick: () => {
                  window.open(`/ticket/process?id=${row.id}`, '_blank')
                },
              },
              {
                default: () => '处理',
                icon: renderIcon('material-symbols:settings-outline', { size: 16 }),
              }
            ),
            [[vPermission, 'post/api/v1/tickets/process']]
          ),
          withDirectives(
            h(
              NPopconfirm,
              {
                onPositiveClick: () => handleDelete({ ticket_id: row.id }),
              },
              {
                trigger: () => h(
                  NButton,
                  {
                    size: 'small',
                    type: 'error',
                  },
                  {
                    default: () => '删除',
                    icon: renderIcon('material-symbols:delete-outline', { size: 16 }),
                  }
                ),
                default: () => '确认删除该工单吗？'
              }
            ),
            [[vPermission, 'delete/api/v1/tickets/delete']]
          ),
        ]
      })
    }
  }
]

onMounted(async () => {
  try {
    // 获取用户列表，实际项目中可以调用API获取
    const { data } = await api.getUserList()
    userOptions.value = data?.map(user => ({
      label: user.username,
      value: user.id
    })) || []
  } catch (err) {
    console.error('获取用户列表失败:', err)
    // 使用备用数据
    userOptions.value = [
      { label: 'admin', value: 1 },
      { label: '李四', value: 2 },
      { label: '王五', value: 3 },
      { label: '赵六', value: 4 }
    ]
  }
  
  // 加载工单列表
  $table.value?.handleSearch()
})

// 重新实现handleSave函数，添加调试信息
function customHandleSave() {
  console.log('CrudModal触发保存事件，当前表单数据:', modalForm.value)
  // 验证表单
  modalFormRef.value?.validate(async (errors) => {
    if (errors) {
      console.error('表单验证失败:', errors)
      return
    }
    
    try {
      console.log('表单验证成功，准备提交数据:', modalForm.value)
      // 创建一个新对象用于提交，保持原始表单数据不变
      const submitData = {
        title: modalForm.value.title || '未命名工单',
        description: modalForm.value.description || '无描述',
        type: modalForm.value.type || 'task',
        priority: modalForm.value.priority || 'medium'
      }
      
      // 可选字段需要特殊处理
      if (modalForm.value.assignee_id) {
        submitData.assignee_id = Number(modalForm.value.assignee_id)
      }
      
      // 日期格式转换
      if (modalForm.value.expected_time) {
        // 如果是Date对象，转为ISO字符串
        if (modalForm.value.expected_time instanceof Date) {
          submitData.expected_time = modalForm.value.expected_time.toISOString()
        } else if (typeof modalForm.value.expected_time === 'string') {
          // 尝试将字符串解析为日期
          try {
            const date = new Date(modalForm.value.expected_time)
            submitData.expected_time = date.toISOString()
          } catch (e) {
            console.error('日期格式转换失败', e)
          }
        }
      }
      
      console.log('最终提交至API的工单数据:', submitData)
      modalLoading.value = true
      const result = await api.createTicket(submitData)
      console.log('API返回结果:', result)
      modalLoading.value = false
      modalVisible.value = false
      message.success('工单创建成功!')
      $table.value?.handleSearch() // 刷新表格数据
    } catch (error) {
      console.error('提交工单出错:', error)
      message.error('创建工单失败: ' + (error.message || '未知错误'))
      modalLoading.value = false
    }
  })
}

// 定义表单项样式
const getFieldStyle = (field) => {
  if (highlightFields.value[field]) {
    return {
      background: 'rgba(255, 241, 232, 0.3)',
      boxShadow: '0 0 0 2px #FF9800',
      borderRadius: '3px',
      transition: 'all 0.3s ease-in-out'
    }
  }
  return {}
}
</script> 