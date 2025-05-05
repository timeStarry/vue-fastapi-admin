<template>
  <n-modal
    :show="show"
    @update:show="$emit('update:show', $event)"
    :title="editMode ? '编辑通知模板' : '创建通知模板'"
    style="width: 800px"
    :loading="submitting"
    preset="card"
  >
    <n-form :model="formState" :rules="rules" ref="formRef" label-placement="left">
      <n-form-item path="name" label="模板名称">
        <n-input v-model:value="formState.name" placeholder="请输入模板名称" />
      </n-form-item>
      
      <n-form-item path="template_key" label="模板键名">
        <n-input 
          v-model:value="formState.template_key" 
          placeholder="请输入模板键名"
          :disabled="editMode"
        />
        <div class="form-help-text">模板键名用于系统中引用此模板，一旦创建不可修改</div>
      </n-form-item>
      
      <n-form-item path="title_template" label="标题模板">
        <n-input v-model:value="formState.title_template" placeholder="请输入标题模板" />
        <div class="form-help-text" v-pre>支持Jinja2模板语法，例如: 监控告警: {{ alert_name }}</div>
      </n-form-item>
      
      <n-form-item path="content_template" label="内容模板">
        <n-input 
          v-model:value="formState.content_template" 
          placeholder="请输入内容模板"
          type="textarea" 
          :autosize="{
            minRows: 6,
            maxRows: 12
          }" 
        />
        <div class="form-help-text" v-pre>
          支持Jinja2模板语法，例如:<br>
          主机 {{ host_name }} ({{ host_ip }}) 资源使用率超过阈值:<br>
          CPU: {{ cpu_usage }}%<br>
          内存: {{ memory_usage }}%<br>
          磁盘: {{ disk_usage }}%
        </div>
      </n-form-item>
      
      <n-form-item path="applicable_channels" label="适用渠道">
        <n-select 
          v-model:value="formState.applicable_channels" 
          multiple
          placeholder="请选择适用渠道，不选则适用于所有渠道"
          style="width: 100%"
          :options="channelOptions"
        />
      </n-form-item>
      
      <n-form-item path="is_active" label="是否启用">
        <n-switch v-model:value="formState.is_active" />
      </n-form-item>
      
      <n-divider>模板预览</n-divider>
      
      <div class="template-preview">
        <h3>标题预览</h3>
        <pre>{{ formState.title_template }}</pre>
        
        <h3>内容预览</h3>
        <pre>{{ formState.content_template }}</pre>
      </div>
      
      <n-space justify="end" style="margin-top: 24px">
        <n-button @click="handleCancel">取消</n-button>
        <n-button type="primary" :loading="submitting" @click="handleSubmit">确定</n-button>
      </n-space>
    </n-form>
  </n-modal>
</template>

<script setup>
import { ref, reactive, watch } from 'vue';
import { useMessage } from 'naive-ui';
import { createTemplate, updateTemplate } from '@/api/notification';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  editMode: {
    type: Boolean,
    default: false
  },
  templateData: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['update:show', 'success']);
const message = useMessage();

// 渠道选项
const channelOptions = [
  { label: '邮件', value: 'email' },
  { label: '短信', value: 'sms' },
  { label: '微信', value: 'wechat' },
  { label: 'Webhook', value: 'webhook' },
  { label: '系统', value: 'system' }
];

// 表单引用
const formRef = ref();

// 提交状态
const submitting = ref(false);

// 表单状态
const formState = reactive({
  name: '',
  template_key: '',
  title_template: '',
  content_template: '',
  applicable_channels: [],
  is_active: true
});

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入模板名称' }],
  template_key: [
    { required: true, message: '请输入模板键名' },
    { pattern: /^[a-z0-9_]+$/, message: '模板键名只能包含小写字母、数字和下划线' }
  ],
  title_template: [{ required: true, message: '请输入标题模板' }],
  content_template: [{ required: true, message: '请输入内容模板' }]
};

// 监听编辑模式变化，初始化表单数据
watch([() => props.show, () => props.templateData], ([isVisible, data]) => {
  if (isVisible && props.editMode && data) {
    // 编辑模式，设置表单数据
    formState.name = data.name;
    formState.template_key = data.template_key;
    formState.title_template = data.title_template;
    formState.content_template = data.content_template;
    formState.applicable_channels = data.applicable_channels || [];
    formState.is_active = data.is_active;
  } else if (isVisible && !props.editMode) {
    // 创建模式，重置表单
    resetForm();
  }
});

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.restoreValidation();
  }
  
  formState.name = '';
  formState.template_key = '';
  formState.title_template = '';
  formState.content_template = '';
  formState.applicable_channels = [];
  formState.is_active = true;
};

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate();
    
    submitting.value = true;
    
    const data = {
      name: formState.name,
      title_template: formState.title_template,
      content_template: formState.content_template,
      applicable_channels: formState.applicable_channels,
      is_active: formState.is_active
    };
    
    // 创建模式需要提供template_key
    if (!props.editMode) {
      data.template_key = formState.template_key;
    }
    
    if (props.editMode && props.templateData) {
      // 编辑模式
      await updateTemplate(props.templateData.id, data);
      message.success(`通知模板 ${formState.name} 已更新`);
    } else {
      // 创建模式
      await createTemplate(data);
      message.success(`通知模板 ${formState.name} 已创建`);
    }
    
    resetForm();
    emit('success');
  } catch (error) {
    message.error(props.editMode ? '更新失败: ' + error.message : '创建失败: ' + error.message);
  } finally {
    submitting.value = false;
  }
};

// 取消操作
const handleCancel = () => {
  resetForm();
  emit('update:show', false);
};
</script>

<style scoped>
.form-help-text {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
  margin-top: 4px;
}

.template-preview {
  background-color: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
}

.template-preview h3 {
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 14px;
}

.template-preview pre {
  margin: 0 0 16px 0;
  padding: 8px;
  background-color: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 2px;
  white-space: pre-wrap;
  word-break: break-all;
}
</style> 