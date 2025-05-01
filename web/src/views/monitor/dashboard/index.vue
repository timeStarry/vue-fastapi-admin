<template>
  <div class="dashboard-container">
    <n-grid :cols="24" :x-gap="16" :y-gap="16">
      <!-- 顶部统计卡片 -->
      <n-grid-item :span="6">
        <n-card title="主机监控" size="small">
          <n-statistic label="总主机数">
            <n-number-animation
              ref="hostCountRef"
              :from="0"
              :to="dashboardData.host_count || 0"
              :duration="1000"
            />
          </n-statistic>
          <n-divider />
          <n-space>
            <n-tag type="success">在线: {{ dashboardData.online_host_count || 0 }}</n-tag>
            <n-tag type="error">离线: {{ dashboardData.offline_host_count || 0 }}</n-tag>
            <n-tag type="warning">未知: {{ dashboardData.unknown_host_count || 0 }}</n-tag>
          </n-space>
        </n-card>
      </n-grid-item>

      <n-grid-item :span="6">
        <n-card title="服务监控" size="small">
          <n-statistic label="总服务数">
            <n-number-animation
              ref="serviceCountRef"
              :from="0"
              :to="dashboardData.service_count || 0"
              :duration="1000"
            />
          </n-statistic>
          <n-divider />
          <n-space>
            <n-tag type="success">正常: {{ dashboardData.normal_service_count || 0 }}</n-tag>
            <n-tag type="error">异常: {{ dashboardData.error_service_count || 0 }}</n-tag>
            <n-tag type="warning">告警: {{ dashboardData.warning_service_count || 0 }}</n-tag>
          </n-space>
        </n-card>
      </n-grid-item>

      <n-grid-item :span="6">
        <n-card title="告警状态" size="small">
          <n-statistic label="总告警数">
            <n-number-animation
              ref="alertCountRef"
              :from="0"
              :to="dashboardData.alert_count || 0"
              :duration="1000"
            />
          </n-statistic>
          <n-divider />
          <n-space>
            <n-tag type="error">错误: {{ dashboardData.error_alert_count || 0 }}</n-tag>
            <n-tag type="warning">警告: {{ dashboardData.warning_alert_count || 0 }}</n-tag>
            <n-tag type="info">信息: {{ dashboardData.info_alert_count || 0 }}</n-tag>
          </n-space>
        </n-card>
      </n-grid-item>

      <n-grid-item :span="6">
        <n-card title="MRTG状态" size="small">
          <n-statistic label="MRTG启用主机">
            <n-number-animation
              ref="mrtgCountRef"
              :from="0"
              :to="dashboardData.mrtg_host_count || 0"
              :duration="1000"
            />
          </n-statistic>
          <n-divider />
          <n-space>
            <n-tag type="success">正常: {{ dashboardData.normal_mrtg_count || 0 }}</n-tag>
            <n-tag type="warning">异常: {{ dashboardData.abnormal_mrtg_count || 0 }}</n-tag>
          </n-space>
        </n-card>
      </n-grid-item>

      <!-- 监控图表 -->
      <n-grid-item :span="12">
        <n-card title="网络流量监控" size="small">
          <div class="chart-container">
            <div ref="trafficChartRef" class="chart"></div>
          </div>
        </n-card>
      </n-grid-item>

      <n-grid-item :span="12">
        <n-card title="系统资源监控" size="small">
          <div class="chart-container">
            <div ref="resourceChartRef" class="chart"></div>
          </div>
        </n-card>
      </n-grid-item>

      <!-- 告警列表 -->
      <n-grid-item :span="24">
        <n-card title="最近告警" size="small">
          <n-data-table
            :columns="alertColumns"
            :data="recentAlerts"
            :pagination="{ pageSize: 5 }"
            :bordered="false"
            :single-line="false"
          />
        </n-card>
      </n-grid-item>
    </n-grid>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, h } from 'vue'
