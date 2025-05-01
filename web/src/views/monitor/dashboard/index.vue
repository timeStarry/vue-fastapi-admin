<template>
  <CommonPage>
    <template #header>
      <div flex items-center justify-between w-full>
        <h2 text-22 font-normal text-hex-333 dark:text-hex-ccc>监控面板</h2>
        <n-space>
          <n-button type="primary" @click="refreshData">
            <template #icon>
              <TheIcon icon="material-symbols:refresh" :size="18" />
            </template>
            刷新数据
          </n-button>
        </n-space>
      </div>
    </template>

    <div v-if="loading" class="loading-container">
      <n-spin size="large" />
    </div>
    <div v-else>
      <!-- 数据概览 -->
      <n-grid :cols="4" :x-gap="12" :y-gap="12" class="mb-4">
        <n-grid-item v-for="(card, index) in overviewCards" :key="index">
          <n-card hoverable>
            <div class="overview-card">
              <div class="overview-icon" :style="{ backgroundColor: card.color }">
                <TheIcon :icon="card.icon" :size="28" />
              </div>
              <div class="overview-content">
                <div class="overview-title">{{ card.title }}</div>
                <div class="overview-value">{{ card.value }}</div>
              </div>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- 告警统计 -->
      <n-grid :cols="3" :x-gap="12" :y-gap="12" class="mb-4">
        <n-grid-item v-for="(alert, index) in alertCards" :key="index">
          <n-card hoverable>
            <div class="alert-card" :class="alert.type">
              <div class="alert-icon">
                <TheIcon :icon="alert.icon" :size="36" />
              </div>
              <div class="alert-content">
                <div class="alert-count">{{ alert.count }}</div>
                <div class="alert-label">{{ alert.label }}</div>
              </div>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- 图表区域 -->
      <n-grid :cols="24" :x-gap="12" :y-gap="12">
        <!-- 主机状态分布 -->
        <n-grid-item :span="8">
          <n-card title="主机状态分布" hoverable>
            <div class="chart-container">
              <div ref="hostChartRef" class="chart"></div>
            </div>
          </n-card>
        </n-grid-item>

        <!-- 服务状态分布 -->
        <n-grid-item :span="8">
          <n-card title="服务状态分布" hoverable>
            <div class="chart-container">
              <div ref="serviceChartRef" class="chart"></div>
            </div>
          </n-card>
        </n-grid-item>

        <!-- 告警类型分布 -->
        <n-grid-item :span="8">
          <n-card title="告警类型分布" hoverable>
            <div class="chart-container">
              <div ref="alertTypeChartRef" class="chart"></div>
            </div>
          </n-card>
        </n-grid-item>

        <!-- 性能趋势 -->
        <n-grid-item :span="16">
          <n-card title="系统性能趋势" hoverable>
            <div class="chart-container" style="height: 300px;">
              <div ref="performanceChartRef" class="chart"></div>
            </div>
          </n-card>
        </n-grid-item>

        <!-- 响应时间 -->
        <n-grid-item :span="8">
          <n-card title="平均响应时间(ms)" hoverable>
            <div class="chart-container" style="height: 300px;">
              <div ref="responseTimeChartRef" class="chart"></div>
            </div>
          </n-card>
        </n-grid-item>

        <!-- 最近告警 -->
        <n-grid-item :span="24">
          <n-card title="最近告警" hoverable>
            <n-data-table
              :columns="alertColumns"
              :data="alertList"
              :pagination="{ pageSize: 5 }"
              :bordered="false"
              size="small"
            />
          </n-card>
        </n-grid-item>
      </n-grid>
    </div>
  </CommonPage>
</template>

<script setup>
import { ref, reactive, h, onMounted, nextTick, computed, onBeforeUnmount, onActivated } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  LegendComponent,
  TooltipComponent,
  GridComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useMessage } from 'naive-ui'
import { NTag, NButton, NTooltip } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import api from '@/api'

defineOptions({ name: '监控面板' })

// 注册 ECharts 组件
echarts.use([
  BarChart,
  LineChart,
  PieChart,
  TitleComponent,
  LegendComponent,
  TooltipComponent,
  GridComponent,
  CanvasRenderer,
])

const message = useMessage()
const loading = ref(false)

