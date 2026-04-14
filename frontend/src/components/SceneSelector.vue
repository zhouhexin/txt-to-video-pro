<template>
  <div class="scene-selector">
    <el-form-item label="场景类型">
      <el-select 
        v-model="selectedScene" 
        placeholder="选择场景类型（可选）"
        clearable
        style="width: 100%"
        @change="handleSceneChange"
      >
        <el-option
          v-for="(style, key) in scenes"
          :key="key"
          :label="key"
          :value="key"
        >
          <div class="scene-option">
            <span class="scene-name">{{ key }}</span>
            <span class="scene-desc">{{ style.style }}</span>
          </div>
        </el-option>
      </el-select>
    </el-form-item>
    
    <!-- 场景详情 -->
    <el-card v-if="selectedScene && scenes[selectedScene]" class="scene-detail" shadow="never">
      <template #header>
        <div class="card-header">
          <span>📍 {{ selectedScene }}</span>
          <el-tag size="small">{{ scenes[selectedScene].camera_motion }}</el-tag>
        </div>
      </template>
      
      <el-descriptions :column="1" size="small">
        <el-descriptions-item label="场景特点">
          {{ scenes[selectedScene].style }}
        </el-descriptions-item>
        <el-descriptions-item label="氛围">
          {{ scenes[selectedScene].atmosphere }}
        </el-descriptions-item>
        <el-descriptions-item label="推荐运镜">
          <el-tag size="small" type="info">
            {{ cameraMotions[scenes[selectedScene].camera_motion] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="推荐时长">
          {{ scenes[selectedScene].duration }}秒
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

const props = defineProps<{
  modelValue?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string | null): void
}>()

const selectedScene = ref<string | undefined>(props.modelValue)
const scenes = ref<any>({})
const cameraMotions = ref<any>({})
const loading = ref(false)

// 加载场景风格列表
const loadSceneStyles = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/prompts/scenes')
    scenes.value = response.data.scenes
    cameraMotions.value = response.data.camera_motions
  } catch (error) {
    console.error('加载场景风格失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSceneChange = (value: string | null) => {
  emit('update:modelValue', value || '')
  emit('change', value)
}

onMounted(() => {
  loadSceneStyles()
})

watch(() => props.modelValue, (value) => {
  selectedScene.value = value
})
</script>

<style scoped>
.scene-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.scene-name {
  font-weight: 500;
}

.scene-desc {
  font-size: 12px;
  color: #666;
}

.scene-detail {
  margin-top: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
