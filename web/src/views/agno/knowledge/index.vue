<script setup>
import { h, onMounted, ref, resolveDirective, withDirectives } from 'vue'
import {
  NButton,
  NForm,
  NFormItem,
  NInput,
  NSpace,
  NPopconfirm,
  NLayout,
  NModal,
  NCard,
  NTag,
  NDataTable,
  NPagination,
  NIcon,
  NTabs,
  NTabPane,
  NEmpty,
  NDivider,
  NCollapse,
  NCollapseItem
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import { formatDate, renderIcon } from '@/utils'
import { 
  getKnowledgeBases, 
  createKnowledgeBase, 
  updateKnowledgeBase, 
  deleteKnowledgeBase,
  getDocuments,
  createDocument,
  updateDocument,
  deleteDocument
} from '@/api/agno'
import { useMessage } from 'naive-ui'

defineOptions({ name: 'AI知识库管理' })

const message = useMessage()
const vPermission = resolveDirective('permission')

// 知识库列表相关
const kbList = ref([])
const loading = ref(false)
const pagination = ref({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 50],
  showSizePicker: true,
  prefix: ({ itemCount }) => `共 ${itemCount} 条`
})

// 模态框相关
const modalVisible = ref(false)
const modalTitle = ref('')
const modalLoading = ref(false)
const modalAction = ref('create') // 'create' 或 'update'
const modalForm = ref({
  id: undefined,
  name: '',
  description: ''
})
const modalFormRef = ref(null)
const rules = {
  name: [{ required: true, message: '名称必填', trigger: 'blur' }]
}

// 文档模态框相关
const docModalVisible = ref(false)
const docModalTitle = ref('')
const docModalLoading = ref(false)
const currentKnowledgeBase = ref(null)
const documentsList = ref([])
const documentsLoading = ref(false)

// 新增文档相关
const newDocForm = ref({
  title: '',
  content: ''
})
const newDocFormRef = ref(null)
const docRules = {
  title: [{ required: true, message: '标题必填', trigger: 'blur' }],
  content: [{ required: true, message: '内容必填', trigger: 'blur' }]
}

// 批量导入文档相关
const bulkImportContent = ref('')
const activeTab = ref('documents') // 'documents' 或 'bulkImport'

// 表格列定义
const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 80,
    align: 'center'
  },
  {
    title: '名称',
    key: 'name',
    align: 'left',
    ellipsis: { tooltip: true },
    width: 200
  },
  {
    title: '描述',
    key: 'description',
    align: 'left',
    ellipsis: { tooltip: true }
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    align: 'center',
    render(row) {
      return h('span', {}, formatDate(row.created_at))
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 220,
    align: 'center',
    fixed: 'right',
    render(row) {
      return [
        h(
          NButton,
          {
            size: 'small',
            type: 'primary',
            style: 'margin-right: 8px;',
            onClick: () => handleViewDocuments(row)
          },
          {
            default: () => '文档',
            icon: renderIcon('material-symbols:article-outline', { size: 16 })
          }
        ),
        h(
          NButton,
          {
            size: 'small',
            type: 'info',
            style: 'margin-right: 8px;',
            onClick: () => handleEdit(row)
          },
          {
            default: () => '编辑',
            icon: renderIcon('material-symbols:edit', { size: 16 })
          }
        ),
        h(
          NPopconfirm,
          {
            onPositiveClick: () => handleDelete(row),
            onNegativeClick: () => {}
          },
          {
            trigger: () =>
              h(
                NButton,
                {
                  size: 'small',
                  type: 'error'
                },
                {
                  default: () => '删除',
                  icon: renderIcon('material-symbols:delete-outline', { size: 16 })
                }
              ),
            default: () => h('div', {}, '确定删除该知识库吗？')
          }
        )
      ]
    }
  }
]

