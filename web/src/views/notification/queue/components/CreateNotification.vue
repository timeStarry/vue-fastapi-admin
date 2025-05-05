<template>
  <n-modal
    :show="show"
    @update:show="$emit('update:show', $event)"
    title="创建通知"
    style="width: 600px"
    :loading="submitting"
    preset="card"
  >
    <n-form
      ref="formRef"
      :model="formModel"
      :rules="rules"
      label-placement="left"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <n-form-item label="标题" path="title">
        <n-input v-model:value="formModel.title" placeholder="请输入通知标题" />
      </n-form-item>
      
      <n-form-item label="内容" path="content">
        <n-input
          v-model:value="formModel.content"
          type="textarea"
          :autosize="{
            minRows: 4,
            maxRows: 8
          }"
          placeholder="请输入通知内容"
        />
      </n-form-item>
      
      <n-form-item label="来源" path="source">
        <n-select
          v-model:value="formModel.source"
          :options="sourceOptions"
          placeholder="请选择通知来源"
        />
      </n-form-item>
      
      <n-form-item label="优先级" path="priority">
        <n-select
          v-model:value="formModel.priority"
          :options="priorityOptions"
          placeholder="请选择优先级"
        />
      </n-form-item>
      
      <n-form-item label="状态" path="status">
        <n-select
          v-model:value="formModel.status"
          :options="statusOptions"
          placeholder="请选择状态"
        />
      </n-form-item>
      
      <n-form-item label="计划发送时间" path="scheduled_at">
        <n-date-picker
          v-model:value="formModel.scheduled_at"
          type="datetime"
          clearable
          placeholder="不填即立即发送"
          style="width: 100%"
        />
      </n-form-item>
      
      <n-form-item label="接收渠道" path="channels">
        <n-select
          v-model:value="formModel.channels"
          multiple
          :options="channelOptions"
          placeholder="请选择接收渠道"
          :loading="loadingChannels"
        />
      </n-form-item>
      
      <n-space justify="end" style="margin-top: 24px">
        <n-button @click="$emit('update:show', false)">取消</n-button>
        <n-button type="primary" :loading="submitting" @click="handleSubmit">确认</n-button>
      </n-space>
    </n-form>
  </n-modal>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useMessage } from 'naive-ui';
import { createNotification, getChannelList } from '@/api/notification';

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['update:show', 'success']);

const message = useMessage();
const formRef = ref(null);
const submitting = ref(false);
const loadingChannels = ref(false);
const channelOptions = ref([]);

// 表单数据
const formModel = reactive({
  title: '',
  content: '',
  source: 'system',
  priority: 'normal',
  status: 'pending',
  scheduled_at: null,
  channels: []
});

// 来源选项
const sourceOptions = [
  { label: '监控', value: 'monitor' },
  { label: '工单', value: 'ticket' },
  { label: '系统', value: 'system' }
];

// 优先级选项
const priorityOptions = [
  { label: '低', value: 'low' },
  { label: '普通', value: 'normal' },
  { label: '高', value: 'high' },
  { label: '紧急', value: 'urgent' }
];

// 状态选项
const statusOptions = [
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' }
];

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入通知标题', trigger: 'blur' },
    { max: 100, message: '标题长度不能超过100个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入通知内容', trigger: 'blur' }
  ],
  source: [
    { required: true, message: '请选择通知来源', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
};

// 加载渠道列表
const fetchChannels = async () => {
  loadingChannels.value = true;
  try {
    const result = await getChannelList({ page: 1, page_size: 100, is_active: true });
    channelOptions.value = (result.items || []).map(item => ({
      label: `${item.name} (${item.channel_type})`,
      value: item.id
    }));
  } catch (error) {
    message.error(error.message || '获取渠道列表失败');
  } finally {
    loadingChannels.value = false;
  }
};

// 提交表单
const handleSubmit = async () => {
  formRef.value?.validate(async (errors) => {
    if (errors) return;
    
    submitting.value = true;
    try {
      // 从表单中提取需要的字段，确保数据格式符合API要求
      const formData = {
        title: formModel.title,
        content: formModel.content,
        source: formModel.source,
        priority: formModel.priority,
        status: formModel.status
      };
      
      // 添加可选字段
      if (formModel.scheduled_at) {
        formData.scheduled_at = new Date(formModel.scheduled_at).toISOString();
      }
      
      // 源ID可为空
      formData.source_id = null;
      
      // 如果选择了渠道，添加到data字段中而不是直接添加到根级别
      if (formModel.channels && formModel.channels.length > 0) {
        formData.data = {
          channels: formModel.channels
        };
      }
      
      await createNotification(formData);
      message.success('创建成功');
      resetForm();
      emit('success');
    } catch (error) {
      message.error(error.message || '创建失败');
    } finally {
      submitting.value = false;
    }
  });
};

// 重置表单
const resetForm = () => {
  formRef.value?.restoreValidation();
  Object.assign(formModel, {
    title: '',
    content: '',
    source: 'system',
    priority: 'normal',
    status: 'pending',
    scheduled_at: null,
    channels: []
  });
};

onMounted(() => {
  fetchChannels();
});
</script>

<style scoped>
.form-help-text {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
  margin-top: 4px;
}
</style> 