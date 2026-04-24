<template>
  <div class="token-statistics">
    <h1>Token 使用统计</h1>
    
    <!-- 概览卡片 -->
    <div class="overview-cards">
      <div class="card">
        <div class="card-title">总调用次数</div>
        <div class="card-value">{{ statistics.total_calls }}</div>
      </div>
      <div class="card">
        <div class="card-title">总输入 Token</div>
        <div class="card-value">{{ formatNumber(statistics.total_input_tokens) }}</div>
      </div>
      <div class="card">
        <div class="card-title">总输出 Token</div>
        <div class="card-value">{{ formatNumber(statistics.total_output_tokens) }}</div>
      </div>
      <div class="card">
        <div class="card-title">总 Token</div>
        <div class="card-value">{{ formatNumber(statistics.total_tokens) }}</div>
      </div>
    </div>

    <!-- 日期筛选 -->
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

    <!-- 图表区域 -->
    <div class="charts-container">
      <div class="chart-card">
        <h3>每日 Token 使用趋势</h3>
        <div ref="dailyChartRef" class="chart"></div>
      </div>
      
      <div class="chart-row">
        <div class="chart-card half">
          <h3>按模型类型分布</h3>
          <div ref="modelTypeChartRef" class="chart"></div>
        </div>
        
        <div class="chart-card half">
          <h3>按模型名称分布</h3>
          <div ref="modelNameChartRef" class="chart"></div>
        </div>
      </div>
    </div>

    <!-- 详细记录表格 -->
    <div class="table-section">
      <h3>使用记录详情</h3>
      <el-table :data="usageList" stripe style="width: 100%" v-loading="tableLoading" :key="tableKey">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="model_type" label="模型类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getModelTypeTag(row.model_type)">{{ row.model_type }}</el-tag>
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
        <el-table-column prop="scene" label="场景" width="120" />
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
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

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="Token 使用详情" width="600px">
      <el-descriptions :column="1" border v-if="currentDetail">
        <el-descriptions-item label="ID">{{ currentDetail.id }}</el-descriptions-item>
        <el-descriptions-item label="模型类型">{{ currentDetail.model_type }}</el-descriptions-item>
        <el-descriptions-item label="模型名称">{{ currentDetail.model_name }}</el-descriptions-item>
        <el-descriptions-item label="输入 Token">{{ formatNumber(currentDetail.input_tokens) }}</el-descriptions-item>
        <el-descriptions-item label="输出 Token">{{ formatNumber(currentDetail.output_tokens) }}</el-descriptions-item>
        <el-descriptions-item label="总 Token">{{ formatNumber(currentDetail.total_tokens) }}</el-descriptions-item>
        <el-descriptions-item label="场景">{{ currentDetail.scene || '-' }}</el-descriptions-item>
        <el-descriptions-item label="任务 ID">{{ currentDetail.task_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(currentDetail.created_at) }}</el-descriptions-item>
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
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getTokenStatistics, getTokenUsageList, type TokenUsage, type TokenStatistics } from '@/api/tokens'

