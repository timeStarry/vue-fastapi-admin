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
            :step="1"
            precision="0"
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

    <!-- MRTG数据显示模态框 -->
    <n-modal v-model:show="showMRTGModal" preset="card" style="width: 800px" :title="`${currentHost.host_name} MRTG监控数据`">
      <div v-if="mrtgLoading" class="loading-container">
        <n-spin size="large" />
      </div>
      <div v-else>
        <n-tabs type="line">
          <n-tab-pane name="traffic" tab="流量监控">
            <div class="chart-container">
              <div ref="trafficChartRef" class="chart"></div>
            </div>
          </n-tab-pane>
          <n-tab-pane name="cpu" tab="CPU监控">
            <div class="chart-container">
              <div ref="cpuChartRef" class="chart"></div>
            </div>
          </n-tab-pane>
          <n-tab-pane name="memory" tab="内存监控">
            <div class="chart-container">
              <div ref="memoryChartRef" class="chart"></div>
            </div>
          </n-tab-pane>
        </n-tabs>
      </div>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, reactive, h, onMounted, watch, nextTick } from 'vue'
import { useMessage } from 'naive-ui'
import { NTag, NButton, NSpace } from 'naive-ui'
import api from '@/api'
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
  host_name: '',
  ip: '',
  status: null,
  host_type: null,
})

// 状态选项
const statusOptions = [
  { label: '在线', value: 'online' },
  { label: '离线', value: 'offline' },
  { label: '未知', value: 'unknown' },
]

// 主机类型选项
const hostTypeOptions = [
  { label: '服务器', value: 'server' },
  { label: '路由器', value: 'router' },
  { label: '交换机', value: 'switch' },
  { label: '防火墙', value: 'firewall' },
  { label: '其他', value: 'other' },
]

// 显示主机类型标签
const getHostTypeLabel = (value) => {
  const option = hostTypeOptions.find(item => item.value === value)
  return option ? option.label : value
}