// 图表引用
const hostChartRef = ref(null)
const serviceChartRef = ref(null)
const alertTypeChartRef = ref(null)
const performanceChartRef = ref(null)
const responseTimeChartRef = ref(null)

// 图表实例
const charts = ref({})

// 概览数据
const overviewData = reactive({
  hostTotal: 0,
  hostOnlineRate: 0,
  serviceTotal: 0,
  serviceAvailableRate: 0,
})

// 告警数据
const alertData = reactive({
  errorCount: 0,
  warningCount: 0,
  infoCount: 0,
})

// 数据概览卡片
const overviewCards = computed(() => [
  {
    title: '主机总数',
    value: overviewData.hostTotal,
    icon: 'material-symbols:dns',
    color: '#1976d2',
  },
  {
    title: '主机在线率',
    value: `${overviewData.hostOnlineRate.toFixed(1)}%`,
    icon: 'material-symbols:monitor-heart',
    color: '#4caf50',
  },
  {
    title: '服务总数',
    value: overviewData.serviceTotal,
    icon: 'material-symbols:layers',
    color: '#9c27b0',
  },
  {
    title: '服务可用率',
    value: `${overviewData.serviceAvailableRate.toFixed(1)}%`,
    icon: 'material-symbols:speed',
    color: '#ff9800',
  },
])

// 告警卡片
const alertCards = computed(() => [
  {
    label: '严重告警',
    count: alertData.errorCount,
    icon: 'material-symbols:error',
    type: 'error',
  },
  {
    label: '警告',
    count: alertData.warningCount,
    icon: 'material-symbols:warning',
    type: 'warning',
  },
  {
    label: '信息',
    count: alertData.infoCount,
    icon: 'material-symbols:info',
    type: 'info',
  },
])

