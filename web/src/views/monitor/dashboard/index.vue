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
  hostTotal: 36,
  hostOnlineRate: 94.4,
  serviceTotal: 48,
  serviceAvailableRate: 97.9,
})

// 告警数据
const alertData = reactive({
  errorCount: 3,
  warningCount: 8,
  infoCount: 12,
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
    value: `${overviewData.hostOnlineRate}%`,
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
    value: `${overviewData.serviceAvailableRate}%`,
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
  { title: '时间', key: 'time', width: 150 },
  { title: '对象', key: 'target', width: 200 },
  { title: '告警内容', key: 'content', ellipsis: true },
  {
    title: '操作',
    key: 'actions',
    width: 80,
    render(row) {
      return h(
        NButton,
        {
          text: true,
          type: 'primary',
          size: 'small',
          onClick: () => handleViewAlert(row),
        },
        { default: () => '详情' }
      )
    },
  },
]

// 告警列表数据
const alertList = ref([
  {
    id: 1,
    level: 'error',
    time: '2023-05-01 10:15:23',
    target: '主机-3 (192.168.1.3)',
    content: '主机无法连接，超时。已尝试5次连接失败。',
  },
  {
    id: 2,
    level: 'warning',
    time: '2023-05-01 09:30:05',
    target: '服务-2 (https://api.example.com/service-2)',
    content: '服务响应时间超过阈值，当前: 580ms，阈值: 500ms。',
  },
  {
    id: 3,
    level: 'error',
    time: '2023-05-01 08:45:12',
    target: '服务-5 (http://web.example.com/service-5)',
    content: '服务返回状态码: 500，预期: 200。',
  },
  {
    id: 4,
    level: 'info',
    time: '2023-05-01 08:30:45',
    target: '主机-8 (192.168.1.8)',
    content: 'MRTG监控数据更新成功。',
  },
  {
    id: 5,
    level: 'warning',
    time: '2023-05-01 07:20:18',
    target: '主机-10 (192.168.1.10)',
    content: 'CPU使用率超过75%，当前: 82%。',
  },
])

// 初始化图表
function initCharts() {
  const options = {
    hostChart: {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'center',
        itemWidth: 14,
        itemHeight: 14,
        icon: 'circle',
      },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
          },
          emphasis: {
            label: {
              show: true,
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: [
            { value: 34, name: '在线', itemStyle: { color: '#18a058' } },
            { value: 2, name: '离线', itemStyle: { color: '#d03050' } },
            { value: 0, name: '未知', itemStyle: { color: '#2080f0' } }
          ]
        }
      ]
    },
    serviceChart: {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'center',
        itemWidth: 14,
        itemHeight: 14,
        icon: 'circle',
      },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
          },
          emphasis: {
            label: {
              show: true,
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: [
            { value: 42, name: '正常', itemStyle: { color: '#18a058' } },
            { value: 3, name: '异常', itemStyle: { color: '#d03050' } },
            { value: 3, name: '警告', itemStyle: { color: '#f0a020' } },
            { value: 0, name: '未知', itemStyle: { color: '#2080f0' } }
          ]
        }
      ]
    },
    alertTypeChart: {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        right: 10,
        top: 'center',
        itemWidth: 14,
        itemHeight: 14,
        icon: 'circle',
      },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
          },
          emphasis: {
            label: {
              show: true,
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: [
            { value: 8, name: '主机离线', itemStyle: { color: '#d03050' } },
            { value: 6, name: '服务异常', itemStyle: { color: '#f0a020' } },
            { value: 5, name: '响应超时', itemStyle: { color: '#f0a020' } },
            { value: 4, name: '资源占用高', itemStyle: { color: '#f0a020' } },
          ]
        }
      ]
    },
    performanceChart: {
      tooltip: {
        trigger: 'axis',
      },
      legend: {
        data: ['CPU使用率', '内存使用率', '网络流量']
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
        data: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00']
      },
      yAxis: [
        {
          type: 'value',
          name: '使用率 (%)',
          min: 0,
          max: 100,
          position: 'left'
        },
        {
          type: 'value',
          name: '流量 (Mbps)',
          min: 0,
          max: 100,
          position: 'right'
        }
      ],
      series: [
        {
          name: 'CPU使用率',
          type: 'line',
          smooth: true,
          data: [30, 32, 28, 45, 58, 62, 55, 40],
          yAxisIndex: 0,
          itemStyle: { color: '#18a058' }
        },
        {
          name: '内存使用率',
          type: 'line',
          smooth: true,
          data: [50, 51, 52, 55, 60, 65, 60, 58],
          yAxisIndex: 0,
          itemStyle: { color: '#2080f0' }
        },
        {
          name: '网络流量',
          type: 'line',
          smooth: true,
          data: [15, 12, 20, 30, 40, 35, 45, 25],
          yAxisIndex: 1,
          itemStyle: { color: '#f0a020' }
        }
      ]
    },
    responseTimeChart: {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['API服务', 'Web服务', '数据库', '缓存服务', '认证服务'],
        axisLabel: {
          rotate: 45,
          interval: 0
        }
      },
      yAxis: {
        type: 'value',
        name: '毫秒'
      },
      series: [
        {
          type: 'bar',
          data: [120, 180, 30, 25, 90],
          itemStyle: {
            color: function(params) {
              // 为不同类型的服务设置不同颜色
              const colors = ['#1890ff', '#2fc25b', '#facc14', '#223273', '#8543e0'];
              return colors[params.dataIndex % colors.length];
            }
          },
          label: {
            show: true,
            position: 'top',
            formatter: '{c} ms'
          }
        }
      ]
    }
  }

  // 初始化各个图表
  charts.value.hostChart = echarts.init(hostChartRef.value)
  charts.value.hostChart.setOption(options.hostChart)

  charts.value.serviceChart = echarts.init(serviceChartRef.value)
  charts.value.serviceChart.setOption(options.serviceChart)

  charts.value.alertTypeChart = echarts.init(alertTypeChartRef.value)
  charts.value.alertTypeChart.setOption(options.alertTypeChart)

  charts.value.performanceChart = echarts.init(performanceChartRef.value)
  charts.value.performanceChart.setOption(options.performanceChart)

  charts.value.responseTimeChart = echarts.init(responseTimeChartRef.value)
  charts.value.responseTimeChart.setOption(options.responseTimeChart)
}

// 刷新数据
function refreshData() {
  loading.value = true
  message.info('正在刷新数据...')
  
  // 这里应该调用实际的API接口获取数据
  setTimeout(() => {
    loading.value = false
    message.success('数据已刷新')
  }, 1000)
}

// 查看告警详情
function handleViewAlert(alert) {
  message.info(`查看告警详情：${alert.content}`)
  // 这里应该显示告警详情弹窗或跳转到告警详情页面
}

// 根据窗口大小调整图表
function resizeCharts() {
  Object.values(charts.value).forEach(chart => {
    chart?.resize()
  })
}

// 销毁图表实例
function disposeCharts() {
  Object.values(charts.value).forEach(chart => {
    chart?.dispose()
  })
  charts.value = {}
}

// 监听窗口大小变化
window.addEventListener('resize', resizeCharts)

onMounted(() => {
  loading.value = true
  // 加载数据
  setTimeout(() => {
    loading.value = false
    nextTick(() => {
      initCharts()
    })
  }, 500)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  disposeCharts()
})

// 解决缓存组件激活时图表不显示的问题
onActivated(() => {
  nextTick(() => {
    resizeCharts()
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