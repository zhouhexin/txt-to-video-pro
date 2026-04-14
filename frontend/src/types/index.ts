// 剧本类型
export interface Shot {
  scene: string
  visual: string
  camera: string
  duration: number
  prompt: string
}

export interface Script {
  id: number
  title: string
  theme: string
  video_type: string
  keywords: string
  overview: string
  style: string
  shots: Shot[]
  task_id: string
  search_source: string
  created_at: string
  updated_at: string
}

// 任务类型
export interface Task {
  id: string
  script_id: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  step: 'script' | 'image' | 'video'
  progress: number
  error_message?: string
  created_at: string
  updated_at: string
}

// 分镜图类型
export interface TaskImage {
  id: number
  task_id: string
  shot_index: number
  file_path: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  prompt?: string
  url?: string
  created_at: string
}

// 视频类型
export interface TaskVideo {
  id: number
  task_id: string
  shot_index: number
  file_path: string
  duration: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  prompt?: string
  url?: string
  created_at: string
}

// API 响应类型
export interface ScriptResponse {
  script_id: number
  task_id: string
  script: Script
}

export interface ImageResponse {
  status: string
  image_id: number
  url: string
}

export interface VideoResponse {
  status: string
  video_id: number
  url: string
}
