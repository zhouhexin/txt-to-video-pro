<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div class="confirm-content">
      <el-alert
        :type="alertType"
        :title="alertTitle"
        :description="description"
        :closable="false"
        show-icon
      />
      
      <!-- 图片预览 -->
      <div v-if="images.length > 0" class="image-preview">
        <h4>生成的分镜图：</h4>
        <el-row :gutter="10">
          <el-col v-for="(img, index) in images" :key="index" :span="8">
            <el-card shadow="hover">
              <img :src="img.url" :alt="`分镜${index + 1}`" style="width: 100%; border-radius: 8px" />
              <p style="text-align: center; margin-top: 8px; font-size: 13px">
                镜头 {{ index + 1 }}
              </p>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 状态信息 -->
      <div class="status-info">
        <el-descriptions :column="1" size="small" border>
          <el-descriptions-item label="任务 ID">{{ taskId }}</el-descriptions-item>
          <el-descriptions-item label="当前状态">
            <el-tag :type="getStatusType(taskStatus)">
              {{ getStatusText(taskStatus) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="生成进度">{{ progress }}%</el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button 
          v-if="showRetry" 
          type="warning" 
          @click="handleRetry"
        >
          🔄 重新生成
        </el-button>
        
        <el-button 
          v-if="showCancel" 
          @click="handleCancel"
        >
          ❌ 取消
        </el-button>
        
        <el-button 
          v-if="showConfirm" 
          type="primary" 
          @click="handleConfirm"
        >
          ✅ 确认继续
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import axios from 'axios'

const props = defineProps<{
  modelValue: boolean
  taskId?: string
  images?: any[]
  title?: string
  description?: string
  taskStatus?: string
  progress?: number
  showConfirm?: boolean
  showRetry?: boolean
  showCancel?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm'): void
  (e: 'retry'): void
  (e: 'cancel'): void
  (e: 'close'): void
}>()

const dialogVisible = ref(props.modelValue)

const alertType = computed(() => {
  if (props.taskStatus === 'waiting_confirm') return 'warning'
  if (props.taskStatus === 'failed') return 'error'
  return 'info'
})

const alertTitle = computed(() => {
  if (props.taskStatus === 'waiting_confirm') return '请确认分镜图'
  if (props.taskStatus === 'failed') return '生成失败'
  return '生成完成'
})

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

const handleConfirm = async () => {
  if (!props.taskId) {
    console.error('任务 ID 为空')
    return
  }
  
  try {
    // 从 task_id 提取 script_id (格式：task_timestamp_scriptId)
    const parts = props.taskId.split('_')
    const scriptId = parts[parts.length - 1]
    
    // 调用剧本确认接口
    const response = await axios.put(`/api/v1/scripts/${scriptId}/confirm`)
    
    if (response.data.success) {
      emit('confirm')
      dialogVisible.value = false
    } else {
      throw new Error(response.data.error || '确认失败')
    }
  } catch (error: any) {
    console.error('确认失败:', error)
    // 显示错误提示
    alert('确认失败：' + (error.response?.data?.error || error.message))
    // 仍然触发 confirm 事件，让前端可以继续
    emit('confirm')
    dialogVisible.value = false
  }
}

const handleRetry = async () => {
  if (!props.taskId) return
  
  try {
    await axios.put(`/api/v1/tasks/${props.taskId}/retry`)
    emit('retry')
    dialogVisible.value = false
  } catch (error: any) {
    console.error('重试失败:', error)
  }
}

const handleCancel = async () => {
  if (!props.taskId) return
  
  try {
    await axios.post(`/api/v1/tasks/${props.taskId}/cancel`)
    emit('cancel')
    dialogVisible.value = false
  } catch (error: any) {
    console.error('取消失败:', error)
  }
}

watch(() => props.modelValue, (value) => {
  dialogVisible.value = value
})

watch(dialogVisible, (value) => {
  emit('update:modelValue', value)
  if (!value) {
    emit('close')
  }
})
</script>

<style scoped>
.confirm-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.image-preview h4 {
  margin-bottom: 10px;
}

.status-info {
  margin-top: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
