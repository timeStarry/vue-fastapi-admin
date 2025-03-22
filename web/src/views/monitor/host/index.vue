<script setup>
import { h, onMounted, ref, computed } from 'vue'
import { NButton, NForm, NFormItem, NInput, NInputNumber, NSelect, NTag, NUpload, NPopconfirm } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import { useCRUD } from '@/composables'
import api from '@/api'

defineOptions({ name: '主机监控' })

const $table = ref(null)
const queryItems = ref({})
const groupOptions = ref([])

// 获取主机分组选项
async function getGroupOptions() {
  const { data } = await api.getHostGroups()
  groupOptions.value = data.map(item => ({
    label: item.name,
    value: item.id,
    isDefault: item.is_default
  }))
  
  // 设置默认分组
  const defaultGroup = groupOptions.value.find(item => item.isDefault)
  if (defaultGroup) {
    modalForm.value.group_id = defaultGroup.value
  }
}

const authTypeOptions = [
  { label: '密码认证', value: 'password' },
  { label: '密钥认证', value: 'key' }
]

const crud = useCRUD({
  name: '主机',
  initForm: {
    port: 22,
    auth_type: 'password',
    group_id: null  // 将在getGroupOptions后设置默认值
  },
  doCreate: api.createMonitorHost,
  doDelete: api.deleteMonitorHost,
  doUpdate: api.updateMonitorHost,
  refresh: () => $table.value?.handleSearch(),
})

// 解构 CRUD 相关变量
const {
  modalVisible,
  modalTitle,
  modalLoading,
  handleDelete,
  handleEdit,
  modalForm,
  modalFormRef,
} = crud

// 重写handleAdd
const handleAdd = async () => {
  modalTitle.value = '新增主机'
  modalVisible.value = true
  modalForm.value = {
    port: 22,
    auth_type: 'password',
    group_id: groupOptions.value.find(item => item.isDefault)?.value
  }
}

const rules = {
  name: {
    required: true,
    message: '请输入主机名称',
    trigger: 'blur'
  },
  group_id: {
    required: true,
    type: 'number',
    message: '请选择分组',
    trigger: ['blur', 'change']
  },
  ip: {
    required: true,
    message: '请输入IP地址',
    trigger: 'blur'
  },
  port: {
    required: true,
    type: 'number',
    min: 1,
    max: 65535,
    message: '请输入有效的SSH端口(1-65535)',
    trigger: ['blur', 'change']
  },
  username: {
    required: true,
    message: '请输入用户名',
    trigger: 'blur'
  },
  auth_type: {
    required: true,
    message: '请选择认证方式',
    trigger: ['blur', 'change']
  }
}

// 动态验证规则
const dynamicRules = computed(() => {
  if (modalForm.value.auth_type === 'password') {
    return {
      password: {
        required: true,
        message: '请输入密码',
        trigger: 'blur'
      }
    }
  } else {
    return {
      private_key: {
        required: true,
        message: '请输入私钥内容',
        trigger: 'blur'
      }
    }
  }
})

// 合并基础规则和动态规则
const formRules = computed(() => ({
  ...rules,
  ...dynamicRules.value
}))

// 检查表单是否可以测试连接
const canTestConnection = computed(() => {
  const { ip, port, username, auth_type, password, private_key } = modalForm.value
  return ip && port && username && auth_type && 
    ((auth_type === 'password' && password) || 
     (auth_type === 'key' && private_key))
})

// 修改测试连接函数
async function handleTestConnection() {
  if (!canTestConnection.value) {
    $message.warning('请填写必要的连接信息')
    return
  }
  modalLoading.value = true
  try {
    const { code, msg } = await api.testHostConnection(modalForm.value)
    if (code === 200) {
      $message.success('连接成功')
    } else {
      $message.error(msg || '连接失败')
    }
  } finally {
    modalLoading.value = false
  }
}

const columns = [
  { title: '主机名称', key: 'name', width: 120, align: 'center' },
  { title: '分组', key: 'group_name', width: 120, align: 'center' },
  { title: 'IP地址', key: 'ip', width: 120, align: 'center' },
  { title: 'SSH端口', key: 'port', width: 80, align: 'center' },
  { title: '用户名', key: 'username', width: 100, align: 'center' },
  {
    title: '状态',
    key: 'status',
    width: 100,
    align: 'center',
    render(row) {
      const statusMap = {
        useful: { type: 'success', text: 'USEFUL' },
        up: { type: 'info', text: 'UP' },
        down: { type: 'error', text: 'DOWN' },
        unknown: { type: 'warning', text: 'UNKNOWN' }
      }
      const status = statusMap[row.status] || statusMap.unknown
      return h(NTag, {
        type: status.type,
        round: true,
      }, { default: () => status.text })
    }
  },
  { title: '备注', key: 'remark', width: 160, align: 'center' },
  {
    title: '操作',
    key: 'actions',
    width: 200,  // 增加宽度以容纳新按钮
    align: 'center',
    render(row) {
      return [
        h(
          NButton,
          {
            size: 'small',
            type: 'info',
            onClick: () => handleRefreshStatus(row),
            style: 'margin-right: 10px',
          },
          { default: () => '刷新' }
        ),
        h(
          NButton,
          {
            size: 'small',
            type: 'primary',
            onClick: () => handleEdit(row),
            style: 'margin-right: 10px',
          },
          { default: () => '编辑' }
        ),
        h(
          NPopconfirm,
          {
            onPositiveClick: () => handleDelete(row),
          },
          {
            trigger: () =>
              h(
                NButton,
                {
                  size: 'small',
                  type: 'error',
                },
                { default: () => '删除' }
              ),
            default: () => '确认删除？'
          }
        )
      ]
    }
  }
]

