<template>
  <div class="setting-form">
    <n-card :title="title">
      <p class="setting-description">{{ description }}</p>
      
      <n-spin :show="loading">
        <n-form :model="formState" label-placement="left">
          <n-form-item label="是否接收此类通知">
            <n-switch v-model:value="formState.is_enabled" />
          </n-form-item>
          
          <n-form-item label="接收渠道" v-if="formState.is_enabled">
            <n-checkbox-group v-model:value="formState.enabled_channels">
              <n-space>
                <n-checkbox 
                  v-for="channel in availableChannels" 
                  :key="channel.value" 
                  :value="channel.value"
                  :label="channel.label" 
                />
              </n-space>
            </n-checkbox-group>
          </n-form-item>
          
          <n-form-item>
            <n-button type="primary" :loading="saving" @click="saveSetting">保存设置</n-button>
          </n-form-item>
        </n-form>
      </n-spin>
    </n-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useMessage } from 'naive-ui';
import { getUserSourceSetting, createOrUpdateSetting, getChannelList } from '@/api/notification';
import { useUserStore } from '@/store/modules/user';

const props = defineProps({
  source: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: '通知设置'
  },
  description: {
    type: String,
    default: '配置通知接收偏好'
  }
});

const message = useMessage();

// 加载状态
const loading = ref(false);
const saving = ref(false);

// 用户信息
const userId = ref(null);

// 可用的渠道
const availableChannels = ref([]);

// 表单状态
const formState = reactive({
  is_enabled: true,
  enabled_channels: []
});

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const userStore = useUserStore();
    
    // 确保userStore已初始化并包含用户ID
    if (!userStore.userId) {
      await userStore.getUserInfo();
    }
    
    userId.value = userStore.userId;
    
    if (!userId.value) {
      throw new Error('无法获取用户ID');
    }
    
    console.log('已获取用户ID:', userId.value);
  } catch (error) {
    console.error('获取用户信息失败:', error);
    message.error('获取用户信息失败，请刷新页面重试');
    throw error; // 重新抛出错误以便上层处理
  }
};

// 加载可用渠道
const loadAvailableChannels = async () => {
  try {
    const result = await getChannelList({ is_active: true });
    availableChannels.value = (result.items || []).map(item => ({
      label: item.name,
      value: item.channel_type
    }));
  } catch (error) {
    message.error(error.message || '获取通知渠道失败');
  }
};

// 加载用户设置
const loadUserSetting = async () => {
  if (!userId.value) {
    return;
  }
  
  loading.value = true;
  try {
    console.log(`加载用户[${userId.value}]的[${props.source}]设置`);
    const result = await getUserSourceSetting(userId.value, props.source);
    console.log('获取到的用户设置:', result);
    
    // 更新表单状态
    formState.is_enabled = result.is_enabled === undefined ? true : !!result.is_enabled;
    formState.enabled_channels = Array.isArray(result.enabled_channels) ? result.enabled_channels : [];
    
    console.log('更新后的表单状态:', { ...formState });
  } catch (error) {
    console.error('获取通知设置失败:', error);
    message.error(error.message || '获取通知设置失败');
  } finally {
    loading.value = false;
  }
};

// 保存设置
const saveSetting = async () => {
  if (!userId.value) {
    message.error('无法获取用户信息');
    return;
  }
  
  const settingData = {
    user_id: userId.value,
    source: props.source,
    is_enabled: formState.is_enabled,
    enabled_channels: formState.enabled_channels
  };
  
  console.log('保存设置，数据：', settingData);
  
  saving.value = true;
  try {
    const result = await createOrUpdateSetting(settingData);
    console.log('保存设置响应：', result);
    
    message.success('通知设置已更新');
    
    // 保存成功后重新加载设置
    await loadUserSetting();
  } catch (error) {
    console.error('保存设置失败：', error);
    message.error(error.message || '保存失败');
  } finally {
    saving.value = false;
  }
};

// 初始化
onMounted(async () => {
  console.log('通知设置组件初始化');
  
  try {
    // 加载用户信息
    await loadUserInfo();
    console.log('用户ID:', userId.value);
    
    // 并行加载渠道和设置
    await Promise.all([
      loadAvailableChannels(),
      loadUserSetting()
    ]);
  } catch (error) {
    console.error('初始化失败:', error);
    message.error('初始化组件失败');
  }
});
</script>

<style scoped>
.setting-form {
  margin-bottom: 20px;
}

.setting-description {
  margin-bottom: 20px;
  color: rgba(0, 0, 0, 0.45);
}
</style> 