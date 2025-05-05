<template>
  <div class="notification-template-page">
    <n-card title="通知模板管理">
      <!-- 操作按钮 -->
      <n-space vertical>
        <n-space>
          <n-button type="primary" @click="openCreateModal">
            <template #icon>
              <TheIcon icon="material-symbols:add" :size="18" />
            </template>
            新建模板
          </n-button>
          <n-button @click="loadData">
            <template #icon>
              <TheIcon icon="material-symbols:refresh" :size="18" />
            </template>
            刷新
          </n-button>
        </n-space>

        <!-- 数据表格 -->
        <n-data-table
          remote
          :columns="columns"
          :data="tableData"
          :loading="loading"
          :pagination="pagination"
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
        />
      </n-space>
    </n-card>

    <!-- 创建/编辑模板对话框 -->
    <TemplateForm 
      :show="formVisible" 
      @update:show="formVisible = $event"
      :edit-mode="editMode"
      :template-data="currentTemplate"
      @success="handleFormSuccess" 
    />
    
    <!-- 查看模板对话框 -->
    <TemplateDetail
      :show="detailVisible"
      @update:show="detailVisible = $event"
      :template-data="currentTemplate"
    />
  </div>
</template>

<script setup>
import { h, ref, reactive, onMounted } from 'vue';
import { useMessage, NTag, NButton, NSpace, NPopconfirm, NSwitch } from 'naive-ui';
import { getTemplateList, updateTemplate, deleteTemplate as deleteTemplateApi } from '@/api/notification';
import TemplateForm from './components/TemplateForm.vue';
import TemplateDetail from './components/TemplateDetail.vue';
import TheIcon from '@/components/icon/TheIcon.vue';

const message = useMessage();

// 表格数据
const tableData = ref([]);
const loading = ref(false);

// 分页配置
const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 30, 40],
  showSizePicker: true,
  prefix({ itemCount }) {
    return `共 ${itemCount} 条`;
  },
});

// 获取渠道类型名称
const getChannelTypeName = (type) => {
  const typeMap = {
    'email': '邮件',
    'sms': '短信',
    'wechat': '微信',
    'webhook': 'Webhook',
    'system': '系统'
  };
  return typeMap[type] || type;
};

// 获取渠道类型颜色
const getChannelTypeType = (type) => {
  const typeMap = {
    'email': 'info',
    'sms': 'success',
    'wechat': 'warning',
    'webhook': 'error',
    'system': 'default'
  };
  return typeMap[type] || 'default';
};

// 表格列定义
const columns = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '模板名称', key: 'name', ellipsis: { tooltip: true } },
  { title: '模板键名', key: 'template_key', width: 150 },
  { 
    title: '适用渠道', 
    key: 'applicable_channels',
    width: 200,
    render(row) {
      if (!row.applicable_channels || row.applicable_channels.length === 0) {
        return h('span', '所有渠道');
      }
      
      return h(NSpace, {}, {
        default: () => row.applicable_channels.map(channel => 
          h(
            NTag,
            {
              type: getChannelTypeType(channel),
              style: { marginRight: '4px' }
            },
            { default: () => getChannelTypeName(channel) }
          )
        )
      });
    }
  },
  { 
    title: '状态',
    key: 'is_active',
    width: 100,
    render(row) {
      return h(NSwitch, {
        size: 'small',
        rubberBand: false,
        value: row.is_active,
        onUpdateValue: () => toggleTemplateStatus(row)
      });
    }
  },
  { title: '创建时间', key: 'created_at', width: 180 },
  {
    title: '操作',
    key: 'actions',
    width: 220,
    fixed: 'right',
    render(row) {
      return h(NSpace, {}, {
        default: () => [
          h(
            NButton,
            {
              text: true,
              type: 'primary',
              onClick: () => viewTemplate(row)
            },
            { default: () => '查看' }
          ),
          h(
            NButton,
            {
              text: true,
              type: 'primary',
              onClick: () => editTemplate(row)
            },
            { default: () => '编辑' }
          ),
          h(
            NPopconfirm,
            {
              onPositiveClick: () => deleteTemplate(row),
            },
            {
              default: () => '确定要删除此模板吗？',
              trigger: () => h(
                NButton,
                {
                  text: true,
                  type: 'error',
                },
                { default: () => '删除' }
              )
            }
          )
        ]
      });
    }
  }
];

// 对话框控制
const formVisible = ref(false);
const detailVisible = ref(false);
const editMode = ref(false);
const currentTemplate = ref(null);

// 加载数据
const loadData = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    };
    
    const result = await getTemplateList(params);
    tableData.value = result.items || [];
    pagination.itemCount = result.total || 0;
  } catch (error) {
    message.error(error.message || '获取通知模板失败');
  } finally {
    loading.value = false;
  }
};

// 分页处理
const handlePageChange = (page) => {
  pagination.page = page;
  loadData();
};

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize;
  pagination.page = 1;
  loadData();
};

// 打开创建对话框
const openCreateModal = () => {
  editMode.value = false;
  currentTemplate.value = null;
  formVisible.value = true;
};

// 查看模板
const viewTemplate = (record) => {
  currentTemplate.value = { ...record };
  detailVisible.value = true;
};

// 编辑模板
const editTemplate = (record) => {
  editMode.value = true;
  currentTemplate.value = { ...record };
  formVisible.value = true;
};

// 切换模板状态
const toggleTemplateStatus = async (record) => {
  try {
    record.publishing = true;
    await updateTemplate(record.id, {
      is_active: !record.is_active
    });
    
    record.is_active = !record.is_active;
    record.publishing = false;
    message.success(`已${record.is_active ? '启用' : '禁用'}模板: ${record.name}`);
  } catch (error) {
    record.publishing = false;
    message.error(error.message || '操作失败');
  }
};

// 删除模板
const deleteTemplate = async (record) => {
  try {
    await deleteTemplateApi(record.id);
    message.success(`已删除模板: ${record.name}`);
    loadData();
  } catch (error) {
    message.error(error.message || '删除失败');
  }
};

// 表单提交成功回调
const handleFormSuccess = () => {
  formVisible.value = false;
  loadData();
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.notification-template-page {
  padding: 16px;
}
</style> 