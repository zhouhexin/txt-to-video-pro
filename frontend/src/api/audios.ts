import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120000
})

/**
 * 生成单个分镜的配音
 */
export async function generateAudio(data: {
  task_id: string
  shot_index: number
  text: string
  voice_id?: string
}) {
  const response = await api.post('/audios/generate', data)
  return response.data
}

/**
 * 批量生成所有分镜的配音
 */
export async function generateAllAudios(data: {
  task_id: string
  script_id?: number
  voice_id?: string
}) {
  const response = await api.post('/audios/generate-all', data)
  return response.data
}

/**
 * 获取任务所有配音
 */
export async function getTaskAudios(taskId: string) {
  const response = await api.get(`/audios/${taskId}`)
  return response.data
}

/**
 * 获取 BGM 列表
 */
export async function getBGMList(params?: {
  category?: string
  mood?: string
}) {
  const response = await api.get('/bgm/list', { params })
  return response.data
}

/**
 * 获取音效列表
 */
export async function getSFXList(params?: {
  category?: string
  tags?: string[]
}) {
  const response = await api.get('/sfx/list', { params })
  return response.data
}

/**
 * 根据场景描述推荐音效
 */
export async function recommendSFX(data: {
  description: string
}) {
  const response = await api.post('/sfx/recommend', data)
  return response.data
}

/**
 * 获取 BGM 和音效分类
 */
export async function getCategories() {
  const response = await api.get('/categories')
  return response.data
}

/**
 * 为任务设置背景音乐
 */
export async function setBGM(data: {
  task_id: string
  bgm_id: string
  bgm_name?: string
  volume?: number
}) {
  const response = await api.post('/bgm/set', data)
  return response.data
}

/**
 * 将配音、BGM、音效与视频合并
 */
export async function mergeAudioVideo(data: {
  task_id: string
}) {
  const response = await api.post('/audios/merge', data)
  return response.data
}
