<template>
  <div class="task-history">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>📹 任务历史</h2>
          <el-input
            v-model="searchQuery"
            placeholder="搜索任务 ID 或剧本主题"
            style="width: 300px"
            clearable
            @input="handleSearch"
          />
        </div>
      </template>
      
      <el-table 
        :data="filteredTasks" 
        style="width: 100%" 
        v-loading="loading"
        @row-click="handleRowClick"
      >
        <el-table-column prop="id" label="任务 ID" min-width="180" />
        <el-table-column prop="script_id" label="剧本 ID" width="100" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="step" label="步骤" width="100">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">
              {{ getStepText(row.step) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :status="row.status === 'failed' ? 'exception' : undefined" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click.stop="handleView(row)">查看</el-button>
            <el-button size="small" type="primary" @click.stop="handleReuse(row)">重用</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="filteredTasks.length === 0 && !loading" description="还没有任务记录" />
      
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
    
    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="任务详情"
      width="800px"
    >
      <div v-if="selectedTask" class="task-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务 ID">{{ selectedTask.id }}</el-descriptions-item>
          <el-descriptions-item label="剧本 ID">{{ selectedTask.script_id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedTask.status)">
              {{ getStatusText(selectedTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="步骤">{{ getStepText(selectedTask.step) }}</el-descriptions-item>
          <el-descriptions-item label="进度">{{ selectedTask.progress }}%</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(selectedTask.created_at) }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider>生成成果</el-divider>
        
        <div v-if="taskImages.length > 0" class="images-section">
          <h4>分镜图（{{ taskImages.length }}）</h4>
          <el-row :gutter="10">
            <el-col v-for="img in taskImages" :key="img.id" :span="6">
              <el-card shadow="hover">
                <img :src="img.url" alt="分镜图" style="width: 100%; border-radius: 8px" />
                <p style="text-align: center; font-size: 13px; margin-top: 5px">
                  镜头 {{ img.shot_index + 1 }}
                </p>
              </el-card>
            </el-col>
          </el-row>
        </div>
        
        <div v-if="taskVideos.length > 0" class="videos-section">
          <h4>视频片段（{{ taskVideos.length }}）</h4>
          <el-row :gutter="10">
            <el-col v-for="vid in taskVideos" :key="vid.id" :span="8">
              <video :src="vid.url" controls style="width: 100%; border-radius: 8px" />
              <p style="text-align: center; font-size: 13px; margin-top: 5px">
                镜头 {{ vid.shot_index + 1 }} - {{ vid.duration }}秒
              </p>
            </el-col>
          </el-row>
          
          <div v-if="mergedVideo" class="merged-video">
            <h4>完整视频</h4>
            <video :src="mergedVideo.url" controls style="width: 100%; max-height: 400px; border-radius: 8px" />
          </div>
        </div>
        
        <el-empty v-if="taskImages.length === 0 && taskVideos.length === 0" description="还没有生成成果" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const loading = ref(false)
const tasks = ref<any[]>([])
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showDetailDialog = ref(false)
const selectedTask = ref<any>(null)
const taskImages = ref<any[]>([])
const taskVideos = ref<any[]>([])
const mergedVideo = ref<any>(null)

const filteredTasks = computed(() => {
  if (!searchQuery.value) {
    return tasks.value
  }
  const query = searchQuery.value.toLowerCase()
  return tasks.value.filter(task => 
    task.id.toLowerCase().includes(query) ||
    task.script_id.toString().includes(query)
  )
})

onMounted(async () => {
  await loadTasks()
})

const loadTasks = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/tasks', {
      params: {
        limit: pageSize.value
      }
    })
    tasks.value = response.data.tasks
    total.value = response.data.total
  } catch (error: any) {
    console.error('加载任务失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleRowClick = (row: any) => {
  // 点击行不触发，避免误操作
}

const handleView = async (task: any) => {
  selectedTask.value = task
  showDetailDialog.value = true
  
  // 加载任务的图片和视频
  try {
    const [imgRes, vidRes] = await Promise.all([
      axios.get(`/api/v1/images/${task.id}`),
      axios.get(`/api/v1/videos/${task.id}`)
    ])
    
    taskImages.value = imgRes.data.images.filter((img: any) => img.status === 'completed')
    taskVideos.value = vidRes.data.videos.filter((vid: any) => vid.status === 'completed')
    mergedVideo.value = vidRes.data.merged_video
  } catch (error) {
    console.error('加载任务成果失败:', error)
  }
}

const handleReuse = (task: any) => {
  // 重用任务，跳转到对应的剧本
  router.push(`/history?reuse=${task.script_id}`)
}

const getStatusType = (status: string) => {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    completed: 'success',
    waiting_confirm: 'warning',
    running: 'warning',
    failed: 'danger',
    cancelled: 'info',
    pending: 'info'
  }
  return map[status || 'pending'] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    completed: '已完成',
    waiting_confirm: '等待确认',
    running: '生成中',
    failed: '失败',
    cancelled: '已取消',
    pending: '待处理'
  }
  return map[status || 'pending'] || status
}

const getStepText = (step: string) => {
  const map: Record<string, string> = {
    script: '剧本',
    image: '分镜',
    video: '视频'
  }
  return map[step || ''] || step
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.task-history {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
}

.task-detail {
  padding: 10px 0;
}

.task-detail h4 {
  margin: 20px 0 10px;
  color: #666;
}

.images-section, .videos-section {
  margin-top: 15px;
}

.merged-video {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}
</style>