// 表单验证和保存
const handleSave = async () => {
  // 表单验证
  try {
    await modalFormRef.value?.validate()
  } catch (err) {
    return
  }

  // 验证认证方式相关字段
  const { auth_type, password, private_key } = modalForm.value
  if (auth_type === 'password' && !password) {
    window.$message.warning('请输入密码')
    return
  }
  if (auth_type === 'key' && !private_key) {
    window.$message.warning('请输入私钥内容')
    return
  }

  modalLoading.value = true
  try {
    if (modalForm.value.id) {
      await api.updateMonitorHost(modalForm.value.id, modalForm.value)
      window.$message.success('更新成功')
    } else {
      await api.createMonitorHost(modalForm.value)
      window.$message.success('创建成功')
    }
    modalVisible.value = false
    $table.value?.handleSearch()
  } catch (err) {
    window.$message.error(err.message || '操作失败')
  } finally {
    modalLoading.value = false
  }
}

// 添加刷新状态处理函数
async function handleRefreshStatus(row) {
  try {
    const { code, msg } = await api.testHostConnection(row)
    if (code === 200) {
      $message.success('连接成功')
      // 只获取当前行的最新数据
      const { data } = await api.getMonitorHostList({
        page: 1,
        page_size: 1,
        id: row.id
      })
      // 更新当前行数据
      Object.assign(row, data.items[0])
    } else {
      $message.error(msg || '连接失败')
      // 连接失败时也需要更新状态
      const { data } = await api.getMonitorHostList({
        page: 1,
        page_size: 1,
        id: row.id
      })
      Object.assign(row, data.items[0])
    }
  } catch (error) {
    $message.error('操作失败')
  }
}

onMounted(() => {
  getGroupOptions()
  $table.value?.handleSearch()
})
</script>

<template>
  <CommonPage show-footer title="主机监控">
    <template #action>
      <NButton type="primary" @click="handleAdd">
        <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />添加主机
      </NButton>
    </template>

    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getMonitorHostList"
    >
      <template #queryBar>
        <QueryBarItem label="分组" :label-width="70">
          <NSelect
            v-model:value="queryItems.group_id"
            style="width: 180px"
            :options="groupOptions"
            clearable
            placeholder="请选择分组"
          />
        </QueryBarItem>
        <QueryBarItem label="主机名称" :label-width="70">
          <NInput
            v-model:value="queryItems.name"
            clearable
            placeholder="请输入主机名称"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="IP地址" :label-width="70">
          <NInput
            v-model:value="queryItems.ip"
            clearable
            placeholder="请输入IP地址"
            @keypress.enter="$table?.handleSearch()"
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
      <NForm
        ref="modalFormRef"
        :model="modalForm"
        :rules="formRules"
        label-placement="left"
        :label-width="100"
      >
        <NFormItem label="主机名称" path="name">
          <NInput v-model:value="modalForm.name" placeholder="请输入主机名称" />
        </NFormItem>
        <NFormItem label="分组" path="group_id">
          <NSelect
            v-model:value="modalForm.group_id"
            :options="groupOptions"
            placeholder="请选择分组"
          />
        </NFormItem>
        <NFormItem label="IP地址" path="ip">
          <NInput v-model:value="modalForm.ip" placeholder="请输入IP地址" />
        </NFormItem>
        <NFormItem label="SSH端口" path="port">
          <NInputNumber
            v-model:value="modalForm.port"
            :min="1"
            :max="65535"
            placeholder="请输入SSH端口"
          />
        </NFormItem>
        <NFormItem label="用户名" path="username">
          <NInput v-model:value="modalForm.username" placeholder="请输入用户名" />
        </NFormItem>
        <NFormItem label="认证方式" path="auth_type">
          <NSelect
            v-model:value="modalForm.auth_type"
            :options="authTypeOptions"
            placeholder="请选择认证方式"
          />
        </NFormItem>
        <NFormItem v-if="modalForm.auth_type === 'password'" label="密码" path="password">
          <NInput
            v-model:value="modalForm.password"
            type="password"
            placeholder="请输入密码"
            show-password-on="click"
          />
        </NFormItem>
        <NFormItem v-else label="私钥" path="private_key">
          <NInput
            v-model:value="modalForm.private_key"
            type="textarea"
            placeholder="请输入私钥内容"
            :rows="4"
          />
        </NFormItem>
        <NFormItem label="备注" path="remark">
          <NInput v-model:value="modalForm.remark" type="textarea" placeholder="请输入备注" />
        </NFormItem>
        <div class="flex justify-center mt-4">
          <NButton 
            type="primary" 
            :disabled="!canTestConnection"
            @click="handleTestConnection"
          >
            测试连接
          </NButton>
        </div>
      </NForm>
    </CrudModal>
  </CommonPage>
</template> 