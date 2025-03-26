<script setup>
import { h, onMounted, ref, resolveDirective } from 'vue'
import {
  NButton,
  NInput,
  NSelect,
  NDatePicker,
  NSpace,
  NTag,
  NPopconfirm,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import TicketForm from '../components/TicketForm.vue'

import { formatDate } from '@/utils'
import { useCRUD } from '@/composables'
import api from '@/api'

defineOptions({ name: '工单管理' })

const $table = ref(null)
const queryItems = ref({})
const vPermission = resolveDirective('permission')

// 工单状态选项
const statusOptions = [
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '已完成', value: 'completed' },
  { label: '已关闭', value: 'closed' }
]

// 优先级选项  
const priorityOptions = [
  { label: '低', value: 'low' },
  { label: '中', value: 'medium' }, 
  { label: '高', value: 'high' }
]

// 工单类型选项
const typeOptions = [
  { label: '故障报修', value: 'repair' },
  { label: '需求建议', value: 'suggestion' },
  { label: '咨询问题', value: 'question' }
]

const columns = [
  { title: '工单编号', key: 'id', width: 100 },
  { title: '工单标题', key: 'title', width: 200 },
  { 
    title: '工单类型', 
    key: 'type', 
    width: 120,
    render(row) {
      const typeMap = {
        repair: '故障报修',
        suggestion: '需求建议',
        question: '咨询问题'
      }
      return typeMap[row.type] || row.type
    }
  },
  { 
    title: '优先级', 
    key: 'priority', 
    width: 100,
    render(row) {
      const priorityMap = {
        low: { type: 'info', text: '低' },
        medium: { type: 'warning', text: '中' },
        high: { type: 'error', text: '高' }
      }
      const priority = priorityMap[row.priority]
      return h(NTag, { type: priority.type }, { default: () => priority.text })
    }
  },
  { 
    title: '状态',
    key: 'status',
    width: 120,
    render(row) {
      const statusMap = {
        pending: { type: 'warning', text: '待处理' },
        processing: { type: 'info', text: '处理中' },
        completed: { type: 'success', text: '已完成' },
        closed: { type: 'error', text: '已关闭' }
      }
      const status = statusMap[row.status]
      return h(NTag, { type: status.type }, { default: () => status.text })
    }
  },
  { title: '创建人', key: 'creator_name', width: 120 },
  { title: '受理人', key: 'assignee_name', width: 120 },
  { 
    title: '创建时间', 
    key: 'created_at', 
    width: 180,
    render(row) {
      return formatDate(row.created_at)
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    fixed: 'right',
    render(row) {
      return h(NSpace, {}, {
        default: () => [
          h(
            NButton,
            {
              size: 'small',
              onClick: () => handleView(row),
            },
            { default: () => '查看' }
          ),
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              onClick: () => handleEdit(row),
              disabled: row.status === 'closed'
            },
            { default: () => '处理' }
          ),
          h(
            NPopconfirm,
            {
              onPositiveClick: () => handleDelete(row),
            },
            {
              default: () => '确认关闭该工单？',
              trigger: () =>
                h(
                  NButton,
                  {
                    size: 'small',
                    type: 'error',
                    disabled: row.status === 'closed'
                  },
                  { default: () => '关闭' }
                ),
            }
          ),
        ],
      })
    },
  },
]

const ticketFormRef = ref(null)

const {
  modalVisible,
  modalTitle,
  modalLoading,
  handleSave,
  modalForm,
  modalFormRef,
  handleEdit,
  handleDelete,
  handleAdd,
  handleView,
} = useCRUD({
  name: '工单',
  initForm: { 
    title: '',
    content: {
      type: 'text',
      content: ''
    },
    type: '',
    priority: 'medium',
    dept_id: null
  },
  doCreate: api.createTicket,
  doUpdate: api.updateTicket,
  doDelete: api.closeTicket,
  refresh: () => $table.value?.handleSearch(),
})

onMounted(() => {
  $table.value?.handleSearch()
})
</script>

<template>
  <CommonPage show-footer title="工单管理">
    <template #action>
      <NButton type="primary" @click="handleAdd">
        <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />新建工单
      </NButton>
    </template>

    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getTicketList"
    >
      <template #queryBar>
        <QueryBarItem label="工单标题" :label-width="70">
          <NInput
            v-model:value="queryItems.title"
            clearable
            type="text"
            placeholder="请输入工单标题"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="工单状态" :label-width="70">
          <NSelect
            v-model:value="queryItems.status"
            :options="statusOptions"
            clearable
            placeholder="请选择状态"
          />
        </QueryBarItem>
        <QueryBarItem label="工单类型" :label-width="70">
          <NSelect
            v-model:value="queryItems.type"
            :options="typeOptions"
            clearable
            placeholder="请选择类型"
          />
        </QueryBarItem>
        <QueryBarItem label="创建时间" :label-width="70">
          <NDatePicker
            v-model:value="queryItems.created_at"
            type="daterange"
            clearable
          />
        </QueryBarItem>
      </template>
    </CrudTable>

    <CrudModal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      @save="handleSave"
    >
      <TicketForm
        ref="ticketFormRef"
        :form-ref="modalFormRef"
        :form-value="modalForm"
      />
    </CrudModal>
  </CommonPage>
</template> 