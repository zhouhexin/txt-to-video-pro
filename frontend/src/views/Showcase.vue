<template>
  <div class="showcase">
    <el-card class="showcase-card">
      <template #header>
        <div class="card-header">
          <h2>📊 成果展示</h2>
          <el-input
            v-model="searchQuery"
            placeholder="搜索剧本标题或主题"
            style="width: 300px"
            clearable
            @input="handleSearch"
          />
        </div>
      </template>
      
      <el-empty v-if="completedTasks.length === 0 && !loading" description="还没有完成的任务">
        <el-button type="primary" @click="router.push('/script')">开始创作</el-button>
      </el-empty>
      
      <el-table 
        v-else
        :data="filteredTasks" 
        style="width: 100%" 
        v-loading="loading"
        @row-click="handleRowClick"
      >
        <el-table-column prop="script_title" label="剧本标题" min-width="200" />
        <el-table-column prop="script_theme" label="主题" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag type="success">已完成</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click.stop="handleView(row)">查看成果</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 成果详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="成果详情"
      width="900px"
    >
      <div v-if="selectedTask" class="task-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="剧本标题">{{ selectedTask.script_title }}</el-descriptions-item>
          <el-descriptions-item label="主题">{{ selectedTask.script_theme }}</el-descriptions-item>
          <el-descriptions-item label="视频类型">{{ selectedTask.script_video_type }}</el-descriptions-item>
          <el-descriptions-item label="分镜数">{{ selectedTask.script_shots?.length || 0 }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider>分镜预览</el-divider>
        
        <div v-if="taskImages.length > 0" class="images-section">
          <el-row :gutter="10">
            <el-col v-for="(img, i) in taskImages" :key="img.id" :span="6">
              <el-card shadow="hover">
                <img :src="img.url" alt="分镜图" style="width: 100%; border-radius: 8px" />
                <p style="text-align: center; font-size: 13px; margin-top: 5px">
                  镜头 {{ img.shot_index + 1 }}
                </p>
              </el-card>
            </el-col>
          </el-row>
        </div>
        <el-empty v-else description="没有分镜图" />
        
        <el-divider>视频</el-divider>
        
        <div v-if="mergedVideo" class="merged-video">
          <h4>完整视频</h4>
          <video :src="mergedVideo.url" controls style="width: 100%; max-height: 400px; border-radius: 8px" />
          <div class="video-actions">
            <el-button type="primary" @click="handleDownload">
              <el-icon><Download /></el-icon> 下载视频
            </el-button>
          </div>
        </div>
        
        <div v-else-if="taskVideos.length > 0" class="videos-section">
          <h4>视频片段（{{ taskVideos.length }}）</h4>
          <el-row :gutter="10">
            <el-col v-for="vid in taskVideos" :key="vid.id" :span="8">
              <video :src="vid.url" controls style="width: 100%; border-radius: 8px" />
              <p style="text-align: center; font-size: 13px; margin-top: 5px">
                镜头 {{ vid.shot_index + 1 }} - {{ vid.duration }}秒
              </p>
            </el-col>
          </el-row>
        </div>
        
        <el-empty v-else description="还没有生成视频" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Download } from '@element-plus/icons-vue'

const router = useRouter()

const loading = ref(false)
const completedTasks = ref<any[]>([])
const searchQuery = ref('')

const showDetailDialog = ref(false)
const selectedTask = ref<any>(null)
const taskImages = ref<any[]>([])
const taskVideos = ref<any[]>([])
const mergedVideo = ref<any>(null)

const filteredTasks = computed(() => {
  if (!searchQuery.value) {
    return completedTasks.value
  }
  const query = searchQuery.value.toLowerCase()
  return completedTasks.value.filter(task => 
    task.script_title?.toLowerCase().includes(query) ||
    task.script_theme?.toLowerCase().includes(query)
  )
})

onMounted(async () => {
  await loadCompletedTasks()
})

const loadCompletedTasks = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/tasks', {
      params: {
        status: 'completed',
        limit: 50
      }
    })
    completedTasks.value = response.data.tasks || []
  } catch (error: any) {
    console.error('加载任务失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 搜索逻辑已在 computed 中处理
}

const handleRowClick = (row: any) => {
  handleView(row)
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
    
    taskImages.value = imgRes.data.images?.filter((img: any) => img.status === 'completed') || []
    taskVideos.value = vidRes.data.videos?.filter((vid: any) => vid.status === 'completed') || []
    mergedVideo.value = vidRes.data.merged_video
  } catch (error) {
    console.error('加载任务成果失败:', error)
  }
}

const handleDownload = () => {
  if (mergedVideo.value) {
    const a = document.createElement('a')
    a.href = mergedVideo.value.url
    a.download = 'video.mp4'
    a.click()
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.showcase {
  max-width: 1200px;
  margin: 0 auto;
}

.showcase-card {
  margin-bottom: 20px;
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

.video-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}
</style>