// 告警列表列定义
const alertColumns = [
  {
    title: '级别',
    key: 'level',
    width: 80,
    render(row) {
      const colorMap = {
        error: 'error',
        warning: 'warning',
        info: 'info',
      }
      const textMap = {
        error: '严重',
        warning: '警告',
        info: '信息',
      }
      return h(NTag, { type: colorMap[row.level], size: 'small' }, { default: () => textMap[row.level] })
    },
  },
  { title: '时间', key: 'created_at', width: 150 },
  { 
    title: '对象', 
    key: 'target_type', 
    width: 200,
    render(row) {
      return `${row.target_type === 'host' ? '主机' : '服务'}: ${row.target_name}`
    }
  },
  { title: '告警内容', key: 'content', ellipsis: true },
  {
    title: '状态',
    key: 'resolved',
    width: 80,
    render(row) {
      return h(
        NTag,
        { type: row.resolved ? 'success' : 'warning', size: 'small' },
        { default: () => (row.resolved ? '已解决' : '未解决') }
      )
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    render(row) {
      if (row.resolved) {
        return h(
          NButton,
          {
            size: 'small',
            type: 'info',
            onClick: () => handleViewAlert(row),
          },
          { default: () => '查看' }
        )
      }
      return h(
        NButton,
        {
          size: 'small',
          type: 'success',
          onClick: () => handleResolveAlert(row),
        },
        { default: () => '标记已解决' }
      )
    },
  },
]

// 告警列表数据
const alertList = ref([])

// 状态分布数据
const hostStatusDistribution = ref({})
const serviceStatusDistribution = ref({})
const alertLevelDistribution = ref({})

// 加载监控面板数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await api.getDashboardData()
    const result = response.data || {}
    
    // 顶部统计卡片数据
    overviewData.hostTotal = result.host_count || 0
    overviewData.serviceTotal = result.service_count || 0
    
    // 计算在线率和可用率
    const onlineHosts = result.online_host_count || 0
    const normalServices = result.normal_service_count || 0
    
    overviewData.hostOnlineRate = overviewData.hostTotal > 0 
      ? (onlineHosts / overviewData.hostTotal) * 100
      : 0
    
    overviewData.serviceAvailableRate = overviewData.serviceTotal > 0
      ? (normalServices / overviewData.serviceTotal) * 100
      : 0
    
    // 更新告警数据
    alertData.errorCount = 0
    alertData.warningCount = 0
    alertData.infoCount = 0
    
    const alertDistribution = result.alert_level_distribution || {}
    alertData.errorCount = alertDistribution.error || 0
    alertData.warningCount = alertDistribution.warning || 0
    alertData.infoCount = alertDistribution.info || 0
    
    // 更新状态分布数据
    hostStatusDistribution.value = result.host_status_distribution || {}
    serviceStatusDistribution.value = result.service_status_distribution || {}
    alertLevelDistribution.value = alertDistribution
    
    // 更新告警列表
    alertList.value = result.recent_alerts || []
    
    // 在数据加载完成后再初始化图表
    nextTick(() => {
      setTimeout(() => {
        initCharts() // 使用setTimeout确保DOM完全渲染
      }, 100)
    })
  } catch (error) {
    message.error('加载监控面板数据失败: ' + (error.message || '未知错误'))
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 处理解决告警
const handleResolveAlert = async (alert) => {
  try {
    loading.value = true
    await api.updateAlert(alert.id, { resolved: true })
    message.success('告警已标记为已解决')
    // 重新加载数据
    loadData()
  } catch (error) {
    message.error('标记告警失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 处理查看告警
const handleViewAlert = (alert) => {
  message.info(`查看告警: ${alert.content}`)
  // 这里可以添加查看告警详情的逻辑
}

// 初始化图表
const initCharts = () => {
  // 清除之前的图表实例
  Object.values(charts.value).forEach(chart => {
    chart && chart.dispose()
  })
  charts.value = {} // 重置图表实例对象
  
  // 延迟一下确保DOM加载完成
  nextTick(() => {
    initHostStatusChart()
    initServiceStatusChart()
    initAlertTypeChart()
    initPerformanceChart()
    initResponseTimeChart()
  })
}

// 初始化主机状态分布图表
const initHostStatusChart = () => {
  if (!hostChartRef.value) return
  
  try {
    const chart = echarts.init(hostChartRef.value)
    charts.value.hostChart = chart
    
    const data = []
    const statusLabels = {
      'online': '在线',
      'offline': '离线',
      'unknown': '未知'
    }
    
    // 转换数据为图表所需格式
    Object.entries(hostStatusDistribution.value).forEach(([status, count]) => {
      data.push({
        name: statusLabels[status] || status,
        value: count
      })
    })
    
    // 如果没有数据，添加一个空数据以显示图表
    if (data.length === 0) {
      data.push({
        name: '无数据',
        value: 1
      })
    }
    
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        data: data.map(item => item.name)
      },
      series: [
        {
          name: '主机状态',
          type: 'pie',
          radius: '70%',
          data: data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          color: ['#4caf50', '#f44336', '#9e9e9e']
        }
      ]
    }
    
    chart.setOption(option)
  } catch (error) {
    console.error('初始化主机状态图表失败:', error)
  }
}

// 初始化服务状态分布图表
const initServiceStatusChart = () => {
  if (!serviceChartRef.value) return
  
  try {
    const chart = echarts.init(serviceChartRef.value)
    charts.value.serviceChart = chart
    
    const data = []
    const statusLabels = {
      'normal': '正常',
      'warning': '警告',
      'error': '异常',
      'unknown': '未知'
    }
    
    // 转换数据为图表所需格式
    Object.entries(serviceStatusDistribution.value).forEach(([status, count]) => {
      data.push({
        name: statusLabels[status] || status,
        value: count
      })
    })
    
    // 如果没有数据，添加一个空数据以显示图表
    if (data.length === 0) {
      data.push({
        name: '无数据',
        value: 1
      })
    }
    
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        data: data.map(item => item.name)
      },
      series: [
        {
          name: '服务状态',
          type: 'pie',
          radius: '70%',
          data: data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          color: ['#4caf50', '#ff9800', '#f44336', '#9e9e9e']
        }
      ]
    }
    
    chart.setOption(option)
  } catch (error) {
    console.error('初始化服务状态图表失败:', error)
  }
}

// 初始化告警类型分布图表
const initAlertTypeChart = () => {
  if (!alertTypeChartRef.value) return
  
  try {
    const chart = echarts.init(alertTypeChartRef.value)
    charts.value.alertTypeChart = chart
    
    const data = []
    const levelLabels = {
      'error': '严重',
      'warning': '警告',
      'info': '信息'
    }
    
    // 转换数据为图表所需格式
    Object.entries(alertLevelDistribution.value).forEach(([level, count]) => {
      data.push({
        name: levelLabels[level] || level,
        value: count
      })
    })
    
    // 如果没有数据，添加一个空数据以显示图表
    if (data.length === 0) {
      data.push({
        name: '无数据',
        value: 1
      })
    }
    
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        data: data.map(item => item.name)
      },
      series: [
        {
          name: '告警级别',
          type: 'pie',
          radius: '70%',
          data: data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          color: ['#f44336', '#ff9800', '#2196f3']
        }
      ]
    }
    
    chart.setOption(option)
  } catch (error) {
    console.error('初始化告警类型图表失败:', error)
  }
}

