<template>
  <div class="token-statistics">
    <h1>Token 使用统计</h1>
    
    <div class="overview-cards">
      <div class="card">
        <div class="card-title">总调用次数</div>
        <div class="card-value">{{ statistics.total_calls || 0 }}</div>
      </div>
      <div class="card">
        <div class="card-title">总输入 Token</div>
        <div class="card-value">{{ formatNumber(statistics.total_input) }}</div>
      </div>
      <div class="card">
        <div class="card-title">总输出 Token</div>
        <div class="card-value">{{ formatNumber(statistics.total_output) }}</div>
      </div>
      <div class="card">
        <div class="card-title">总 Token</div>
        <div class="card-value">{{ formatNumber(statistics.total_tokens) }}</div>
      </div>
    </div>

    <div class="view-tabs">
      <el-radio-group v-model="currentView" size="large">
        <el-radio-button value="tasks">按项目查看</el-radio-button>
        <el-radio-button value="overview">总览统计</el-radio-button>
      </el-radio-group>
    </div>

    <div v-if="currentView === 'tasks'" class="tasks-view">
      <div class="filter-section">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="handleDateChange"
        />
        <el-button @click="refreshData" :loading="loading">刷新数据</el-button>
      </div>

      <div v-if="taskStats.length > 0" class="task-cards">
        <el-card 
          v-for="task in taskStats" 
          :key="task.task_id" 
          class="task-card"
          shadow="hover"
        >
          <template #header>
            <div class="task-header">
              <div class="task-title">
                <el-icon><VideoCamera /></el-icon>
                <span>{{ task.title || task.task_id }}</span>
              </div>
              <el-tag type="info" size="small">
                {{ formatNumber(task.total_tokens) }} tokens
              </el-tag>
            </div>
          </template>
          
          <div class="task-content">
            <div class="flow-chart">
              <div 
                v-for="(stage, index) in stageOrder" 
                :key="stage.key"
                class="flow-item"
                :class="{ 'has-data': task.stages[stage.name] }"
              >
                <div class="flow-icon">{{ stage.icon }}</div>
                <div class="flow-name">{{ stage.name }}</div>
                <div class="flow-value">
                  <template v-if="task.stages[stage.name]">
                    {{ formatNumber(task.stages[stage.name].tokens) }}
                    <span class="flow-calls">({{ task.stages[stage.name].calls }}次)</span>
                  </template>
                  <template v-else>
                    <span class="no-data">-</span>
                  </template>
                </div>
                <div v-if="index < stageOrder.length - 1" class="flow-arrow">→</div>
              </div>
            </div>
            
            <div class="task-summary">
              <div class="item">
                <span class="label">调用次数：</span>
                <span class="value">{{ task.call_count }}次</span>
              </div>
              <div class="item">
                <span class="label">创建时间：</span>
                <span class="value">{{ formatDate(task.created_at) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>
      
      <el-empty v-else-if="!loading" description="暂无项目数据" />
    </div>

    <div v-else class="overview-view">
      <div class="filter-section">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="handleDateChange"
        />
        <el-button @click="refreshData" :loading="loading">刷新数据</el-button>
      </div>

      <div class="charts-container">
        <div class="chart-card">
          <h3>每日 Token 使用趋势</h3>
          <div ref="dailyChartRef" class="chart"></div>
        </div>
        
        <div class="chart-row">
          <div class="chart-card half">
            <h3>按阶段分布</h3>
            <div ref="stageChartRef" class="chart"></div>
          </div>
          
          <div class="chart-card half">
            <h3>调用次数分布</h3>
            <div ref="callChartRef" class="chart"></div>
          </div>
        </div>
      </div>

      <div class="table-section">
        <h3>使用记录详情</h3>
        <el-table :data="usageList" stripe style="width: 100%" v-loading="tableLoading">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="model_type" label="阶段" width="120">
            <template #default="{ row }">
              <el-tag :type="getModelTypeTag(row.model_type)">{{ getStageName(row.model_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="model_name" label="模型名称" width="150" />
          <el-table-column prop="input_tokens" label="输入 Token" width="120">
            <template #default="{ row }">{{ formatNumber(row.input_tokens) }}</template>
          </el-table-column>
          <el-table-column prop="output_tokens" label="输出 Token" width="120">
            <template #default="{ row }">{{ formatNumber(row.output_tokens) }}</template>
          </el-table-column>
          <el-table-column prop="total_tokens" label="总 Token" width="120">
            <template #default="{ row }">{{ formatNumber(row.total_tokens) }}</template>
          </el-table-column>
          <el-table-column prop="task_id" label="项目" width="150">
            <template #default="{ row }">
              <span class="task-id-text">{{ row.task_id ? row.task_id.slice(0, 12) + '...' : '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="180">
            <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button size="small" @click="showDetail(row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          style="margin-top: 20px; justify-content: flex-end;"
        />
      </div>
    </div>

    <el-dialog v-model="detailVisible" title="Token 使用详情" width="600px">
      <el-descriptions :column="1" border v-if="currentDetail">
        <el-descriptions-item label="ID">{{ currentDetail.id }}</el-descriptions-item>
        <el-descriptions-item label="阶段">{{ getStageName(currentDetail.model_type) }}</el-descriptions-item>
        <el-descriptions-item label="模型名称">{{ currentDetail.model_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="输入 Token">{{ formatNumber(currentDetail.input_tokens) }}</el-descriptions-item>
        <el-descriptions-item label="输出 Token">{{ formatNumber(currentDetail.output_tokens) }}</el-descriptions-item>
        <el-descriptions-item label="总 Token">{{ formatNumber(currentDetail.total_tokens) }}</el-descriptions-item>
        <el-descriptions-item label="项目">{{ currentDetail.task_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDateTime(currentDetail.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="提示词">
          <div class="text-content">{{ currentDetail.prompt_text || '-' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="响应内容">
          <div class="text-content">{{ currentDetail.response_text || '-' }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { VideoCamera } from '@element-plus/icons-vue'
import { getTokenStatistics, getTokenUsageList, type TaskStats, type TokenUsage } from '@/api/tokens'

const stageOrder = [
  { key: 'prompt', name: '提示词优化', icon: '🔧' },
  { key: 'script', name: '剧本生成', icon: '📝' },
  { key: 'image', name: '分镜图生成', icon: '🖼️' },
  { key: 'video', name: '视频生成', icon: '🎬' }
]

const stageNameMap: Record<string, string> = {
  'script_generate': '剧本生成',
  'prompt_optimize': '提示词优化',
  'image_generate': '分镜图生成',
  'video_generate': '视频生成'
}

const loading = ref(false)
const tableLoading = ref(false)
const currentView = ref('tasks')
const statistics = ref<any>({})
const taskStats = ref<TaskStats[]>([])
const usageList = ref<TokenUsage[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dateRange = ref<[Date, Date] | null>(null)
const detailVisible = ref(false)
const currentDetail = ref<TokenUsage | null>(null)

const dailyChartRef = ref<HTMLElement | null>(null)
const stageChartRef = ref<HTMLElement | null>(null)
const callChartRef = ref<HTMLElement | null>(null)
let dailyChart: echarts.ECharts | null = null
let stageChart: echarts.ECharts | null = null
let callChart: echarts.ECharts | null = null

const formatNumber = (num: number | undefined | null): string => {
  if (num === undefined || num === null) return '0'
  return num.toLocaleString()
}

const formatDate = (dateStr: string | null): string => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateStr: string): string => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStageName = (modelType: string): string => {
  return stageNameMap[modelType] || modelType
}

const getModelTypeTag = (type: string): string => {
  const tagMap: Record<string, string> = {
    'script_generate': 'primary',
    'prompt_optimize': 'success',
    'image_generate': 'warning',
    'video_generate': 'danger'
  }
  return tagMap[type] || 'info'
}

const loadStatistics = async () => {
  loading.value = true
  try {
    let startDate: string | undefined
    let endDate: string | undefined
    if (dateRange.value) {
      startDate = dateRange.value[0].toISOString().split('T')[0]
      endDate = dateRange.value[1].toISOString().split('T')[0]
    }
    statistics.value = await getTokenStatistics(startDate, endDate)
    taskStats.value = statistics.value.tasks || []
    
    if (currentView.value === 'overview') {
      updateCharts()
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

const loadUsageList = async () => {
  tableLoading.value = true
  try {
    let startDate: string | undefined
    let endDate: string | undefined
    if (dateRange.value) {
      startDate = dateRange.value[0].toISOString().split('T')[0]
      endDate = dateRange.value[1].toISOString().split('T')[0]
    }
    
    usageList.value = []
    const result = await getTokenUsageList({
      page: currentPage.value,
      per_page: pageSize.value,
      start_date: startDate,
      end_date: endDate
    })
    
    total.value = result.total
    await nextTick()
    usageList.value = result.records
  } catch (error) {
    console.error('加载使用记录失败:', error)
  } finally {
    tableLoading.value = false
  }
}

const refreshData = () => {
  if (currentView.value === 'tasks') {
    loadStatistics()
  } else {
    loadStatistics()
    loadUsageList()
  }
}

const handleDateChange = () => {
  currentPage.value = 1
  refreshData()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadUsageList()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadUsageList()
}

const showDetail = (row: TokenUsage) => {
  currentDetail.value = row
  detailVisible.value = true
}

const initCharts = () => {
  if (dailyChartRef.value) {
    dailyChart = echarts.init(dailyChartRef.value)
  }
  if (stageChartRef.value) {
    stageChart = echarts.init(stageChartRef.value)
  }
  if (callChartRef.value) {
    callChart = echarts.init(callChartRef.value)
  }
}

const updateCharts = () => {
  if (dailyChart && statistics.value.daily_stats?.length > 0) {
    const dates = statistics.value.daily_stats.map((s: any) => s.date)
    const inputData = statistics.value.daily_stats.map((s: any) => s.input_tokens)
    const outputData = statistics.value.daily_stats.map((s: any) => s.output_tokens)
    
    dailyChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
      legend: { data: ['输入 Token', '输出 Token'] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: dates },
      yAxis: { type: 'value' },
      series: [
        { name: '输入 Token', type: 'line', data: inputData, smooth: true, areaStyle: { opacity: 0.3 } },
        { name: '输出 Token', type: 'line', data: outputData, smooth: true, areaStyle: { opacity: 0.3 } }
      ]
    })
  }

  if (stageChart && taskStats.value.length > 0) {
    const stageData: Record<string, number> = {}
    taskStats.value.forEach(task => {
      Object.entries(task.stages).forEach(([stage, data]) => {
        if (!stageData[stage]) stageData[stage] = 0
        stageData[stage] += (data as any).tokens
      })
    })
    
    const data = Object.entries(stageData).map(([name, value]) => ({ name, value }))
    
    stageChart.setOption({
      tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
      legend: { orient: 'vertical', left: 'left' },
      series: [{
        name: 'Token消耗',
        type: 'pie',
        radius: '50%',
        data,
        emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
      }]
    })
  }

  if (callChart && taskStats.value.length > 0) {
    const stageCalls: Record<string, number> = {}
    taskStats.value.forEach(task => {
      Object.entries(task.stages).forEach(([stage, data]) => {
        if (!stageCalls[stage]) stageCalls[stage] = 0
        stageCalls[stage] += (data as any).calls
      })
    })
    
    const data = Object.entries(stageCalls).map(([name, value]) => ({ name, value }))
    
    callChart.setOption({
      tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
      legend: { orient: 'vertical', left: 'left' },
      series: [{
        name: '调用次数',
        type: 'pie',
        radius: '50%',
        data,
        emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
      }]
    })
  }
}

const handleResize = () => {
  dailyChart?.resize()
  stageChart?.resize()
  callChart?.resize()
}

watch(currentView, async (newView) => {
  if (newView === 'overview') {
    await nextTick()
    if (!dailyChart) initCharts()
    updateCharts()
    loadUsageList()
  }
})

onMounted(() => {
  loadStatistics()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  dailyChart?.dispose()
  stageChart?.dispose()
  callChart?.dispose()
})
</script>

<style scoped>
.token-statistics {
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
  color: #303133;
}

h3 {
  margin-bottom: 15px;
  color: #303133;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 24px;
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.card:nth-child(2) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
}

.card:nth-child(3) {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
}

.card:nth-child(4) {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  box-shadow: 0 4px 15px rgba(67, 233, 123, 0.3);
}

.card-title {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 10px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
}

.view-tabs {
  margin-bottom: 20px;
}

.filter-section {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.tasks-view {
  margin-top: 20px;
}

.task-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 20px;
}

.task-card {
  border-radius: 12px;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.task-content {
  padding: 10px 0;
}

.flow-chart {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 10px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 15px;
  overflow-x: auto;
}

.flow-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
  position: relative;
}

.flow-item.has-data .flow-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.flow-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  margin-bottom: 8px;
}

.flow-name {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
  text-align: center;
}

.flow-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.flow-calls {
  font-size: 11px;
  color: #909399;
}

.flow-arrow {
  position: absolute;
  right: -15px;
  color: #c0c4cc;
  font-size: 16px;
}

.task-summary {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #606266;
}

.overview-view {
  margin-top: 20px;
}

.charts-container {
  margin-bottom: 30px;
}

.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.chart-card.half {
  width: calc(50% - 10px);
}

.chart-row {
  display: flex;
  gap: 20px;
}

.chart {
  height: 300px;
  width: 100%;
}

.table-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.task-id-text {
  font-size: 12px;
  color: #909399;
}

.text-content {
  max-height: 150px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.no-data {
  color: #c0c4cc;
}
</style>