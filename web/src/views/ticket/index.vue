
<template>
  <CommonPage show-footer title="工单列表">
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
        <QueryBarItem label="标题" :label-width="40">
          <NInput
            v-model:value="queryItems.title"
            clearable
            type="text"
            placeholder="请输入工单标题"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="状态" :label-width="40">
          <NSelect
            v-model:value="queryItems.status"
            :options="statusOptions"
            clearable
            placeholder="请选择工单状态"
          />
        </QueryBarItem>
        <QueryBarItem label="优先级" :label-width="50">
          <NSelect
            v-model:value="queryItems.priority"
            :options="priorityOptions"
            clearable
            placeholder="请选择优先级"
          />
        </QueryBarItem>
        <QueryBarItem label="分类" :label-width="40">
          <NSelect
            v-model:value="queryItems.category_id"
            :options="categoryOptions"
            clearable
            placeholder="请选择工单分类"
          />
        </QueryBarItem>
      </template>
    </CrudTable>

    <!-- 新增/编辑 弹窗 -->
    <CrudModal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      @save="handleSave"
    >
      <NForm
        ref="modalFormRef"
        :model="modalForm"
        :rules="rules"
        label-placement="left"
        :label-width="100"
      >
        <NFormItem label="工单标题" path="title">
          <NInput v-model:value="modalForm.title" placeholder="请输入工单标题" />
        </NFormItem>
        <NFormItem label="工单分类" path="category_id">
          <NSelect
            v-model:value="modalForm.category_id"
            :options="categoryOptions"
            placeholder="请选择工单分类"
          />
        </NFormItem>
        <NFormItem label="优先级" path="priority">
          <NSelect
            v-model:value="modalForm.priority"
            :options="priorityOptions"
            placeholder="请选择优先级"
          />
        </NFormItem>
        <NFormItem label="处理人" path="assignee_id">
          <NSelect
            v-model:value="modalForm.assignee_id"
            :options="userOptions"
            placeholder="请选择处理人"
          />
        </NFormItem>
        <NFormItem label="工单内容" path="content">
          <NSelect v-model:value="modalForm.content.type" :options="contentTypeOptions" />
          <div v-if="modalForm.content.type === 'text'" class="mt-2">
            <NInput
              v-model:value="modalForm.content.data"
              type="textarea"
              placeholder="请输入工单内容"
            />
          </div>
          <div v-if="modalForm.content.type === 'rich_text'" class="mt-2">
            <Editor v-model:value="modalForm.content.data" />
          </div>
          <div v-if="modalForm.content.type === 'form'" class="mt-2">
            <DynamicForm v-model:value="modalForm.content.data" />
          </div>
        </NFormItem>
      </NForm>
    </CrudModal>
  </CommonPage>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import api from '@/api'
import { useUserStore } from '@/store'

const message = useMessage()
const userStore = useUserStore()

// 查询条件
const queryItems = ref({
  title: '',
  status: '',
  priority: '',
  category_id: null
})

// 表格列配置
const columns = [
  { title: '工单标题', key: 'title' },
  { 
    title: '状态',
    key: 'status',
    render: (row) => {
      const statusMap = {
        pending: '待处理',
        processing: '处理中',
        completed: '已完成',
        closed: '已关闭'
      }
      return statusMap[row.status]
    }
  },
  {
    title: '优先级',
    key: 'priority',
    render: (row) => {
      const priorityMap = {
        low: '低',
        medium: '中',
        high: '高',
        urgent: '紧急'
      }
      return priorityMap[row.priority]
    }
  },
  { title: '分类', key: 'category_name' },
  { title: '创建人', key: 'creator_name' },
  { title: '处理人', key: 'assignee_name' },
  { title: '创建时间', key: 'created_at' },
  {
    title: '操作',
    key: 'actions',
    render: (row) => {
      return h(
        NSpace,
        {},
        {
          default: () => [
            h(
              NButton,
              {
                size: 'small',
                onClick: () => handleEdit(row),
              },
              { default: () => '编辑' }
            ),
            h(
              NButton,
              {
                size: 'small',
                type: 'error',
                onClick: () => handleDelete(row),
              },
              { default: () => '删除' }
            ),
          ],
        }
      )
    },
  },
]

// 选项数据
const statusOptions = [
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '已完成', value: 'completed' },
  { label: '已关闭', value: 'closed' }
]

const priorityOptions = [
  { label: '低', value: 'low' },
  { label: '中', value: 'medium' },
  { label: '高', value: 'high' },
  { label: '紧急', value: 'urgent' }
]

const contentTypeOptions = [
  { label: '纯文本', value: 'text' },
  { label: '富文本', value: 'rich_text' },
  { label: '表单', value: 'form' }
]

// 弹窗表单
const modalVisible = ref(false)
const modalTitle = ref('')
const modalLoading = ref(false)
const modalForm = ref({
  title: '',
  category_id: null,
  priority: 'medium',
  assignee_id: null,
  content: {
    type: 'text',
    data: ''
  }
})

const rules = {
  title: { required: true, message: '请输入工单标题' },
  category_id: { required: true, message: '请选择工单分类' },
  priority: { required: true, message: '请选择优先级' },
  'content.data': { required: true, message: '请输入工单内容' }
}

// 处理新增
const handleAdd = () => {
  modalTitle.value = '新建工单'
  modalVisible.value = true
  modalForm.value = {
    title: '',
    category_id: null,
    priority: 'medium',
    assignee_id: null,
    content: {
      type: 'text',
      data: ''
    }
  }
}

// 处理编辑
const handleEdit = (row) => {
  modalTitle.value = '编辑工单'
  modalVisible.value = true
  modalForm.value = {
    ...row,
    content: JSON.parse(row.content)
  }
}

// 处理保存
const handleSave = async () => {
  modalLoading.value = true
  try {
    if (modalForm.value.id) {
      await api.updateTicket(modalForm.value)
      message.success('更新成功')
    } else {
      await api.createTicket(modalForm.value)
      message.success('创建成功')
    }
    modalVisible.value = false
    $table.value?.handleSearch()
  } catch (error) {
    message.error(error.message)
  } finally {
    modalLoading.value = false
  }
}

// 处理删除
const handleDelete = async (row) => {
  try {
    await api.deleteTicket({ id: row.id })
    message.success('删除成功')
    $table.value?.handleSearch()
  } catch (error) {
    message.error(error.message)
  }
}
</script>