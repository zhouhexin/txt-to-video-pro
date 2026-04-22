<template>
  <div class="prompt-optimizer">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>🤖 提示词优化</h3>
          <el-button 
            type="primary" 
            size="small"
            :loading="optimizing"
            @click="handleOptimize"
          >
            {{ optimizing ? '优化中...' : '✨ 优化提示词' }}
          </el-button>
        </div>
      </template>
      
      <el-form label-position="top">
        <el-form-item label="原始提示词">
          <el-input
            v-model="originalPrompt"
            type="textarea"
            :rows="3"
            placeholder="输入简单的提示词，例如：大唐芙蓉园夜景"
            :disabled="optimizing"
          />
        </el-form-item>
        
        <el-form-item label="优化后的提示词">
          <el-input
            v-model="optimizedPrompt"
            type="textarea"
            :rows="5"
            placeholder="点击优化按钮，AI 将自动生成详细提示词"
            readonly
          />
        </el-form-item>
        
        <el-alert
          v-if="optimizationError"
          type="error"
          :title="optimizationError"
          :closable="false"
          show-icon
        />
        
        <el-alert
          v-else-if="optimizedPrompt"
          type="success"
          title="优化成功！你可以手动调整优化结果。"
          :closable="false"
          show-icon
        />
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import axios from 'axios'

const props = defineProps<{
  originalPrompt?: string
  optimizedPrompt?: string
  sceneType?: string
  taskId?: string
}>()

const emit = defineEmits<{
  (e: 'update:originalPrompt', value: string): void
  (e: 'update:optimizedPrompt', value: string): void
}>()

const originalPrompt = ref(props.originalPrompt || '')
const optimizedPrompt = ref(props.optimizedPrompt || '')
const optimizing = ref(false)
const optimizationError = ref('')

const handleOptimize = async () => {
  if (!originalPrompt.value.trim()) {
    optimizationError.value = '请输入原始提示词'
    return
  }
  
  optimizing.value = true
  optimizationError.value = ''
  
  try {
    const response = await axios.post('/api/v1/prompts/optimize', {
      prompt: originalPrompt.value,
      scene_type: props.sceneType || undefined,
      task_id: props.taskId || undefined
    })
    
    const result = response.data
    
    if (result.success) {
      optimizedPrompt.value = result.optimized
      emit('update:optimizedPrompt', result.optimized)
    } else {
      optimizationError.value = result.error || '优化失败'
      // 失败时也返回原始提示词
      optimizedPrompt.value = result.optimized || originalPrompt.value
    }
  } catch (error: any) {
    optimizationError.value = error.message || '优化失败，请重试'
  } finally {
    optimizing.value = false
  }
}

watch(() => props.originalPrompt, (value) => {
  if (value !== undefined) {
    originalPrompt.value = value
  }
})

watch(() => props.optimizedPrompt, (value) => {
  if (value !== undefined) {
    optimizedPrompt.value = value
  }
})
</script>

<style scoped>
.prompt-optimizer {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
}
</style>