// 数据
const loading = ref(false)
const tableLoading = ref(false)
const statistics = ref<TokenStatistics>({
  total_input_tokens: 0,
  total_output_tokens: 0,
  total_tokens: 0,
  total_calls: 0,
  today_tokens: 0,
  month_tokens: 0,
  avg_daily: 0,
  by_model: {},
  by_model_type: {},
  by_model_name: {},
  daily_stats: []
})
const usageList = ref<TokenUsage[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const tableKey = ref(0)  // 用于强制刷新表格
const dateRange = ref<[Date, Date] | null>(null)
const detailVisible = ref(false)
const currentDetail = ref<TokenUsage | null>(null)

// 图表引用
const dailyChartRef = ref<HTMLElement | null>(null)
const modelTypeChartRef = ref<HTMLElement | null>(null)
const modelNameChartRef = ref<HTMLElement | null>(null)
let dailyChart: echarts.ECharts | null = null
let modelTypeChart: echarts.ECharts | null = null
let modelNameChart: echarts.ECharts | null = null

// 格式化数字（处理undefined/null情况）
const formatNumber = (num: number | undefined | null): string => {
  if (num === undefined || num === null) return '0'
  return num.toLocaleString()
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 获取模型类型标签颜色
const getModelTypeTag = (type: string): string => {
  const typeMap: Record<string, string> = {
    'script_generate': 'primary',
    'prompt_optimize': 'success',
    'image_generate': 'warning',
    'video_generate': 'danger'
  }
  return typeMap[type] || 'info'
}

// 加载统计数据
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
    updateCharts()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载使用记录
const loadUsageList = async () => {
  tableLoading.value = true
  try {
    let startDate: string | undefined
    let endDate: string | undefined
    if (dateRange.value) {
      startDate = dateRange.value[0].toISOString().split('T')[0]
      endDate = dateRange.value[1].toISOString().split('T')[0]
    }
    console.log('Loading page:', currentPage.value, 'pageSize:', pageSize.value)
    
    // 先清空数据
    usageList.value = []
    
    const result = await getTokenUsageList({
      page: currentPage.value,
      per_page: pageSize.value,
      start_date: startDate,
      end_date: endDate
    })
    console.log('Result:', result)
    
    total.value = result.total
    
    // 使用nextTick确保DOM更新后再设置数据
    await nextTick()
    usageList.value = result.records
    tableKey.value++
    
    // 再次等待DOM更新
    await nextTick()
  } catch (error) {
    console.error('加载使用记录失败:', error)
  } finally {
    tableLoading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  loadStatistics()
  loadUsageList()
}

// 日期变化处理
const handleDateChange = () => {
  currentPage.value = 1
  refreshData()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1  // 改变每页条数时重置到第一页
  loadUsageList()
}

const handlePageChange = (page: number) => {
  // 使用事件参数 page，确保使用正确的页码值
  currentPage.value = page
  loadUsageList()
}

// 显示详情
const showDetail = (row: TokenUsage) => {
  currentDetail.value = row
  detailVisible.value = true
}

// 初始化图表
const initCharts = () => {
  if (dailyChartRef.value) {
    dailyChart = echarts.init(dailyChartRef.value)
  }
  if (modelTypeChartRef.value) {
    modelTypeChart = echarts.init(modelTypeChartRef.value)
  }
  if (modelNameChartRef.value) {
    modelNameChart = echarts.init(modelNameChartRef.value)
  }
}

// 更新图表
const updateCharts = () => {
  // 每日趋势图
  if (dailyChart && statistics.value.daily_stats.length > 0) {
    const dates = statistics.value.daily_stats.map(s => s.date)
    const inputData = statistics.value.daily_stats.map(s => s.input_tokens)
    const outputData = statistics.value.daily_stats.map(s => s.output_tokens)
    
    dailyChart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' }
      },
      legend: {
        data: ['输入 Token', '输出 Token']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: dates
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '输入 Token',
          type: 'line',
          data: inputData,
          smooth: true,
          areaStyle: { opacity: 0.3 }
        },
        {
          name: '输出 Token',
          type: 'line',
          data: outputData,
          smooth: true,
          areaStyle: { opacity: 0.3 }
        }
      ]
    })
  }

  // 模型类型饼图
  if (modelTypeChart && Object.keys(statistics.value.by_model_type).length > 0) {
    const data = Object.entries(statistics.value.by_model_type).map(([name, value]) => ({
      name,
      value: value.calls
    }))
    
    modelTypeChart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '调用次数',
          type: 'pie',
          radius: '50%',
          data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    })
  }

  // 模型名称饼图
  if (modelNameChart && Object.keys(statistics.value.by_model_name).length > 0) {
    const data = Object.entries(statistics.value.by_model_name).map(([name, value]) => ({
      name,
      value: value.calls
    }))
    
    modelNameChart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '调用次数',
          type: 'pie',
          radius: '50%',
          data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    })
  }
}

// 窗口大小变化时重绘图表
const handleResize = () => {
  dailyChart?.resize()
  modelTypeChart?.resize()
  modelNameChart?.resize()
}

onMounted(() => {
  initCharts()
  refreshData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  dailyChart?.dispose()
  modelTypeChart?.dispose()
  modelNameChart?.dispose()
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

.filter-section {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
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

.text-content {
  max-height: 150px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>