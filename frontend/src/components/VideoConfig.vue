<template>
  <div class="video-config">
    <el-card>
      <template #header>
        <h3>🎬 视频生成配置</h3>
      </template>
      
      <el-form :model="config" label-width="100px" label-position="top">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="视频时长">
              <el-slider 
                v-model="config.duration" 
                :min="3" 
                :max="10" 
                :step="1" 
                show-input
                :disabled="disabled"
              />
              <p class="form-hint">推荐：5-8 秒</p>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="分辨率">
              <el-select 
                v-model="config.resolution" 
                placeholder="选择分辨率"
                style="width: 100%"
                :disabled="disabled"
              >
                <el-option label="480P (标清)" value="480P" />
                <el-option label="720P (高清)" value="720P" />
                <el-option label="1080P (超清)" value="1080P" />
              </el-select>
              <p class="form-hint">分辨率越高，生成时间越长</p>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="生成模式">
              <el-radio-group v-model="config.mode" :disabled="disabled">
                <el-radio-button label="single">单镜头</el-radio-button>
                <el-radio-button label="chain">链式连续</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="首尾帧模式">
              <el-switch 
                v-model="config.firstLastMode"
                :disabled="disabled"
                active-text="启用"
                inactive-text="禁用"
              />
              <p class="form-hint">启用后用相邻分镜图作为首尾帧，视频过渡更连贯</p>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 预估时间 -->
        <el-alert
          type="info"
          :closable="false"
          show-icon
        >
          <template #title>
            <div>
              <strong>预估生成时间：</strong>
              <span>{{ estimatedTime }}</span>
            </div>
          </template>
        </el-alert>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'

const props = defineProps<{
  duration?: number
  resolution?: string
  mode?: string
  firstLastMode?: boolean
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:duration', value: number): void
  (e: 'update:resolution', value: string): void
  (e: 'update:mode', value: string): void
  (e: 'update:firstLastMode', value: boolean): void
}>()

const config = reactive({
  duration: props.duration || 5,
  resolution: props.resolution || '480P',
  mode: props.mode || 'single',
  firstLastMode: props.firstLastMode || false
})

const estimatedTime = computed(() => {
  const baseTime = config.duration * 30 // 每秒约 30 秒生成时间
  const resolutionMultiplier = {
    '480P': 1,
    '720P': 1.5,
    '1080P': 2
  }
  const totalSeconds = Math.round(baseTime * resolutionMultiplier[config.resolution])
  
  if (totalSeconds < 60) {
    return `${totalSeconds}秒`
  } else {
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = totalSeconds % 60
    return `${minutes}分${seconds}秒`
  }
})

watch(() => config.duration, (value) => {
  emit('update:duration', value)
})

watch(() => config.resolution, (value) => {
  emit('update:resolution', value)
})

watch(() => config.mode, (value) => {
  emit('update:mode', value)
})

watch(() => config.firstLastMode, (value) => {
  emit('update:firstLastMode', value)
})
</script>

<style scoped>
.video-config {
  margin-top: 20px;
}

.video-config h3 {
  margin: 0;
  font-size: 16px;
}

.form-hint {
  margin-top: 5px;
  font-size: 12px;
  color: #666;
}
</style>
