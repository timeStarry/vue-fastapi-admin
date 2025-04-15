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
  count: 4,
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
    
    const response = await axios.post('/api/v1/toolbox/ping', null, {
      params: formValue,
      headers: {
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
    title: '序号',
    key: 'index',
    render: (row, index) => index + 1
  },
  {
    title: '响应时间(ms)',
    key: 'time',
    render: (row) => `${row} ms`
  }
]
</script>

<template>
  <div>
    <NCard title="Ping测试" size="small">
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
        
        <NFormItem label="发送次数" path="count">
          <NInputNumber v-model:value="formValue.count" :min="1" :max="100" />
        </NFormItem>
        
        <NFormItem label="超时时间(秒)" path="timeout">
          <NInputNumber v-model:value="formValue.timeout" :min="0.1" :max="10" :step="0.1" />
        </NFormItem>
        
        <NFormItem>
          <NButton 
            v-permission="'post/api/v1/toolbox/ping'" 
            type="primary" 
            @click="handleSubmit" 
            :loading="loading"
          >
            开始测试
          </NButton>
        </NFormItem>
      </NForm>
    </NCard>
    
    <NDivider v-if="result" />
    
    <NCard v-if="result" title="测试结果" size="small">
      <NSpace vertical>
        <div>
          <NText strong>主机：</NText> {{ result.host }}
        </div>
        <div>
          <NText strong>发送包数：</NText> {{ result.sent }}
        </div>
        <div>
          <NText strong>接收包数：</NText> {{ result.received }}
        </div>
        <div>
          <NText strong>丢失包数：</NText> {{ result.lost }}
        </div>
        
        <NDivider />
        
        <NDataTable
          :columns="columns"
          :data="result.times"
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