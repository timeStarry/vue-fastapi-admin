<template>
  <CommonPage>
    <template #header>
      <div flex items-center justify-between w-full>
        <h2 text-22 font-normal text-hex-333 dark:text-hex-ccc>工单面板</h2>
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

      <!-- 图表区域 -->
      <n-grid :cols="24" :x-gap="12" :y-gap="12">
        <!-- 工单类型分布 -->
        <n-grid-item :span="8">
          <n-card title="工单类型分布" hoverable>
            <div class="chart-container">
              <div ref="typeChartRef" class="chart"></div>
            </div>
          </n-card>
        </n-grid-item>

        <!-- 工单状态分布 -->
        <n-grid-item :span="8">
          <n-card title="工单状态分布" hoverable>
            <div class="chart-container">
              <div ref="statusChartRef" class="chart"></div>
            </div>
          </n-card>
        </n-grid-item>

        <!-- 工单优先级分布 -->
        <n-grid-item :span="8">
          <n-card title="工单优先级分布" hoverable>
            <div class="chart-container">
              <div ref="priorityChartRef" class="chart"></div>
            </div>
          </n-card>
        </n-grid-item>

        <!-- 工单数量趋势 -->
        <n-grid-item :span="16">
          <n-card title="工单数量趋势" hoverable>
            <div class="chart-container" style="height: 300px;">
              <div ref="trendChartRef" class="chart"></div>
            </div>
          </n-card>
        </n-grid-item>

        <!-- 平均处理时长 -->
        <n-grid-item :span="8">
          <n-card title="平均处理时长(小时)" hoverable>
            <div class="chart-container" style="height: 300px;">
              <div ref="timeChartRef" class="chart"></div>
            </div>
          </n-card>
        </n-grid-item>

        <!-- 待处理工单 -->
        <n-grid-item :span="12">
          <n-card title="待处理工单" hoverable>
            <n-data-table
              :columns="pendingColumns"
              :data="pendingTickets"
              :max-height="300"
              :pagination="{ pageSize: 5 }"
              :bordered="false"
              size="small"
            />
          </n-card>
        </n-grid-item>

        <!-- 处理人工作量 -->
        <n-grid-item :span="12">
          <n-card title="处理人工作量" hoverable>
            <div class="chart-container" style="height: 300px;">
              <div ref="assigneeChartRef" class="chart"></div>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>
    </div>
  </CommonPage>
</template>

<script setup>
import { onMounted, ref, computed, onBeforeUnmount, h, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NCard,
  NDataTable,
  NGrid,
  NGridItem,
  NSpace,
  NSpin,
  NTag,
  NTooltip,
} from 'naive-ui'
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  LegendComponent,
  TooltipComponent,
  GridComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

import CommonPage from '@/components/page/CommonPage.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

import { formatDate } from '@/utils'
import api from '@/api'

defineOptions({ name: '工单面板' })

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

const router = useRouter()
const loading = ref(true)
const typeChartRef = ref(null)
const statusChartRef = ref(null)
const priorityChartRef = ref(null)
const trendChartRef = ref(null)
const timeChartRef = ref(null)
const assigneeChartRef = ref(null)

// 图表实例
const charts = ref({})

// 工单数据
const dashboardData = ref({
  overview: {
    total: 0,
    pending: 0,
    completed: 0,
    avg_process_time: 0,
  },
  type_distribution: [],
  status_distribution: [],
  priority_distribution: [],
  trend_data: [],
  process_time: [],
  assignee_workload: [],
  pending_tickets: [],
})

// 工单类型选项
const typeOptions = [
  { label: '故障报修', value: 'fault' },
  { label: '资源申请', value: 'resource' },
  { label: '配置变更', value: 'config' },
  { label: '日常维护', value: 'maintenance' },
  { label: '紧急处理', value: 'emergency' },
]

// 工单状态选项
const statusOptions = [
  { label: '待接单', value: 'pending', type: 'warning' },
  { label: '处理中', value: 'processing', type: 'info' },
  { label: '待确认', value: 'confirming', type: 'success' },
  { label: '已完成', value: 'completed', type: 'success' },
  { label: '已关闭', value: 'closed', type: 'error' },
]

// 工单优先级选项
const priorityOptions = [
  { label: '低', value: 'low', type: 'default' },
  { label: '中', value: 'medium', type: 'info' },
  { label: '高', value: 'high', type: 'warning' },
  { label: '紧急', value: 'urgent', type: 'error' },
]

