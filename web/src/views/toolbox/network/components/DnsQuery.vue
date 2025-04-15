<script setup>
import { ref, reactive } from 'vue'
import { 
  NForm, 
  NFormItem, 
  NInput, 
  NButton, 
  NSpace, 
  NCard, 
  NDivider,
  NDataTable,
  NText,
  NSelect
} from 'naive-ui'
import axios from 'axios'

const formRef = ref(null)
const loading = ref(false)
const result = ref(null)

const formValue = reactive({
  domain: '',
  record_type: 'A'
})

const recordTypeOptions = [
  { label: 'A记录', value: 'A' },
  { label: 'AAAA记录', value: 'AAAA' },
  { label: 'CNAME记录', value: 'CNAME' },
  { label: 'MX记录', value: 'MX' },
  { label: 'TXT记录', value: 'TXT' },
  { label: 'NS记录', value: 'NS' }
]

const rules = {
  domain: {
    required: true,
    message: '请输入域名',
    trigger: ['blur', 'input']
  }
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    loading.value = true
    result.value = null
    
    const response = await axios.post('/api/v1/toolbox/dns-query', null, {
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
    title: '记录类型',
    key: 'type'
  },
  {
    title: '值',
    key: 'value'
  },
  {
    title: '优先级',
    key: 'preference',
    render: (row) => row.preference !== undefined ? row.preference : '-'
  }
]
</script>

<template>
  <div>
    <NCard title="DNS查询" size="small">
      <NForm
        ref="formRef"
        :model="formValue"
        :rules="rules"
        label-placement="left"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <NFormItem label="域名" path="domain">
          <NInput v-model:value="formValue.domain" placeholder="请输入域名" />
        </NFormItem>
        
        <NFormItem label="记录类型" path="record_type">
          <NSelect v-model:value="formValue.record_type" :options="recordTypeOptions" />
        </NFormItem>
        
        <NFormItem>
          <NButton type="primary" @click="handleSubmit" :loading="loading">
            开始查询
          </NButton>
        </NFormItem>
      </NForm>
    </NCard>
    
    <NDivider v-if="result" />
    
    <NCard v-if="result" title="查询结果" size="small">
      <NSpace vertical>
        <div>
          <NText strong>域名：</NText> {{ result.domain }}
        </div>
        <div>
          <NText strong>记录类型：</NText> {{ result.record_type }}
        </div>
        
        <NDivider />
        
        <NDataTable
          :columns="columns"
          :data="result.results"
          :bordered="false"
          :single-line="false"
        />
      </NSpace>
    </NCard>
  </div>
</template> 