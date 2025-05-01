<template>
  <div class="h-full">
    <n-card class="h-full">
      <n-space vertical>
        <n-space>
          <n-input v-model:value="searchParams.service_name" placeholder="服务名称" clearable />
          <n-input v-model:value="searchParams.url" placeholder="服务URL" clearable />
          <n-select
            v-model:value="searchParams.status"
            :options="statusOptions"
            placeholder="状态"
            clearable
            style="width: 150px"
          />
          <n-button type="primary" @click="loadData">搜索</n-button>
          <n-button @click="resetSearch">重置</n-button>
          <n-button type="success" @click="showAddModal = true">添加服务</n-button>
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

    <!-- 添加服务弹窗 -->
    <n-modal v-model:show="showAddModal" preset="card" title="添加服务" style="width: 600px">
      <n-form
        ref="formRef"
        :model="formModel"
        :rules="rules"
        label-placement="left"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <n-form-item label="服务名称" path="service_name">
          <n-input v-model:value="formModel.service_name" placeholder="请输入服务名称" />
        </n-form-item>
        <n-form-item label="服务URL" path="url">
          <n-input v-model:value="formModel.url" placeholder="请输入服务URL" />
        </n-form-item>
        <n-form-item label="服务类型" path="service_type">
          <n-select
            v-model:value="formModel.service_type"
            :options="serviceTypeOptions"
            placeholder="请选择服务类型"
          />
        </n-form-item>
        <n-form-item label="检测方法" path="check_method">
          <n-select
            v-model:value="formModel.check_method"
            :options="checkMethodOptions"
            placeholder="请选择检测方法"
          />
        </n-form-item>
        <n-form-item label="正常状态码" path="expected_status">
          <n-input v-model:value="formModel.expected_status" placeholder="预期状态码，如：200,201,204" />
        </n-form-item>
        <n-form-item label="监控间隔(秒)" path="check_interval">
          <n-input-number
            v-model:value="formModel.check_interval"
            :min="10"
            :max="3600"
            :step="1"
            precision="0"
            placeholder="请输入监控间隔"
          />
        </n-form-item>
        <n-form-item label="超时时间(秒)" path="timeout">
          <n-input-number
            v-model:value="formModel.timeout"
            :min="1"
            :max="60"
            :step="1"
            precision="0"
            placeholder="请输入超时时间"
          />
        </n-form-item>
        <n-form-item label="关联主机" path="host_id">
          <n-select
            v-model:value="formModel.host_id"
            :options="hostOptions"
            placeholder="请选择关联的主机（可选）"
            clearable
          />
        </n-form-item>
        <n-form-item label="备注" path="remark">
          <n-input v-model:value="formModel.remark" type="textarea" placeholder="请输入备注" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showAddModal = false">取消</n-button>
          <n-button type="primary" @click="handleAddService">确认</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 详情抽屉 -->
    <n-drawer v-model:show="showDetail" width="600" placement="right">
      <n-drawer-content title="服务详情">
        <n-descriptions bordered>
          <n-descriptions-item label="服务名称">{{ currentService.service_name }}</n-descriptions-item>
          <n-descriptions-item label="服务URL">{{ currentService.url }}</n-descriptions-item>
          <n-descriptions-item label="服务类型">{{ currentService.service_type }}</n-descriptions-item>
          <n-descriptions-item label="状态">
            <n-tag :type="getStatusType(currentService.status)">
              {{ getStatusText(currentService.status) }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="检测方法">{{ currentService.check_method }}</n-descriptions-item>
          <n-descriptions-item label="预期状态码">{{ currentService.expected_status }}</n-descriptions-item>
          <n-descriptions-item label="最后响应时间">{{ currentService.last_response_time }} ms</n-descriptions-item>
          <n-descriptions-item label="最后检测时间">{{ currentService.last_check_time }}</n-descriptions-item>
          <n-descriptions-item label="监控间隔">{{ currentService.check_interval }} 秒</n-descriptions-item>
          <n-descriptions-item label="超时时间">{{ currentService.timeout }} 秒</n-descriptions-item>
          <n-descriptions-item label="创建时间">{{ currentService.created_at }}</n-descriptions-item>
          <n-descriptions-item label="备注">{{ currentService.remark }}</n-descriptions-item>
        </n-descriptions>

        <n-divider />
        
        <n-h3>响应时间趋势</n-h3>
        <div ref="chartRef" style="width: 100%; height: 300px"></div>

        <template #footer>
          <n-space>
            <n-button @click="handleCheckService(currentService)">立即检测</n-button>
            <n-button type="info" @click="handleViewHistory(currentService)">历史记录</n-button>
            <n-button type="warning" @click="handleEdit(currentService)">编辑</n-button>
            <n-button type="error" @click="handleDelete(currentService)">删除</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, h, onMounted, nextTick, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { NTag, NButton, NSpace } from 'naive-ui'
import * as echarts from 'echarts'
import api from '@/api'

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
  service_name: '',
  url: '',
  status: null,
  service_type: null,
  host_id: null,
})

