<template>
  <div class="statistics">
    <el-row :gutter="20">
      <!-- 概览卡片 -->
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon scripts">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_scripts }}</div>
              <div class="stat-label">总剧本数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon tasks">
              <el-icon><List /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_tasks }}</div>
              <div class="stat-label">总任务数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon images">
              <el-icon><Picture /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_images }}</div>
              <div class="stat-label">总分镜图</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon videos">
              <el-icon><VideoCamera /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_videos }}</div>
              <div class="stat-label">总视频数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 成功率卡片 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <h3>📊 生成统计</h3>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-label">成功率</div>
            <el-progress 
              :percentage="stats.success_rate" 
              :color="successRateColor"
              :format="format => `${format}%`"
            />
          </div>
        </el-col>
        
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-label">平均时长</div>
            <div class="stat-value-small">{{ stats.avg_duration }}秒</div>
          </div>
        </el-col>
        
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-label">本月任务</div>
            <div class="stat-value-small">{{ usageStats.tasks_this_month }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 每日趋势 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <h3>📈 生成趋势（最近 7 天）</h3>
        </div>
      </template>
      
      <el-table :data="dailyStats" style="width: 100%">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="tasks" label="任务数" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.tasks }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="images" label="图片数" width="100">
          <template #default="{ row }">
            <el-tag size="small" type="success">{{ row.images }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="videos" label="视频数" width="100">
          <template #default="{ row }">
            <el-tag size="small" type="warning">{{ row.videos }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="趋势">
          <template #default="{ row }">
            <div class="mini-chart">
              <div 
                v-for="i in 3" 
                :key="i"
                class="chart-bar"
                :style="{
                  height: `${getChartHeight(row, i)}px`,
                  background: getChartColor(i)
                }"
              />
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="dailyStats.length === 0" description="暂无数据" />
    </el-card>
    
    <!-- 本月用量 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <h3>📋 本月用量</h3>
      </template>
      
      <el-descriptions :column="3" border>
        <el-descriptions-item label="任务数">
          {{ usageStats.tasks_this_month }}
        </el-descriptions-item>
        <el-descriptions-item label="图片数">
          {{ usageStats.images_this_month }}
        </el-descriptions-item>
        <el-descriptions-item label="视频数">
          {{ usageStats.videos_this_month }}
        </el-descriptions-item>
        <el-descriptions-item label="预估 API 调用">
          {{ usageStats.api_calls_estimate }} 次
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const stats = ref<any>({
  total_scripts: 0,
  total_tasks: 0,
  total_images: 0,
  total_videos: 0,
  success_rate: 0,
  avg_duration: 5,
  tasks_by_status: {}
})

const dailyStats = ref<any[]>([])
const usageStats = ref<any>({
  tasks_this_month: 0,
  images_this_month: 0,
  videos_this_month: 0,
  api_calls_estimate: 0
})

const loading = ref(false)

const successRateColor = computed(() => {
  if (stats.value.success_rate >= 80) return '#67C23A'
  if (stats.value.success_rate >= 60) return '#E6A23C'
  return '#F56C6C'
})

onMounted(async () => {
  await loadStats()
})

const loadStats = async () => {
  loading.value = true
  try {
    // 加载概览统计
    const overviewRes = await axios.get('/api/v1/statistics/overview')
    stats.value = overviewRes.data
    
    // 加载每日统计
    const dailyRes = await axios.get('/api/v1/statistics/daily')
    dailyStats.value = dailyRes.data.stats
    
    // 加载用量统计
    const usageRes = await axios.get('/api/v1/statistics/usage')
    usageStats.value = usageRes.data
  } catch (error: any) {
    console.error('加载统计失败:', error)
  } finally {
    loading.value = false
  }
}

const getChartHeight = (row: any, type: number) => {
  const max = Math.max(row.tasks, row.images, row.videos, 1)
  const value = type === 1 ? row.tasks : type === 2 ? row.images : row.videos
  return (value / max) * 40 + 5
}

const getChartColor = (type: number) => {
  return type === 1 ? '#409EFF' : type === 2 ? '#67C23A' : '#E6A23C'
}
</script>

<style scoped>
.statistics {
  max-width: 1200px;
  margin: 0 auto;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
}

.stat-icon.scripts {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.tasks {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.images {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.videos {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-value-small {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.stat-item {
  padding: 10px;
  text-align: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
}

.mini-chart {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 50px;
}

.chart-bar {
  flex: 1;
  border-radius: 2px;
  min-height: 5px;
  transition: height 0.3s;
}
</style>
