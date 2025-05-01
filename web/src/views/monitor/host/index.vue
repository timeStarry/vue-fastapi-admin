<template>
  <div class="h-full">
    <n-card class="h-full">
      <n-space vertical>
        <n-space>
          <n-input v-model:value="searchParams.host_name" placeholder="主机名" clearable />
          <n-input v-model:value="searchParams.ip" placeholder="IP地址" clearable />
          <n-select
            v-model:value="searchParams.status"
            :options="statusOptions"
            placeholder="状态"
            clearable
            style="width: 150px"
          />
          <n-button type="primary" @click="loadData">搜索</n-button>
          <n-button @click="resetSearch">重置</n-button>
          <n-button type="success" @click="showAddModal = true">添加主机</n-button>
        </n-space>

        <n-data-table
          remote
          :columns="columns"
          :data="tableData"
          :loading="loading"
          :pagination="pagination"
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
        />
      </n-space>
    </n-card>

    <!-- 添加主机弹窗 -->
    <n-modal v-model:show="showAddModal" preset="card" title="添加主机" style="width: 600px">
      <n-form
        ref="formRef"
        :model="formModel"
        :rules="rules"
        label-placement="left"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <n-form-item label="主机名" path="host_name">
          <n-input v-model:value="formModel.host_name" placeholder="请输入主机名" />
        </n-form-item>
        <n-form-item label="IP地址" path="ip">
          <n-input v-model:value="formModel.ip" placeholder="请输入IP地址" />
        </n-form-item>
        <n-form-item label="主机类型" path="host_type">
          <n-select
            v-model:value="formModel.host_type"
            :options="hostTypeOptions"
            placeholder="请选择主机类型"
          />
        </n-form-item>
        <n-form-item label="监控间隔(秒)" path="ping_interval">
          <n-input-number
            v-model:value="formModel.ping_interval"
            :min="10"
            :max="3600"
            placeholder="请输入监控间隔"
          />
        </n-form-item>
        <n-form-item label="启用MRTG" path="enable_mrtg">
          <n-switch v-model:value="formModel.enable_mrtg" />
        </n-form-item>
        <n-form-item label="备注" path="remark">
          <n-input v-model:value="formModel.remark" type="textarea" placeholder="请输入备注" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showAddModal = false">取消</n-button>
          <n-button type="primary" @click="handleAddHost">确认</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 详情抽屉 -->
    <n-drawer v-model:show="showDetail" width="600" placement="right">
      <n-drawer-content title="主机详情">
        <n-descriptions bordered>
          <n-descriptions-item label="主机名">{{ currentHost.host_name }}</n-descriptions-item>
          <n-descriptions-item label="IP地址">{{ currentHost.ip }}</n-descriptions-item>
          <n-descriptions-item label="主机类型">{{ currentHost.host_type }}</n-descriptions-item>
          <n-descriptions-item label="状态">
            <n-tag :type="currentHost.status === 'online' ? 'success' : 'error'">
              {{ currentHost.status === 'online' ? '在线' : '离线' }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="最后在线时间">{{ currentHost.last_online_time }}</n-descriptions-item>
          <n-descriptions-item label="监控间隔">{{ currentHost.ping_interval }} 秒</n-descriptions-item>
          <n-descriptions-item label="MRTG状态">
            <n-tag :type="currentHost.mrtg_status === 'normal' ? 'success' : 'warning'">
              {{ currentHost.mrtg_status === 'normal' ? '正常' : '异常' }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="创建时间">{{ currentHost.created_at }}</n-descriptions-item>
          <n-descriptions-item label="备注">{{ currentHost.remark }}</n-descriptions-item>
        </n-descriptions>

        <template #footer>
          <n-space>
            <n-button @click="handlePingTest(currentHost)">Ping测试</n-button>
            <n-button type="info" @click="handleViewMRTG(currentHost)">查看MRTG</n-button>
            <n-button type="warning" @click="handleEdit(currentHost)">编辑</n-button>
            <n-button type="error" @click="handleDelete(currentHost)">删除</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, h, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { NTag, NButton, NSpace } from 'naive-ui'

const message = useMessage()

// 表格数据
const tableData = ref([])
const loading = ref(false)
const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 30, 40],
  showSizePicker: true,
  prefix({ itemCount }) {
    return `共 ${itemCount} 条`
  },
})

// 搜索参数
const searchParams = reactive({
  host_name: '',
  ip: '',
  status: null,
})

// 状态选项
const statusOptions = [
  { label: '在线', value: 'online' },
  { label: '离线', value: 'offline' },
]

// 主机类型选项
const hostTypeOptions = [
  { label: '服务器', value: 'server' },
  { label: '路由器', value: 'router' },
  { label: '交换机', value: 'switch' },
  { label: '防火墙', value: 'firewall' },
  { label: '其他', value: 'other' },
]

