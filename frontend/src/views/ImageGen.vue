<template>
  <div class="image-gen">
    <el-card v-if="!scriptStore.currentScript" class="empty-card">
      <el-empty description="请先生成剧本">
        <el-button type="primary" @click="router.push('/script')">去生成剧本</el-button>
      </el-empty>
    </el-card>
    
    <template v-else>
      <ScriptPreview :script="scriptStore.currentScript" />
      
      <el-card class="image-card" style="margin-top: 20px">
        <template #header>
          <div class="card-header">
            <h2>🎨 分镜生成</h2>
            <div class="header-actions">
              <!-- 镜头运动配置 -->
              <CameraMotionSelector 
                v-model="defaultCameraMotion" 
                label="默认运镜"
                placeholder="选择镜头运动"
                style="width: 250px; margin-right: 15px"
              />
              
              <el-button type="primary" :loading="generatingAll" @click="handleGenerateAll">
                {{ generatingAll ? '批量生成中...' : '🚀 批量生成所有分镜' }}
              </el-button>
            </div>
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
                <el-tag size="small">{{ shot.camera || defaultCameraMotion }}</el-tag>
              </div>
              
              <p class="visual-text">{{ shot.visual }}</p>
              
              <div v-if="images[index]?.status === 'completed'" class="image-preview">
                <img :src="images[index].url" alt="分镜图" />
              </div>
              <div v-else-if="images[index]?.status === 'running'" class="loading-state">
                <el-spinner />
                <p>生成中...</p>
              </div>
              <div v-else class="placeholder">
                <el-icon><Picture /></el-icon>
                <p>点击生成</p>
              </div>
              
              <el-button 
                :loading="images[index]?.status === 'running'"
                @click="handleGenerateSingle(index, shot.prompt, shot.camera)"
                style="width: 100%; margin-top: 10px"
              >
                {{ images[index]?.status === 'completed' ? '重新生成' : '生成此镜头' }}
              </el-button>
            </el-card>
          </el-col>
        </el-row>
        
        <el-divider />
        
        <div class="confirm-section">
          <el-button 
            type="success" 
            size="large" 
            :disabled="!allCompleted"
            @click="handleConfirmAndNext"
            style="width: 100%"
          >
            {{ taskStore.taskId && images.some(img => img.status === 'completed') ? '✅ 确认并进入视频生成' : '下一步：视频生成 →' }}
          </el-button>
          
          <p class="confirm-hint" v-if="images.some(img => img.status === 'completed')">
            💡 提示：生成图片后，建议先确认满意再生成视频，避免浪费时间和费用。
          </p>
        </div>
      </el-card>
    </template>
    
    <!-- 确认对话框 -->
    <ConfirmDialog
      v-model="showConfirmDialog"
      :task-id="taskStore.taskId"
      :images="images.filter(img => img.status === 'completed')"
      :task-status="currentTaskStatus"
      :progress="100"
      title="请确认分镜图"
      description="请检查生成的分镜图是否满意，确认后将继续生成视频。"
      :show-confirm="true"
      :show-retry="true"
      :show-cancel="true"
      @confirm="handleConfirmSuccess"
      @retry="handleRetryImages"
      @cancel="handleCancelTask"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useScriptStore } from '@/stores/script'
import { useTaskStore } from '@/stores/task'
import { useUIStore } from '@/stores/ui'
import { generateImage, getTaskImages } from '@/api/images'
import axios from 'axios'
import ScriptPreview from '@/components/ScriptPreview.vue'
import CameraMotionSelector from '@/components/CameraMotionSelector.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const router = useRouter()
const scriptStore = useScriptStore()
const taskStore = useTaskStore()
const uiStore = useUIStore()

const generatingAll = ref(false)
const images = ref<any[]>([])
const defaultCameraMotion = ref('push')
const showConfirmDialog = ref(false)
const currentTaskStatus = ref('pending')

const allCompleted = computed(() => {
  if (!scriptStore.currentScript) return false
  return images.value.length === scriptStore.currentScript.shots.length &&
         images.value.every(img => img.status === 'completed')
})

onMounted(async () => {
  if (taskStore.taskId) {
    await loadImages()
    await loadTaskStatus()
  }
})

const loadImages = async () => {
  try {
    const result = await getTaskImages(taskStore.taskId!)
    images.value = result.images
  } catch (err) {
    // 没有历史记录，正常
  }
}

