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
            placeholder="请输入监控间隔"
          />
        </n-form-item>
        <n-form-item label="超时时间(秒)" path="timeout">
          <n-input-number
            v-model:value="formModel.timeout"
            :min="1"
            :max="60"
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
import { ref, reactive, h, onMounted, nextTick } from 'vue'
import { useMessage } from 'naive-ui'
import { NTag, NButton, NSpace } from 'naive-ui'
import * as echarts from 'echarts'

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
const hostOptions = [
  { label: '主机-1 (192.168.1.1)', value: 1 },
  { label: '主机-2 (192.168.1.2)', value: 2 },
  { label: '主机-3 (192.168.1.3)', value: 3 },
]

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

// 表格列定义
const columns = [
  { title: '服务名称', key: 'service_name' },
  { title: '服务URL', key: 'url', ellipsis: true },
  { title: '服务类型', key: 'service_type' },
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
  { title: '响应时间', key: 'last_response_time', render: (row) => `${row.last_response_time} ms` },
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
    validator(rule, value) {
      const urlPattern = /^(http|https):\/\/.+/
      if (!urlPattern.test(value) && formModel.check_method.startsWith('http')) {
        return new Error('HTTP(S)服务URL格式不正确')
      }
      return true
    },
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
  },
  timeout: {
    required: true,
    message: '请输入超时时间',
    trigger: 'change',
  },
}

// 详情抽屉
const showDetail = ref(false)
const currentService = ref({})
const chartRef = ref(null)
let chart = null

// 加载服务数据
const loadData = async () => {
  loading.value = true
  try {
    // 这里应该调用实际的API接口获取数据
    // const { data } = await fetchServiceList({ 
    //   ...searchParams,
    //   page: pagination.page,
    //   page_size: pagination.pageSize
    // })
    
    // 模拟数据
    await new Promise(resolve => setTimeout(resolve, 500))
    const mockData = Array.from({ length: 10 }).map((_, index) => ({
      id: index + 1,
      service_name: `服务-${index + 1}`,
      url: index % 2 === 0 ? `https://api.example.com/service-${index + 1}` : `http://web.example.com/service-${index + 1}`,
      service_type: index % 3 === 0 ? 'api' : 'web',
      status: index % 4 === 0 ? 'error' : (index % 3 === 0 ? 'warning' : 'normal'),
      check_method: index % 2 === 0 ? 'http_get' : 'http_post',
      expected_status: '200',
      last_response_time: Math.floor(Math.random() * 500) + 50,
      last_check_time: '2023-05-01 10:00:00',
      check_interval: 60,
      timeout: 5,
      host_id: index % 3 + 1,
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
  currentService.value = row
  showDetail.value = true
  
  // 初始化图表
  nextTick(() => {
    initChart()
  })
}

// 初始化趋势图表
const initChart = () => {
  if (!chartRef.value) return
  
  // 销毁旧图表
  if (chart) {
    chart.dispose()
  }
  
  // 创建新图表
  chart = echarts.init(chartRef.value)
  
  // 生成模拟数据
  const dates = []
  const data = []
  const now = new Date()
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(now - (6 - i) * 24 * 3600 * 1000)
    dates.push(`${date.getMonth() + 1}/${date.getDate()}`)
    
    // 模拟响应时间数据，正常在200ms左右波动，异常时会有波峰
    let value = Math.floor(Math.random() * 100) + 150
    if (i === 3) value = 450 // 模拟出现一次异常波峰
    data.push(value)
  }
  
  // 设置图表选项
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br>{a}: {c} ms',
    },
    xAxis: {
      type: 'category',
      data: dates,
    },
    yAxis: {
      type: 'value',
      name: '响应时间(ms)',
    },
    series: [
      {
        name: '响应时间',
        type: 'line',
        data: data,
        markLine: {
          data: [
            {
              name: '警告阈值',
              yAxis: 300,
              lineStyle: { color: '#f0a020' },
            },
            {
              name: '错误阈值',
              yAxis: 400,
              lineStyle: { color: '#d03050' },
            },
          ],
        },
      },
    ],
    color: ['#18a058'],
  }
  
  chart.setOption(option)
}

// 添加服务
const handleAddService = () => {
  formRef.value?.validate(async (errors) => {
    if (errors) return

    try {
      // 这里应该调用实际的API接口添加服务
      // await addService(formModel)
      message.success('添加服务成功')
      showAddModal.value = false
      
      // 重置表单
      Object.keys(formModel).forEach(key => {
        if (key === 'service_type') formModel[key] = 'web'
        else if (key === 'check_method') formModel[key] = 'http_get'
        else if (key === 'expected_status') formModel[key] = '200'
        else if (key === 'check_interval') formModel[key] = 60
        else if (key === 'timeout') formModel[key] = 5
        else if (key === 'host_id') formModel[key] = null
        else formModel[key] = ''
      })
      
      // 重新加载数据
      loadData()
    } catch (error) {
      message.error('添加服务失败')
      console.error(error)
    }
  })
}

// 检测服务
const handleCheckService = (service) => {
  message.info(`正在检测服务 ${service.service_name}...`)
  // 这里应该调用实际的API接口进行服务检测
  setTimeout(() => {
    message.success(`服务 ${service.service_name} 检测成功，响应时间: 215ms`)
  }, 1000)
}

// 查看历史记录
const handleViewHistory = (service) => {
  message.info(`查看服务 ${service.service_name} 的历史记录`)
  // 这里应该跳转到历史记录页面或显示历史记录弹窗
}

// 编辑服务
const handleEdit = (service) => {
  message.info(`编辑服务 ${service.service_name}`)
  // 这里应该打开编辑弹窗
}

// 删除服务
const handleDelete = (service) => {
  if (confirm(`确定要删除服务 ${service.service_name} 吗？`)) {
    // 这里应该调用实际的API接口删除服务
    message.success(`已删除服务 ${service.service_name}`)
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