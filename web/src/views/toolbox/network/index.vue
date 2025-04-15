<script setup>
import { ref } from 'vue'
import { NCard, NTabs, NTabPane, NSpace } from 'naive-ui'
import PingTest from './components/PingTest.vue'
import PortScan from './components/PortScan.vue'
import DnsQuery from './components/DnsQuery.vue'
import Traceroute from './components/Traceroute.vue'
import CommonPage from '@/components/page/CommonPage.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

defineOptions({ name: '网络工具' })

const activeTab = ref('ping')
</script>

<template>
  <CommonPage show-footer title="网络工具">
    <NCard>
      <NTabs v-model:value="activeTab" type="line" animated>
        <NTabPane name="ping" tab="Ping测试">
          <template #tab>
            <NSpace align="center">
              <TheIcon icon="mdi:access-point-network" />
              Ping测试
            </NSpace>
          </template>
          <PingTest />
        </NTabPane>
        
        <NTabPane name="port-scan" tab="端口扫描">
          <template #tab>
            <NSpace align="center">
              <TheIcon icon="mdi:radar" />
              端口扫描
            </NSpace>
          </template>
          <PortScan />
        </NTabPane>
        
        <NTabPane name="dns-query" tab="DNS查询">
          <template #tab>
            <NSpace align="center">
              <TheIcon icon="mdi:dns" />
              DNS查询
            </NSpace>
          </template>
          <DnsQuery />
        </NTabPane>
        
        <NTabPane name="traceroute" tab="路由追踪">
          <template #tab>
            <NSpace align="center">
              <TheIcon icon="mdi:map-marker-path" />
              路由追踪
            </NSpace>
          </template>
          <Traceroute />
        </NTabPane>
      </NTabs>
    </NCard>
  </CommonPage>
</template> 