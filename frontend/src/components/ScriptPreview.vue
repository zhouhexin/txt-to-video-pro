<template>
  <el-card class="script-preview" shadow="hover">
    <template #header>
      <div class="card-header">
        <h3>{{ script.title }}</h3>
        <el-tag>{{ script.video_type }}</el-tag>
      </div>
    </template>
    
    <el-descriptions :column="2" border>
      <el-descriptions-item label="主题">{{ script.theme }}</el-descriptions-item>
      <el-descriptions-item label="分镜数">{{ script.shots?.length || 0 }}</el-descriptions-item>
      <el-descriptions-item label="关键词">{{ script.keywords }}</el-descriptions-item>
      <el-descriptions-item label="风格">{{ script.style || '未指定' }}</el-descriptions-item>
    </el-descriptions>
    
    <el-divider>剧本概览</el-divider>
    
    <p class="overview">{{ script.overview }}</p>
    
    <el-divider>分镜详情</el-divider>
    
    <el-collapse>
      <el-collapse-item 
        v-for="(shot, i) in script.shots" 
        :key="i" 
        :title="shot.scene"
        :name="i"
      >
        <div class="shot-detail">
          <p><strong>画面描述:</strong></p>
          <p class="visual">{{ shot.visual }}</p>
          
          <p><strong>运镜:</strong> <el-tag size="small">{{ shot.camera }}</el-tag></p>
          
          <p><strong>时长:</strong> {{ shot.duration }}秒</p>
          
          <p><strong>Prompt:</strong></p>
          <pre class="prompt">{{ shot.prompt }}</pre>
        </div>
      </el-collapse-item>
    </el-collapse>
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
  color: #333;
}

.overview {
  line-height: 1.8;
  color: #666;
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
}

.shot-detail {
  padding: 10px;
}

.visual {
  background: #f0f9eb;
  padding: 10px;
  border-radius: 6px;
  margin: 8px 0;
  line-height: 1.6;
}

.prompt {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 12px;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
