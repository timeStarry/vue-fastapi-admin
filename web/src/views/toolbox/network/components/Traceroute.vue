<script setup>
import { ref, reactive } from 'vue'
import { 
  NForm, 
  NFormItem, 
  NInput, 
  NInputNumber, 
  NButton, 
  NSpace, 
  NCard, 
  NDivider,
  NDataTable,
  NText,
  NTimeline,
  NTimelineItem
} from 'naive-ui'
import axios from 'axios'

const formRef = ref(null)
const loading = ref(false)
const result = ref(null)

const formValue = reactive({
  host: '',
  max_hops: 30,
  timeout: 1.0
})

const rules = {
  host: {
    required: true,
    message: '请输入目标主机',
    trigger: ['blur', 'input']
  }
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    loading.value = true
    result.value = null
    
    const response = await axios.post('/api/v1/toolbox/traceroute', null, {
      params: {
        ...formValue,
        token: localStorage.getItem('token') || ''
      }
    })
    
    if (response.data.code === 200) {
      result.value = response.data.data
    } else {
      $message.error(response.data.msg || '请求失败')
    }
  } catch (error) {
    console.error(error)
    $message.error('请求发生错误')
  } finally {
    loading.value = false
  }
}

const columns = [
  {
    title: '跳数',
    key: 'hop'
  },
  {
    title: 'IP地址',
    key: 'ip'
  },
  {
    title: '响应时间',
    key: 'times',
    render: (row) => {
      if (row.times && row.times.length > 0) {
        return row.times.map(t => `${t} ms`).join(', ')
      }
      return '超时'
    }
  }
]
</script>

<template>
  <div>
    <NCard title="路由追踪" size="small">
      <NForm
        ref="formRef"
        :model="formValue"
        :rules="rules"
        label-placement="left"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <NFormItem label="目标主机" path="host">
          <NInput v-model:value="formValue.host" placeholder="请输入IP地址或域名" />
        </NFormItem>
        
        <NFormItem label="最大跳数" path="max_hops">
          <NInputNumber v-model:value="formValue.max_hops" :min="1" :max="64" />
        </NFormItem>
        
        <NFormItem label="超时时间(秒)" path="timeout">
          <NInputNumber v-model:value="formValue.timeout" :min="0.1" :max="10" :step="0.1" />
        </NFormItem>
        
        <NFormItem>
          <NButton type="primary" @click="handleSubmit" :loading="loading">
            开始追踪
          </NButton>
        </NFormItem>
      </NForm>
    </NCard>
    
    <NDivider v-if="result" />
    
    <NCard v-if="result" title="追踪结果" size="small">
      <NSpace vertical>
        <div>
          <NText strong>目标主机：</NText> {{ result.host }}
        </div>
        
        <NDivider />
        
        <NTimeline>
          <NTimelineItem v-for="hop in result.hops" :key="hop.hop" :title="`第 ${hop.hop} 跳`">
            <template #content>
              <div>IP: {{ hop.ip }}</div>
              <div>
                响应时间: 
                <template v-if="hop.times && hop.times.length > 0">
                  {{ hop.times.map(t => `${t} ms`).join(', ') }}
                </template>
                <template v-else>
                  超时
                </template>
              </div>
            </template>
          </NTimelineItem>
        </NTimeline>
        
        <NDivider />
        
        <NDataTable
          :columns="columns"
          :data="result.hops"
          :bordered="false"
          :single-line="false"
        />
        
        <NDivider />
        
        <NCard title="原始输出" size="small">
          <pre>{{ result.raw }}</pre>
        </NCard>
      </NSpace>
    </NCard>
  </div>
</template> 