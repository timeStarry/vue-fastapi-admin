<template>
  <n-modal
    :show="show"
    @update:show="$emit('update:show', $event)"
    :title="notification ? `通知详情 - ${notification.title}` : '通知详情'"
    style="width: 600px"
    preset="card"
  >
    <n-spin :show="loading">
      <template v-if="notification">
        <n-descriptions bordered label-placement="left" label-width="120px">
          <n-descriptions-item label="通知ID">{{ notification.id }}</n-descriptions-item>
          <n-descriptions-item label="标题">{{ notification.title }}</n-descriptions-item>
          <n-descriptions-item label="来源">
            <n-tag :type="getSourceType(notification.source)">
              {{ getSourceName(notification.source) }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="状态">
            <n-tag :type="getStatusType(notification.status)">
              {{ getStatusName(notification.status) }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="优先级">
            <n-tag :type="getPriorityType(notification.priority)">
              {{ getPriorityName(notification.priority) }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="创建时间">{{ notification.created_at }}</n-descriptions-item>
          <n-descriptions-item label="处理时间">{{ notification.processed_at || '-' }}</n-descriptions-item>
        </n-descriptions>

        <n-divider />

        <!-- 通知内容卡片 -->
        <n-card title="通知内容" style="margin-bottom: 16px">
          <div v-html="notification.content || '无内容'"></div>
        </n-card>

        <!-- 通知详情数据 -->
        <n-card v-if="notification.data" title="详细数据" style="margin-bottom: 16px">
          <pre>{{ JSON.stringify(notification.data, null, 2) }}</pre>
        </n-card>

        <!-- 处理结果卡片 -->
        <n-card v-if="notification.result" title="处理结果">
          <div v-html="notification.result"></div>
        </n-card>
      </template>
      <template v-else-if="!loading">
        <n-empty description="未找到通知数据" />
      </template>
    </n-spin>
    <template #footer>
      <n-space justify="end">
        <n-button @click="$emit('update:show', false)">关闭</n-button>
        <n-button type="primary" @click="handleEdit" v-if="notification && notification.status !== 'completed'">
          更新状态
        </n-button>
      </n-space>
    </template>

    <!-- 编辑状态对话框 -->
    <n-modal
      :show="editModalVisible"
      @update:show="editModalVisible = $event"
      title="更新状态"
      style="width: 500px"
      preset="card"
    >
      <n-form
        ref="formRef"
        :model="editForm"
        label-placement="left"
        label-width="auto"
      >
        <n-form-item label="状态" path="status">
          <n-select
            v-model:value="editForm.status"
            :options="statusOptions"
            placeholder="请选择状态"
          />
        </n-form-item>
        <n-form-item label="处理结果" path="result">
          <n-input
            v-model:value="editForm.result"
            type="textarea"
            :autosize="{
              minRows: 3,
              maxRows: 6
            }"
            placeholder="请输入处理结果"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="editModalVisible = false">取消</n-button>
          <n-button type="primary" :loading="submitting" @click="handleUpdate">确认</n-button>
        </n-space>
      </template>
    </n-modal>
  </n-modal>
</template>

<script setup>
import { ref, watch, reactive } from 'vue';
import { useMessage } from 'naive-ui';
import { getNotification, updateNotification } from '@/api/notification';

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  notificationId: {
    type: Number,
    default: null
  }
});

const emit = defineEmits(['update:show', 'refresh']);

const message = useMessage();
const loading = ref(false);
const notification = ref(null);
const editModalVisible = ref(false);
const submitting = ref(false);
const formRef = ref(null);

// 状态选项
const statusOptions = [
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '已完成', value: 'completed' },
  { label: '失败', value: 'failed' }
];

// 编辑表单
const editForm = reactive({
  status: '',
  result: ''
});

// 获取通知详情
const fetchNotification = async () => {
  if (!props.notificationId) return;
  
  loading.value = true;
  try {
    const data = await getNotification(props.notificationId);
    console.log('获取到的通知详情数据:', data);
    notification.value = data;
    
    // 确保notification有值后打印内容，方便调试
    console.log('设置到组件的通知详情:', notification.value);
  } catch (error) {
    console.error('获取通知详情失败:', error);
    message.error(error.message || '获取通知详情失败');
  } finally {
    loading.value = false;
  }
};

// 打开编辑对话框
const handleEdit = () => {
  editForm.status = notification.value.status;
  editForm.result = notification.value.result || '';
  editModalVisible.value = true;
};

// 更新通知状态
const handleUpdate = async () => {
  submitting.value = true;
  try {
    await updateNotification(props.notificationId, {
      status: editForm.status,
      result: editForm.result
    });
    
    message.success('更新成功');
    editModalVisible.value = false;
    await fetchNotification();
    emit('refresh');
  } catch (error) {
    message.error(error.message || '更新失败');
  } finally {
    submitting.value = false;
  }
};

// 获取来源名称
const getSourceName = (source) => {
  const sourceMap = {
    'monitor': '监控',
    'ticket': '工单',
    'system': '系统'
  };
  return sourceMap[source] || source;
};

// 获取来源类型
const getSourceType = (source) => {
  const typeMap = {
    'monitor': 'info',
    'ticket': 'success',
    'system': 'warning'
  };
  return typeMap[source] || 'default';
};

// 获取状态名称
const getStatusName = (status) => {
  const statusMap = {
    'pending': '待处理',
    'processing': '处理中',
    'completed': '已完成',
    'failed': '失败'
  };
  return statusMap[status] || status;
};

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'processing': 'info',
    'completed': 'success',
    'failed': 'error'
  };
  return typeMap[status] || 'default';
};

// 获取优先级名称
const getPriorityName = (priority) => {
  const priorityMap = {
    'low': '低',
    'normal': '普通',
    'high': '高',
    'urgent': '紧急'
  };
  return priorityMap[priority] || priority;
};

// 获取优先级类型
const getPriorityType = (priority) => {
  const typeMap = {
    'low': 'default',
    'normal': 'info',
    'high': 'warning',
    'urgent': 'error'
  };
  return typeMap[priority] || 'default';
};

// 监听通知ID变化
watch(() => props.notificationId, () => {
  if (props.notificationId) {
    fetchNotification();
  }
}, { immediate: true });

// 监听visible变化，关闭时清空数据
watch(() => props.show, (val) => {
  if (!val) {
    notification.value = null;
  }
});
</script> 