// 状态选项
const statusOptions = [
  { label: '正常', value: 'normal' },
  { label: '异常', value: 'error' },
  { label: '警告', value: 'warning' },
  { label: '未知', value: 'unknown' },
]

// 服务类型选项
const serviceTypeOptions = [
  { label: 'Web服务', value: 'web' },
  { label: 'API服务', value: 'api' },
  { label: '数据库服务', value: 'database' },
  { label: '缓存服务', value: 'cache' },
  { label: '其他', value: 'other' },
]

// 检测方法选项
const checkMethodOptions = [
  { label: 'HTTP GET', value: 'http_get' },
  { label: 'HTTP POST', value: 'http_post' },
  { label: 'TCP连接', value: 'tcp' },
  { label: 'PING', value: 'ping' },
]

// 主机选项（从主机监控获取）
const hostOptions = ref([])

// 加载主机选项数据
const loadHostOptions = async () => {
  try {
    const result = await api.getHostList({ page: 1, page_size: 100 })
    // 后端返回的数据结构是 {code: 200, data: [...], total: X}
    const hosts = result.data || []
    
    if (hosts && hosts.length > 0) {
      hostOptions.value = hosts.map(host => ({
        label: `${host.host_name} (${host.ip})`,
        value: host.id
      }))
    } else {
      console.warn('未找到可用的主机列表')
      hostOptions.value = []
    }
  } catch (error) {
    console.error('获取主机列表失败:', error)
    hostOptions.value = []
  }
}

// 状态类型映射
const getStatusType = (status) => {
  const map = {
    normal: 'success',
    warning: 'warning',
    error: 'error',
    unknown: 'info',
  }
  return map[status] || 'info'
}

// 状态文本映射
const getStatusText = (status) => {
  const map = {
    normal: '正常',
    warning: '警告',
    error: '异常',
    unknown: '未知',
  }
  return map[status] || '未知'
}

// 服务类型文本映射
const getServiceTypeText = (type) => {
  const option = serviceTypeOptions.find(item => item.value === type)
  return option ? option.label : type
}

// 检测方法文本映射
const getCheckMethodText = (method) => {
  const option = checkMethodOptions.find(item => item.value === method)
  return option ? option.label : method
}

// 表格列定义
const columns = [
  { title: '服务名称', key: 'service_name' },
  { title: '服务URL', key: 'url', ellipsis: true },
  { 
    title: '服务类型', 
    key: 'service_type',
    render: (row) => getServiceTypeText(row.service_type)
  },
  {
    title: '状态',
    key: 'status',
    render(row) {
      return h(
        NTag,
        {
          type: getStatusType(row.status),
        },
        { default: () => getStatusText(row.status) }
      )
    },
  },
  { title: '响应时间', key: 'last_response_time', render: (row) => row.last_response_time ? `${row.last_response_time} ms` : '-' },
  { title: '最后检测', key: 'last_check_time' },
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
              onClick: () => handleCheckService(row),
            },
            { default: () => '检测' }
          ),
        ],
      })
    },
  },
]

// 图表实例
let chart = null
const chartRef = ref(null)

