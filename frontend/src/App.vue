<template>
  <div id="app">
    <el-container>
      <el-header>
        <h1>🎬 AI 视频生成平台 <span class="pro-badge">Pro</span></h1>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useUIStore } from '@/stores/ui'

const uiStore = useUIStore()

// 监听消息变化并显示
watch(() => uiStore.message, (msg) => {
  if (msg) {
    ElMessage({
      type: msg.type,
      message: msg.content,
      duration: 3000
    })
  }
})
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
}

.el-container {
  height: 100%;
}

.el-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.el-header h1 {
  font-size: 24px;
  margin: 0;
  font-weight: 600;
}

.pro-badge {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  margin-left: 10px;
}

.el-main {
  background: #f5f7fa;
  padding: 20px;
}
</style>
