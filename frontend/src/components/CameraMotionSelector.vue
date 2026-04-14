<template>
  <div class="camera-motion-selector">
    <el-form-item :label="label || '镜头运动'">
      <el-select 
        v-model="selectedMotion" 
        :placeholder="placeholder"
        clearable
        style="width: 100%"
        @change="handleMotionChange"
      >
        <el-option
          v-for="(desc, key) in motions"
          :key="key"
          :label="key"
          :value="key"
        >
          <div class="motion-option">
            <span class="motion-name">{{ key }}</span>
            <span class="motion-desc">{{ desc }}</span>
          </div>
        </el-option>
      </el-select>
    </el-form-item>
    
    <!-- 镜头运动说明 -->
    <el-card v-if="selectedMotion && motions[selectedMotion]" class="motion-detail" shadow="never">
      <div class="motion-info">
        <el-icon class="motion-icon"><VideoCamera /></el-icon>
        <div class="motion-text">
          <strong>{{ selectedMotion }}</strong>
          <p>{{ motions[selectedMotion] }}</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

const props = defineProps<{
  modelValue?: string
  label?: string
  placeholder?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string | null): void
}>()

const selectedMotion = ref<string | undefined>(props.modelValue)
const motions = ref<any>({})
const loading = ref(false)

// 加载镜头运动列表
const loadCameraMotions = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/prompts/scenes')
    motions.value = response.data.camera_motions
  } catch (error) {
    console.error('加载镜头运动失败:', error)
    // 使用默认值
    motions.value = {
      'push': '缓慢的镜头推进，靠近主体，展示细节',
      'pull': '镜头缓缓拉远，展现更广阔的场景',
      'pan': '水平摇摄镜头，从左到右平滑移动',
      'tilt': '垂直倾斜镜头，从上到下缓慢移动',
      'zoom': '变焦效果，聚焦关键细节',
      'orbit': '环绕拍摄，360 度展示主体'
    }
  } finally {
    loading.value = false
  }
}

const handleMotionChange = (value: string | null) => {
  emit('update:modelValue', value || '')
  emit('change', value)
}

onMounted(() => {
  loadCameraMotions()
})

watch(() => props.modelValue, (value) => {
  selectedMotion.value = value
})
</script>

<style scoped>
.motion-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.motion-name {
  font-weight: 500;
}

.motion-desc {
  font-size: 12px;
  color: #666;
}

.motion-detail {
  margin-top: 10px;
}

.motion-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.motion-icon {
  font-size: 24px;
  color: #409EFF;
}

.motion-text strong {
  display: block;
  margin-bottom: 4px;
  color: #333;
}

.motion-text p {
  margin: 0;
  font-size: 13px;
  color: #666;
}
</style>
