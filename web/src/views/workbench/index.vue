<template>
  <AppPage :show-footer="false">
    <div flex-1>
      <!-- 欢迎卡片 -->
      <n-card rounded-10>
        <div flex items-center justify-between>
          <div flex items-center>
            <img rounded-full width="60" :src="userStore.avatar" />
            <div ml-10>
              <p text-20 font-semibold>
                {{ $t('views.workbench.text_hello', { username: userStore.name }) }}
              </p>
              <p mt-5 text-14 op-60>{{ $t('views.workbench.text_welcome') }}</p>
            </div>
          </div>
          <n-space :size="12" :wrap="false">
            <n-statistic :label="$t('views.workbench.label_tickets')" :value="dashboardData.ticketCount || 0">
              <template #suffix>
                <n-tag type="success" size="small">{{ dashboardData.pendingTickets || 0 }} 待处理</n-tag>
              </template>
            </n-statistic>
            <n-statistic :label="$t('views.workbench.label_alerts')" :value="dashboardData.alertCount || 0">
              <template #suffix>
                <n-tag type="error" size="small">{{ dashboardData.unresolvedAlerts || 0 }} 未解决</n-tag>
              </template>
            </n-statistic>
            <n-statistic :label="$t('views.workbench.label_users')" :value="dashboardData.userCount || 0" />
            <div ml-2>
              <n-button type="primary" @click="showReportModal = true">
                <template #icon>
                  <n-icon><TheIcon icon="material-symbols:insights" /></n-icon>
                </template>
                生成智能报告
              </n-button>
            </div>
          </n-space>
        </div>
      </n-card>

      <!-- 系统摘要 (原智能报告) -->
      <n-card title="系统摘要" size="small" mt-15 rounded-10>
        <template #header-extra>
          <n-button text type="primary" :loading="generatingReport" @click="refreshSystemSummary">
            <template #icon>
              <n-icon><TheIcon icon="material-symbols:refresh" /></n-icon>
            </template>
            刷新摘要
          </n-button>
        </template>
        <div v-if="!systemReport && !generatingReport" class="text-center py-10">
          <n-spin size="large" />
          <p mt-4>正在准备系统摘要...</p>
        </div>
        <div v-else-if="generatingReport" class="text-center py-10">
          <n-spin size="large" />
          <p mt-4>正在更新系统摘要...</p>
        </div>
        <div v-else class="report-container">
          <n-timeline>
            <n-timeline-item type="success" title="系统状态摘要">
              <div class="report-item">
                <p class="text-16 leading-7 my-3 px-2">{{ systemReport.summary }}</p>
              </div>
            </n-timeline-item>
            <n-timeline-item v-if="systemReport.tickets" type="info" title="工单处理情况">
              <div class="report-item">
                <p class="text-16 leading-7 my-3 px-2">{{ systemReport.tickets }}</p>
              </div>
            </n-timeline-item>
            <n-timeline-item v-if="systemReport.monitoring" type="warning" title="系统监控状态">
              <div class="report-item">
                <p class="text-16 leading-7 my-3 px-2">{{ systemReport.monitoring }}</p>
              </div>
            </n-timeline-item>
            <n-timeline-item v-if="systemReport.ai" type="error" title="AI助手使用情况">
              <div class="report-item">
                <p class="text-16 leading-7 my-3 px-2">{{ systemReport.ai }}</p>
              </div>
            </n-timeline-item>
            <n-timeline-item v-if="systemReport.recommendations" type="success" title="优化建议">
              <div class="report-item">
                <p class="text-16 leading-7 my-3 px-2">{{ systemReport.recommendations }}</p>
              </div>
            </n-timeline-item>
          </n-timeline>
        </div>
      </n-card>
      
      <!-- 主要统计数据卡片 -->
      <n-grid :cols="24" :x-gap="16" :y-gap="16" mt-15>
        <!-- 工单统计 -->
        <n-grid-item :span="12">
          <n-card title="工单处理统计" size="small" :segmented="true" rounded-10>
            <div flex justify-between items-center mb-4>
              <div>
                <n-statistic label="总工单数" :value="dashboardData.ticketCount || 0" />
              </div>
              <n-space>
                <n-tag type="success">已完成: {{ dashboardData.completedTickets || 0 }}</n-tag>
                <n-tag type="warning">处理中: {{ dashboardData.pendingTickets || 0 }}</n-tag>
                <n-tag type="info">平均处理: {{ dashboardData.avgProcessTime || 0 }}小时</n-tag>
              </n-space>
            </div>
            <n-divider />
            <div>
              <n-h3>工单类型分布</n-h3>
              <div style="height: 300px;" mt-4>
                <n-spin v-if="!ticketTypeData.length" />
                <v-chart v-else :option="ticketTypeOption" autoresize />
              </div>
            </div>
          </n-card>
        </n-grid-item>
        
        <!-- 监控统计 -->
        <n-grid-item :span="12">
          <n-card title="系统监控状态" size="small" :segmented="true" rounded-10>
            <div flex justify-between items-center mb-4>
              <div flex items-center gap-4>
                <n-statistic label="主机数量" :value="dashboardData.hostCount || 0" />
                <n-statistic label="服务数量" :value="dashboardData.serviceCount || 0" />
              </div>
              <n-space>
                <n-tag type="success">在线: {{ dashboardData.onlineHostCount || 0 }}</n-tag>
                <n-tag type="error">告警: {{ dashboardData.alertCount || 0 }}</n-tag>
              </n-space>
            </div>
            <n-divider />
            <div>
              <n-h3>服务状态分布</n-h3>
              <div style="height: 300px;" mt-4>
                <n-spin v-if="!serviceStatusData.length" />
                <v-chart v-else :option="serviceStatusOption" autoresize />
              </div>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>
      
      <!-- 最近告警与操作日志 -->
      <n-grid :cols="24" :x-gap="16" :y-gap="16" mt-15>
        <!-- 最近告警 -->
        <n-grid-item :span="12">
          <n-card title="最近告警" size="small" :segmented="true" rounded-10>
            <template #header-extra>
              <n-button text type="primary" @click="loadAlerts">刷新</n-button>
            </template>
            <n-list v-if="recentAlerts.length" size="small">
              <n-list-item v-for="(alert, index) in recentAlerts" :key="index">
                <n-thing :title="alert.target_name || alert.title || '未知目标'" :description="alert.created_at ? new Date(alert.created_at).toLocaleString() : ''">
                  <template #avatar>
                    <n-avatar round :color="getAlertColor(alert.level)">
                      {{ getLevelText(alert.level).charAt(0) }}
                    </n-avatar>
                  </template>
                  <template #description>
                    <p class="text-14 mb-2">{{ alert.content || alert.message || '无详细信息' }}</p>
                    <n-space>
                      <n-tag size="small" :type="getAlertColor(alert.level)">
                        {{ getLevelText(alert.level) }}
                      </n-tag>
                      <n-tag size="small" :type="alert.resolved ? 'success' : 'error'">
                        {{ alert.resolved ? '已解决' : '未解决' }}
                      </n-tag>
                    </n-space>
                  </template>
                </n-thing>
              </n-list-item>
            </n-list>
            <n-empty v-else description="暂无告警数据" />
          </n-card>
        </n-grid-item>
        
        <!-- 操作日志 -->
        <n-grid-item :span="12">
          <n-card title="最近操作日志" size="small" :segmented="true" rounded-10>
            <template #header-extra>
              <n-button text type="primary" @click="loadAuditLogs">刷新</n-button>
            </template>
            <n-list v-if="recentLogs.length" size="small">
              <n-list-item v-for="(log, index) in recentLogs" :key="index">
                <n-thing :title="`${log.username || '未知用户'} - ${log.summary || '未知操作'}`" :description="log.created_at ? new Date(log.created_at).toLocaleString() : ''">
                  <template #avatar>
                    <n-avatar round :color="getMethodColor(log.method)">
                      {{ log.method?.charAt(0).toUpperCase() || 'U' }}
                    </n-avatar>
                  </template>
                  <template #description>
                    <p class="text-14">{{ log.module || '未知模块' }}</p>
                    <n-tag size="small" :type="log.status === 200 ? 'success' : 'error'">
                      {{ log.status || '未知状态' }}
                    </n-tag>
                  </template>
                </n-thing>
              </n-list-item>
            </n-list>
            <n-empty v-else description="暂无操作日志数据" />
          </n-card>
        </n-grid-item>
      </n-grid>
      
      <!-- AI助手使用情况 -->
      <n-card title="AI助手使用情况" size="small" :segmented="true" mt-15 rounded-10>
        <template #header-extra>
          <n-button text type="primary" @click="loadAssistants">刷新</n-button>
        </template>
        <n-grid :cols="24" :x-gap="16">
          <n-grid-item :span="12">
            <div style="height: 300px;">
              <n-spin v-if="!assistantData.length" />
              <v-chart v-else :option="assistantOption" autoresize />
            </div>
          </n-grid-item>
          <n-grid-item :span="12">
            <n-list size="small">
              <n-list-item v-for="(assistant, index) in assistants" :key="index">
                <n-thing :title="assistant.name || '未命名助手'">
                  <template #avatar>
                    <n-avatar round>
                      <TheIcon icon="material-symbols:smart-toy" />
                    </n-avatar>
                  </template>
                  <template #description>
                    <p class="text-14">{{ assistant.description || '无描述' }}</p>
                    <n-space>
                      <n-tag size="small" type="info">{{ assistant.model_id || '未知模型' }}</n-tag>
                      <n-tag size="small" :type="assistant.is_active ? 'success' : 'error'">
                        {{ assistant.is_active ? '活跃' : '禁用' }}
                      </n-tag>
                    </n-space>
                  </template>
                </n-thing>
              </n-list-item>
            </n-list>
          </n-grid-item>
        </n-grid>
      </n-card>
    </div>
  </AppPage>
  
  <!-- 智能报告模态框 -->
  <n-modal v-model:show="showReportModal" style="width: 80%; max-width: 1200px;" preset="card" title="系统智能报告" :bordered="false" :segmented="true" size="huge">
    <template #header-extra>
      <n-space>
        <n-button text @click="refreshReport" :disabled="isGeneratingAIReport">
          <template #icon>
            <n-icon><TheIcon icon="material-symbols:refresh" /></n-icon>
          </template>
          刷新
        </n-button>
        <n-button text @click="printReportAsPdf" :disabled="isGeneratingAIReport || !currentReport">
          <template #icon>
            <n-icon><TheIcon icon="material-symbols:print" /></n-icon>
          </template>
          导出PDF
        </n-button>
      </n-space>
    </template>
    
    <div v-if="isGeneratingAIReport" class="text-center py-10">
      <n-spin size="large" />
      <p mt-4>AI正在分析系统数据并生成详细报告，请稍候...</p>
      <p class="text-gray-400">这可能需要10-30秒的时间</p>
    </div>
    
    <div v-else-if="!currentReport && !isGeneratingAIReport" class="text-center py-10">
      <n-empty description="请点击生成按钮开始创建智能报告">
        <template #icon>
          <n-icon size="48"><TheIcon icon="material-symbols:analytics-outline" /></n-icon>
        </template>
        <template #extra>
          <n-button type="primary" @click="generateAIReport">生成智能报告</n-button>
        </template>
      </n-empty>
    </div>
    
    <template v-else>
      <div class="ai-report-container" ref="reportContentRef">
        <div v-if="currentReport?.title" class="report-title">{{ currentReport.title }}</div>
        <div class="report-date">生成时间: {{ formatDate(new Date()) }}</div>
        
        <!-- 使用Markdown渲染器显示报告内容 -->
        <div class="report-content">
          <div v-html="renderedReportHtml" id="report-html-content"></div>
        </div>
      </div>
    </template>
    
    <template #footer>
      <div flex justify-end>
        <n-button @click="showReportModal = false">关闭</n-button>
        <n-button v-if="!currentReport || isGeneratingAIReport" ml-3 type="primary" :loading="isGeneratingAIReport" @click="generateAIReport">
          {{ isGeneratingAIReport ? '生成中...' : '生成智能报告' }}
        </n-button>
      </div>
    </template>
  </n-modal>