// 初始化性能趋势图表 (模拟数据)
const initPerformanceChart = () => {
  if (!performanceChartRef.value) return
  
  const chart = echarts.init(performanceChartRef.value)
  charts.value.performanceChart = chart
  
  // 模拟24小时性能数据
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  
  // 随机生成性能数据
  const generateRandomData = (baseValue, variance, length) => {
    return Array.from({ length }, () => Math.floor(baseValue + (Math.random() * variance * 2 - variance)))
  }
  
  const cpuData = generateRandomData(40, 20, 24)
  const memoryData = generateRandomData(60, 15, 24)
  const diskData = generateRandomData(50, 10, 24)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['CPU使用率', '内存使用率', '磁盘使用率']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: hours
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      },
      max: 100
    },
    series: [
      {
        name: 'CPU使用率',
        type: 'line',
        data: cpuData,
        areaStyle: {
          opacity: 0.2
        },
        smooth: true
      },
      {
        name: '内存使用率',
        type: 'line',
        data: memoryData,
        areaStyle: {
          opacity: 0.2
        },
        smooth: true
      },
      {
        name: '磁盘使用率',
        type: 'line',
        data: diskData,
        areaStyle: {
          opacity: 0.2
        },
        smooth: true
      }
    ]
  }
  
  chart.setOption(option)
}

// 初始化响应时间图表 (模拟数据)
const initResponseTimeChart = () => {
  if (!responseTimeChartRef.value) return
  
  const chart = echarts.init(responseTimeChartRef.value)
  charts.value.responseTimeChart = chart
  
  // 模拟7天的数据
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  
  // 随机生成响应时间数据
  const responseTimeData = Array.from({ length: 7 }, () => Math.floor(Math.random() * 200 + 100))
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br>{a}: {c} ms'
    },
    xAxis: {
      type: 'category',
      data: days
    },
    yAxis: {
      type: 'value',
      name: '响应时间(ms)'
    },
    series: [
      {
        name: '平均响应时间',
        type: 'bar',
        data: responseTimeData,
        itemStyle: {
          color: '#1890ff'
        }
      }
    ]
  }
  
  chart.setOption(option)
}

// 刷新数据
const refreshData = () => {
  loadData()
  message.success('数据已刷新')
}

// 窗口大小变化时调整图表大小
const handleResize = () => {
  nextTick(() => {
    Object.values(charts.value).forEach(chart => {
      chart && chart.resize()
    })
  })
}

// 页面挂载
onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

// 页面销毁前
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  // 销毁图表实例
  Object.values(charts.value).forEach(chart => {
    chart && chart.dispose()
  })
  charts.value = {}
})

// 页面激活时（缓存模式）
onActivated(() => {
  nextTick(() => {
    loadData() // 确保在DOM更新后加载数据
  })
})
</script>

<style scoped>
.chart-container {
  height: 250px;
  width: 100%;
}

.chart {
  height: 100%;
  width: 100%;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

.overview-card {
  display: flex;
  align-items: center;
}

.overview-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 16px;
  color: white;
}

.overview-content {
  flex: 1;
}

.overview-title {
  font-size: 14px;
  color: #888;
  margin-bottom: 8px;
}

.overview-value {
  font-size: 24px;
  font-weight: bold;
}

.alert-card {
  padding: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  color: white;
}

.alert-card.error {
  background: linear-gradient(to right, #d03050, #ff6d6d);
}

.alert-card.warning {
  background: linear-gradient(to right, #f0a020, #ffcf8c);
}

.alert-card.info {
  background: linear-gradient(to right, #2080f0, #5cbbff);
}

.alert-icon {
  margin-right: 16px;
}

.alert-content {
  flex: 1;
}

.alert-count {
  font-size: 36px;
  font-weight: bold;
  line-height: 1;
  margin-bottom: 8px;
}

.alert-label {
  font-size: 16px;
}
</style> 