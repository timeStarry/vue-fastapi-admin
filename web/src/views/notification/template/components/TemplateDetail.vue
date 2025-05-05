<template>
  <n-modal
    :show="show"
    @update:show="$emit('update:show', $event)"
    :title="'模板详情: ' + (templateData ? templateData.name : '')"
    style="width: 800px"
    preset="card"
  >
    <n-spin :show="loading">
      <n-descriptions bordered label-placement="left" :column="1" size="small">
        <n-descriptions-item label="ID">
          {{ templateData ? templateData.id : '' }}
        </n-descriptions-item>
        <n-descriptions-item label="模板名称">
          {{ templateData ? templateData.name : '' }}
        </n-descriptions-item>
        <n-descriptions-item label="模板键名">
          {{ templateData ? templateData.template_key : '' }}
        </n-descriptions-item>
        <n-descriptions-item label="适用渠道">
          <template v-if="templateData && templateData.applicable_channels && templateData.applicable_channels.length > 0">
            <n-tag 
              v-for="channel in templateData.applicable_channels" 
              :key="channel"
              :type="getChannelTypeType(channel)"
              style="margin-right: 4px"
            >
              {{ getChannelTypeName(channel) }}
            </n-tag>
          </template>
          <span v-else>所有渠道</span>
        </n-descriptions-item>
        <n-descriptions-item label="状态">
          <n-badge 
            v-if="templateData" 
            :type="templateData.is_active ? 'success' : 'error'" 
            dot
          >
            {{ templateData.is_active ? '启用' : '禁用' }}
          </n-badge>
        </n-descriptions-item>
        <n-descriptions-item label="创建时间">
          {{ templateData ? templateData.created_at : '' }}
        </n-descriptions-item>
        <n-descriptions-item label="更新时间">
          {{ templateData ? templateData.updated_at : '' }}
        </n-descriptions-item>
      </n-descriptions>

      <n-divider>模板内容</n-divider>
      
      <n-card title="标题模板" size="small" class="content-card">
        <div class="template-content">{{ templateData ? templateData.title_template : '' }}</div>
      </n-card>
      
      <n-card title="内容模板" size="small" class="content-card" style="margin-top: 16px">
        <div class="template-content">{{ templateData ? templateData.content_template : '' }}</div>
      </n-card>
      
      <div class="footer-btns">
        <n-button @click="handleCancel">关闭</n-button>
      </div>
    </n-spin>
  </n-modal>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  templateData: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['update:show']);

// 加载状态
const loading = ref(false);

// 获取渠道类型名称
const getChannelTypeName = (type) => {
  const typeMap = {
    'email': '邮件',
    'sms': '短信',
    'wechat': '微信',
    'webhook': 'Webhook',
    'system': '系统'
  };
  return typeMap[type] || type;
};

// 获取渠道类型颜色
const getChannelTypeType = (type) => {
  const typeMap = {
    'email': 'info',
    'sms': 'success',
    'wechat': 'warning',
    'webhook': 'error',
    'system': 'default'
  };
  return typeMap[type] || 'default';
};

// 关闭弹窗
const handleCancel = () => {
  emit('update:show', false);
};
</script>

<style scoped>
.content-card {
  background-color: #f5f5f5;
}

.template-content {
  white-space: pre-wrap;
  word-break: break-all;
  padding: 12px;
  background-color: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 2px;
}

.footer-btns {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}
</style> 