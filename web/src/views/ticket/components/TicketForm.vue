<script setup>
import { ref, onMounted } from 'vue'
import { NForm, NFormItem, NInput, NSelect, NRadioGroup, NRadio, NTreeSelect } from 'naive-ui'
import api from '@/api'

const props = defineProps({
  formRef: {
    type: Object,
    required: true
  },
  formValue: {
    type: Object,
    required: true
  }
})

// 部门选项
const deptOptions = ref([])

onMounted(async () => {
  const res = await api.getDepts()
  deptOptions.value = res.data
})

// 工单类型选项
const typeOptions = [
  { label: '故障报修', value: 'repair' },
  { label: '需求建议', value: 'suggestion' },
  { label: '咨询问题', value: 'question' }
]

// 优先级选项
const priorityOptions = [
  { label: '低', value: 'low' },
  { label: '中', value: 'medium' },
  { label: '高', value: 'high' }
]

// 表单校验规则
const rules = {
  title: {
    required: true,
    message: '请输入工单标题',
    trigger: 'blur'
  },
  type: {
    required: true,
    message: '请选择工单类型',
    trigger: 'change'
  },
  dept_id: {
    required: true,
    type: 'number',
    message: '请选择所属部门',
    trigger: 'change'
  },
  priority: {
    required: true,
    message: '请选择优先级',
    trigger: 'change'
  },
  'content.content': {
    required: true,
    message: '请输入工单内容',
    trigger: 'blur',
    validator: (rule, value) => {
      if (!value || value.trim() === '') {
        return new Error('请输入工单内容')
      }
      return true
    }
  }
}

// 在提交前处理表单数据
const handleBeforeSubmit = () => {
  const formData = { ...props.formValue }
  
  // 确保content是一个对象
  if (typeof formData.content === 'string') {
    formData.content = {
      type: 'text',
      content: formData.content
    }
  }
  
  // 添加额外的content字段
  formData.content = {
    ...formData.content,
    // 可以在这里添加更多的content字段
    created_at: new Date().toISOString(),
    version: '1.0'
  }
  
  return formData
}

// 暴露方法给父组件
defineExpose({
  handleBeforeSubmit
})
</script>

<template>
  <NForm
    ref="props.formRef"
    :model="props.formValue"
    :rules="rules"
    label-placement="left"
    label-width="auto"
    require-mark-placement="right-hanging"
  >
    <NFormItem label="工单标题" path="title">
      <NInput v-model:value="props.formValue.title" placeholder="请输入工单标题" />
    </NFormItem>
    
    <NFormItem label="工单类型" path="type">
      <NSelect
        v-model:value="props.formValue.type"
        :options="typeOptions"
        placeholder="请选择工单类型"
      />
    </NFormItem>
    
    <NFormItem label="所属部门" path="dept_id">
      <NTreeSelect
        v-model:value="props.formValue.dept_id"
        :options="deptOptions"
        key-field="id"
        label-field="name"
        placeholder="请选择所属部门"
        clearable
        default-expand-all
      />
    </NFormItem>
    
    <NFormItem label="优先级" path="priority">
      <NRadioGroup v-model:value="props.formValue.priority">
        <NRadio
          v-for="option in priorityOptions"
          :key="option.value"
          :value="option.value"
        >
          {{ option.label }}
        </NRadio>
      </NRadioGroup>
    </NFormItem>
    
    <NFormItem label="工单内容" path="content.content">
      <NInput
        v-model:value="props.formValue.content.content"
        type="textarea"
        :rows="6"
        placeholder="请输入工单内容"
      />
    </NFormItem>
  </NForm>
</template> 