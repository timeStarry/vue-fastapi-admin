<template>
  <CommonPage>
    <template #header>
      <div flex items-center justify-between w-full>
        <h2 text-22 font-normal text-hex-333 dark:text-hex-ccc>工单处理</h2>
        <n-space>
          <n-button @click="$router.back()">
            <template #icon>
              <the-icon name="material-symbols:arrow-back" />
            </template>
            返回
          </n-button>
        </n-space>
      </div>
    </template>

    <div v-if="loading">
      <n-spin size="large" />
    </div>
    <div v-else-if="!ticketData">
      <n-empty description="未找到工单信息" />
    </div>
    <div v-else>
      <!-- 工单基本信息 -->
      <n-card title="基本信息" class="mb-4">
        <n-grid :cols="3" :x-gap="24">
          <n-grid-item>
            <div class="info-item">
              <span class="info-label">工单编号</span>
              <span>{{ ticketData.ticket_no }}</span>
            </div>
          </n-grid-item>
          <n-grid-item>
            <div class="info-item">
              <span class="info-label">工单标题</span>
              <span>{{ ticketData.title }}</span>
            </div>
          </n-grid-item>
          <n-grid-item>
            <div class="info-item">
              <span class="info-label">工单类型</span>
              <span>{{ getTypeName(ticketData.type) }}</span>
            </div>
          </n-grid-item>
          <n-grid-item>
            <div class="info-item">
              <span class="info-label">工单状态</span>
              <n-tag :type="getStatusType(ticketData.status)">
                {{ getStatusName(ticketData.status) }}
              </n-tag>
            </div>
          </n-grid-item>
          <n-grid-item>
            <div class="info-item">
              <span class="info-label">优先级</span>
              <n-tag :type="getPriorityType(ticketData.priority)">
                {{ getPriorityName(ticketData.priority) }}
              </n-tag>
            </div>
          </n-grid-item>
          <n-grid-item>
            <div class="info-item">
              <span class="info-label">创建人</span>
              <span>{{ ticketData.creator_name }}</span>
            </div>
          </n-grid-item>
          <n-grid-item>
            <div class="info-item">
              <span class="info-label">处理人</span>
              <span>{{ ticketData.assignee_name || '未分配' }}</span>
            </div>
          </n-grid-item>
          <n-grid-item>
            <div class="info-item">
              <span class="info-label">创建时间</span>
              <span>{{ formatDate(ticketData.created_at) }}</span>
            </div>
          </n-grid-item>
          <n-grid-item>
            <div class="info-item">
              <span class="info-label">期望完成时间</span>
              <span>{{ ticketData.expected_time ? formatDate(ticketData.expected_time) : '未设置' }}</span>
            </div>
          </n-grid-item>
        </n-grid>

        <div class="info-item mt-4">
          <span class="info-label">描述</span>
          <div class="description">{{ ticketData.description }}</div>
        </div>

        <div v-if="ticketData.related_devices && ticketData.related_devices.length > 0" class="info-item mt-4">
          <span class="info-label">关联设备</span>
          <div>
            <n-tag
              v-for="device in ticketData.related_devices"
              :key="device.id"
              type="info"
              class="mr-2"
            >
              {{ device.name }}
            </n-tag>
          </div>
        </div>

        <div v-if="ticketData.attachments && ticketData.attachments.length > 0" class="info-item mt-4">
          <span class="info-label">附件</span>
          <div>
            <n-image-group>
              <div v-for="(attachment, index) in ticketData.attachments" :key="index" class="inline-block m-2">
                <n-image
                  v-if="isImage(attachment.url)"
                  :src="attachment.url"
                  height="100"
                  width="100"
                  :alt="attachment.name"
                  object-fit="cover"
                />
                <n-button
                  v-else
                  @click="downloadFile(attachment.url, attachment.name)"
                  size="small"
                  class="mt-2"
                >
                  <template #icon>
                    <the-icon name="material-symbols:download" />
                  </template>
                  {{ attachment.name }}
                </n-button>
              </div>
            </n-image-group>
          </div>
        </div>
      </n-card>

      <!-- 工单流转记录 -->
      <n-card title="处理记录" class="mb-4">
        <n-timeline>
          <n-timeline-item
            v-for="(record, index) in ticketData.process_records"
            :key="index"
            :type="getTimelineType(record.action)"
            :title="record.action_name"
            :time="formatDate(record.created_at)"
          >
            <template #icon>
              <the-icon :name="getTimelineIcon(record.action)" />
            </template>
            <div>
              <div class="font-bold">{{ record.operator_name }}</div>
              <div>{{ record.content }}</div>
              <div v-if="record.attachments && record.attachments.length > 0" class="mt-2">
                <n-image-group>
                  <div v-for="(attachment, aidx) in record.attachments" :key="aidx" class="inline-block m-2">
                    <n-image
                      v-if="isImage(attachment.url)"
                      :src="attachment.url"
                      height="80"
                      width="80"
                      :alt="attachment.name"
                      object-fit="cover"
                    />
                    <n-button
                      v-else
                      @click="downloadFile(attachment.url, attachment.name)"
                      size="small"
                      class="mt-2"
                    >
                      <template #icon>
                        <the-icon name="material-symbols:download" />
                      </template>
                      {{ attachment.name }}
                    </n-button>
                  </div>
                </n-image-group>
              </div>
            </div>
          </n-timeline-item>
        </n-timeline>
      </n-card>

      <!-- 工单处理表单 -->
      <n-card title="处理工单" v-if="canProcess">
        <n-form
          ref="processFormRef"
          :model="processForm"
          :rules="processRules"
          label-placement="left"
          label-width="100"
          require-mark-placement="right-hanging"
        >
          <n-form-item label="处理动作" path="action">
            <n-radio-group v-model:value="processForm.action">
              <n-space>
                <n-radio
                  v-for="action in availableActions"
                  :key="action.value"
                  :value="action.value"
                  :disabled="action.disabled"
                >
                  {{ action.label }}
                </n-radio>
              </n-space>
            </n-radio-group>
          </n-form-item>

          <n-form-item v-if="processForm.action === 'transfer'" label="转派给" path="assignee_id">
            <n-select
              v-model:value="processForm.assignee_id"
              :options="userOptions"
              placeholder="请选择转派对象"
            />
          </n-form-item>

          <n-form-item label="处理意见" path="content">
            <n-input
              v-model:value="processForm.content"
              type="textarea"
              :autosize="{
                minRows: 3,
                maxRows: 6,
              }"
              placeholder="请输入处理意见"
            />
          </n-form-item>

          <n-form-item label="上传附件">
            <n-upload
              v-model:file-list="processForm.attachments"
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

          <n-form-item>
            <n-button type="primary" @click="handleProcess" :loading="processLoading">
              提交处理
            </n-button>
          </n-form-item>
        </n-form>
      </n-card>
    </div>
  </CommonPage>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NCard,
  NEmpty,
  NForm,
  NFormItem,
  NGrid,
  NGridItem,
  NImage,
  NImageGroup,
  NInput,
  NRadio,
  NRadioGroup,
  NSelect,
  NSpace,
  NTag,
  NSpin,
  NTimeline,
  NTimelineItem,
  useMessage,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

