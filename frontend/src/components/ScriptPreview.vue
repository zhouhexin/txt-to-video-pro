<template>
  <el-card class="script-preview" shadow="hover">
    <template #header>
      <div class="card-header">
        <h3 class="title">{{ truncateTitle(script.title) }}</h3>
        <div class="meta">
          <el-tag type="success" size="small">{{ script.video_type }}</el-tag>
          <span class="shot-count">{{ script.shots?.length || 0 }}个镜头</span>
        </div>
      </div>
    </template>
    
    <div class="shots">
      <div v-for="(shot, i) in script.shots" :key="i" class="shot-item">
        <div class="shot-number">{{ i + 1 }}</div>
        <div class="shot-content">
          <div class="shot-visual">{{ shot.visual || shot.content }}</div>
          <div class="shot-meta">
            <span class="shot-type">{{ shot['镜头类型'] || shot.camera || '镜头' }}</span>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { Script } from '@/types'

defineProps<{
  script: Script
}>()

function truncateTitle(title: string, maxLen = 50) {
  if (!title) return ''
  return title.length > maxLen ? title.slice(0, maxLen) + '...' : title
}
</script>

<style scoped>
.script-preview {
  margin-top: 20px;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.shot-count {
  font-size: 13px;
  color: #909399;
}

.shots {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.shot-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 12px;
  transition: background 0.2s;
}

.shot-item:hover {
  background: #f0f0f0;
}

.shot-number {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #409eff;
  color: #fff;
  border-radius: 50%;
  font-weight: 600;
  font-size: 14px;
}

.shot-content {
  flex: 1;
  min-width: 0;
}

.shot-visual {
  color: #333;
  line-height: 1.7;
  font-size: 14px;
  margin-bottom: 8px;
}

.shot-meta {
  display: flex;
  gap: 8px;
}

.shot-type {
  font-size: 12px;
  color: #909399;
  padding: 2px 8px;
  background: #e8e8e8;
  border-radius: 4px;
}
</style>