// 数据概览卡片
const overviewCards = computed(() => [
  {
    title: '工单总数',
    value: dashboardData.value.overview.total || 0,
    icon: 'material-symbols:list-alt',
    color: '#1976d2',
  },
  {
    title: '待处理工单',
    value: dashboardData.value.overview.pending || 0,
    icon: 'material-symbols:pending-actions',
    color: '#ff9800',
  },
  {
    title: '已完成工单',
    value: dashboardData.value.overview.completed || 0,
    icon: 'material-symbols:task-alt',
    color: '#4caf50',
  },
  {
    title: '平均处理时长(小时)',
    value: dashboardData.value.overview.avg_process_time?.toFixed(1) || 0,
    icon: 'material-symbols:timer',
    color: '#9c27b0',
  },
])

// 待处理工单表格
const pendingColumns = [
  {
    title: '工单编号',
    key: 'ticket_no',
    width: 100,
  },
  {
    title: '标题',
    key: 'title',
    ellipsis: true,
  },
  {
    title: '优先级',
    key: 'priority',
    width: 80,
    render(row) {
      const priority = priorityOptions.find(p => p.value === row.priority) || { label: '未知', type: 'default' }
      return h(NTag, { type: priority.type, size: 'small' }, { default: () => priority.label })
    }
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 120,
    render(row) {
      return h(NTooltip, {}, {
        trigger: () => h('span', formatDate(row.created_at, 'MM-DD HH:mm')),
        default: () => formatDate(row.created_at)
      })
    }
  },
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
          onClick: () => {
            router.push(`/ticket/process?id=${row.id}`)
          },
        },
        { default: () => '处理' }
      )
    }
  }
]

const pendingTickets = computed(() => dashboardData.value.pending_tickets || [])

// 初始化图表
function initCharts() {
  const options = {
    typeChart: {
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
          data: (dashboardData.value.type_distribution || []).map(item => ({
            name: typeOptions.find(t => t.value === item.type)?.label || item.type,
            value: item.count
          }))
        }
      ]
    },
    statusChart: {
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
          data: (dashboardData.value.status_distribution || []).map(item => ({
            name: statusOptions.find(s => s.value === item.status)?.label || item.status,
            value: item.count
          }))
        }
      ]
    },
    priorityChart: {
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
          data: (dashboardData.value.priority_distribution || []).map(item => ({
            name: priorityOptions.find(p => p.value === item.priority)?.label || item.priority,
            value: item.count
          }))
        }
      ]
    },
    trendChart: {
      tooltip: {
        trigger: 'axis',
      },
      legend: {
        data: ['新建工单', '已完成工单']
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
        data: (dashboardData.value.trend_data || []).map(item => item.date)
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '新建工单',
          type: 'line',
          smooth: true,
          data: (dashboardData.value.trend_data || []).map(item => item.created)
        },
        {
          name: '已完成工单',
          type: 'line',
          smooth: true,
          data: (dashboardData.value.trend_data || []).map(item => item.completed)
        }
      ]
    },
    timeChart: {
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
        data: (dashboardData.value.process_time || []).map(item => item.type_name),
        axisLabel: {
          rotate: 45,
          interval: 0
        }
      },
      yAxis: {
        type: 'value',
        name: '小时'
      },
      series: [
        {
          type: 'bar',
          data: (dashboardData.value.process_time || []).map(item => item.avg_time),
          itemStyle: {
            color: '#1890ff'
          }
        }
      ]
    },
    assigneeChart: {
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
        type: 'value'
      },
      yAxis: {
        type: 'category',
        data: (dashboardData.value.assignee_workload || []).map(item => item.assignee_name),
        axisLabel: {
          width: 80,
          overflow: 'truncate'
        }
      },
      series: [
        {
          name: '已处理',
          type: 'bar',
          stack: 'total',
          emphasis: {
            focus: 'series'
          },
          data: (dashboardData.value.assignee_workload || []).map(item => item.completed)
        },
        {
          name: '处理中',
          type: 'bar',
          stack: 'total',
          emphasis: {
            focus: 'series'
          },
          data: (dashboardData.value.assignee_workload || []).map(item => item.processing)
        }
      ]
    }
  }

  // 初始化图表
  if (typeChartRef.value && !charts.value.typeChart) {
    charts.value.typeChart = echarts.init(typeChartRef.value)
  }
  if (statusChartRef.value && !charts.value.statusChart) {
    charts.value.statusChart = echarts.init(statusChartRef.value)
  }
  if (priorityChartRef.value && !charts.value.priorityChart) {
    charts.value.priorityChart = echarts.init(priorityChartRef.value)
  }
  if (trendChartRef.value && !charts.value.trendChart) {
    charts.value.trendChart = echarts.init(trendChartRef.value)
  }
  if (timeChartRef.value && !charts.value.timeChart) {
    charts.value.timeChart = echarts.init(timeChartRef.value)
  }
  if (assigneeChartRef.value && !charts.value.assigneeChart) {
    charts.value.assigneeChart = echarts.init(assigneeChartRef.value)
  }

  // 设置图表选项
  charts.value.typeChart?.setOption(options.typeChart)
  charts.value.statusChart?.setOption(options.statusChart)
  charts.value.priorityChart?.setOption(options.priorityChart)
  charts.value.trendChart?.setOption(options.trendChart)
  charts.value.timeChart?.setOption(options.timeChart)
  charts.value.assigneeChart?.setOption(options.assigneeChart)
}