import { formatDate } from '@/utils'
import api from '@/api'
import { getToken } from '@/utils/auth/token'
import { useUserStore } from '@/store'

defineOptions({ name: '工单处理' })

const $message = useMessage()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const token = getToken()
const uploadUrl = `${import.meta.env.VITE_API_BASE_URL}/api/v1/ticket/upload`

// 工单数据
const ticketId = computed(() => route.query.id)
const loading = ref(true)
const ticketData = ref(null)

// 处理表单
const processFormRef = ref(null)
const processLoading = ref(false)
const processForm = ref({
  action: 'process',
  content: '',
  assignee_id: null,
  attachments: [],
})

// 用户选项，在mounted中获取
const userOptions = ref([])

// 表单验证规则
const processRules = {
  action: { required: true, message: '请选择处理动作', trigger: 'blur' },
  content: { required: true, message: '请输入处理意见', trigger: ['blur', 'input'] },
  assignee_id: {
    required: true,
    message: '请选择转派对象',
    trigger: ['blur', 'change'],
    type: 'number',
  },
}

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

// 可用的处理动作
const availableActions = computed(() => {
  if (!ticketData.value) return []
  
  const actions = []
  const currentStatus = ticketData.value.status
  
  // 根据当前状态决定可用的操作
  if (currentStatus === 'pending') {
    actions.push({ label: '接单', value: 'accept' })
    actions.push({ label: '转派', value: 'transfer' })
    actions.push({ label: '关闭', value: 'close' })
  } else if (currentStatus === 'processing') {
    actions.push({ label: '处理', value: 'process' })
    actions.push({ label: '完成', value: 'complete' })
    actions.push({ label: '转派', value: 'transfer' })
    actions.push({ label: '关闭', value: 'close' })
  } else if (currentStatus === 'confirming') {
    // 只有创建人才能确认
    const isCreator = userStore.userId === ticketData.value.creator_id
    actions.push({ label: '确认', value: 'confirm', disabled: !isCreator })
    actions.push({ label: '退回', value: 'reject', disabled: !isCreator })
    actions.push({ label: '关闭', value: 'close' })
  } else if (currentStatus === 'completed' || currentStatus === 'closed') {
    actions.push({ label: '重开', value: 'reopen' })
  }
  
  return actions
})

