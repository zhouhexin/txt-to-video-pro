<template>
  <div class="home">
    <!-- 欢迎横幅 -->
    <el-card class="welcome-card" shadow="hover">
      <div class="welcome-content">
        <div class="welcome-text">
          <h2>从剧本到成片，AI 驱动的全流程视频创作</h2>
          <p class="description">
            基于阿里云百炼大模型，支持智能剧本生成、自动分镜绘制、视频生成与合并
          </p>
        </div>
        <div class="welcome-actions">
          <el-button type="primary" size="large" @click="router.push('/script')">
            <el-icon><VideoCamera /></el-icon> 开始创作
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 功能步骤 -->
    <el-row :gutter="20" class="steps-row">
      <el-col :span="6">
        <el-card class="step-card" shadow="hover">
          <div class="step-icon">📝</div>
          <h3>智能剧本生成</h3>
          <p>AI 自动生成专业剧本和分镜描述</p>
          <ul class="feature-list">
            <li>支持多种视频类型</li>
            <li>场景风格智能推荐</li>
            <li>提示词优化</li>
          </ul>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="step-card" shadow="hover">
          <div class="step-icon">🎨</div>
          <h3>分镜图生成</h3>
          <p>文生图，批量生成分镜画面</p>
          <ul class="feature-list">
            <li>多镜头模式</li>
            <li>链式连贯生成</li>
            <li>支持重新生成</li>
          </ul>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="step-card" shadow="hover">
          <div class="step-icon">🎬</div>
          <h3>视频生成</h3>
          <p>图生视频，首尾帧控制</p>
          <ul class="feature-list">
            <li>单镜头/链式连续</li>
            <li>自定义时长</li>
            <li>运镜控制</li>
          </ul>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="step-card" shadow="hover">
          <div class="step-icon">📊</div>
          <h3>成果展示</h3>
          <p>完整视频播放与下载</p>
          <ul class="feature-list">
            <li>分镜预览</li>
            <li>视频下载</li>
            <li>项目管理</li>
          </ul>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近项目 -->
    <el-card class="section-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2>📁 最近项目</h2>
          <el-button link type="primary" @click="router.push('/history')">
            查看全部 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>
      
      <el-empty v-if="recentScripts.length === 0" description="还没有项目，开始创作吧">
        <el-button type="primary" @click="router.push('/script')">开始创作</el-button>
      </el-empty>
      
      <el-table v-else :data="recentScripts" style="width: 100%" @row-click="handleRowClick">
        <el-table-column prop="title" label="项目名称" min-width="200" />
        <el-table-column prop="video_type" label="类型" width="120" />
        <el-table-column prop="shots" label="分镜数" width="100">
          <template #default="{ row }">
            {{ row.shots?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="handleContinue(row)">
              继续
            </el-button>
            <el-button link type="danger" @click.stop="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 功能特性 -->
    <el-card class="section-card" shadow="hover">
      <template #header>
        <h2>✨ 核心特性</h2>
      </template>
      <el-row :gutter="30">
        <el-col :span="8">
          <div class="feature-item">
            <div class="feature-icon">🤖</div>
            <h4>AI 大模型驱动</h4>
            <p>基于阿里云百炼通义千问 + 通义万相，专业级视频生成</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="feature-item">
            <div class="feature-icon">🎯</div>
            <h4>场景风格库</h4>
            <p>内置 6+ 种预设场景，支持自定义扩展</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="feature-item">
            <div class="feature-icon">🔗</div>
            <h4>链式生成模式</h4>
            <p>首尾帧控制，保证镜头连贯性</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="feature-item">
            <div class="feature-icon">💾</div>
            <h4>任务管理</h4>
            <p>完整的任务历史与成果管理</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="feature-item">
            <div class="feature-icon">📈</div>
            <h4>数据统计</h4>
            <p>生成统计与使用分析</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="feature-item">
            <div class="feature-icon">🔧</div>
            <h4>提示词优化</h4>
            <p>AI 自动优化，提升生成质量</p>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { VideoCamera, ArrowRight } from '@element-plus/icons-vue'
import { searchScripts, deleteScript } from '@/api/scripts'
import { useScriptStore } from '@/stores/script'
import { useTaskStore } from '@/stores/task'
import { useUIStore } from '@/stores/ui'

const router = useRouter()
const scriptStore = useScriptStore()
const taskStore = useTaskStore()
const uiStore = useUIStore()

const recentScripts = ref<any[]>([])

// 加载最近项目
const loadRecentScripts = async () => {
  try {
    const result = await searchScripts({})
    recentScripts.value = result.scripts.slice(0, 5)
  } catch (error) {
    console.error('加载最近项目失败:', error)
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleRowClick = (row: any) => {
  scriptStore.setCurrentScript(row)
  taskStore.setTaskId(row.task_id)
}

const handleContinue = (row: any) => {
  scriptStore.setCurrentScript(row)
  taskStore.setTaskId(row.task_id)
  router.push('/image')
}

const handleDelete = async (row: any) => {
  try {
    await deleteScript(row.id)
    uiStore.showSuccess('删除成功')
    loadRecentScripts()
  } catch (err: any) {
    uiStore.showError(err.message || '删除失败')
  }
}

onMounted(() => {
  loadRecentScripts()
})
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 20px;
  background: linear-gradient(135deg, #e8ecf4 0%, #d5dce8 100%);
  border: 1px solid #dcdfe6;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
}

.welcome-text {
  flex: 1;
}

.welcome-text h2 {
  font-size: 20px;
  margin: 0 0 8px 0;
  font-weight: 600;
  color: #333;
}

.description {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.welcome-actions {
  display: flex;
  gap: 15px;
  flex-shrink: 0;
}

.steps-row {
  margin-bottom: 20px;
}

.step-card {
  transition: all 0.3s;
  height: 100%;
  text-align: center;
}

.step-card:hover {
  transform: translateY(-3px);
  border-color: #667eea;
}

.step-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.step-card h3 {
  font-size: 16px;
  margin: 10px 0;
  color: #333;
}

.step-card p {
  font-size: 13px;
  color: #666;
  margin: 8px 0;
}

.feature-list {
  text-align: left;
  margin: 15px 0 0 0;
  padding-left: 20px;
  font-size: 13px;
  color: #666;
}

.feature-list li {
  margin: 5px 0;
}

.section-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2,
.section-card h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.feature-item {
  text-align: center;
  padding: 10px;
}

.feature-icon {
  font-size: 36px;
  margin-bottom: 10px;
}

.feature-item h4 {
  font-size: 16px;
  margin: 10px 0;
  color: #333;
}

.feature-item p {
  font-size: 13px;
  color: #666;
  margin: 0;
}
</style>