import { useMessage } from 'naive-ui'
import * as echarts from 'echarts'
import { NTag, NButton, NSpace } from 'naive-ui'
import api from '@/api'

const message = useMessage()

// 图表相关
const trafficChartRef = ref(null)
const resourceChartRef = ref(null)
let trafficChart = null
let resourceChart = null

// 仪表盘数据
const dashboardData = ref({
  host_count: 0,
  online_host_count: 0,
  offline_host_count: 0,
  unknown_host_count: 0,
  service_count: 0,
  normal_service_count: 0,
  error_service_count: 0,
  warning_service_count: 0,
  alert_count: 0,
  error_alert_count: 0,
  warning_alert_count: 0,
  info_alert_count: 0,
  mrtg_host_count: 0,
  normal_mrtg_count: 0,
  abnormal_mrtg_count: 0
})

// 最近告警数据
const recentAlerts = ref([])

// 告警列表列定义
const alertColumns = [
  {
    title: '级别',
    key: 'level',
    render(row) {
      const levelMap = {
        'error': { type: 'error', text: '错误' },
        'warning': { type: 'warning', text: '警告' },
        'info': { type: 'info', text: '信息' }
      }
      const level = levelMap[row.level] || levelMap.info
      return h(
        NTag,
        {
          type: level.type,
        },
        { default: () => level.text }
      )
    }
  },
  { title: '目标', key: 'target_name' },
  { title: '目标IP', key: 'target_ip' },
  { title: '告警内容', key: 'content' },
  { title: '告警时间', key: 'created_at' },
  {
    title: '状态',
    key: 'resolved',
    render(row) {
      return h(
        NTag,
        {
          type: row.resolved ? 'success' : 'default',
        },
        { default: () => row.resolved ? '已解决' : '未解决' }
      )
    }
  },
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
              type: row.resolved ? 'default' : 'primary',
              disabled: row.resolved,
              onClick: () => resolveAlert(row),
            },
            { default: () => '解决' }
          ),
        ],
      })
    },
  }
]

// MRTG监控数据
const mrtgData = ref([])

// 定时器
let dashboardTimer = null
let chartTimer = null

// 加载仪表盘数据
const loadDashboardData = async () => {
  try {
    const result = await api.getDashboardData()
    if (result && result.data) {
      dashboardData.value = result.data
    }
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
    message.error('获取仪表盘数据失败')
  }
}

// 加载最近告警数据
const loadRecentAlerts = async () => {
  try {
    const result = await api.getAlertList({ page: 1, page_size: 5 })
    if (result && result.data) {
      recentAlerts.value = result.data
    }
  } catch (error) {
    console.error('获取告警数据失败:', error)
    message.error('获取告警数据失败')
  }
}

// 加载MRTG数据
const loadMRTGData = async () => {
  try {
    // 获取启用MRTG的主机列表
    const hosts = await api.getHostList({ enable_mrtg: true, page_size: 100 })
    if (!hosts || !hosts.data || hosts.data.length === 0) {
      return
    }

    // 获取最近一天的MRTG数据（第一个主机）
    const host = hosts.data[0]
    const result = await api.getMRTGData(host.id, { days: 1 })
    if (result && result.data && result.data.items) {
      mrtgData.value = result.data.items
      
      // 更新图表
      updateCharts()
    }
  } catch (error) {
    console.error('获取MRTG数据失败:', error)
    message.error('获取MRTG数据失败')
  }
}

// 解决告警
const resolveAlert = async (alert) => {
  try {
    await api.updateAlert(alert.id, { resolved: true })
    message.success('告警已解决')
    
    // 刷新告警列表
    loadRecentAlerts()
  } catch (error) {
    console.error('解决告警失败:', error)
    message.error('解决告警失败')
  }
}