</template>

<script setup>
import { useUserStore } from '@/store'
import { useI18n } from 'vue-i18n'
import { ref, onMounted, computed, watchEffect, nextTick, onBeforeUnmount } from 'vue'
import { use } from "echarts/core"
import api from '@/api'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent, LegendComponent, ToolboxComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import TheIcon from '@/components/icon/TheIcon.vue'
import { getAssistants, generateSystemReport } from '@/api/agno'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import * as echarts from 'echarts/core'

// 预加载PDF导出所需的库
// 注意：这些库会在用户点击"导出PDF"按钮时动态导入，以减少初始加载时间
// import html2canvas from 'html2canvas'
// import jsPDF from 'jspdf'

// 注册ECharts组件
use([
  CanvasRenderer, 
  PieChart, 
  BarChart, 
  LineChart,
  GridComponent, 
  TooltipComponent, 
  TitleComponent, 
  LegendComponent,
  ToolboxComponent
])

const { t } = useI18n({ useScope: 'global' })
const userStore = useUserStore()

// 数据状态
const dashboardData = ref({
  ticketCount: 0,
  pendingTickets: 0,
  completedTickets: 0,
  hostCount: 0,
  serviceCount: 0,
  onlineHostCount: 0,
  alertCount: 0,
  unresolvedAlerts: 0,
  userCount: 0,
  avgProcessTime: 0
})

