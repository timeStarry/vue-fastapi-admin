<template>
  <div class="notification-setting-page">
    <n-card title="通知设置">
      <n-tabs v-model:value="activeKey">
        <n-tab-pane name="monitor" tab="监控通知">
          <SettingForm 
            source="monitor" 
            title="监控通知设置" 
            description="配置监控告警通知的接收方式"
          />
        </n-tab-pane>
        
        <n-tab-pane name="ticket" tab="工单通知">
          <SettingForm 
            source="ticket" 
            title="工单通知设置" 
            description="配置工单状态变更通知的接收方式"
          />
        </n-tab-pane>
        
        <n-tab-pane name="system" tab="系统通知">
          <SettingForm 
            source="system" 
            title="系统通知设置" 
            description="配置系统通知的接收方式"
          />
        </n-tab-pane>
      </n-tabs>
    </n-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import SettingForm from './components/SettingForm.vue';

// 当前选项卡
const activeKey = ref('monitor');
</script>

<style scoped>
.notification-setting-page {
  padding: 16px;
}
</style> 