<template>
  <div class="showcase">
    <el-card class="showcase-card">
      <template #header>
        <h2>📊 成果展示</h2>
      </template>
      
      <div v-if="scriptStore.currentScript" class="project-info">
        <h1>{{ scriptStore.currentScript.title }}</h1>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="主题">{{ scriptStore.currentScript.theme }}</el-descriptions-item>
          <el-descriptions-item label="类型">{{ scriptStore.currentScript.video_type }}</el-descriptions-item>
          <el-descriptions-item label="关键词">{{ scriptStore.currentScript.keywords }}</el-descriptions-item>
          <el-descriptions-item label="分镜数">{{ scriptStore.currentScript.shots?.length || 0 }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider />
        
        <h3>完整视频</h3>
        <div v-if="mergedVideo" class="video-container">
          <video :src="mergedVideo.url" controls style="width: 100%; max-height: 600px; border-radius: 12px" />
          <div class="video-actions">
            <el-button type="primary" @click="handleDownload">
              <el-icon><Download /></el-icon> 下载视频
            </el-button>
            <el-button @click="handleNewProject">
              新建项目
            </el-button>
          </div>
        </div>
        <el-empty v-else description="还没有生成完整视频">
          <el-button type="primary" @click="router.push('/video')">去生成视频</el-button>
        </el-empty>
        
        <el-divider />
        
        <h3>分镜预览</h3>
        <el-row :gutter="10">
          <el-col v-for="(shot, i) in scriptStore.currentScript.shots" :key="i" :span="6">
            <el-card shadow="hover">
              <img 
                v-if="images[i]?.status === 'completed'" 
                :src="images[i].url" 
                :alt="shot.scene"
                style="width: 100%; border-radius: 8px"
              />
              <div v-else class="placeholder">
                <el-icon><Picture /></el-icon>
              </div>
              <p style="margin-top: 8px; font-size: 13px">{{ shot.scene }}</p>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <el-empty v-else description="还没有项目，去创建一个吧">
        <el-button type="primary" @click="router.push('/script')">开始创作</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useScriptStore } from '@/stores/script'
import { useTaskStore } from '@/stores/task'
import { getTaskImages, getTaskVideos } from '@/api/images'
import { getTaskVideos as getVideos } from '@/api/videos'

const router = useRouter()
const scriptStore = useScriptStore()
const taskStore = useTaskStore()

const images = ref<any[]>([])
const mergedVideo = ref<any>(null)

onMounted(async () => {
  if (taskStore.taskId) {
    try {
      const [imgRes, vidRes] = await Promise.all([
        getTaskImages(taskStore.taskId),
        getVideos(taskStore.taskId)
      ])
      images.value = imgRes.images
      mergedVideo.value = vidRes.merged_video
    } catch (err) {
      // 正常
    }
  }
})

const handleDownload = () => {
  if (mergedVideo.value) {
    const a = document.createElement('a')
    a.href = mergedVideo.value.url
    a.download = 'video.mp4'
    a.click()
  }
}

const handleNewProject = () => {
  taskStore.reset()
  scriptStore.setCurrentScript(null)
  router.push('/script')
}
</script>

<style scoped>
.showcase {
  max-width: 1000px;
  margin: 0 auto;
}

.showcase-card h1 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

.showcase-card h3 {
  margin: 20px 0 10px;
  color: #666;
}

.project-info {
  padding: 10px 0;
}

.video-container {
  margin: 20px 0;
}

.video-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.placeholder {
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 8px;
  color: #999;
  font-size: 48px;
}
</style>