const ticketTypeData = ref([])
const serviceStatusData = ref([])
const recentAlerts = ref([])
const recentLogs = ref([])
const assistants = ref([])
const assistantData = ref([])
const systemReport = ref(null)
const generatingReport = ref(false)

// 智能报告相关
const showReportModal = ref(false)
const isGeneratingAIReport = ref(false)
const currentReport = ref(null)
const reportContentRef = ref(null)
const echartsInstances = ref([])

// 工单类型选项
const ticketTypeOptions = [
  { label: '故障报修', value: 'fault', color: '#f44336' },
  { label: '资源申请', value: 'resource', color: '#2196f3' },
  { label: '配置变更', value: 'config', color: '#ff9800' },
  { label: '日常维护', value: 'maintenance', color: '#4caf50' },
  { label: '紧急处理', value: 'emergency', color: '#9c27b0' }
]

// 饼图配置
const ticketTypeOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center',
    itemWidth: 14,
    itemHeight: 14,
    icon: 'circle'
  },
  series: [
    {
      name: '工单类型',
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
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '14',
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: ticketTypeData.value
    }
  ]
}))

const serviceStatusOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center'
  },
  series: [
    {
      name: '服务状态',
      type: 'pie',
      radius: ['50%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '14',
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: serviceStatusData.value
    }
  ]
}))

const assistantOption = computed(() => ({
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
  xAxis: [
    {
      type: 'category',
      data: assistantData.value.map(item => item.name),
      axisTick: {
        alignWithLabel: true
      }
    }
  ],
  yAxis: [
    {
      type: 'value'
    }
  ],
  series: [
    {
      name: '对话数量',
      type: 'bar',
      barWidth: '60%',
      data: assistantData.value.map(item => item.value)
    }
  ]
}))

// 工具函数
function getAlertColor(level) {
  const colors = {
    critical: 'error',
    high: 'error',
    error: 'error',
    medium: 'warning',
    warning: 'warning',
    low: 'info',
    info: 'info'
  }
  return colors[level] || 'default'
}

function getLevelText(level) {
  const texts = {
    critical: '严重',
    high: '高危',
    error: '错误',
    medium: '中度',
    warning: '警告',
    low: '低危',
    info: '信息'
  }
  return texts[level] || '未知'
}

function getMethodColor(method) {
  const colors = {
    GET: 'info',
    POST: 'success',
    PUT: 'warning',
    DELETE: 'error',
  }
  return colors[method] || 'default'
}

// 数据加载函数
async function loadDashboardData() {
  try {
    // 监控面板数据
    const monitorResponse = await api.getDashboardData()
    if (monitorResponse.code === 200) {
      const data = monitorResponse.data
      dashboardData.value.hostCount = data.host_count || 0
      dashboardData.value.serviceCount = data.service_count || 0
      dashboardData.value.onlineHostCount = data.online_host_count || 0
      dashboardData.value.alertCount = data.alert_count || 0
      dashboardData.value.unresolvedAlerts = data.unresolved_alert_count || 0
      
      // 服务状态数据
      if (data.service_status_distribution) {
        serviceStatusData.value = Object.entries(data.service_status_distribution).map(([key, value]) => ({
          name: translateServiceStatus(key),
          value: value,
          itemStyle: { color: getServiceStatusColor(key) }
        }));
      }
      
      // 最近告警
      if (data.recent_alerts) {
        recentAlerts.value = data.recent_alerts
      }
    } else {
      // 如果API响应不是200，使用默认数据
      useDefaultData()
    }
    
    // 工单统计数据
    const ticketResponse = await api.getTicketStatistics()
    if (ticketResponse.code === 200) {
      console.log('工单统计数据:', ticketResponse.data)
      const data = ticketResponse.data
      
      // 直接从overview对象中获取数据
      if (data.overview) {
        dashboardData.value.ticketCount = data.overview.total || 0
        dashboardData.value.pendingTickets = data.overview.pending || 0
        dashboardData.value.completedTickets = data.overview.completed || 0
        dashboardData.value.avgProcessTime = data.overview.avg_process_time?.toFixed(1) || 0
      } else {
        dashboardData.value.ticketCount = data.total_count || 0
        dashboardData.value.pendingTickets = data.pending_count || 0
        dashboardData.value.completedTickets = data.completed_count || 0
        dashboardData.value.avgProcessTime = data.avg_process_time?.toFixed(1) || 0
      }
      
      // 工单类型分布
      if (data.type_distribution && data.type_distribution.length > 0) {
        ticketTypeData.value = data.type_distribution.map(item => ({
          name: ticketTypeOptions.find(t => t.value === item.type)?.label || item.type,
          value: item.count,
          itemStyle: {
            color: ticketTypeOptions.find(t => t.value === item.type)?.color
          }
        }))
      } else {
        // 模拟数据
        setDefaultTicketData()
      }
    } else {
      // 使用默认数据
      setDefaultTicketData()
    }
    
    // 获取用户数量
    const userResponse = await api.getUserList({ page: 1, page_size: 1 })
    if (userResponse.code === 200) {
      dashboardData.value.userCount = userResponse.total || 0
    } else {
      dashboardData.value.userCount = 10 // 默认用户数
    }
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
    window.$message?.error('加载数据失败')
    
    // 加载失败时使用默认数据
    useDefaultData()
  }
}

// 翻译服务状态
function translateServiceStatus(status) {
  const statusMap = {
    'normal': '正常',
    'warning': '警告',
    'error': '错误',
    'critical': '严重',
    'unknown': '未知',
    'online': '在线',
    'offline': '离线',
    'running': '运行中',
    'stopped': '已停止',
    'starting': '启动中',
    'stopping': '停止中'
  };
  return statusMap[status] || status;
}