// 添加服务表单
const showAddModal = ref(false)
const formRef = ref(null)
const formModel = reactive({
  service_name: '',
  url: '',
  service_type: 'web',
  check_method: 'http_get',
  expected_status: '200',
  check_interval: 60,
  timeout: 5,
  host_id: null,
  remark: '',
})

// 监听弹窗显示状态
watch(showAddModal, (show) => {
  if (show) {
    // 弹窗显示时，确保表单初始化正确
    if (!formModel.id) {
      // 如果不是编辑模式，重置表单为默认值
      formModel.service_name = ''
      formModel.url = ''
      formModel.service_type = 'web'
      formModel.check_method = 'http_get'
      formModel.expected_status = '200'
      formModel.check_interval = 60
      formModel.timeout = 5
      formModel.host_id = null
      formModel.remark = ''
    }
    
    // 加载主机选项数据（如果还未加载）
    if (hostOptions.value.length === 0) {
      loadHostOptions()
    }
    
    // 下一个tick重置表单验证状态
    nextTick(() => {
      formRef.value?.restoreValidation()
    })
  }
})

// 表单验证规则
const rules = {
  service_name: {
    required: true,
    message: '请输入服务名称',
    trigger: 'blur',
  },
  url: {
    required: true,
    message: '请输入服务URL',
    trigger: 'blur',
  },
  service_type: {
    required: true,
    message: '请选择服务类型',
    trigger: 'change',
  },
  check_method: {
    required: true,
    message: '请选择检测方法',
    trigger: 'change',
  },
  check_interval: {
    required: true,
    message: '请输入监控间隔',
    trigger: 'change',
    type: 'number',
    validator(rule, value) {
      if (value === null || value === undefined || value === '') {
        return new Error('请输入监控间隔')
      }
      if (typeof value !== 'number') {
        return new Error('监控间隔必须是数字')
      }
      if (value < 10 || value > 3600) {
        return new Error('监控间隔必须在10-3600秒之间')
      }
      return true
    }
  },
  timeout: {
    required: true,
    message: '请输入超时时间',
    trigger: 'change',
    type: 'number',
    validator(rule, value) {
      if (value === null || value === undefined || value === '') {
        return new Error('请输入超时时间')
      }
      if (typeof value !== 'number') {
        return new Error('超时时间必须是数字')
      }
      if (value < 1 || value > 60) {
        return new Error('超时时间必须在1-60秒之间')
      }
      return true
    }
  },
}

// 详情抽屉
const showDetail = ref(false)
const currentService = ref({})
const serviceHistory = ref([])

