<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-left">
          <h1 @click="router.push('/')" class="header-title">🎬 AI 视频生成平台 <span class="pro-badge">Pro</span></h1>
        </div>
        <nav class="header-nav">
          <router-link to="/" :class="{ active: route.path === '/' }">首页</router-link>
          <router-link to="/script" :class="{ active: route.path === '/script' }">剧本生成</router-link>
          <router-link to="/history" :class="{ active: route.path === '/history' }">历史剧本</router-link>
          <router-link to="/task-history" :class="{ active: route.path === '/task-history' }">任务历史</router-link>
          <router-link to="/showcase" :class="{ active: route.path === '/showcase' }">成果展示</router-link>
          <router-link to="/statistics" :class="{ active: route.path === '/statistics' }">数据统计</router-link>
          <router-link to="/token-statistics" :class="{ active: route.path === '/token-statistics' }">Token 统计</router-link>
        </nav>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUIStore } from '@/stores/ui'

const router = useRouter()
const route = useRoute()
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
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  height: 60px !important;
}

.header-left {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.header-title {
  font-size: 22px;
  margin: 0;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.pro-badge {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  margin-left: 8px;
  vertical-align: middle;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.header-nav a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
  white-space: nowrap;
}

.header-nav a:hover {
  color: white;
  background: rgba(255, 255, 255, 0.15);
}

.header-nav a.active,
.header-nav a.router-link-exact-active {
  color: white;
  background: rgba(255, 255, 255, 0.25);
  font-weight: 500;
}

.el-main {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