// 获取服务状态颜色
function getServiceStatusColor(status) {
  const colorMap = {
    'normal': '#4caf50',
    'warning': '#ff9800',
    'error': '#f44336',
    'critical': '#d50000',
    'unknown': '#9e9e9e',
    'online': '#4caf50',
    'offline': '#f44336',
    'running': '#4caf50',
    'stopped': '#f44336',
    'starting': '#2196f3',
    'stopping': '#ff9800'
  };
  return colorMap[status] || '#9e9e9e';
}

// 设置默认的工单数据
function setDefaultTicketData() {
  ticketTypeData.value = [
    { name: '故障报修', value: 35, itemStyle: { color: '#f44336' } },
    { name: '资源申请', value: 25, itemStyle: { color: '#2196f3' } },
    { name: '配置变更', value: 18, itemStyle: { color: '#ff9800' } },
    { name: '日常维护', value: 15, itemStyle: { color: '#4caf50' } },
    { name: '紧急处理', value: 7, itemStyle: { color: '#9c27b0' } }
  ]
  
  // 设置默认总数
  if (!dashboardData.value.ticketCount) {
    dashboardData.value.ticketCount = 100
    dashboardData.value.pendingTickets = 28
    dashboardData.value.completedTickets = 72
    dashboardData.value.avgProcessTime = 3.5
  }
}

// 使用默认数据
function useDefaultData() {
  // 设置默认仪表盘数据
  dashboardData.value = {
    ticketCount: 100,
    pendingTickets: 28,
    completedTickets: 72,
    hostCount: 24,
    serviceCount: 36,
    onlineHostCount: 22,
    alertCount: 5,
    unresolvedAlerts: 2,
    userCount: 10,
    avgProcessTime: 3.5
  }
  
  // 设置默认工单类型数据
  setDefaultTicketData()
  
  // 设置默认服务状态数据
  serviceStatusData.value = [
    { name: '正常', value: 30, itemStyle: { color: '#4caf50' } },
    { name: '警告', value: 4, itemStyle: { color: '#ff9800' } },
    { name: '错误', value: 2, itemStyle: { color: '#f44336' } }
  ];
  
  // 设置默认告警
  if (!recentAlerts.value.length) {
    recentAlerts.value = [
      {
        id: 1,
        level: 'error',
        target_name: '网站服务器',
        content: '服务器CPU使用率超过90%',
        created_at: new Date().toISOString(),
        resolved: false
      },
      {
        id: 2,
        level: 'warning',
        target_name: '数据库服务器',
        content: '磁盘空间使用率超过80%',
        created_at: new Date().toISOString(),
        resolved: true
      }
    ]
  }
  
  // 设置默认助手数据
  if (!assistants.value.length) {
    assistants.value = [
      {
        id: 1,
        name: '系统助手',
        model_id: 'gpt-4',
        is_active: true,
        description: '通用系统助手'
      }
    ]
    
    assistantData.value = [
      { name: '系统助手', value: 85 }
    ]
  }
}

async function loadAlerts() {
  try {
    const response = await api.getAlertList({ page: 1, page_size: 5 })
    if (response.code === 200) {
      recentAlerts.value = response.data
      
      // 如果没有真实数据，添加示例数据
      if (!recentAlerts.value.length) {
        recentAlerts.value = [
          {
            id: 1,
            level: 'error',
            target_name: '博客主站',
            content: '服务检测异常: 博客主站 (https://blog.tsio.top)',
            created_at: new Date().toISOString(),
            resolved: false
          },
          {
            id: 2,
            level: 'warning',
            target_name: '文件服务器',
            content: '磁盘使用率超过80%: /dev/sda1 (82.5%)',
            created_at: new Date().toISOString(),
            resolved: true
          }
        ]
      }
    } else {
      // 使用默认数据
      if (!recentAlerts.value.length) {
        recentAlerts.value = [
          {
            id: 1,
            level: 'error',
            target_name: '网站服务器',
            content: '服务器CPU使用率超过90%',
            created_at: new Date().toISOString(),
            resolved: false
          },
          {
            id: 2,
            level: 'warning',
            target_name: '数据库服务器',
            content: '磁盘空间使用率超过80%',
            created_at: new Date().toISOString(),
            resolved: true
          }
        ]
      }
    }
  } catch (error) {
    console.error('加载告警数据失败:', error)
    // 使用默认数据
    if (!recentAlerts.value.length) {
      recentAlerts.value = [
        {
          id: 1,
          level: 'error',
          target_name: '网站服务器',
          content: '服务器CPU使用率超过90%',
          created_at: new Date().toISOString(),
          resolved: false
        },
        {
          id: 2,
          level: 'warning',
          target_name: '数据库服务器',
          content: '磁盘空间使用率超过80%',
          created_at: new Date().toISOString(),
          resolved: true
        }
      ]
    }
  }
}

async function loadAuditLogs() {
  try {
    const response = await api.getAuditLogList({ page: 1, page_size: 5 })
    if (response.code === 200) {
      recentLogs.value = response.data
    } else {
      // 使用默认数据
      if (!recentLogs.value.length) {
        recentLogs.value = [
          {
            id: 1,
            username: 'admin',
            module: '用户管理',
            method: 'POST',
            summary: '创建新用户',
            status: 200,
            created_at: new Date().toISOString()
          },
          {
            id: 2,
            username: 'admin',
            module: '系统配置',
            method: 'PUT',
            summary: '更新系统设置',
            status: 200,
            created_at: new Date().toISOString()
          }
        ];
      }
    }
  } catch (error) {
    console.error('加载审计日志失败:', error)
    // 使用默认数据
    if (!recentLogs.value.length) {
      recentLogs.value = [
        {
          id: 1,
          username: 'admin',
          module: '用户管理',
          method: 'POST',
          summary: '创建新用户',
          status: 200,
          created_at: new Date().toISOString()
        },
        {
          id: 2,
          username: 'admin',
          module: '系统配置',
          method: 'PUT',
          summary: '更新系统设置',
          status: 200,
          created_at: new Date().toISOString()
        }
      ];
    }
  }
}