// 初始化图表
const initCharts = () => {
  // 初始化流量图表
  if (trafficChartRef.value) {
    trafficChart = echarts.init(trafficChartRef.value)
    const option = generateTrafficChartOption()
    trafficChart.setOption(option)
  }
  
  // 初始化资源图表
  if (resourceChartRef.value) {
    resourceChart = echarts.init(resourceChartRef.value)
    const option = generateResourceChartOption()
    resourceChart.setOption(option)
  }
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleChartResize)
}

// 更新图表
const updateCharts = () => {
  if (mrtgData.value.length === 0) {
    return
  }
  
  // 更新流量图表
  if (trafficChart) {
    const option = generateTrafficChartOption()
    trafficChart.setOption(option)
  }
  
  // 更新资源图表
  if (resourceChart) {
    const option = generateResourceChartOption()
    resourceChart.setOption(option)
  }
}

// 生成流量图表配置
const generateTrafficChartOption = () => {
  const timestamps = mrtgData.value.map(item => item.timestamp)
  const inbound = mrtgData.value.map(item => item.inbound_traffic)
  const outbound = mrtgData.value.map(item => item.outbound_traffic)
  
  return {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const date = params[0].axisValue
        let result = `${date}<br/>`
        params.forEach(param => {
          const value = param.value
          const formatted = value > 1000 ? `${(value/1000).toFixed(2)} Gbps` : `${value.toFixed(2)} Mbps`
          result += `${param.seriesName}: ${formatted}<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['入站流量', '出站流量']
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
      data: timestamps,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '流量 (Mbps)',
      axisLabel: {
        formatter: function(value) {
          if (value >= 1000) {
            return (value / 1000).toFixed(1) + ' Gbps'
          }
          return value + ' Mbps'
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

// 生成资源图表配置
const generateResourceChartOption = () => {
  const timestamps = mrtgData.value.map(item => item.timestamp)
  const cpuUsage = mrtgData.value.map(item => item.cpu_usage)
  const memoryUsage = mrtgData.value.map(item => item.memory_usage)
  const diskUsage = mrtgData.value.map(item => item.disk_usage)
  
  return {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const date = params[0].axisValue
        let result = `${date}<br/>`
        params.forEach(param => {
          result += `${param.seriesName}: ${param.value}%<br/>`
        })
        return result
      }
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
      data: timestamps,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '使用率 (%)',
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
      },
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
      },
      {
        name: '磁盘使用率',
        type: 'line',
        data: diskUsage,
        areaStyle: {
          opacity: 0.2
        },
        smooth: true,
        lineStyle: {
          width: 2
        },
        color: '#9c27b0'
      }
    ]
  }
}

// 处理图表大小调整
const handleChartResize = () => {
  trafficChart && trafficChart.resize()
  resourceChart && resourceChart.resize()
}

// 页面加载完成
onMounted(async () => {
  // 加载数据
  await loadDashboardData()
  await loadRecentAlerts()
  await loadMRTGData()
  
  // 初始化图表
  initCharts()
  
  // 设置定时刷新
  dashboardTimer = setInterval(() => {
    loadDashboardData()
    loadRecentAlerts()
  }, 30000) // 30秒刷新一次仪表盘和告警数据
  
  chartTimer = setInterval(() => {
    loadMRTGData()
  }, 60000) // 1分钟刷新一次MRTG数据
})

// 页面卸载前
onBeforeUnmount(() => {
  // 清除定时器
  if (dashboardTimer) clearInterval(dashboardTimer)
  if (chartTimer) clearInterval(chartTimer)
  
  // 移除窗口大小变化监听
  window.removeEventListener('resize', handleChartResize)
  
  // 销毁图表
  if (trafficChart) {
    trafficChart.dispose()
    trafficChart = null
  }
  if (resourceChart) {
    resourceChart.dispose()
    resourceChart = null
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 16px;
  height: 100%;
}

.chart-container {
  height: 350px;
  width: 100%;
}

.chart {
  height: 100%;
  width: 100%;
}
</style> 