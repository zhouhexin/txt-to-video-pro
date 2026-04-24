import axios from 'axios'
import type { Script, ScriptResponse } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000
})

export interface GenerateScriptParams {
  video_type: string
  theme: string
  keywords?: string
  num_shots?: number
}

/**
 * 生成剧本
 */
export async function generateScript(params: GenerateScriptParams): Promise<ScriptResponse> {
  const response = await api.post<ScriptResponse>('/scripts/generate', params)
  return response.data
}

/**
 * 获取剧本详情
 */
export async function getScript(id: number): Promise<Script> {
  const response = await api.get<Script>(`/scripts/${id}`)
  return response.data
}

/**
 * 搜索剧本列表
 */
export async function searchScripts(params?: {
  theme?: string
  video_type?: string
  limit?: number
}): Promise<{ scripts: Script[]; total: number }> {
  const response = await api.get('/scripts', { params })
  return response.data
}

/**
 * 删除剧本
 */
export async function deleteScript(scriptId: number): Promise<{ success: boolean; deleted_files: string[] }> {
  const response = await api.delete(`/scripts/${scriptId}`)
  return response.data
}