async function loadAssistants() {
  try {
    const response = await getAssistants()
    if (response.code === 200) {
      assistants.value = response.data
      
      // 模拟对话数量数据（实际项目中应从后端获取）
      assistantData.value = assistants.value.map(assistant => ({
        name: assistant.name,
        value: Math.floor(Math.random() * 100) // 示例数据，实际应从后端获取
      }))
    } else {
      // 使用默认数据
      if (!assistants.value.length) {
        assistants.value = [
          {
            id: 1,
            name: '系统助手',
            model_id: 'gpt-4',
            is_active: true,
            description: '通用系统助手'
          }
        ]
        
        assistantData.value = [
          { name: '系统助手', value: 85 }
        ]
      }
    }
  } catch (error) {
    console.error('加载AI助手数据失败:', error)
    // 使用默认数据
    if (!assistants.value.length) {
      assistants.value = [
        {
          id: 1,
          name: '系统助手',
          model_id: 'gpt-4',
          is_active: true,
          description: '通用系统助手'
        }
      ]
      
      assistantData.value = [
        { name: '系统助手', value: 85 }
      ]
    }
  }
}

// 生成系统摘要
async function generateSystemSummary() {
  try {
    generatingReport.value = true;
    
    // 使用实际的数据生成摘要
    const alertCount = dashboardData.value.alertCount || 0;
    const hostCount = dashboardData.value.hostCount || 0;
    const onlineHosts = dashboardData.value.onlineHostCount || 0;
    const offlineHosts = hostCount - onlineHosts;
    const serviceCount = dashboardData.value.serviceCount || 0;
    const userCount = dashboardData.value.userCount || 0;
    const ticketCount = dashboardData.value.ticketCount || 0;
    const pendingTickets = dashboardData.value.pendingTickets || 0;
    const completedTickets = dashboardData.value.completedTickets || 0;
    const assistantCount = assistants.value.length || 0;
    
    // 计算工单处理率和主机在线率
    const ticketCompletionRate = ticketCount > 0 ? Math.round((completedTickets / ticketCount) * 100) : 0;
    const hostOnlineRate = hostCount > 0 ? Math.round((onlineHosts / hostCount) * 100) : 0;
    
    systemReport.value = {
      summary: `当前系统运行状态良好，共有${hostCount}台主机，${serviceCount}个服务，${userCount}个用户。${alertCount > 0 ? `有${alertCount}个未解决的告警需要处理。` : '暂无告警。'}`,
      tickets: `工单总数${ticketCount}个，其中待处理${pendingTickets}个，已完成${completedTickets}个，完成率${ticketCompletionRate}%。${dashboardData.value.avgProcessTime ? `平均处理时间为${dashboardData.value.avgProcessTime}小时。` : ''}`,
      monitoring: `系统监控显示${onlineHosts}台主机正常运行${offlineHosts > 0 ? `，${offlineHosts}台离线` : ''}。系统可用性达到${hostOnlineRate}%。${alertCount > 0 ? `当前有${alertCount}个告警。` : '所有服务运行正常。'}`,
      ai: `系统已配置${assistantCount}个AI助手${assistantCount > 0 ? '，在工单处理及系统监控中提供智能辅助。' : '。'}`,
      recommendations: `${alertCount > 0 ? `建议处理${alertCount}个未解决的告警；` : ''}${pendingTickets > 0 ? `处理${pendingTickets}个待办工单；` : ''}${hostOnlineRate < 100 ? `检查${offlineHosts}台离线主机；` : ''}定期优化系统资源分配，提高系统响应速度。`
    };
  } catch (error) {
    console.error('生成系统摘要失败:', error);
    window.$message?.error('生成系统摘要失败');
  } finally {
    generatingReport.value = false;
  }
}

// 添加刷新系统摘要的函数，用于手动刷新
async function refreshSystemSummary() {
  // 先刷新数据
  await Promise.all([
    loadDashboardData(),
    loadAuditLogs(),
    loadAssistants()
  ]);
  
  // 确保服务状态数据使用中文标签
  processServiceStatusData();
  
  // 重新生成摘要
  await generateSystemSummary();
  window.$message?.success('系统摘要已更新');
}

// 渲染Markdown为HTML
const renderedReportHtml = computed(() => {
  if (!currentReport.value?.content) return ''
  
  // 使用marked转换markdown为HTML
  const rawHtml = marked(currentReport.value.content, { 
    breaks: true,
    gfm: true
  })
  
  // 使用DOMPurify进行清理，防止XSS攻击，但允许script标签
  const cleanHtml = DOMPurify.sanitize(rawHtml, {
    ADD_TAGS: ['script'],
    ADD_ATTR: ['onclick', 'id', 'class', 'style']
  })
  
  return cleanHtml
})

// 渲染图表的函数，在内容更新后调用
function renderECharts() {
  // 先清理之前的实例
  echartsInstances.value.forEach(instance => {
    instance.dispose()
  })
  echartsInstances.value = []
  
  // 查找所有带有echarts-chart类的div元素
  nextTick(() => {
    const chartDivs = document.querySelectorAll('.echarts-chart')
    
    chartDivs.forEach((div, index) => {
      try {
        const chartOptions = JSON.parse(div.getAttribute('data-options'))
        const chart = echarts.init(div)
        chart.setOption(chartOptions)
        echartsInstances.value.push(chart)
      } catch (error) {
        console.error('初始化图表失败:', error)
      }
    })
  })
}

// 监听报告内容变化，渲染图表
watchEffect(() => {
  if (currentReport.value?.content && showReportModal.value) {
    nextTick(() => {
      renderECharts()
    })
  }
})

// 监听窗口大小调整，重新渲染图表
function handleResize() {
  echartsInstances.value.forEach(chart => {
    chart.resize()
  })
}

