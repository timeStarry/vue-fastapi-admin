<template>
  <n-modal
    :show="show"
    @update:show="$emit('update:show', $event)"
    :title="isEdit ? '编辑通知渠道' : '添加通知渠道'"
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
      <n-form-item label="渠道名称" path="name">
        <n-input v-model:value="formModel.name" placeholder="请输入渠道名称" />
      </n-form-item>
      
      <n-form-item label="渠道类型" path="channel_type">
        <n-select
          v-model:value="formModel.channel_type"
          :options="channelTypeOptions"
          placeholder="请选择渠道类型"
          :disabled="isEdit"
        />
      </n-form-item>
      
      <n-divider>渠道配置</n-divider>
      
      <!-- 邮件配置 -->
      <template v-if="formModel.channel_type === 'email'">
        <n-form-item label="SMTP服务器" path="config.host">
          <n-input v-model:value="formModel.config.host" placeholder="请输入SMTP服务器地址" />
        </n-form-item>
        
        <n-form-item label="SMTP端口" path="config.port">
          <n-input-number
            v-model:value="formModel.config.port"
            :min="1"
            :max="65535"
            placeholder="请输入SMTP端口"
            style="width: 100%"
          />
        </n-form-item>
        
        <n-form-item label="用户名" path="config.username">
          <n-input v-model:value="formModel.config.username" placeholder="请输入SMTP用户名" />
        </n-form-item>
        
        <n-form-item label="密码" path="config.password">
          <n-input
            v-model:value="formModel.config.password"
            type="password"
            placeholder="请输入SMTP密码"
            show-password-on="click"
          />
        </n-form-item>
        
        <n-form-item label="发件人" path="config.from_email">
          <n-input v-model:value="formModel.config.from_email" placeholder="请输入发件人邮箱" />
        </n-form-item>
        
        <n-form-item label="使用SSL/TLS" path="config.use_tls">
          <n-switch v-model:value="formModel.config.use_tls" />
        </n-form-item>
      </template>
      
      <!-- 短信配置 -->
      <template v-if="formModel.channel_type === 'sms'">
        <n-form-item label="短信平台" path="config.platform">
          <n-select
            v-model:value="formModel.config.platform"
            :options="smsPlatformOptions"
            placeholder="请选择短信平台"
          />
        </n-form-item>
        
        <n-form-item label="AccessKey" path="config.access_key">
          <n-input v-model:value="formModel.config.access_key" placeholder="请输入AccessKey" />
        </n-form-item>
        
        <n-form-item label="SecretKey" path="config.secret_key">
          <n-input
            v-model:value="formModel.config.secret_key"
            type="password"
            placeholder="请输入SecretKey"
            show-password-on="click"
          />
        </n-form-item>
        
        <n-form-item label="短信签名" path="config.sign_name">
          <n-input v-model:value="formModel.config.sign_name" placeholder="请输入短信签名" />
        </n-form-item>
        
        <n-form-item label="模板ID" path="config.template_id">
          <n-input v-model:value="formModel.config.template_id" placeholder="请输入短信模板ID" />
        </n-form-item>
      </template>
      
      <!-- 钉钉配置 -->
      <template v-if="formModel.channel_type === 'dingtalk'">
        <n-form-item label="Webhook地址" path="config.webhook_url">
          <n-input v-model:value="formModel.config.webhook_url" placeholder="请输入钉钉Webhook地址" />
        </n-form-item>
        
        <n-form-item label="安全密钥" path="config.secret">
          <n-input
            v-model:value="formModel.config.secret"
            type="password"
            placeholder="请输入安全密钥"
            show-password-on="click"
          />
        </n-form-item>
        
        <n-form-item label="@手机号列表" path="config.at_mobiles">
          <n-dynamic-tags
            v-model:value="formModel.config.at_mobiles"
            placeholder="请输入手机号"
          />
        </n-form-item>
        
        <n-form-item label="@所有人" path="config.at_all">
          <n-switch v-model:value="formModel.config.at_all" />
        </n-form-item>
      </template>
      
      <!-- 企业微信配置 -->
      <template v-if="formModel.channel_type === 'wecom'">
        <n-form-item label="Webhook地址" path="config.webhook_url">
          <n-input v-model:value="formModel.config.webhook_url" placeholder="请输入企业微信Webhook地址" />
        </n-form-item>
      </template>
      
      <!-- 飞书配置 -->
      <template v-if="formModel.channel_type === 'feishu'">
        <n-form-item label="Webhook地址" path="config.webhook_url">
          <n-input v-model:value="formModel.config.webhook_url" placeholder="请输入飞书Webhook地址" />
        </n-form-item>
        
        <n-form-item label="安全密钥" path="config.secret">
          <n-input
            v-model:value="formModel.config.secret"
            type="password"
            placeholder="请输入安全密钥"
            show-password-on="click"
          />
        </n-form-item>
      </template>
      
      <!-- 自定义配置 -->
      <template v-if="formModel.channel_type === 'custom'">
        <n-form-item label="配置JSON" path="config.custom_config">
          <n-input
            v-model:value="formModel.config.custom_config"
            type="textarea"
            :autosize="{
              minRows: 3,
              maxRows: 10
            }"
            placeholder="请输入JSON格式的自定义配置"
          />
        </n-form-item>
      </template>
      
      <n-form-item label="启用状态" path="is_active">
        <n-switch v-model:value="formModel.is_active" />
      </n-form-item>
      
      <n-space justify="end" style="margin-top: 24px">
        <n-button @click="$emit('update:show', false)">取消</n-button>
        <n-button type="primary" :loading="submitting" @click="handleSubmit">确认</n-button>
        <n-button v-if="!isEdit" type="success" :loading="testing" @click="handleTest">测试连接</n-button>
      </n-space>
    </n-form>
  </n-modal>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue';
