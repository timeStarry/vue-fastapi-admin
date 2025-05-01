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
      @save="handleSave"
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
            <n-form-item label="工单标题" path="title">
              <n-input v-model:value="modalForm.title" placeholder="请输入工单标题" />
            </n-form-item>
          </n-grid-item>
          <n-grid-item :span="12">
            <n-form-item label="工单类型" path="type">
              <n-select
                v-model:value="modalForm.type"
                clearable
                :options="typeOptions"
                placeholder="请选择工单类型"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item :span="12">
            <n-form-item label="优先级" path="priority">
              <n-select
                v-model:value="modalForm.priority"
                clearable
                :options="priorityOptions"
                placeholder="请选择优先级"
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
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item :span="24">
            <n-form-item label="工单描述" path="description">
              <n-input
                v-model:value="modalForm.description"
                type="textarea"
                :autosize="{
                  minRows: 3,
                  maxRows: 6,
                }"
                placeholder="请输入工单详细描述"
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
  </CommonPage>
</template>

<script setup>
import { h, onMounted, ref, resolveDirective, withDirectives } from 'vue'
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

defineOptions({ name: '工单列表' })

const $table = ref(null)
const queryItems = ref({})
const vPermission = resolveDirective('permission')
const token = getToken()
const uploadUrl = `${import.meta.env.VITE_API_BASE_URL}/api/v1/ticket/upload`

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
  doCreate: (data) => {
    // 调用实际的API创建工单
    return api.createTicket(data)
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
            [[vPermission, 'post/api/v1/ticket/process']]
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
            [[vPermission, 'delete/api/v1/ticket/delete']]
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
</script> 