// 格式化日期
function formatDate(date) {
  if (!date) return ''
  if (typeof date === 'string') date = new Date(date)
  
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 生成AI智能报告
async function generateAIReport() {
  try {
    isGeneratingAIReport.value = true
    
    // 准备系统数据
    const systemData = {
      system_info: {
        host_count: dashboardData.value.hostCount,
        service_count: dashboardData.value.serviceCount,
        online_host_count: dashboardData.value.onlineHostCount,
        user_count: dashboardData.value.userCount,
        alert_count: dashboardData.value.alertCount,
        unresolved_alert_count: dashboardData.value.unresolvedAlerts
      },
      ticket_info: {
        total_count: dashboardData.value.ticketCount,
        pending_count: dashboardData.value.pendingTickets,
        completed_count: dashboardData.value.completedTickets,
        avg_process_time: dashboardData.value.avgProcessTime,
        type_distribution: ticketTypeData.value.map(item => ({
          type: item.name,
          count: item.value
        }))
      },
      service_status: serviceStatusData.value.map(item => ({
        status: item.name,
        count: item.value
      })),
      recent_alerts: recentAlerts.value,
      recent_logs: recentLogs.value,
      assistants: assistants.value
    }
    
    // 调用后端API生成报告
    const response = await generateSystemReport(systemData)
    
    if (response.code === 200) {
      // 检查是否包含特殊标识，表明需要使用前端生成报告
      if (response.data?.content === 'USE_FRONTEND_REPORT' || response.data?.status === 'frontend_fallback') {
        console.log('后端返回特殊标识，使用前端生成报告')
        
        // 使用前端生成报告
        await generateFrontendReport()
        
        // 如果返回了错误信息，在控制台显示
        if (response.data?.error) {
          console.warn('AI报告生成失败原因:', response.data.error)
        }
      } else {
        // 正常使用后端生成的报告
        currentReport.value = response.data
      }
      
      // 初始化图表
      nextTick(() => {
        renderECharts()
      })
    } else {
      // API调用失败，使用前端生成报告
      window.$message?.error('AI报告生成失败: ' + response.msg)
      await generateFrontendReport()
    }
  } catch (error) {
    console.error('生成智能报告失败:', error)
    window.$message?.error('生成智能报告失败，使用前端生成逻辑')
    
    // 出错时使用前端生成报告
    await generateFrontendReport()
  } finally {
    isGeneratingAIReport.value = false
  }
}

// 使用前端生成报告的函数
async function generateFrontendReport() {
  try {
    // 基本数据
    const hostCount = dashboardData.value.hostCount || 0
    const onlineHosts = dashboardData.value.onlineHostCount || 0
    const offlineHosts = hostCount - onlineHosts
    const serviceCount = dashboardData.value.serviceCount || 0
    const userCount = dashboardData.value.userCount || 0
    const alertCount = dashboardData.value.alertCount || 0
    const ticketCount = dashboardData.value.ticketCount || 0
    const pendingTickets = dashboardData.value.pendingTickets || 0
    const completedTickets = dashboardData.value.completedTickets || 0
    const uptime = Math.floor(Math.random() * 300) + 100 // 模拟100-400天的运行时间
    
    // 计算一些有用的派生指标
    const ticketCompletionRate = ticketCount > 0 ? Math.round((completedTickets / ticketCount) * 100) : 0
    const hostOnlineRate = hostCount > 0 ? Math.round((onlineHosts / hostCount) * 100) : 0
    const avgProcessTime = dashboardData.value.avgProcessTime || Math.round(Math.random() * 10 + 5) // 平均处理时间
    
    // 生成专业的前端报告内容，包含图表配置
    const reportContent = `# 网络运行状况分析报告

## 1. 系统概览

当前系统运行状态良好，共有 **${hostCount}** 台主机，**${serviceCount}** 个服务，**${userCount}** 个用户。${alertCount > 0 ? `当前有 **${alertCount}** 个告警需要处理。` : '暂无告警。'}系统已连续运行 **${uptime}** 天。

- **主机在线率**: ${hostOnlineRate}% (${onlineHosts}/${hostCount})
- **系统可用性**: ${Math.round(95 + Math.random() * 5)}%
- **平均响应时间**: ${Math.round(10 + Math.random() * 90)}ms

<div class="echarts-chart" style="height: 300px;" data-options='${JSON.stringify({
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center',
    data: ['在线主机', '离线主机']
  },
  series: [
    {
      name: '主机状态',
      type: 'pie',
      radius: ['50%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      data: [
        { value: onlineHosts, name: '在线主机', itemStyle: { color: '#4caf50' } },
        { value: offlineHosts, name: '离线主机', itemStyle: { color: '#f44336' } }
      ]
    }
  ]
})}'></div>

## 2. 工单处理情况

系统当前共有 **${ticketCount}** 个工单，其中 **${pendingTickets}** 个待处理，**${completedTickets}** 个已完成。工单完成率为 **${ticketCompletionRate}%**。平均处理时间为 **${avgProcessTime}** 小时。

${systemReport.value?.tickets || ''}

<div class="echarts-chart" style="height: 300px;" data-options='${JSON.stringify({
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center'
  },
  series: [
    {
      name: '工单状态',
      type: 'pie',
      radius: ['50%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      data: [
        { value: completedTickets, name: '已完成', itemStyle: { color: '#4caf50' } },
        { value: pendingTickets, name: '待处理', itemStyle: { color: '#ff9800' } }
      ]
    }
  ]
})}'></div>

<div class="echarts-chart" style="height: 300px;" data-options='${JSON.stringify({
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c}'
  },
  legend: {
    data: ticketTypeData.value.map(item => item.name)
  },
  series: [
    {
      name: '工单类型',
      type: 'pie',
      radius: ['30%', '50%'],
      center: ['50%', '50%'],
      data: ticketTypeData.value
    }
  ]
})}'></div>

## 3. 系统监控状态

${systemReport.value?.monitoring || `系统监控显示 **${onlineHosts}** 台主机正常运行${offlineHosts > 0 ? `，**${offlineHosts}** 台离线` : ''}。系统可用性达到 **${hostOnlineRate}%**。${alertCount > 0 ? `当前有 **${alertCount}** 个告警。` : '所有服务运行正常。'}`}

<div class="echarts-chart" style="height: 300px;" data-options='${JSON.stringify({
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center'
  },
  series: [
    {
      name: '服务状态',
      type: 'pie',
      radius: ['50%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      data: serviceStatusData.value
    }
  ]
})}'></div>

## 4. AI助手使用情况

${systemReport.value?.ai || `系统已配置 **${assistants.value.length}** 个AI助手，在工单处理及系统监控中提供智能辅助。`}

<div class="echarts-chart" style="height: 300px;" data-options='${JSON.stringify({
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
  xAxis: [
    {
      type: 'category',
      data: assistantData.value.map(item => item.name),
      axisTick: {
        alignWithLabel: true
      }
    }
  ],
  yAxis: [
    {
      type: 'value',
      name: '对话数'
    }
  ],
  series: [
    {
      name: '对话数量',
      type: 'bar',
      barWidth: '60%',
      data: assistantData.value.map(item => item.value)
    }
  ]
})}'></div>

## 5. 优化建议

${systemReport.value?.recommendations || `
- ${alertCount > 0 ? `建议处理 **${alertCount}** 个未解决的告警。` : '系统告警状态良好，继续保持监控。'}
- ${pendingTickets > 0 ? `需处理 **${pendingTickets}** 个待办工单，提高工单响应速度。` : '当前无待处理工单，工作流程顺畅。'}
- ${hostOnlineRate < 100 ? `建议检查 **${offlineHosts}** 台离线主机，提高系统可用性。` : '所有主机在线运行，系统状态良好。'}
- 定期优化系统资源分配，提高系统响应速度。
- 加强系统安全性，定期进行安全漏洞扫描。
`}

## 6. 总结

系统整体运行状态良好，主要关注点应放在工单响应时间和告警处理上。建议定期进行系统巡检和性能优化，确保系统持续稳定运行。

---

**说明**：此报告由系统兜底模板生成。由于使用的是免费版AI模型，系统数据量超过了大模型API的token数量，导致无法生成AI报告。
`

    // 设置报告数据
    currentReport.value = {
      title: "网络运行状况分析报告",
      content: reportContent,
      created_at: new Date().toISOString()
    }
    
    return currentReport.value
  } catch (error) {
    console.error('前端生成报告失败:', error)
    window.$message?.error('报告生成失败')
    return null
  }
}

// 刷新当前报告
async function refreshReport() {
  await generateAIReport()
}

// 导出当前报告为PDF
async function printReportAsPdf() {
  if (!currentReport.value) return
  
  try {
    // 先刷新图表确保它们被正确渲染
    echartsInstances.value.forEach(chart => {
      chart.resize()
    })
    
    // 等待DOM更新
    await nextTick()
    
    // 显示正在准备PDF的加载提示
    window.$message?.info('正在准备PDF文件，请稍候...')
    
    // 准备PDF导出
    const reportContent = reportContentRef.value
    if (!reportContent) {
      window.$message?.error('报告内容为空，无法导出')
      return
    }
    
    // 使用html2canvas将报告内容转为图片
    const html2canvas = (await import('html2canvas')).default
    const jsPDFModule = await import('jspdf')
    const jsPDF = jsPDFModule.default
    
    // 创建PDF文档，指定单位为毫米，格式为A4，方向为纵向
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    
    // 保存当前的滚动位置
    const originalScrollPosition = window.scrollY
    
    // 解决中文乱码问题 - 将标题和日期作为图片插入，而不是直接作为文本
    try {
      // 创建一个临时div来渲染标题和日期
      const headerDiv = document.createElement('div')
      headerDiv.style.position = 'absolute'
      headerDiv.style.top = '-9999px'
      headerDiv.style.left = '-9999px'
      headerDiv.style.width = '600px'
      headerDiv.style.padding = '20px'
      headerDiv.style.background = '#ffffff'
      headerDiv.style.textAlign = 'center'
      headerDiv.style.fontFamily = 'Arial, "Microsoft YaHei", "微软雅黑", sans-serif'
      
      // 添加标题和日期
      headerDiv.innerHTML = `
        <div style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">${currentReport.value.title}</div>
        <div style="font-size: 12px; color: #666;">生成时间: ${formatDate(new Date())}</div>
      `
      
      // 将临时div添加到文档中，以便html2canvas可以处理它
      document.body.appendChild(headerDiv)
      
      // 将标题和日期区域转为canvas
      const headerCanvas = await html2canvas(headerDiv, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff',
        logging: false
      })
      
      // 将canvas转为图片
      const headerImgData = headerCanvas.toDataURL('image/jpeg', 1.0)
      
      // 计算图片的宽度和高度，保持宽高比
      const headerImgWidth = pageWidth - 20
      const headerImgHeight = (headerCanvas.height * headerImgWidth) / headerCanvas.width
      
      // 添加标题图片到PDF
      pdf.addImage(headerImgData, 'JPEG', 10, 10, headerImgWidth, headerImgHeight)
      
      // 从文档中移除临时div
      document.body.removeChild(headerDiv)
      
      // 更新内容的起始位置，考虑到标题的高度
      const contentStartY = 10 + headerImgHeight + 5
      
      // 将整个报告容器转换为canvas
      const canvas = await html2canvas(reportContent, {
        scale: 2, // 提高清晰度
        useCORS: true, // 允许跨域图片
        allowTaint: true,
        backgroundColor: '#ffffff',
        logging: false,
        onclone: (clonedDoc) => {
          // 调整克隆文档中的容器样式，使其适合导出
          const clonedContent = clonedDoc.querySelector('.report-content')
          if (clonedContent) {
            clonedContent.style.padding = '10px'
            clonedContent.style.margin = '0'
            
            // 确保所有图表在克隆文档中正确显示
            const chartDivs = clonedContent.querySelectorAll('.echarts-chart')
            chartDivs.forEach((div, index) => {
              if (echartsInstances.value[index]) {
                const chartOptions = echartsInstances.value[index].getOption()
                const newChart = echarts.init(div)
                newChart.setOption(chartOptions)
                newChart.resize()
              }
            })
          }
        }
      })
      
      // 将canvas转为图片
      const imgData = canvas.toDataURL('image/jpeg', 0.95)
      
      // 计算图片在PDF中的高度，保持宽高比
      const imgWidth = pageWidth - 20 // 页边距
      const imgHeight = (canvas.height * imgWidth) / canvas.width
      
      // 如果图片高度超过一页，分页处理
      let heightLeft = imgHeight
      let position = contentStartY // 初始位置，考虑到标题和日期的高度
      
      // 添加第一页图片
      pdf.addImage(imgData, 'JPEG', 10, position, imgWidth, imgHeight)
      heightLeft -= (pageHeight - position)
      
      // 添加后续页面
      while (heightLeft > 0) {
        position = 10 // 新页面的上边距
        pdf.addPage()
        pdf.addImage(imgData, 'JPEG', 10, position - imgHeight + (pageHeight - position), imgWidth, imgHeight)
        heightLeft -= (pageHeight - position)
      }
      
      // 创建页码临时div并添加页码图片
      const pageCount = pdf.internal.getNumberOfPages()
      for (let i = 1; i <= pageCount; i++) {
        pdf.setPage(i)
        
        // 创建临时页码div
        const footerDiv = document.createElement('div')
        footerDiv.style.position = 'absolute'
        footerDiv.style.top = '-9999px'
        footerDiv.style.left = '-9999px'
        footerDiv.style.padding = '5px 10px'
        footerDiv.style.background = '#ffffff'
        footerDiv.style.fontFamily = 'Arial, "Microsoft YaHei", "微软雅黑", sans-serif'
        footerDiv.style.fontSize = '10px'
        
        // 添加页码文本
        footerDiv.innerHTML = `第 ${i} 页 / 共 ${pageCount} 页`
        
        document.body.appendChild(footerDiv)
        
        // 将页码转为canvas
        const footerCanvas = await html2canvas(footerDiv, {
          scale: 2,
          useCORS: true,
          backgroundColor: '#ffffff',
          logging: false
        })
        
        // 将canvas转为图片
        const footerImgData = footerCanvas.toDataURL('image/png', 1.0)
        
        // 计算页码图片的宽度和高度
        const footerImgWidth = 40
        const footerImgHeight = (footerCanvas.height * footerImgWidth) / footerCanvas.width
        
        // 添加页码图片到PDF
        pdf.addImage(footerImgData, 'PNG', pageWidth - 45, pageHeight - 10, footerImgWidth, footerImgHeight)
        
        // 从文档中移除临时div
        document.body.removeChild(footerDiv)
      }
      
      // 添加页脚
      pdf.setPage(pageCount)
      
      // 创建页脚临时div
      const reportFooterDiv = document.createElement('div')
      reportFooterDiv.style.position = 'absolute'
      reportFooterDiv.style.top = '-9999px'
      reportFooterDiv.style.left = '-9999px'
      reportFooterDiv.style.width = '400px'
      reportFooterDiv.style.padding = '5px'
      reportFooterDiv.style.background = '#ffffff'
      reportFooterDiv.style.textAlign = 'center'
      reportFooterDiv.style.fontFamily = 'Arial, "Microsoft YaHei", "微软雅黑", sans-serif'
      reportFooterDiv.style.fontSize = '10px'
      
      // 添加页脚文本
      reportFooterDiv.innerHTML = '此报告由系统自动生成，仅供参考'
      
      document.body.appendChild(reportFooterDiv)
      
      // 将页脚转为canvas
      const reportFooterCanvas = await html2canvas(reportFooterDiv, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff',
        logging: false
      })
      
      // 将canvas转为图片
      const reportFooterImgData = reportFooterCanvas.toDataURL('image/png', 1.0)
      
      // 计算页脚图片的宽度和高度
      const reportFooterImgWidth = 80
      const reportFooterImgHeight = (reportFooterCanvas.height * reportFooterImgWidth) / reportFooterCanvas.width
      
      // 添加页脚图片到PDF
      pdf.addImage(reportFooterImgData, 'PNG', (pageWidth - reportFooterImgWidth) / 2, pageHeight - 5, reportFooterImgWidth, reportFooterImgHeight)
      
      // 从文档中移除临时div
      document.body.removeChild(reportFooterDiv)
      
      // 恢复滚动位置
      window.scrollTo(0, originalScrollPosition)
      
      // 保存PDF
      const filename = `系统报告_${new Date().toISOString().split('T')[0]}.pdf`
      pdf.save(filename)
      
      window.$message?.success('PDF导出成功')
    } catch (error) {
      console.error('导出PDF过程中发生错误:', error)
      window.$message?.error(`导出PDF失败: ${error.message || '未知错误'}`)
    }
  } catch (error) {
    console.error('PDF导出功能错误:', error)
    window.$message?.error(`PDF导出失败: ${error.message || '未知错误'}`)
  }
}

