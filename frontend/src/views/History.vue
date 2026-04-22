<template>
  <div class="history">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>📜 历史剧本</h2>
          <div class="search-bar">
            <el-input
              v-model="searchQuery"
              placeholder="搜索剧本标题或主题"
              style="width: 300px"
              clearable
              @input="handleSearch"
            />
            <el-select 
              v-model="filterType" 
              placeholder="视频类型" 
              clearable
              style="width: 150px; margin-left: 10px"
              @change="handleFilter"
            >
              <el-option label="文旅宣传" value="文旅宣传" />
              <el-option label="产品展示" value="产品展示" />
              <el-option label="教程视频" value="教程视频" />
              <el-option label="故事短片" value="故事短片" />
              <el-option label="企业宣传片" value="企业宣传片" />
            </el-select>
          </div>
        </div>
      </template>
      
      <el-table 
        :data="filteredScripts" 
        style="width: 100%" 
        v-loading="scriptStore.isLoading"
        @row-click="handleRowClick"
      >
        <el-table-column prop="title" label="标题" min-width="150" header-align="center" align="left" />
        <el-table-column prop="theme" label="主题提示词" width="450" header-align="center" align="left"/>
        <el-table-column prop="video_type" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.video_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="shots" label="分镜数" width="70" align="center">
          <template #default="{ row }">
            {{ row.shots?.length || 0 }}
          </template>
        </el-table-column>
<!--        <el-table-column prop="task_id" label="任务 ID" width="120">-->
<!--          <template #default="{ row }">-->
<!--            <span v-if="row.task_id" style="font-size: 12px; color: #606266;">{{ row.task_id.substring(0, 8) }}...</span>-->
<!--            <span v-else style="color: #999; font-size: 12px">未生成</span>-->
<!--          </template>-->
<!--        </el-table-column>-->
        <el-table-column prop="created_at" label="创建时间" width="120" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" @click.stop="handleView(row)">查看</el-button>
            <el-button size="small" type="primary" @click.stop="handleUse(row)">使用</el-button>
            <el-button size="small" type="danger" @click.stop="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="filteredScripts.length === 0 && !scriptStore.isLoading" description="还没有历史剧本" />
      
      <!-- 分页 -->
      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
    
    <!-- 剧本详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="剧本详情"
      width="900px"
    >
      <div v-if="selectedScript" class="script-detail">
        <ScriptPreview :script="selectedScript" />
        
        <el-divider>操作</el-divider>
        
        <div class="actions">
          <el-button type="primary" @click="handleReuseScript">
            🚀 使用此剧本生成分镜
          </el-button>
          <el-button @click="handleEditScript">
            ✏️ 编辑剧本
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useScriptStore } from '@/stores/script'
import { useTaskStore } from '@/stores/task'
import { useUIStore } from '@/stores/ui'
import ScriptPreview from '@/components/ScriptPreview.vue'
import { deleteScript } from '@/api/scripts'

const router = useRouter()
const route = useRoute()
const scriptStore = useScriptStore()
const taskStore = useTaskStore()
const uiStore = useUIStore()

const loading = ref(false)
const searchQuery = ref('')
const filterType = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showDetailDialog = ref(false)
const selectedScript = ref<any>(null)

const filteredScripts = computed(() => {
  let result = scriptStore.scriptList
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(script => 
      script.title.toLowerCase().includes(query) ||
      script.theme.toLowerCase().includes(query)
    )
  }
  
  // 类型过滤
  if (filterType.value) {
    result = result.filter(script => script.video_type === filterType.value)
  }
  
  return result
})

onMounted(async () => {
  await loadScripts()
  
  // 检查是否有重用参数
  if (route.query.reuse) {
    const scriptId = parseInt(route.query.reuse as string)
    const script = scriptStore.scriptList.find(s => s.id === scriptId)
    if (script) {
      handleUse(script)
    }
  }
})

const loadScripts = async () => {
  loading.value = true
  try {
    await scriptStore.fetchList({
      limit: pageSize.value
    })
    total.value = scriptStore.scriptList.length
  } catch (err: any) {
    uiStore.showError(err.message)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  currentPage.value = 1
}

const handleRowClick = (_row: any) => {
  // 点击行不触发，避免误操作
}

const handleView = (script: any) => {
  selectedScript.value = script
  showDetailDialog.value = true
}

const handleUse = (script: any) => {
  scriptStore.setCurrentScript(script)
  if (script.task_id) {
    taskStore.setTaskId(script.task_id)
  }
  uiStore.showSuccess(`已加载剧本：${script.title}`)
  router.push('/image')
}

const handleReuseScript = () => {
  if (selectedScript.value) {
    handleUse(selectedScript.value)
    showDetailDialog.value = false
  }
}

const handleEditScript = () => {
  uiStore.showInfo('编辑功能开发中...')
}

const handleDelete = async (script: any) => {
  try {
    await deleteScript(script.id)
    uiStore.showSuccess('删除成功')
    await loadScripts()
  } catch (err: any) {
    uiStore.showError(err.message)
  }
}

const formatDate = (dateStr: string | null | undefined) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.history {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
}

.search-bar {
  display: flex;
  align-items: center;
}

.script-detail {
  padding: 10px 0;
}

.actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
