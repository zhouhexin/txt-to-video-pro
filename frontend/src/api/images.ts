import axios from 'axios'
import type { TaskImage } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120000
})

export interface GenerateImageParams {
  task_id: string
  shot_index: number
  prompt: string
}

/**
 * 生成单个分镜图
 */
export async function generateImage(params: GenerateImageParams): Promise<{
  status: string
  image_id: number
  url: string
}> {
  const response = await api.post('/images/generate', params)
  return response.data
}

/**
 * 获取任务所有分镜图
 */
export async function getTaskImages(taskId: string): Promise<{
  task_id: string
  images: TaskImage[]
}> {
  const response = await api.get(`/images/${taskId}`)
  return response.data
}

/**
 * 重新生成分镜图
 */
export async function regenerateImages(scriptId: number): Promise<{
  new_task_id: string
  status: string
}> {
  const response = await api.post('/images/regenerate', { script_id: scriptId })
  return response.data
}
