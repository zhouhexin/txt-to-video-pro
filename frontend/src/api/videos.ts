import axios from 'axios'
import type { TaskVideo } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 1200000  // 20分钟，匹配后端视频生成最长等待时间
})

export interface GenerateVideoParams {
  task_id: string
  shot_index: number
  duration?: number
  mode?: 'single' | 'chain'
  resolution?: string
  camera_motion?: string
  first_last_mode?: boolean
  total_shots?: number
  visual_desc?: string  // 分镜的视觉描述
}

/**
 * 生成单个视频
 */
export async function generateVideo(params: GenerateVideoParams): Promise<{
  status: string
  video_id: number
  url: string
  first_last_mode?: boolean
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
 * 批量生成所有视频
 */
export async function generateAllVideos(params: {
  task_id: string
  shots: Array<{
    index: number
    duration?: number
    camera_motion?: string
    visual?: string  // 分镜的视觉描述
  }>
  resolution?: string
  first_last_mode?: boolean
}): Promise<{
  task_id: string
  results: Array<{
    shot_index: number
    status: string
    video_id?: number
    url?: string
    error?: string
    first_last_mode?: boolean
  }>
  first_last_mode?: boolean
}> {
  const response = await api.post('/videos/generate-all', params)
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