import { useMessage } from 'naive-ui';
import { createChannel, updateChannel, testChannel } from '@/api/notification';

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  formData: {
    type: Object,
    default: null
  },
  isEdit: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:show', 'success']);

const message = useMessage();
const formRef = ref(null);
const submitting = ref(false);
const testing = ref(false);

// 表单数据
const formModel = reactive({
  name: '',
  channel_type: 'email',
  is_active: true,
  config: {
    // Email 配置
    host: '',
    port: 465,
    username: '',
    password: '',
    from_email: '',
    use_tls: true,
    
    // SMS 配置
    platform: 'aliyun',
    access_key: '',
    secret_key: '',
    sign_name: '',
    template_id: '',
    
    // 钉钉 配置
    webhook_url: '',
    secret: '',
    at_mobiles: [],
    at_all: false,
    
    // 自定义配置
    custom_config: '{}'
  }
});

// 渠道类型选项
const channelTypeOptions = [
  { label: '邮件', value: 'email' },
  { label: '短信', value: 'sms' },
  { label: '钉钉', value: 'dingtalk' },
  { label: '企业微信', value: 'wecom' },
  { label: '飞书', value: 'feishu' },
  { label: '自定义', value: 'custom' }
];

// 短信平台选项
const smsPlatformOptions = [
  { label: '阿里云', value: 'aliyun' },
  { label: '腾讯云', value: 'tencent' },
  { label: '华为云', value: 'huawei' }
];

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入渠道名称', trigger: 'blur' }
  ],
  channel_type: [
    { required: true, message: '请选择渠道类型', trigger: 'change' }
  ],
  'config.host': [
    { 
      required: true, 
      message: '请输入SMTP服务器地址', 
      trigger: 'blur',
      validator: (rule, value) => {
        if (formModel.channel_type === 'email' && !value) {
          return new Error(rule.message);
        }
        return true;
      }
    }
  ],
  'config.port': [
    { 
      required: true, 
      message: '请输入SMTP端口', 
      trigger: 'blur',
      validator: (rule, value) => {
        if (formModel.channel_type === 'email' && !value) {
          return new Error(rule.message);
        }
        return true;
      }
    }
  ],
  'config.username': [
    { 
      required: true, 
      message: '请输入SMTP用户名', 
      trigger: 'blur',
      validator: (rule, value) => {
        if (formModel.channel_type === 'email' && !value) {
          return new Error(rule.message);
        }
        return true;
      }
    }
  ],
  'config.from_email': [
    { 
      required: true, 
      message: '请输入发件人邮箱', 
      trigger: 'blur',
      validator: (rule, value) => {
        if (formModel.channel_type === 'email' && !value) {
          return new Error(rule.message);
        }
        return true;
      }
    }
  ],
  'config.platform': [
    { 
      required: true, 
      message: '请选择短信平台', 
      trigger: 'change',
      validator: (rule, value) => {
        if (formModel.channel_type === 'sms' && !value) {
          return new Error(rule.message);
        }
        return true;
      }
    }
  ],
  'config.access_key': [
    { 
      required: true, 
      message: '请输入AccessKey', 
      trigger: 'blur',
      validator: (rule, value) => {
        if (formModel.channel_type === 'sms' && !value) {
          return new Error(rule.message);
        }
        return true;
      }
    }
  ],
  'config.secret_key': [
    { 
      required: true, 
      message: '请输入SecretKey', 
      trigger: 'blur',
      validator: (rule, value) => {
        if (formModel.channel_type === 'sms' && !value) {
          return new Error(rule.message);
        }
        return true;
      }
    }
  ],
  'config.webhook_url': [
    { 
      required: true, 
      message: '请输入Webhook地址', 
      trigger: 'blur',
      validator: (rule, value) => {
        if (['dingtalk', 'wecom', 'feishu'].includes(formModel.channel_type) && !value) {
          return new Error(rule.message);
        }
        return true;
      }
    }
  ],
  'config.custom_config': [
    {
      required: true,
      message: '请输入自定义配置',
      trigger: 'blur',
      validator: (rule, value) => {
        if (formModel.channel_type === 'custom') {
          if (!value) {
            return new Error(rule.message);
          }
          try {
            JSON.parse(value);
            return true;
          } catch (error) {
            return new Error('请输入有效的JSON格式');
          }
        }
        return true;
      }
    }
  ]
};

