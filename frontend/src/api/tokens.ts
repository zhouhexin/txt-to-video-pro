import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1'
})

export interface TokenUsage {
  id: number
  model_type: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  model_name: string
  task_id: string | null
  prompt_text: string | null
  response_text: string | null
  scene: string | null
  created_at: string
}

export interface TokenStatistics {
  total_input_tokens: number
  total_output_tokens: number
  total_tokens: number
  total_calls: number
  today_tokens: number
  month_tokens: number
  avg_daily: number
  by_model: Record<string, number>
  by_model_type: Record<string, { input: number; output: number; calls: number; total: number }>
  by_model_name: Record<string, { input: number; output: number; calls: number; total: number }>
  daily_stats: Array<{ date: string; input_tokens: number; output_tokens: number; total_tokens: number; call_count: number }>
}

export interface DailyStats {
  date: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  call_count: number
}

// 获取 Token 使用统计概览
export const getTokenOverview = async (): Promise<TokenStatistics> => {
  const response = await api.get('/tokens/overview')
  return response.data
}

// 获取每日统计
export const getDailyStats = async (days?: number): Promise<{ stats: DailyStats[]; days: number }> => {
  const params = days ? `?days=${days}` : ''
  const response = await api.get(`/tokens/daily${params}`)
  return response.data
}

// 获取按模型统计
export const getByModelStats = async (): Promise<Array<{
  model_type: string
  model_name: string
  total_input: number
  total_output: number
  total_tokens: number
  call_count: number
}>> => {
  const response = await api.get('/tokens/by-model')
  return response.data.stats
}

// 获取 Token 使用记录列表
export const getTokenUsageList = async (params?: {
  model_type?: string
  task_id?: string
  start_date?: string
  end_date?: string
  page?: number
  per_page?: number
}): Promise<{ records: TokenUsage[]; total: number; page: number; per_page: number; pages: number }> => {
  const searchParams = new URLSearchParams()
  if (params?.model_type) searchParams.append('model_type', params.model_type)
  if (params?.task_id) searchParams.append('task_id', params.task_id)
  if (params?.start_date) searchParams.append('start_date', params.start_date)
  if (params?.end_date) searchParams.append('end_date', params.end_date)
  if (params?.page) searchParams.append('page', params.page.toString())
  if (params?.per_page) searchParams.append('per_page', params.per_page.toString())
  
  const response = await api.get(`/tokens/records?${searchParams.toString()}`)
  return response.data
}

// 获取单条记录详情
export const getTokenRecordDetail = async (recordId: number): Promise<TokenUsage> => {
  const response = await api.get(`/tokens/records/${recordId}`)
  return response.data
}

// 综合获取统计数据（用于 TokenStatistics 页面）
export const getTokenStatistics = async (startDate?: string, endDate?: string): Promise<TokenStatistics> => {
  // 获取概览数据
  const overview = await getTokenOverview()
  
  // 获取每日统计（默认7天）
  const dailyResult = await getDailyStats(7)
  
  // 获取按模型统计
  const modelStats = await getByModelStats()
  
  // 转换按模型统计数据格式
  const byModelType: Record<string, { input: number; output: number; calls: number; total: number }> = {}
  const byModelName: Record<string, { input: number; output: number; calls: number; total: number }> = {}
  
  modelStats.forEach(stat => {
    if (stat.model_type) {
      if (!byModelType[stat.model_type]) {
        byModelType[stat.model_type] = { input: 0, output: 0, calls: 0, total: 0 }
      }
      byModelType[stat.model_type].input += stat.total_input
      byModelType[stat.model_type].output += stat.total_output
      byModelType[stat.model_type].calls += stat.call_count
      byModelType[stat.model_type].total += stat.total_tokens
    }
    
    if (stat.model_name) {
      if (!byModelName[stat.model_name]) {
        byModelName[stat.model_name] = { input: 0, output: 0, calls: 0, total: 0 }
      }
      byModelName[stat.model_name].input += stat.total_input
      byModelName[stat.model_name].output += stat.total_output
      byModelName[stat.model_name].calls += stat.call_count
      byModelName[stat.model_name].total += stat.total_tokens
    }
  })
  
  return {
    ...overview,
    by_model_type: byModelType,
    by_model_name: byModelName,
    daily_stats: dailyResult.stats
  }
}