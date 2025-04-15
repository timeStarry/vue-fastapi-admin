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
  NTag
} from 'naive-ui'
import axios from 'axios'

const formRef = ref(null)
const loading = ref(false)
const result = ref(null)

const formValue = reactive({
  host: '',
  ports: '80,443,22,21,3306,6379',
  timeout: 1.0
})

const rules = {
  host: {
    required: true,
    message: '请输入目标主机',
    trigger: ['blur', 'input']
  },
  ports: {
    required: true,
    message: '请输入要扫描的端口',
    trigger: ['blur', 'input']
  }
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    loading.value = true
    result.value = null
    
    const response = await axios.post('/api/v1/toolbox/port-scan', null, {
      params: formValue
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
    title: '端口',
    key: 'port'
  },
  {
    title: '状态',
    key: 'status',
    render: (row) => {
      if (row.status === 'open') {
        return h(NTag, { type: 'success' }, { default: () => '开放' })
      } else if (row.status === 'closed') {
        return h(NTag, { type: 'error' }, { default: () => '关闭' })
      } else {
        return h(NTag, { type: 'warning' }, { default: () => '错误' })
      }
    }
  },
  {
    title: '错误信息',
    key: 'error'
  }
]
</script>

<template>
  <div>
    <NCard title="端口扫描" size="small">
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
        
        <NFormItem label="扫描端口" path="ports">
          <NInput v-model:value="formValue.ports" placeholder="多个端口用逗号分隔，如：80,443,22" />
        </NFormItem>
        
        <NFormItem label="超时时间(秒)" path="timeout">
          <NInputNumber v-model:value="formValue.timeout" :min="0.1" :max="10" :step="0.1" />
        </NFormItem>
        
        <NFormItem>
          <NButton type="primary" @click="handleSubmit" :loading="loading">
            开始扫描
          </NButton>
        </NFormItem>
      </NForm>
    </NCard>
    
    <NDivider v-if="result" />
    
    <NCard v-if="result" title="扫描结果" size="small">
      <NSpace vertical>
        <div>
          <NText strong>主机：</NText> {{ result.host }}
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