// 表格列定义
const columns = [
  { title: '主机名', key: 'host_name' },
  { title: 'IP地址', key: 'ip' },
  {
    title: '状态',
    key: 'status',
    render(row) {
      const statusMap = {
        'online': { type: 'success', text: '在线' },
        'offline': { type: 'error', text: '离线' },
        'unknown': { type: 'warning', text: '未知' }
      }
      const status = statusMap[row.status] || statusMap.unknown
      return h(
        NTag,
        {
          type: status.type,
        },
        { default: () => status.text }
      )
    },
  },
  {
    title: 'MRTG状态',
    key: 'mrtg_status',
    render(row) {
      if (!row.enable_mrtg) return '未启用'
      const statusMap = {
        'normal': { type: 'success', text: '正常' },
        'abnormal': { type: 'warning', text: '异常' },
      }
      const status = statusMap[row.mrtg_status] || { type: 'default', text: '未知' }
      return h(
        NTag,
        {
          type: status.type,
        },
        { default: () => status.text }
      )
    },
  },
  { 
    title: '主机类型', 
    key: 'host_type',
    render(row) {
      return getHostTypeLabel(row.host_type)
    }
  },
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

// 监听弹窗显示状态
watch(showAddModal, (show) => {
  if (show) {
    // 弹窗显示时，确保表单初始化正确
    if (!formModel.id) {
      // 如果不是编辑模式，重置表单
      formModel.host_name = ''
      formModel.ip = ''
      formModel.host_type = 'server'
      formModel.ping_interval = 60
      formModel.enable_mrtg = false
      formModel.remark = ''
    }
    // 下一个tick重置表单验证状态
    nextTick(() => {
      formRef.value?.restoreValidation()
    })
  }
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
}

// 详情抽屉
const showDetail = ref(false)
const currentHost = ref({})

// MRTG相关
const showMRTGModal = ref(false)
const mrtgLoading = ref(false)
const mrtgData = ref([])
const trafficChartRef = ref(null)
const cpuChartRef = ref(null)
const memoryChartRef = ref(null)
let trafficChart = null
let cpuChart = null
let memoryChart = null

// 加载主机数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchParams
    }
    
    const result = await api.getHostList(params)
    if (!result) {
      message.error('返回数据格式错误')
      return
    }
    
    // 解析响应数据，data.data包含实际数据列表
    tableData.value = result.data || []
    pagination.itemCount = result.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
    // 改进错误消息展示
    if (error.code) {
      message.error(`加载数据失败: [${error.code}] ${error.message}`)
    } else if (error.message && error.message !== 'OK') {
      message.error(`加载数据失败: ${error.message}`)
    } else if (typeof error === 'string') {
      message.error(`加载数据失败: ${error}`)
    } else {
      message.error('加载数据失败，请检查网络连接')
    }
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
    const hostData = await api.getHostById({ host_id: row.id })
    currentHost.value = hostData.data || {}
    showDetail.value = true
  } catch (error) {
    message.error('获取主机详情失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 添加主机
const handleAddHost = () => {
  formRef.value?.validate(async (errors) => {
    if (errors) return

    try {
      loading.value = true
      
      let result;
      if (formModel.id) {
        // 编辑模式
        result = await api.updateHost(formModel.id, formModel)
        if (!result) {
          message.error('主机更新失败：服务器返回空数据')
          return
        }
        message.success('更新主机成功')
      } else {
        // 新增模式
        result = await api.createHost(formModel)
        if (!result) {
          message.error('主机添加失败：服务器返回空数据')
          return
        }
        message.success('添加主机成功')
      }
      
      showAddModal.value = false
      
      // 重置表单
      delete formModel.id // 删除id字段
      formModel.host_name = ''
      formModel.ip = ''
      formModel.host_type = 'server'
      formModel.ping_interval = 60
      formModel.enable_mrtg = false
      formModel.remark = ''
      
      // 重新加载数据
      loadData()
    } catch (error) {
      console.error('主机操作失败:', error)
      // 改进错误消息展示
      if (error.code) {
        message.error(`${formModel.id ? '更新' : '添加'}主机失败: [${error.code}] ${error.message}`)
      } else if (error.message && error.message !== 'OK') {
        message.error(`${formModel.id ? '更新' : '添加'}主机失败: ${error.message}`)
      } else if (typeof error === 'string') {
        message.error(`${formModel.id ? '更新' : '添加'}主机失败: ${error}`)
      } else {
        message.error(`${formModel.id ? '更新' : '添加'}主机失败，请检查网络连接`)
      }
    } finally {
      loading.value = false
    }
  })
}

// Ping测试
const handlePingTest = async (host) => {
  try {
    message.info(`正在测试主机 ${host.host_name} (${host.ip})...`)
    loading.value = true
    const response = await api.pingHost(host.id)
    const result = response.data || {}
    
    if (result.success) {
      const data = result.data || {}
      if (data.status === 'online') {
        message.success(`主机 ${host.host_name} (${host.ip}) Ping测试成功，延迟: ${data.response_time}ms，丢包率: ${data.packet_loss}%`)
      } else {
        message.error(`主机 ${host.host_name} (${host.ip}) Ping测试失败，丢包率: ${data.packet_loss}%`)
      }
    } else {
      message.error(`Ping测试失败: ${result.message}`)
    }
    
    // 重新加载数据以更新状态
    loadData()
  } catch (error) {
    message.error('Ping测试失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 查看MRTG
const handleViewMRTG = async (host) => {
  if (!host.enable_mrtg) {
    message.warning('该主机未启用MRTG监控')
    return
  }
  
  currentHost.value = host
  showMRTGModal.value = true
  mrtgLoading.value = true
  
  try {
    message.info(`正在获取主机 ${host.host_name} 的MRTG监控数据...`)
    
    // 获取最近7天的数据
    const response = await api.getMRTGData(host.id, { days: 7 })
    const data = response.data || {}
    
    if (data.items && data.items.length > 0) {
      message.success(`成功获取MRTG监控数据，共 ${data.items.length} 条记录`)
      mrtgData.value = data.items
      
      // 在下一个tick初始化图表
      nextTick(() => {
        initMRTGCharts()
      })
    } else {
      message.info('暂无MRTG监控数据，正在生成模拟数据...')
      const mockResponse = await api.generateMockMRTGData(host.id)
      if (mockResponse && mockResponse.data) {
        message.success('已生成模拟MRTG数据')
        // 再次获取数据以显示图表
        const refreshResponse = await api.getMRTGData(host.id, { days: 7 })
        if (refreshResponse && refreshResponse.data && refreshResponse.data.items) {
          mrtgData.value = refreshResponse.data.items
          nextTick(() => {
            initMRTGCharts()
          })
        }
      }
    }
  } catch (error) {
    message.error('获取MRTG数据失败: ' + (error.message || '未知错误'))
    mrtgLoading.value = false
    showMRTGModal.value = false
  } finally {
    mrtgLoading.value = false
  }
}

// 初始化MRTG图表
const initMRTGCharts = () => {
  // 销毁已有图表
  if (trafficChart) trafficChart.dispose()
  if (cpuChart) cpuChart.dispose()
  if (memoryChart) memoryChart.dispose()
  
  // 初始化流量图表
  if (trafficChartRef.value) {
    trafficChart = echarts.init(trafficChartRef.value)
    const option = generateTrafficChartOption()
    trafficChart.setOption(option)
  }
  
  // 初始化CPU图表
  if (cpuChartRef.value) {
    cpuChart = echarts.init(cpuChartRef.value)
    const option = generateCpuChartOption()
    cpuChart.setOption(option)
  }
  
  // 初始化内存图表
  if (memoryChartRef.value) {
    memoryChart = echarts.init(memoryChartRef.value)
    const option = generateMemoryChartOption()
    memoryChart.setOption(option)
  }
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleChartResize)
}

// 处理图表大小调整
const handleChartResize = () => {
  trafficChart && trafficChart.resize()
  cpuChart && cpuChart.resize()
  memoryChart && memoryChart.resize()
}

// 生成流量图表选项
const generateTrafficChartOption = () => {
  const dates = mrtgData.value.map(item => item.timestamp)
  const inbound = mrtgData.value.map(item => item.inbound_traffic)
  const outbound = mrtgData.value.map(item => item.outbound_traffic)
  
  return {
    title: {
      text: '网络流量监控'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const date = params[0].axisValue
        let result = `${date}<br/>`
        params.forEach(param => {
          const value = param.value
          const formatted = value > 1024 ? `${(value/1024).toFixed(2)} MB/s` : `${value.toFixed(2)} KB/s`
          result += `${param.seriesName}: ${formatted}<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['入站流量', '出站流量']
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '流量 (KB/s)',
      axisLabel: {
        formatter: function(value) {
          if (value >= 1024) {
            return (value / 1024).toFixed(1) + ' MB/s'
          }
          return value + ' KB/s'
        }
      }
    },
    series: [
      {
        name: '入站流量',
        type: 'line',
        data: inbound,
        areaStyle: {
          opacity: 0.2
        },
        smooth: true,
        lineStyle: {
          width: 2
        },
        color: '#4caf50'
      },
      {
        name: '出站流量',
        type: 'line',
        data: outbound,
        areaStyle: {
          opacity: 0.2
        },
        smooth: true,
        lineStyle: {
          width: 2
        },
        color: '#2196f3'
      }
    ]
  }
}

// 生成CPU图表选项
const generateCpuChartOption = () => {
  const dates = mrtgData.value.map(item => item.timestamp)
  const cpuUsage = mrtgData.value.map(item => item.cpu_usage)
  
  return {
    title: {
      text: 'CPU使用率'
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>{a}: {c}%'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: 'CPU使用率 (%)',
      max: 100
    },
    series: [
      {
        name: 'CPU使用率',
        type: 'line',
        data: cpuUsage,
        areaStyle: {
          opacity: 0.2
        },
        smooth: true,
        lineStyle: {
          width: 2
        },
        color: '#f44336'
      }
    ]
  }
}

// 生成内存图表选项
const generateMemoryChartOption = () => {
  const dates = mrtgData.value.map(item => item.timestamp)
  const memoryUsage = mrtgData.value.map(item => item.memory_usage)
  
  return {
    title: {
      text: '内存使用率'
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>{a}: {c}%'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '内存使用率 (%)',
      max: 100
    },
    series: [
      {
        name: '内存使用率',
        type: 'line',
        data: memoryUsage,
        areaStyle: {
          opacity: 0.2
        },
        smooth: true,
        lineStyle: {
          width: 2
        },
        color: '#ff9800'
      }
    ]
  }
}

// 监听模态框关闭事件，移除事件监听
watch(showMRTGModal, (show) => {
  if (!show) {
    // 移除窗口大小变化监听
    window.removeEventListener('resize', handleChartResize)
    
    // 销毁图表
    if (trafficChart) {
      trafficChart.dispose()
      trafficChart = null
    }
    if (cpuChart) {
      cpuChart.dispose()
      cpuChart = null
    }
    if (memoryChart) {
      memoryChart.dispose()
      memoryChart = null
    }
  }
})

// 编辑主机
const handleEdit = (host) => {
  // 填充表单数据
  formModel.host_name = host.host_name
  formModel.ip = host.ip
  formModel.host_type = host.host_type
  formModel.ping_interval = host.ping_interval
  formModel.enable_mrtg = host.enable_mrtg
  formModel.remark = host.remark
  
  // 标记为编辑模式
  formModel.id = host.id
  showAddModal.value = true
}

// 删除主机
const handleDelete = async (host) => {
  if (confirm(`确定要删除主机 ${host.host_name} 吗？`)) {
    try {
      loading.value = true
      await api.deleteHost(host.id)
      message.success(`已删除主机 ${host.host_name}`)
      showDetail.value = false
      loadData()
    } catch (error) {
      message.error('删除主机失败: ' + (error.message || '未知错误'))
    } finally {
      loading.value = false
    }
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

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.chart-container {
  height: 350px;
  width: 100%;
  margin: 16px 0;
}

.chart {
  height: 100%;
  width: 100%;
}
</style> 