// 文档表格列定义
const documentColumns = [
  {
    title: 'ID',
    key: 'id',
    width: 80,
    align: 'center'
  },
  {
    title: '标题',
    key: 'title',
    align: 'left',
    ellipsis: { tooltip: true }
  },
  {
    title: '内容预览',
    key: 'content',
    align: 'left',
    ellipsis: { tooltip: true },
    render(row) {
      const content = row.content || '';
      const preview = content.length > 50 ? content.substring(0, 50) + '...' : content;
      return h('span', {}, preview);
    }
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    align: 'center',
    render(row) {
      return h('span', {}, formatDate(row.created_at))
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 160,
    align: 'center',
    fixed: 'right',
    render(row) {
      return [
        h(
          NButton,
          {
            size: 'small',
            type: 'info',
            style: 'margin-right: 8px;',
            onClick: () => handleEditDocument(row)
          },
          {
            default: () => '编辑',
            icon: renderIcon('material-symbols:edit', { size: 16 })
          }
        ),
        h(
          NPopconfirm,
          {
            onPositiveClick: () => handleDeleteDocument(row),
            onNegativeClick: () => {}
          },
          {
            trigger: () =>
              h(
                NButton,
                {
                  size: 'small',
                  type: 'error'
                },
                {
                  default: () => '删除',
                  icon: renderIcon('material-symbols:delete-outline', { size: 16 })
                }
              ),
            default: () => h('div', {}, '确定删除该文档吗？')
          }
        )
      ]
    }
  }
]

// 生命周期钩子
onMounted(() => {
  loadKnowledgeBases()
})

// 加载知识库列表
async function loadKnowledgeBases() {
  loading.value = true
  try {
    const response = await getKnowledgeBases()
    if (response.code === 200) {
      kbList.value = response.data
      pagination.value.itemCount = response.data.length
    } else {
      message.error('获取知识库列表失败')
    }
  } catch (error) {
    message.error('获取知识库列表出错: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 加载文档列表
async function loadDocuments(knowledgeBaseId) {
  documentsLoading.value = true
  try {
    const response = await getDocuments(knowledgeBaseId)
    if (response.code === 200) {
      documentsList.value = response.data
    } else {
      message.error('获取文档列表失败')
    }
  } catch (error) {
    message.error('获取文档列表出错: ' + error.message)
  } finally {
    documentsLoading.value = false
  }
}

// 处理页码变化
function handlePageChange(page) {
  pagination.value.page = page
}

// 处理每页条数变化
function handlePageSizeChange(pageSize) {
  pagination.value.pageSize = pageSize
  pagination.value.page = 1
}

// 重置表单
function resetModalForm() {
  modalForm.value = {
    id: undefined,
    name: '',
    description: ''
  }
  if (modalFormRef.value) {
    modalFormRef.value.restoreValidation()
  }
}

// 重置文档表单
function resetDocForm() {
  newDocForm.value = {
    title: '',
    content: ''
  }
  if (newDocFormRef.value) {
    newDocFormRef.value.restoreValidation()
  }
  bulkImportContent.value = ''
}

// 添加知识库
function handleAdd() {
  resetModalForm()
  modalAction.value = 'create'
  modalTitle.value = '创建知识库'
  modalVisible.value = true
}

// 编辑知识库
function handleEdit(row) {
  resetModalForm()
  modalAction.value = 'update'
  modalTitle.value = '编辑知识库'
  modalForm.value = { ...row }
  modalVisible.value = true
}

// 保存知识库（新增或更新）
async function handleSave() {
  if (!modalFormRef.value) return
  
  await modalFormRef.value.validate()
  modalLoading.value = true
  
  try {
    if (modalAction.value === 'create') {
      // 创建知识库
      const response = await createKnowledgeBase(modalForm.value)
      if (response.code === 200) {
        message.success('创建知识库成功')
        modalVisible.value = false
        loadKnowledgeBases()
      } else {
        message.error('创建知识库失败: ' + response.msg)
      }
    } else {
      // 更新知识库
      const response = await updateKnowledgeBase(modalForm.value.id, modalForm.value)
      if (response.code === 200) {
        message.success('更新知识库成功')
        modalVisible.value = false
        loadKnowledgeBases()
      } else {
        message.error('更新知识库失败: ' + response.msg)
      }
    }
  } catch (error) {
    message.error('操作失败: ' + error.message)
  } finally {
    modalLoading.value = false
  }
}

// 删除知识库
async function handleDelete(row) {
  try {
    const response = await deleteKnowledgeBase(row.id)
    if (response.code === 200) {
      message.success('删除知识库成功')
      loadKnowledgeBases()
    } else {
      message.error('删除知识库失败: ' + response.msg)
    }
  } catch (error) {
    message.error('删除失败: ' + error.message)
  }
}

// 查看知识库文档
function handleViewDocuments(row) {
  currentKnowledgeBase.value = row
  docModalTitle.value = `${row.name} - 文档管理`
  activeTab.value = 'documents'
  resetDocForm()
  loadDocuments(row.id)
  docModalVisible.value = true
}

// 处理添加文档
async function handleAddDocument() {
  if (!currentKnowledgeBase.value) return
  if (!newDocFormRef.value) return

  await newDocFormRef.value.validate()
  docModalLoading.value = true
  
  try {
    const response = await createDocument(currentKnowledgeBase.value.id, newDocForm.value)
    if (response.code === 200) {
      message.success('添加文档成功')
      resetDocForm()
      await loadDocuments(currentKnowledgeBase.value.id)
    } else {
      message.error('添加文档失败: ' + response.msg)
    }
  } catch (error) {
    message.error('添加文档失败: ' + error.message)
  } finally {
    docModalLoading.value = false
  }
}

// 编辑文档
async function handleEditDocument(row) {
  // 在实际应用中，这里可以实现单条文档的编辑功能
  message.info('文档编辑功能将在后续版本中提供')
}

// 删除文档
async function handleDeleteDocument(row) {
  try {
    const response = await deleteDocument(row.id)
    if (response.code === 200) {
      message.success('删除文档成功')
      await loadDocuments(currentKnowledgeBase.value.id)
    } else {
      message.error('删除文档失败: ' + response.msg)
    }
  } catch (error) {
    message.error('删除失败: ' + error.message)
  }
}

// 批量导入文档
async function handleBulkImport() {
  if (!currentKnowledgeBase.value) return
  if (!bulkImportContent.value.trim()) {
    message.warning('请输入要导入的内容')
    return
  }
  
  docModalLoading.value = true
  
  try {
    // 将内容按行分割，每行作为一条知识
    const lines = bulkImportContent.value.trim().split('\n')
    let successCount = 0
    let failCount = 0
    
    for (const line of lines) {
      const trimmedLine = line.trim()
      if (!trimmedLine) continue
      
      // 提取标题和内容，以冒号分隔，如果没有冒号则整行作为内容
      let title, content
      const colonIndex = trimmedLine.indexOf(':')
      if (colonIndex > 0) {
        title = trimmedLine.substring(0, colonIndex).trim()
        content = trimmedLine.substring(colonIndex + 1).trim()
      } else {
        title = `知识条目 ${new Date().toLocaleString()}`
        content = trimmedLine
      }
      
      try {
        const response = await createDocument(currentKnowledgeBase.value.id, {
          title,
          content
        })
        
        if (response.code === 200) {
          successCount++
        } else {
          failCount++
          console.error('导入条目失败:', response.msg)
        }
      } catch (error) {
        failCount++
        console.error('导入条目出错:', error)
      }
    }
    
    if (successCount > 0) {
      message.success(`成功导入 ${successCount} 条知识，失败 ${failCount} 条`)
      bulkImportContent.value = ''
      await loadDocuments(currentKnowledgeBase.value.id)
      activeTab.value = 'documents'
    } else if (failCount > 0) {
      message.error(`导入失败，全部 ${failCount} 条导入失败`)
    } else {
      message.warning('没有有效的内容需要导入')
    }
  } catch (error) {
    message.error('批量导入失败: ' + error.message)
  } finally {
    docModalLoading.value = false
  }
}
</script>

<template>
  <CommonPage>
    <div class="kb-container">
      <!-- 操作栏 -->
      <div class="action-bar">
        <NSpace>
          <NButton type="primary" @click="handleAdd">
            <template #icon>
              <NIcon>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6z" />
                </svg>
              </NIcon>
            </template>
            新建知识库
          </NButton>
          <NButton @click="loadKnowledgeBases">
            <template #icon>
              <NIcon>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M17.65 6.35A7.958 7.958 0 0 0 12 4a8 8 0 0 0-8 8a8 8 0 0 0 8 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0 1 12 18a6 6 0 0 1-6-6a6 6 0 0 1 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4z" />
                </svg>
              </NIcon>
            </template>
            刷新
          </NButton>
        </NSpace>
      </div>

      <!-- 数据表格 -->
      <NDataTable
        :columns="columns"
        :data="kbList"
        :loading="loading"
        :pagination="pagination"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
        :bordered="false"
        striped
        size="medium"
      />

      <!-- 知识库模态框 -->
      <NModal
        v-model:show="modalVisible"
        preset="card"
        :title="modalTitle"
        :style="{ width: '500px' }"
      >
        <NForm
          ref="modalFormRef"
          :model="modalForm"
          :rules="rules"
          label-placement="left"
          label-width="80"
          require-mark-placement="right-hanging"
        >
          <NFormItem label="名称" path="name">
            <NInput v-model:value="modalForm.name" placeholder="请输入知识库名称" />
          </NFormItem>
          <NFormItem label="描述" path="description">
            <NInput 
              type="textarea" 
              v-model:value="modalForm.description" 
              placeholder="请输入知识库描述" 
              :autosize="{ minRows: 3, maxRows: 5 }"
            />
          </NFormItem>
        </NForm>
        <template #footer>
          <NSpace justify="end">
            <NButton @click="modalVisible = false">取消</NButton>
            <NButton type="primary" :loading="modalLoading" @click="handleSave">确定</NButton>
          </NSpace>
        </template>
      </NModal>
      
      <!-- 文档管理模态框 -->
      <NModal
        v-model:show="docModalVisible"
        preset="card"
        :title="docModalTitle"
        :style="{ width: '800px' }"
        :segmented="{ footer: 'soft' }"
      >
        <NTabs v-model:value="activeTab" type="line" animated>
          <NTabPane name="documents" tab="文档列表">
            <NDataTable
              :columns="documentColumns"
              :data="documentsList"
              :loading="documentsLoading"
              :bordered="false"
              striped
              size="small"
            />
            
            <div v-if="!documentsLoading && documentsList.length === 0" class="empty-state">
              <NEmpty description="暂无文档数据" size="small">
                <template #extra>
                  <p class="empty-hint">您可以添加新文档或使用批量导入功能</p>
                </template>
              </NEmpty>
            </div>
            
            <NDivider>添加新文档</NDivider>
            
            <NForm
              ref="newDocFormRef"
              :model="newDocForm"
              :rules="docRules"
              label-placement="left"
              label-width="80"
              require-mark-placement="right-hanging"
            >
              <NFormItem label="标题" path="title">
                <NInput 
                  v-model:value="newDocForm.title" 
                  placeholder="请输入文档标题"
                />
              </NFormItem>
              <NFormItem label="内容" path="content">
                <NInput 
                  type="textarea" 
                  v-model:value="newDocForm.content" 
                  placeholder="请输入文档内容" 
                  :autosize="{ minRows: 3, maxRows: 6 }"
                />
              </NFormItem>
              <NFormItem>
                <NButton 
                  type="primary" 
                  @click="handleAddDocument" 
                  :loading="docModalLoading"
                >
                  添加
                </NButton>
              </NFormItem>
            </NForm>
          </NTabPane>
          
          <NTabPane name="bulkImport" tab="批量导入">
            <div class="bulk-import-container">
              <p class="import-tips">
                每行一条知识，支持"标题:内容"格式，如果不包含冒号，则整行视为内容
              </p>
              
              <NInput 
                type="textarea" 
                v-model:value="bulkImportContent" 
                placeholder="请输入要导入的知识，每行一条..." 
                :autosize="{ minRows: 10, maxRows: 20 }"
              />
              
              <div class="import-actions">
                <NButton 
                  type="primary" 
                  @click="handleBulkImport" 
                  :loading="docModalLoading"
                  :disabled="!bulkImportContent.trim()"
                >
                  导入
                </NButton>
              </div>
              
              <NCollapse>
                <NCollapseItem title="导入格式说明" name="formatHelp">
                  <div class="import-help">
                    <p>批量导入支持两种格式：</p>
                    <ol>
                      <li><strong>标题:内容</strong> - 冒号前为标题，冒号后为内容</li>
                      <li><strong>纯内容</strong> - 整行视为内容，标题将自动生成</li>
                    </ol>
                    <p>示例：</p>
                    <pre>如何使用知识库:知识库是一个存储和管理知识的工具
Python基础:Python是一种高级编程语言
这是一条没有标题的知识</pre>
                  </div>
                </NCollapseItem>
              </NCollapse>
            </div>
          </NTabPane>
        </NTabs>
        
        <template #footer>
          <NSpace justify="end">
            <NButton @click="docModalVisible = false">关闭</NButton>
          </NSpace>
        </template>
      </NModal>
    </div>
  </CommonPage>
</template>

<style scoped>
.kb-container {
  width: 100%;
}

.action-bar {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
}

.empty-state {
  padding: 20px 0;
  text-align: center;
}

.empty-hint {
  font-size: 13px;
  color: var(--text-color-3);
  margin-top: 8px;
}

.bulk-import-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.import-tips {
  font-size: 14px;
  color: var(--text-color-3);
  margin: 0 0 8px;
}

.import-actions {
  display: flex;
  justify-content: flex-start;
  margin: 8px 0;
}

.import-help {
  font-size: 13px;
  line-height: 1.6;
}

.import-help pre {
  background-color: var(--body-color);
  padding: 12px;
  border-radius: 4px;
  font-family: monospace;
  margin: 8px 0;
  white-space: pre-wrap;
}
</style> 