// 是否可以处理工单
const canProcess = computed(() => {
  if (!ticketData.value) return false
  
  // 管理员可以处理所有工单
  if (userStore.isSuperuser) return true
  
  // 处理人可以处理分配给自己的工单
  if (ticketData.value.assignee_id === userStore.userId) return true
  
  // 创建人可以对待确认的工单进行确认或退回
  if (ticketData.value.creator_id === userStore.userId && ticketData.value.status === 'confirming') return true
  
  return false
})

// 获取类型名称
function getTypeName(type) {
  const found = typeOptions.find(item => item.value === type)
  return found ? found.label : '未知'
}

// 获取状态名称
function getStatusName(status) {
  const found = statusOptions.find(item => item.value === status)
  return found ? found.label : '未知'
}

// 获取状态类型
function getStatusType(status) {
  const found = statusOptions.find(item => item.value === status)
  return found ? found.type : 'default'
}

// 获取优先级名称
function getPriorityName(priority) {
  const found = priorityOptions.find(item => item.value === priority)
  return found ? found.label : '未知'
}

// 获取优先级类型
function getPriorityType(priority) {
  const found = priorityOptions.find(item => item.value === priority)
  return found ? found.type : 'default'
}

// 获取时间线图标
function getTimelineIcon(action) {
  const actionIcons = {
    create: 'material-symbols:add-circle-outline',
    accept: 'material-symbols:check-circle-outline',
    process: 'material-symbols:settings-outline',
    complete: 'material-symbols:task-alt',
    confirm: 'material-symbols:thumb-up-outline',
    reject: 'material-symbols:thumb-down-outline',
    transfer: 'material-symbols:swap-horiz',
    close: 'material-symbols:cancel-outline',
    reopen: 'material-symbols:restart-alt',
  }
  return actionIcons[action] || 'material-symbols:info-outline'
}

// 获取时间线类型
function getTimelineType(action) {
  const actionTypes = {
    create: 'info',
    accept: 'success',
    process: 'info',
    complete: 'success',
    confirm: 'success',
    reject: 'error',
    transfer: 'warning',
    close: 'error',
    reopen: 'warning',
  }
  return actionTypes[action] || 'default'
}

// 判断是否为图片
function isImage(url) {
  if (!url) return false
  const ext = url.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)
}

// 下载文件
function downloadFile(url, filename) {
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
}

// 获取工单详情
async function fetchTicketDetail() {
  if (!ticketId.value) return
  
  try {
    loading.value = true
    const res = await api.getTicketById({ ticket_id: ticketId.value })
    ticketData.value = res.data
    
    // 如果工单状态为pending且当前用户是分配的处理人，自动选择接单操作
    if (ticketData.value.status === 'pending' && ticketData.value.assignee_id === userStore.userId) {
      processForm.value.action = 'accept'
    }
  } catch (error) {
    $message.error('获取工单详情失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 处理工单
async function handleProcess() {
  processFormRef.value?.validate(async (errors) => {
    if (errors) return
    
    try {
      processLoading.value = true
      
      // 构建处理参数
      const params = {
        ticket_id: ticketId.value,
        action: processForm.value.action,
        content: processForm.value.content,
        attachments: processForm.value.attachments.map(file => file.id || file),
      }
      
      // 如果是转派操作，添加转派目标
      if (processForm.value.action === 'transfer') {
        params.assignee_id = processForm.value.assignee_id
      }
      
      await api.processTicket(params)
      $message.success('处理成功')
      
      // 重新获取工单详情
      await fetchTicketDetail()
      
      // 重置表单
      processForm.value = {
        action: 'process',
        content: '',
        assignee_id: null,
        attachments: [],
      }
    } catch (error) {
      $message.error('处理失败')
      console.error(error)
    } finally {
      processLoading.value = false
    }
  })
}

onMounted(async () => {
  // 加载用户列表
  try {
    const userRes = await api.getUserList({ page: 1, page_size: 99999 })
    userOptions.value = userRes.data.map(user => ({
      label: user.username,
      value: user.id
    }))
  } catch (error) {
    console.error('加载用户列表失败', error)
  }
  
  // 加载工单详情
  await fetchTicketDetail()
})
</script>

<style scoped>
.info-item {
  margin-bottom: 10px;
}

.info-label {
  display: inline-block;
  width: 100px;
  color: #666;
  margin-right: 10px;
}

.description {
  margin-top: 8px;
  white-space: pre-wrap;
  line-height: 1.5;
}
</style> 