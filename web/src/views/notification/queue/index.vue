<template>
  <div class="notification-queue-page">
    <n-card title="通知队列管理">
      <!-- 搜索表单 -->
      <n-space vertical>
        <n-space>
          <n-select
            v-model:value="searchParams.source"
            placeholder="消息来源" 
            :options="sourceOptions"
            clearable
            style="width: 120px"
          />
          <n-select
            v-model:value="searchParams.status"
            placeholder="处理状态"
            :options="statusOptions"
            clearable
            style="width: 120px"
          />
          <n-select
            v-model:value="searchParams.priority"
            placeholder="优先级"
            :options="priorityOptions"
            clearable
            style="width: 120px"
          />
          <n-button type="primary" @click="loadData">搜索</n-button>
          <n-button @click="resetSearch">重置</n-button>
        </n-space>

        <!-- 操作按钮 -->
        <n-space>
          <n-button type="primary" @click="openCreateModal">
            <template #icon>
              <TheIcon icon="material-symbols:add" :size="18" />
            </template>
            新建通知
          </n-button>
          <n-button @click="loadData">
            <template #icon>
              <TheIcon icon="material-symbols:refresh" :size="18" />
            </template>
            刷新
          </n-button>
        </n-space>

        <!-- 数据表格 -->
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

    <!-- 通知查看/编辑对话框 -->
    <NotificationDetail 
      :show="detailVisible" 
      @update:show="detailVisible = $event"
      :notification-id="currentNotificationId" 
      @refresh="loadData" 
    />

    <!-- 创建通知对话框 -->
    <CreateNotification 
      :show="createVisible"
      @update:show="createVisible = $event" 
      @success="handleCreateSuccess" 
    />
  </div>
</template>

<script setup>
import { ref, reactive, h, onMounted } from 'vue';
import { useMessage } from 'naive-ui';
import { NTag, NButton, NSpace, NIcon } from 'naive-ui';
import { getQueueList, deleteNotification as deleteNotificationApi } from '@/api/notification';
import NotificationDetail from './components/NotificationDetail.vue';
import CreateNotification from './components/CreateNotification.vue';
import TheIcon from '@/components/icon/TheIcon.vue';

const message = useMessage();

// 表格数据
const tableData = ref([]);
const loading = ref(false);

// 分页配置
const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 30, 40],
  showSizePicker: true,
  prefix({ itemCount }) {
    return `共 ${itemCount} 条`;
  },
});

// 搜索参数
const searchParams = reactive({
  source: null,
  status: null,
  priority: null
});

// 来源选项
const sourceOptions = [
  { label: '监控', value: 'monitor' },
  { label: '工单', value: 'ticket' },
  { label: '系统', value: 'system' }
];

// 状态选项
const statusOptions = [
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '已完成', value: 'completed' },
  { label: '失败', value: 'failed' }
];

// 优先级选项
const priorityOptions = [
  { label: '低', value: 'low' },
  { label: '普通', value: 'normal' },
  { label: '高', value: 'high' },
  { label: '紧急', value: 'urgent' }
];

// 弹窗控制
const detailVisible = ref(false);
const createVisible = ref(false);
const currentNotificationId = ref(null);

// 获取来源颜色
const getSourceType = (source) => {
  const typeMap = {
    'monitor': 'info',
    'ticket': 'success',
    'system': 'warning'
  };
  return typeMap[source] || 'default';
};

// 获取状态颜色
const getStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'processing': 'info',
    'completed': 'success',
    'failed': 'error'
  };
  return typeMap[status] || 'default';
};

// 获取优先级颜色
const getPriorityType = (priority) => {
  const typeMap = {
    'low': 'default',
    'normal': 'info',
    'high': 'warning',
    'urgent': 'error'
  };
  return typeMap[priority] || 'default';
};

// 表格列定义
const columns = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '标题', key: 'title', ellipsis: { tooltip: true } },
  { 
    title: '来源', 
    key: 'source',
    width: 100,
    render(row) {
      const sourceMap = {
        'monitor': '监控',
        'ticket': '工单',
        'system': '系统'
      };
      return h(
        NTag,
        {
          type: getSourceType(row.source)
        },
        { default: () => sourceMap[row.source] || row.source }
      );
    }
  },
  { 
    title: '状态',
    key: 'status',
    width: 100,
    render(row) {
      const statusMap = {
        'pending': '待处理',
        'processing': '处理中',
        'completed': '已完成',
        'failed': '失败'
      };
      return h(
        NTag,
        {
          type: getStatusType(row.status)
        },
        { default: () => statusMap[row.status] || row.status }
      );
    }
  },
  { 
    title: '优先级',
    key: 'priority',
    width: 100,
    render(row) {
      const priorityMap = {
        'low': '低',
        'normal': '普通',
        'high': '高',
        'urgent': '紧急'
      };
      return h(
        NTag,
        {
          type: getPriorityType(row.priority)
        },
        { default: () => priorityMap[row.priority] || row.priority }
      );
    }
  },
  { title: '创建时间', key: 'created_at', width: 180 },
  { title: '处理时间', key: 'processed_at', width: 180 },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    fixed: 'right',
    render(row) {
      return h(NSpace, {}, {
        default: () => [
          h(
            NButton,
            {
              text: true,
              type: 'primary',
              onClick: () => viewNotification(row)
            },
            { default: () => '查看' }
          ),
          h(
            NButton,
            {
              text: true,
              type: 'error',
              onClick: () => handleDelete(row)
            },
            { default: () => '删除' }
          )
        ]
      });
    }
  }
];

// 加载数据
const loadData = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchParams
    };
    
    const result = await getQueueList(params);
    tableData.value = result.items || [];
    pagination.itemCount = result.total || 0;
  } catch (error) {
    message.error(error.message || '获取通知队列失败');
  } finally {
    loading.value = false;
  }
};

// 重置搜索条件
const resetSearch = () => {
  Object.keys(searchParams).forEach(key => {
    searchParams[key] = null;
  });
  pagination.page = 1;
  loadData();
};

// 分页处理
const handlePageChange = (page) => {
  pagination.page = page;
  loadData();
};

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize;
  pagination.page = 1;
  loadData();
};

// 查看通知详情
const viewNotification = (row) => {
  currentNotificationId.value = row.id;
  detailVisible.value = true;
};

// 删除通知
const handleDelete = async (row) => {
  try {
    await deleteNotificationApi(row.id);
    message.success(`已删除通知: ${row.title}`);
    loadData();
  } catch (error) {
    message.error(error.message || '删除失败');
  }
};

// 打开创建对话框
const openCreateModal = () => {
  createVisible.value = true;
};

// 创建成功回调
const handleCreateSuccess = () => {
  createVisible.value = false;
  loadData();
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.notification-queue-page {
  padding: 16px;
}
</style> 