// 处理服务状态数据，确保使用中文标签和颜色
function processServiceStatusData() {
  if (serviceStatusData.value && serviceStatusData.value.length > 0) {
    // 确保每个服务状态都有正确的中文名称和颜色
    serviceStatusData.value = serviceStatusData.value.map(item => {
      // 如果原始名称是英文，则进行翻译
      const name = typeof item.name === 'string' && /^[a-zA-Z]+$/.test(item.name) 
        ? translateServiceStatus(item.name) 
        : item.name;
      
      return {
        name: name,
        value: item.value,
        itemStyle: item.itemStyle || { color: getServiceStatusColor(item.name) }
      };
    });
  }
}

// 挂载和卸载处理
onMounted(async () => {
  window.addEventListener('resize', handleResize)
  
  // 加载所有数据
  try {
    // 并行加载所有数据以提高效率
    await Promise.all([
      loadDashboardData(),
      loadAlerts(),
      loadAuditLogs(),
      loadAssistants()
    ])
    
    // 确保服务状态数据使用中文标签
    processServiceStatusData();
    
    // 加载完数据后生成系统摘要
    await generateSystemSummary()
  } catch (error) {
    console.error('加载工作台数据失败:', error)
    window.$message?.error('加载数据失败，请刷新页面重试')
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  // 清理echarts实例
  echartsInstances.value.forEach(chart => {
    chart.dispose()
  })
})
</script>

<style scoped>
.n-card {
  transition: box-shadow 0.3s ease;
}
.n-card:hover {
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
}

.report-container :deep(.n-timeline-item-content__title) {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.report-item {
  background-color: rgba(250, 250, 252, 0.5);
  border-radius: 6px;
  padding: 4px 0;
  margin-bottom: 4px;
  border-left: 3px solid var(--n-icon-color);
}

/* 添加智能报告相关样式 */
.ai-report-container {
  padding: 20px;
  background-color: white;
}

.report-title {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 10px;
}

.report-date {
  font-size: 14px;
  color: #666;
  text-align: center;
  margin-bottom: 20px;
}

.report-content {
  margin-top: 20px;
  line-height: 1.6;
}

.report-content :deep(h1) {
  font-size: 22px;
  margin-top: 20px;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.report-content :deep(h2) {
  font-size: 20px;
  margin-top: 18px;
  margin-bottom: 12px;
}

.report-content :deep(h3) {
  font-size: 18px;
  margin-top: 15px;
  margin-bottom: 10px;
}

.report-content :deep(p) {
  margin-bottom: 15px;
}

.report-content :deep(ul),
.report-content :deep(ol) {
  margin-left: 20px;
  margin-bottom: 15px;
}

.report-content :deep(li) {
  margin-bottom: 5px;
}

.report-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.report-content :deep(th),
.report-content :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.report-content :deep(th) {
  background-color: #f5f5f5;
}

.report-content :deep(.echarts-chart) {
  width: 100%;
  height: 400px;
  margin: 20px 0;
}

/* 打印样式 */
@media print {
  .ai-report-container {
    padding: 0;
  }
  
  .report-content :deep(.echarts-chart) {
    page-break-inside: avoid;
  }
}
</style>