// 重置表单
const resetForm = () => {
  formRef.value?.restoreValidation();
  Object.assign(formModel, {
    name: '',
    channel_type: 'email',
    is_active: true,
    config: {
      host: '',
      port: 465,
      username: '',
      password: '',
      from_email: '',
      use_tls: true,
      
      platform: 'aliyun',
      access_key: '',
      secret_key: '',
      sign_name: '',
      template_id: '',
      
      webhook_url: '',
      secret: '',
      at_mobiles: [],
      at_all: false,
      
      custom_config: '{}'
    }
  });
};

// 初始化编辑表单
const initEditForm = () => {
  if (props.formData) {
    formModel.name = props.formData.name;
    formModel.channel_type = props.formData.channel_type;
    formModel.is_active = props.formData.is_active;
    
    // 重置所有配置字段
    Object.keys(formModel.config).forEach(key => {
      formModel.config[key] = '';
    });
    
    // 填充配置字段
    if (props.formData.config) {
      Object.keys(props.formData.config).forEach(key => {
        formModel.config[key] = props.formData.config[key];
      });
    }
  }
};

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate();
    
    submitting.value = true;
    try {
      const formData = {
        name: formModel.name,
        channel_type: formModel.channel_type,
        is_active: formModel.is_active,
        config: {}
      };
      
      // 根据不同渠道类型组装不同配置
      if (formModel.channel_type === 'email') {
        formData.config = {
          host: formModel.config.host,
          port: formModel.config.port,
          username: formModel.config.username,
          password: formModel.config.password,
          from_email: formModel.config.from_email,
          use_tls: formModel.config.use_tls
        };
      } else if (formModel.channel_type === 'sms') {
        formData.config = {
          platform: formModel.config.platform,
          access_key: formModel.config.access_key,
          secret_key: formModel.config.secret_key,
          sign_name: formModel.config.sign_name,
          template_id: formModel.config.template_id
        };
      } else if (formModel.channel_type === 'dingtalk') {
        formData.config = {
          webhook_url: formModel.config.webhook_url,
          secret: formModel.config.secret,
          at_mobiles: formModel.config.at_mobiles,
          at_all: formModel.config.at_all
        };
      } else if (formModel.channel_type === 'wecom' || formModel.channel_type === 'feishu') {
        formData.config = {
          webhook_url: formModel.config.webhook_url,
          secret: formModel.config.secret
        };
      } else if (formModel.channel_type === 'custom') {
        try {
          formData.config = JSON.parse(formModel.config.custom_config);
        } catch (error) {
          message.error('自定义配置JSON格式错误');
          submitting.value = false;
          return;
        }
      }
      
      if (props.isEdit && props.formData) {
        await updateChannel(props.formData.id, formData);
        message.success('更新成功');
      } else {
        await createChannel(formData);
        message.success('创建成功');
      }
      
      resetForm();
      emit('success');
    } catch (error) {
      message.error(error.message || '操作失败');
    } finally {
      submitting.value = false;
    }
  } catch (error) {
    // 验证失败，错误已由表单组件显示
  }
};

// 测试连接
const handleTest = async () => {
  try {
    await formRef.value?.validate();
    
    testing.value = true;
    try {
      const formData = {
        channel_type: formModel.channel_type,
        config: {}
      };
      
      // 根据不同渠道类型组装不同配置
      if (formModel.channel_type === 'email') {
        formData.config = {
          host: formModel.config.host,
          port: formModel.config.port,
          username: formModel.config.username,
          password: formModel.config.password,
          from_email: formModel.config.from_email,
          use_tls: formModel.config.use_tls
        };
      } else if (formModel.channel_type === 'sms') {
        formData.config = {
          platform: formModel.config.platform,
          access_key: formModel.config.access_key,
          secret_key: formModel.config.secret_key,
          sign_name: formModel.config.sign_name,
          template_id: formModel.config.template_id
        };
      } else if (formModel.channel_type === 'dingtalk') {
        formData.config = {
          webhook_url: formModel.config.webhook_url,
          secret: formModel.config.secret
        };
      } else if (formModel.channel_type === 'wecom' || formModel.channel_type === 'feishu') {
        formData.config = {
          webhook_url: formModel.config.webhook_url,
          secret: formModel.config.secret
        };
      } else if (formModel.channel_type === 'custom') {
        try {
          formData.config = JSON.parse(formModel.config.custom_config);
        } catch (error) {
          message.error('自定义配置JSON格式错误');
          testing.value = false;
          return;
        }
      }
      
      await testChannel(formData);
      message.success('测试连接成功');
    } catch (error) {
      message.error(error.message || '测试连接失败');
    } finally {
      testing.value = false;
    }
  } catch (error) {
    // 验证失败，错误已由表单组件显示
  }
};

// 监听显示状态变化，初始化表单
watch(() => props.show, (val) => {
  if (val) {
    if (props.isEdit && props.formData) {
      initEditForm();
    } else {
      resetForm();
    }
  }
});

// 监听formData变化，更新表单
watch(() => props.formData, () => {
  if (props.show && props.isEdit && props.formData) {
    initEditForm();
  }
});
</script>

<style scoped>
.form-help-text {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
  margin-top: 4px;
}
</style> 