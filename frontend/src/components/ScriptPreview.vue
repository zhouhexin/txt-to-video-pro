<template>
  <el-card class="script-preview" shadow="hover">
    <template #header>
      <div class="card-header">
        <h3>{{ script.title }}</h3>
        <el-tag type="success">{{ script.video_type }}</el-tag>
      </div>
    </template>
    
    <el-descriptions :column="2" border size="small">
      <el-descriptions-item label="原始提示词">{{ script.original_theme || '无' }}</el-descriptions-item>
      <el-descriptions-item label="优化后">{{ script.theme }}</el-descriptions-item>
      <el-descriptions-item label="分镜数">{{ script.shots?.length || 0 }}个</el-descriptions-item>
      <el-descriptions-item label="关键词">{{ script.keywords || '无' }}</el-descriptions-item>
      <el-descriptions-item label="风格" :span="2">{{ script.style || '未指定' }}</el-descriptions-item>
    </el-descriptions>
    
    <el-divider>剧本概览</el-divider>
    
    <div class="overview">{{ script.overview }}</div>
    
    <el-divider>分镜详情</el-divider>
    
    <div class="shots">
      <div v-for="(shot, i) in script.shots" :key="i" class="shot-item">
        <div class="shot-header">
          <span class="shot-title">镜头 {{ i + 1 }}: {{ shot.scene }}</span>
          <div class="shot-tags">
            <el-tag size="small" type="info">{{ shot.camera }}</el-tag>
            <el-tag size="small">{{ shot.duration }}秒</el-tag>
          </div>
        </div>
        <div class="shot-visual">{{ shot.visual }}</div>
        <div class="shot-prompt">
          <span class="prompt-label">Prompt</span>
          <pre>{{ shot.prompt }}</pre>
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
</script>

<style scoped>
.script-preview {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
}

.overview {
  color: #606266;
  line-height: 1.8;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
}

.shots {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.shot-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
}

.shot-item:hover {
  border-color: #409eff;
}

.shot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.shot-title {
  font-weight: 600;
  color: #303133;
}

.shot-tags {
  display: flex;
  gap: 8px;
}

.shot-visual {
  color: #606266;
  line-height: 1.7;
  padding: 12px;
  background: linear-gradient(135deg, #f0f9eb 0%, #e8f5e0 100%);
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 14px;
}

.shot-prompt {
  margin-top: 8px;
}

.prompt-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
  text-transform: uppercase;
}

pre {
  margin: 0;
  padding: 12px;
  background: #1e1e1e;
  color: #d4d4d4;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
