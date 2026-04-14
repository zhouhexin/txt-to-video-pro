<template>
  <div class="video-gen">
    <el-card v-if="!scriptStore.currentScript" class="empty-card">
      <el-empty description="请先生成剧本和分镜图">
        <el-button type="primary" @click="router.push('/script')">去生成剧本</el-button>
      </el-empty>
    </el-card>
    
    <template v-else>
      <!-- 视频配置 -->
      <VideoConfig
        v-model:duration="defaultDuration"
        v-model:resolution="resolution"
        v-model:mode="taskStore.genMode"
        v-model:first-last-mode="firstLastMode"
      />
      
      <el-card class="video-card" style="margin-top: 20px">
        <template #header>
          <div class="card-header">
            <h2>视频片段生成</h2>
            <el-button 
              type="primary" 
              :loading="generatingAll"
              :disabled="!hasImages"
              @click="handleGenerateAll"
            >
              {{ generatingAll ? '批量生成中...' : '🚀 批量生成所有视频' }}
            </el-button>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col 
            v-for="(shot, index) in scriptStore.currentScript.shots" 
            :key="index" 
            :span="8"
            style="margin-bottom: 20px"
          >
            <el-card shadow="hover">
              <div class="shot-header">
                <h4>{{ shot.scene }}</h4>
                <el-tag size="small" type="info">{{ shot.duration || defaultDuration }}秒</el-tag>
              </div>
              
              <div v-if="images[index]?.status === 'completed'" class="image-preview">
                <img :src="images[index].url" alt="分镜图" />
              </div>
              <div v-else class="no-image">
                <el-empty :image-size="80" description="请先生成分镜图" />
              </div>
              
              <div v-if="videos[index]?.status === 'completed'" class="video-preview">
                <video :src="videos[index].url" controls style="width: 100%; border-radius: 8px" />
              </div>
              <div v-else-if="videos[index]?.status === 'running'" class="loading-state">
                <el-spinner />
                <p>视频生成中...</p>
              </div>
              
              <el-button 
                :loading="videos[index]?.status === 'running'"
                :disabled="images[index]?.status !== 'completed'"
                @click="handleGenerateSingle(index, shot.duration || defaultDuration, shot.camera)"
                style="width: 100%; margin-top: 10px"
              >
                {{ videos[index]?.status === 'completed' ? '重新生成' : '生成此镜头视频' }}
              </el-button>
            </el-card>
          </el-col>
        </el-row>
        
        <el-divider />
        
        <div class="merge-section">
          <el-button 
            type="success" 
            size="large"
            :disabled="!canMerge"
            :loading="merging"
            @click="handleMerge"
            style="width: 100%"
          >
            {{ merging ? '合并中...' : '🎞️ 合并为完整视频' }}
          </el-button>
          
          <div v-if="mergedVideo" class="merged-video">
            <h3>完整视频</h3>
            <video :src="mergedVideo.url" controls style="width: 100%; max-height: 500px; border-radius: 8px" />
            <el-button type="primary" @click="handleFinish" style="margin-top: 10px">
              ✨ 完成，查看成果
            </el-button>
          </div>
        </div>
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useScriptStore } from '@/stores/script'
import { useTaskStore } from '@/stores/task'
import { useUIStore } from '@/stores/ui'
import { getTaskImages } from '@/api/images'
import { generateVideo, getTaskVideos, mergeVideos } from '@/api/videos'
import VideoConfig from '@/components/VideoConfig.vue'

const router = useRouter()
const scriptStore = useScriptStore()
const taskStore = useTaskStore()
const uiStore = useUIStore()

const defaultDuration = ref(5)
const resolution = ref('480P')
const firstLastMode = ref(false)
const generatingAll = ref(false)
const merging = ref(false)
const images = ref<any[]>([])
const videos = ref<any[]>([])
const mergedVideo = ref<any>(null)

const hasImages = computed(() => {
  return images.value.some(img => img.status === 'completed')
})

const canMerge = computed(() => {
  if (!scriptStore.currentScript) return false
  return videos.value.length === scriptStore.currentScript.shots.length &&
         videos.value.every(v => v.status === 'completed')
})

onMounted(async () => {
  if (taskStore.taskId) {
    await Promise.all([loadImages(), loadVideos()])
  }
})

const loadImages = async () => {
  try {
    const result = await getTaskImages(taskStore.taskId!)
    images.value = result.images
  } catch (err) {
    // 正常
  }
}

const loadVideos = async () => {
  try {
    const result = await getTaskVideos(taskStore.taskId!)
    videos.value = result.videos
    mergedVideo.value = result.merged_video || null
  } catch (err) {
    // 正常
  }
}

const handleGenerateSingle = async (index: number, duration: number, camera?: string) => {
  if (!taskStore.taskId) return
  
  videos.value[index] = { status: 'running' }
  
  try {
    const result = await generateVideo({
      task_id: taskStore.taskId,
      shot_index: index,
      duration: duration,
      mode: taskStore.genMode,
      resolution: resolution.value,
      camera_motion: camera || 'push'
    })
    
    videos.value[index] = {
      ...result,
      shot_index: index,
      status: 'completed'
    }
    
    uiStore.showSuccess(`镜头${index + 1} 视频生成成功`)
    await loadVideos()
  } catch (err: any) {
    videos.value[index] = { status: 'failed' }
    uiStore.showError(err.message)
  }
}

const handleGenerateAll = async () => {
  if (!scriptStore.currentScript || !taskStore.taskId) return
  
  generatingAll.value = true
  
  try {
    for (let i = 0; i < scriptStore.currentScript.shots.length; i++) {
      const shot = scriptStore.currentScript.shots[i]
      
      if (images.value[i]?.status !== 'completed') continue
      
      videos.value[i] = { status: 'running' }
      
      try {
        await generateVideo({
          task_id: taskStore.taskId,
          shot_index: i,
          duration: shot.duration || defaultDuration.value,
          mode: taskStore.genMode,
          resolution: resolution.value,
          camera_motion: shot.camera || 'push'
        })
        
        videos.value[i] = { status: 'completed' }
      } catch (err: any) {
        videos.value[i] = { status: 'failed' }
        uiStore.showError(`镜头${i + 1} 生成失败`)
      }
    }
    
    uiStore.showSuccess('所有视频片段生成完成')
    await loadVideos()
  } finally {
    generatingAll.value = false
  }
}

const handleMerge = async () => {
  if (!taskStore.taskId) return
  
  merging.value = true
  
  try {
    const result = await mergeVideos(taskStore.taskId)
    mergedVideo.value = result
    uiStore.showSuccess('视频合并成功')
  } catch (err: any) {
    uiStore.showError(err.message)
  } finally {
    merging.value = false
  }
}

const handleFinish = () => {
  router.push('/showcase')
}
</script>

<style scoped>
.video-gen {
  max-width: 1200px;
  margin: 0 auto;
}

.empty-card {
  max-width: 600px;
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

.shot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.shot-header h4 {
  margin: 0;
  font-size: 15px;
}

.image-preview img {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 10px;
}

.no-image {
  margin: 20px 0;
}

.video-preview {
  margin: 10px 0;
}

.loading-state {
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
}

.merge-section {
  margin-top: 20px;
}

.merged-video h3 {
  margin-bottom: 10px;
}
</style>