// 加载服务数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchParams
    }
    
    const result = await api.getServiceList(params)
    tableData.value = result.data || []
    pagination.itemCount = result.total || 0
  } catch (error) {
    message.error('加载数据失败: ' + (error.message || '未知错误'))
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 重置搜索
const resetSearch = () => {
  Object.keys(searchParams).forEach(key => {
    searchParams[key] = null
  })
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
const handleDetail = async (row) => {
  try {
    loading.value = true
    const serviceData = await api.getServiceById({ service_id: row.id })
    currentService.value = serviceData.data || {}
    showDetail.value = true
    
    // 加载服务响应时间历史数据用于图表展示
    await loadServiceHistory(row.id)
  } catch (error) {
    message.error('获取服务详情失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 加载服务响应时间历史数据
const loadServiceHistory = async (serviceId) => {
  try {
    const response = await api.getServiceHistory(serviceId, { days: 7 })
    const result = response.data || {}
    serviceHistory.value = result.items || []
    
    // 在下一个渲染周期初始化图表
    nextTick(() => {
      initChart()
    })
  } catch (error) {
    message.error('获取服务历史数据失败: ' + (error.message || '未知错误'))
  }
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  
  if (chart) {
    chart.dispose()
  }
  
  chart = echarts.init(chartRef.value)
  
  // 准备图表数据
  const dateList = serviceHistory.value.map(item => item.created_at)
  const responseTimeList = serviceHistory.value.map(item => item.response_time)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>{a}: {c} ms'
    },
    xAxis: {
      type: 'category',
      data: dateList,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '响应时间(ms)'
    },
    series: [
      {
        name: '响应时间',
        type: 'line',
        data: responseTimeList,
        markLine: {
          data: [
            {
              type: 'average',
              name: '平均值'
            }
          ]
        }
      }
    ]
  }
  
  chart.setOption(option)
  
  // 窗口大小变化时自动调整图表
  window.addEventListener('resize', () => {
    chart && chart.resize()
  })
}

// 添加服务
const handleAddService = () => {
  // 确保表单验证状态是最新的
  nextTick(() => {
    formRef.value?.validate(async (errors) => {
      if (errors) {
        console.error('表单验证失败:', errors)
        return
      }

      try {
        loading.value = true
        
        let result;
        const isEdit = !!formModel.id
        
        // 确保数值字段是数字类型
        const submitData = { ...formModel }
        submitData.check_interval = Number(submitData.check_interval)
        submitData.timeout = Number(submitData.timeout)
        
        if (isEdit) {
          // 编辑模式
          result = await api.updateService(submitData.id, submitData)
          message.success('更新服务成功')
        } else {
          // 新增模式
          result = await api.createService(submitData)
          message.success('添加服务成功')
        }
        
        showAddModal.value = false
        
        // 重置表单
        delete formModel.id // 删除id字段
        formModel.service_name = ''
        formModel.url = ''
        formModel.service_type = 'web'
        formModel.check_method = 'http_get'
        formModel.expected_status = '200'
        formModel.check_interval = 60
        formModel.timeout = 5
        formModel.host_id = null
        formModel.remark = ''
        
        // 确保表单验证状态重置
        nextTick(() => {
          formRef.value?.restoreValidation()
        })
        
        // 重新加载数据
        loadData()
      } catch (error) {
        console.error('服务操作失败:', error)
        message.error(`${formModel.id ? '更新' : '添加'}服务失败: ${error.message || '未知错误'}`)
      } finally {
        loading.value = false
      }
    })
  })
}

// 检测服务
const handleCheckService = async (service) => {
  try {
    message.info(`正在检测服务 ${service.service_name}...`)
    loading.value = true
    const response = await api.checkService(service.id)
    const result = response.data || {}
    
    if (result.success) {
      const data = result.data || {}
      if (data.status === 'normal') {
        message.success(`服务 ${service.service_name} 检测成功，响应时间: ${data.response_time}ms`)
      } else {
        message.error(`服务 ${service.service_name} 检测失败: ${data.error || '服务异常'}`)
      }
    } else {
      message.error(`服务检测失败: ${result.message}`)
    }
    
    // 重新加载数据以更新状态
    loadData()
  } catch (error) {
    message.error('服务检测失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 查看历史记录
const handleViewHistory = async (service) => {
  try {
    message.info(`正在获取服务 ${service.service_name} 的历史记录...`)
    loading.value = true
    await loadServiceHistory(service.id)
    message.success('历史数据加载成功')
  } catch (error) {
    message.error('获取历史记录失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 编辑服务
const handleEdit = (service) => {
  // 填充表单数据
  formModel.id = service.id
  formModel.service_name = service.service_name
  formModel.url = service.url
  formModel.service_type = service.service_type
  formModel.check_method = service.check_method
  formModel.expected_status = service.expected_status
  formModel.check_interval = service.check_interval
  formModel.timeout = service.timeout
  formModel.host_id = service.host_id
  formModel.remark = service.remark
  
  showAddModal.value = true
}

// 删除服务
const handleDelete = async (service) => {
  if (confirm(`确定要删除服务 ${service.service_name} 吗？`)) {
    try {
      loading.value = true
      await api.deleteService(service.id)
      message.success(`已删除服务 ${service.service_name}`)
      showDetail.value = false
      loadData()
    } catch (error) {
      message.error('删除服务失败: ' + (error.message || '未知错误'))
    } finally {
      loading.value = false
    }
  }
}

onMounted(() => {
  loadData()
  loadHostOptions()
})
</script>

<style scoped>
.h-full {
  height: 100%;
}
</style> 