// 表格列定义
const columns = [
  { title: '主机名', key: 'host_name' },
  { title: 'IP地址', key: 'ip' },
  {
    title: '状态',
    key: 'status',
    render(row) {
      return h(
        NTag,
        {
          type: row.status === 'online' ? 'success' : 'error',
        },
        { default: () => (row.status === 'online' ? '在线' : '离线') }
      )
    },
  },
  {
    title: 'MRTG状态',
    key: 'mrtg_status',
    render(row) {
      if (!row.enable_mrtg) return '未启用'
      return h(
        NTag,
        {
          type: row.mrtg_status === 'normal' ? 'success' : 'warning',
        },
        { default: () => (row.mrtg_status === 'normal' ? '正常' : '异常') }
      )
    },
  },
  { title: '主机类型', key: 'host_type' },
  { title: '最后在线时间', key: 'last_online_time' },
  {
    title: '操作',
    key: 'actions',
    render(row) {
      return h(NSpace, {}, {
        default: () => [
          h(
            NButton,
            {
              size: 'small',
              onClick: () => handleDetail(row),
            },
            { default: () => '详情' }
          ),
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              onClick: () => handlePingTest(row),
            },
            { default: () => 'Ping' }
          ),
        ],
      })
    },
  },
]

// 添加主机表单
const showAddModal = ref(false)
const formRef = ref(null)
const formModel = reactive({
  host_name: '',
  ip: '',
  host_type: 'server',
  ping_interval: 60,
  enable_mrtg: false,
  remark: '',
})

// 表单验证规则
const rules = {
  host_name: {
    required: true,
    message: '请输入主机名',
    trigger: 'blur',
  },
  ip: {
    required: true,
    message: '请输入IP地址',
    trigger: 'blur',
    validator(rule, value) {
      // 简单的IP地址验证
      const pattern = /^(\d{1,3}\.){3}\d{1,3}$/
      if (!pattern.test(value)) {
        return new Error('IP地址格式不正确')
      }
      return true
    },
  },
  host_type: {
    required: true,
    message: '请选择主机类型',
    trigger: 'change',
  },
  ping_interval: {
    required: true,
    message: '请输入监控间隔',
    trigger: 'change',
  },
}

// 详情抽屉
const showDetail = ref(false)
const currentHost = ref({})

// 加载主机数据
const loadData = async () => {
  loading.value = true
  try {
    // 这里应该调用实际的API接口获取数据
    // const { data } = await fetchHostList({ 
    //   ...searchParams,
    //   page: pagination.page,
    //   page_size: pagination.pageSize
    // })
    
    // 模拟数据
    await new Promise(resolve => setTimeout(resolve, 500))
    const mockData = Array.from({ length: 10 }).map((_, index) => ({
      id: index + 1,
      host_name: `主机-${index + 1}`,
      ip: `192.168.1.${index + 1}`,
      status: index % 3 === 0 ? 'offline' : 'online',
      host_type: index % 2 === 0 ? 'server' : 'router',
      enable_mrtg: index % 2 === 0,
      mrtg_status: index % 4 === 0 ? 'abnormal' : 'normal',
      last_online_time: '2023-05-01 10:00:00',
      ping_interval: 60,
      created_at: '2023-01-01 12:00:00',
      remark: '这是备注信息',
    }))
    
    tableData.value = mockData
    pagination.itemCount = 100 // 总数应该从API获取
  } catch (error) {
    message.error('加载数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 重置搜索
const resetSearch = () => {
  Object.keys(searchParams).forEach(key => {
    searchParams[key] = ''
  })
  searchParams.status = null
  loadData()
}

// 分页处理
const handlePageChange = (page) => {
  pagination.page = page
  loadData()
}

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  loadData()
}

// 详情处理
const handleDetail = (row) => {
  currentHost.value = row
  showDetail.value = true
}

// 添加主机
const handleAddHost = () => {
  formRef.value?.validate(async (errors) => {
    if (errors) return

    try {
      // 这里应该调用实际的API接口添加主机
      // await addHost(formModel)
      message.success('添加主机成功')
      showAddModal.value = false
      
      // 重置表单
      Object.keys(formModel).forEach(key => {
        if (key === 'host_type') formModel[key] = 'server'
        else if (key === 'ping_interval') formModel[key] = 60
        else if (key === 'enable_mrtg') formModel[key] = false
        else formModel[key] = ''
      })
      
      // 重新加载数据
      loadData()
    } catch (error) {
      message.error('添加主机失败')
      console.error(error)
    }
  })
}

// Ping测试
const handlePingTest = (host) => {
  message.info(`正在测试主机 ${host.host_name} (${host.ip})...`)
  // 这里应该调用实际的API接口进行Ping测试
  setTimeout(() => {
    message.success(`主机 ${host.host_name} (${host.ip}) Ping测试成功，延迟: 5ms`)
  }, 1000)
}

// 查看MRTG
const handleViewMRTG = (host) => {
  if (!host.enable_mrtg) {
    message.warning('该主机未启用MRTG监控')
    return
  }
  
  // 这里应该跳转到MRTG图表页面或显示MRTG图表弹窗
  message.info(`查看主机 ${host.host_name} 的MRTG监控数据`)
}

// 编辑主机
const handleEdit = (host) => {
  message.info(`编辑主机 ${host.host_name}`)
  // 这里应该打开编辑弹窗
}

// 删除主机
const handleDelete = (host) => {
  if (confirm(`确定要删除主机 ${host.host_name} 吗？`)) {
    // 这里应该调用实际的API接口删除主机
    message.success(`已删除主机 ${host.host_name}`)
    showDetail.value = false
    loadData()
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.h-full {
  height: 100%;
}
</style> 