// 获取仪表盘数据
async function fetchDashboardData() {
  try {
    loading.value = true
    const res = await api.getTicketStatistics()
    dashboardData.value = res.data

    // 使用模拟数据（实际项目中请删除这部分代码）
    if (!dashboardData.value.overview) {
      dashboardData.value = generateMockData()
    }

    // 初始化图表
    await nextTick()
    initCharts()
  } catch (error) {
    console.error('获取工单统计数据失败', error)
    // 使用模拟数据
    dashboardData.value = generateMockData()
    await nextTick()
    initCharts()
  } finally {
    loading.value = false
  }
}

// 刷新数据
function refreshData() {
  fetchDashboardData()
}

// 窗口大小变化时重新调整图表大小
function handleResize() {
  Object.values(charts.value).forEach(chart => {
    chart?.resize()
  })
}

// 生成模拟数据（实际项目中可以删除此函数）
function generateMockData() {
  return {
    overview: {
      total: 256,
      pending: 42,
      completed: 187,
      avg_process_time: 8.5,
    },
    type_distribution: [
      { type: 'fault', count: 98 },
      { type: 'resource', count: 56 },
      { type: 'config', count: 42 },
      { type: 'maintenance', count: 35 },
      { type: 'emergency', count: 25 },
    ],
    status_distribution: [
      { status: 'pending', count: 18 },
      { status: 'processing', count: 24 },
      { status: 'confirming', count: 27 },
      { status: 'completed', count: 152 },
      { status: 'closed', count: 35 },
    ],
    priority_distribution: [
      { priority: 'low', count: 65 },
      { priority: 'medium', count: 107 },
      { priority: 'high', count: 68 },
      { priority: 'urgent', count: 16 },
    ],
    trend_data: [
      { date: '5-1', created: 10, completed: 8 },
      { date: '5-2', created: 12, completed: 10 },
      { date: '5-3', created: 15, completed: 11 },
      { date: '5-4', created: 8, completed: 9 },
      { date: '5-5', created: 9, completed: 12 },
      { date: '5-6', created: 13, completed: 8 },
      { date: '5-7', created: 7, completed: 10 },
    ],
    process_time: [
      { type: 'fault', type_name: '故障报修', avg_time: 5.8 },
      { type: 'resource', type_name: '资源申请', avg_time: 12.3 },
      { type: 'config', type_name: '配置变更', avg_time: 8.4 },
      { type: 'maintenance', type_name: '日常维护', avg_time: 3.6 },
      { type: 'emergency', type_name: '紧急处理', avg_time: 2.1 },
    ],
    assignee_workload: [
      { assignee_name: '张三', completed: 28, processing: 5 },
      { assignee_name: '李四', completed: 32, processing: 3 },
      { assignee_name: '王五', completed: 24, processing: 8 },
      { assignee_name: '赵六', completed: 18, processing: 4 },
      { assignee_name: '钱七', completed: 12, processing: 2 },
    ],
    pending_tickets: [
      {
        id: 1,
        ticket_no: 'TK20230501001',
        title: '核心交换机A区链路异常',
        priority: 'urgent',
        created_at: '2023-05-01 10:25:36',
      },
      {
        id: 2,
        ticket_no: 'TK20230502003',
        title: '防火墙策略更新申请',
        priority: 'high',
        created_at: '2023-05-02 14:38:21',
      },
      {
        id: 3,
        ticket_no: 'TK20230503005',
        title: '服务器扩容申请',
        priority: 'medium',
        created_at: '2023-05-03 09:12:45',
      },
      {
        id: 4,
        ticket_no: 'TK20230504008',
        title: '网络设备巡检',
        priority: 'low',
        created_at: '2023-05-04 11:05:18',
      },
      {
        id: 5,
        ticket_no: 'TK20230505012',
        title: 'VPN连接异常',
        priority: 'high',
        created_at: '2023-05-05 16:42:33',
      },
    ],
  }
}

onMounted(() => {
  // 获取仪表盘数据
  fetchDashboardData()

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  // 移除事件监听
  window.removeEventListener('resize', handleResize)

  // 销毁图表实例
  Object.values(charts.value).forEach(chart => {
    chart?.dispose()
  })
})
</script>

<style scoped>
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
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
  margin-right: 12px;
}

.overview-content {
  flex: 1;
}

.overview-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.overview-value {
  font-size: 24px;
  font-weight: bold;
}

.chart-container {
  width: 100%;
  height: 240px;
}

.chart {
  width: 100%;
  height: 100%;
}
</style> 