const loadTaskStatus = async () => {
  try {
    const response = await axios.get(`/api/v1/tasks/${taskStore.taskId}`)
    currentTaskStatus.value = response.data.status
  } catch (err) {
    // 正常
  }
}

const handleGenerateSingle = async (index: number, prompt: string, _camera?: string) => {
  if (!taskStore.taskId) return
  
  images.value[index] = { status: 'running' }
  
  try {
    // 获取主题信息用于增强prompt
    const script = scriptStore.currentScript
    const result = await generateImage({
      task_id: taskStore.taskId,
      shot_index: index,
      prompt,
      theme: script?.theme,           // 传递主题
      video_type: script?.video_type, // 传递视频类型
      style: script?.style            // 传递风格
    })
    
    images.value[index] = {
      ...result,
      shot_index: index,
      status: 'completed'
    }
    
    uiStore.showSuccess(`镜头${index + 1} 生成成功`)
    await loadTaskStatus()
  } catch (err: any) {
    images.value[index] = { status: 'failed' }
    uiStore.showError(err.message)
  }
}

const handleGenerateAll = async () => {
  // 前置检查
  if (!scriptStore.currentScript) {
    uiStore.showError('请先生成剧本')
    return
  }
  if (!taskStore.taskId) {
    uiStore.showError('任务 ID 不存在，请重新生成剧本')
    return
  }
  
  generatingAll.value = true
  
  try {
    // 顺序生成每个分镜
    const totalShots = scriptStore.currentScript.shots.length
        
    for (let i = 0; i < totalShots; i++) {
      const shot = scriptStore.currentScript.shots[i]
      
      // 验证 prompt
      if (!shot.prompt) {
        images.value[i] = { status: 'failed' }
        uiStore.showError(`镜头${i + 1} 缺少 prompt，无法生成`)
        continue
      }
      
      images.value[i] = { status: 'running' }
      
      try {
        // 获取主题信息用于增强prompt
        const script = scriptStore.currentScript
        const result = await generateImage({
          task_id: taskStore.taskId,
          shot_index: i,
          prompt: shot.prompt,
          theme: script?.theme,           // 传递主题
          video_type: script?.video_type, // 传递视频类型
          style: script?.style            // 传递风格
        })
        
        images.value[i] = {
          ...result,
          shot_index: i,
          status: 'completed'
        }
        
        uiStore.showSuccess(`镜头${i + 1} 生成成功`)
      } catch (err: any) {
        images.value[i] = { status: 'failed' }
        uiStore.showError(`镜头${i + 1} 生成失败：${err.message}`)
      }
      
      // 等待 10 秒再生成下一个（最后一个不需要等待）
      if (i < totalShots - 1) {
        uiStore.showInfo(`等待 10 秒后继续生成下一个分镜...`)
        await new Promise(resolve => setTimeout(resolve, 10000))
      }
    }
    
    // 生成完成后，检查是否需要确认
    await loadTaskStatus()
    
    // 检查是否所有分镜都成功
    const successCount = images.value.filter(img => img.status === 'completed').length
    if (successCount === totalShots) {
      uiStore.showSuccess('所有分镜图生成完成！')
    } else {
      uiStore.showInfo(`已完成 ${successCount}/${totalShots} 个分镜图`)
    }
  } finally {
    generatingAll.value = false
  }
}

const handleConfirmAndNext = () => {
  // 如果有已完成的图片，显示确认对话框
  if (images.value.some(img => img.status === 'completed')) {
    showConfirmDialog.value = true
  } else {
    // 没有图片，直接下一步
    router.push('/video')
  }
}

const handleConfirmSuccess = () => {
  uiStore.showSuccess('确认成功，进入视频生成')
  router.push('/video')
}

const handleRetryImages = async () => {
  // 重新生成所有图片
  generatingAll.value = true
  images.value = []
  await handleGenerateAll()
}

const handleCancelTask = () => {
  uiStore.showInfo('任务已取消')
  router.push('/script')
}
</script>

<style scoped>
.image-gen {
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
  flex-wrap: wrap;
  gap: 10px;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
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

.visual-text {
  font-size: 13px;
  color: #666;
  margin: 10px 0;
  line-height: 1.5;
}

.image-preview img {
  width: 100%;
  border-radius: 8px;
}

.loading-state, .placeholder {
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  background: #f5f7fa;
  border-radius: 8px;
}

.placeholder .el-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.confirm-section {
  margin-top: 20px;
}

.confirm-hint {
  margin-top: 10px;
  font-size: 13px;
  color: #666;
  text-align: center;
}
</style>
