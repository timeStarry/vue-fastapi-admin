<template>
  <div class="notification-channel-page">
    <n-card title="通知渠道管理">
      <!-- 搜索表单 -->
      <n-space vertical>
        <n-space>
          <n-select
            v-model:value="searchParams.channel_type"
            placeholder="渠道类型" 
            :options="channelTypeOptions"
            clearable
            style="width: 150px"
          />
          <n-select
            v-model:value="searchParams.is_active"
            placeholder="状态"
            :options="statusOptions"
            clearable
            style="width: 120px"
          />
          <n-button type="primary" @click="loadData">搜索</n-button>
          <n-button @click="resetSearch">重置</n-button>
        </n-space>

        <!-- 操作按钮 -->
        <n-space>
          <n-button type="primary" @click="openCreateModal">
            <template #icon>
              <TheIcon icon="material-symbols:add" :size="18" />
            </template>
            添加渠道
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

    <!-- 渠道创建/编辑对话框 -->
    <ChannelForm
      :show="formVisible"
      @update:show="formVisible = $event"
      :form-data="currentChannel"
      :is-edit="isEdit"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup>
import { ref, reactive, h, onMounted } from 'vue';
import { useMessage, NTag, NButton, NSpace, NPopconfirm, NSwitch } from 'naive-ui';
import { getChannelList, updateChannel, deleteChannel as deleteChannelApi } from '@/api/notification';
import ChannelForm from './components/ChannelForm.vue';
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

// 搜索参数
const searchParams = reactive({
  channel_type: null,
  is_active: null
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

// 状态选项
const statusOptions = [
  { label: '启用', value: true },
  { label: '禁用', value: false }
];

// 表单控制
const formVisible = ref(false);
const isEdit = ref(false);
const currentChannel = ref(null);

// 获取渠道类型标签
const getChannelTypeLabel = (type) => {
  const option = channelTypeOptions.find(item => item.value === type);
  return option ? option.label : type;
};

// 获取渠道类型颜色
const getChannelTypeType = (type) => {
  const typeMap = {
    'email': 'info',
    'sms': 'success',
    'dingtalk': 'warning',
    'wecom': 'success',
    'feishu': 'info',
    'custom': 'default'
  };
  return typeMap[type] || 'default';
};

// 表格列定义
const columns = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '名称', key: 'name', ellipsis: { tooltip: true } },
  { 
    title: '渠道类型', 
    key: 'channel_type',
    width: 120,
    render(row) {
      return h(
        NTag,
        {
          type: getChannelTypeType(row.channel_type)
        },
        { default: () => getChannelTypeLabel(row.channel_type) }
      );
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
        onUpdateValue: () => handleToggleStatus(row)
      });
    }
  },
  { title: '创建时间', key: 'created_at', width: 180 },
  { title: '更新时间', key: 'updated_at', width: 180 },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    fixed: 'right',
    render(row) {
      return h(NSpace, {}, {
        default: () => [
          h(
            NButton,
            {
              text: true,
              type: 'primary',
              onClick: () => handleEdit(row)
            },
            { default: () => '编辑' }
          ),
          h(
            NPopconfirm,
            {
              onPositiveClick: () => handleDelete(row),
            },
            {
              default: () => '确定删除该渠道吗？',
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

// 加载数据
const loadData = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchParams
    };
    
    const result = await getChannelList(params);
    tableData.value = result.items || [];
    pagination.itemCount = result.total || 0;
  } catch (error) {
    message.error(error.message || '获取渠道列表失败');
  } finally {
    loading.value = false;
  }
};

// 重置搜索条件
const resetSearch = () => {
  Object.keys(searchParams).forEach(key => {
    searchParams[key] = null;
  });
  pagination.page = 1;
  loadData();
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

// 打开编辑对话框
const handleEdit = (row) => {
  currentChannel.value = { ...row };
  isEdit.value = true;
  formVisible.value = true;
};

// 打开创建对话框
const openCreateModal = () => {
  currentChannel.value = null;
  isEdit.value = false;
  formVisible.value = true;
};

// 切换渠道状态
const handleToggleStatus = async (row) => {
  try {
    row.publishing = true;
    await updateChannel(row.id, {
      is_active: !row.is_active
    });
    
    row.is_active = !row.is_active;
    row.publishing = false;
    message.success(`已${row.is_active ? '启用' : '禁用'}渠道: ${row.name}`);
  } catch (error) {
    row.publishing = false;
    message.error(error.message || '操作失败');
  }
};

// 删除渠道
const handleDelete = async (row) => {
  try {
    await deleteChannelApi(row.id);
    message.success(`已删除渠道: ${row.name}`);
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
.notification-channel-page {
  padding: 16px;
}
</style> 