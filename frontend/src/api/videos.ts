import axios from 'axios'
import type { TaskVideo } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 300000
})

export interface GenerateVideoParams {
  task_id: string
  shot_index: number
  duration?: number
  mode?: 'single' | 'chain'
}

/**
 * 生成单个视频
 */
export async function generateVideo(params: GenerateVideoParams): Promise<{
  status: string
  video_id: number
  url: string
}> {
  const response = await api.post('/videos/generate', params)
  return response.data
}

/**
 * 获取任务所有视频
 */
export async function getTaskVideos(taskId: string): Promise<{
  task_id: string
  videos: TaskVideo[]
  merged_video?: {
    url: string
    status: string
  }
}> {
  const response = await api.get(`/videos/${taskId}`)
  return response.data
}

/**
 * 合并视频
 */
export async function mergeVideos(taskId: string): Promise<{
  status: string
  merged_url: string
}> {
  const response = await api.post('/videos/merge', { task_id: taskId })
  return response.data
}
