<template>
  <div class="image-grid">
    <el-row :gutter="15">
      <el-col 
        v-for="(image, index) in images" 
        :key="index" 
        :span="6"
      >
        <el-card shadow="hover" class="image-card">
          <div v-if="image.status === 'completed'" class="image-wrapper">
            <img :src="image.url" :alt="`Shot ${index + 1}`" loading="lazy" />
          </div>
          <div v-else-if="image.status === 'running'" class="loading">
            <el-spinner />
            <p>生成中...</p>
          </div>
          <div v-else class="placeholder">
            <el-icon><Picture /></el-icon>
            <p>待生成</p>
          </div>
          
          <div class="image-footer">
            <span class="shot-label">镜头 {{ index + 1 }}</span>
            <el-tag size="small" :type="getStatusType(image.status)">
              {{ getStatusText(image.status) }}
            </el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import type { TaskImage } from '@/types'

defineProps<{
  images: TaskImage[]
}>()

const getStatusType = (status: string) => {
  const map: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
    completed: 'success',
    running: 'warning',
    failed: 'danger',
    pending: 'info'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    completed: '完成',
    running: '生成中',
    failed: '失败',
    pending: '待生成'
  }
  return map[status] || status
}
</script>

<style scoped>
.image-grid {
  padding: 10px 0;
}

.image-card {
  margin-bottom: 15px;
}

.image-wrapper {
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 8px;
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.loading, .placeholder {
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  background: #f5f7fa;
}

.placeholder .el-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.image-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.shot-label {
  font-size: 13px;
  color: #666;
}
</style>
