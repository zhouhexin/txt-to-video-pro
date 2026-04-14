# txt-to-video-pro - AI 视频生成平台专业版

## 技能描述

基于 Vue 3 + Flask 的 AI 视频生成平台，从剧本到成片的全流程自动化。相比 Streamlit 版本提供更好的用户体验和性能。

## 适用场景

- 用户希望替换 Streamlit 前端为更现代的 Vue 3
- 需要更好的用户体验和页面性能
- 保持简单的本地部署（无需 Docker/容器化）
- 使用 SQLite 数据库，无需复杂的数据库配置
- 文件存储在本地，无需云存储

## 项目架构

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Vue 3.4 + TypeScript | 组合式 API，类型安全 |
| **状态管理** | Pinia | Vue 官方推荐的状态管理 |
| **路由** | Vue Router 4 | 页面路由和导航守卫 |
| **UI 组件** | Element Plus | 成熟的 Admin 组件库 |
| **HTTP** | Axios | 请求拦截和错误处理 |
| **构建工具** | Vite 5 | 快速 HMR 和构建 |
| **后端** | Flask 3.0 | Python Web 框架 |
| **数据库** | SQLite 3 | 本地文件数据库 |
| **文件存储** | 本地文件系统 | 直接保存到磁盘 |
| **部署** | 直接运行 | Python + Nginx |

### 目录结构

```
txt-video-pipeline/
├── backend/                    # Flask 后端
│   ├── app/
│   │   ├── __init__.py        # Flask 应用工厂
│   │   ├── config.py          # 配置文件
│   │   ├── models/            # 数据库模型
│   │   │   ├── script.py      # 剧本模型
│   │   │   ├── task.py        # 任务模型
│   │   │   └── knowledge.py   # 知识库模型
│   │   ├── routes/            # API 路由
│   │   │   ├── scripts.py     # 剧本 API
│   │   │   ├── images.py      # 图片 API
│   │   │   ├── videos.py      # 视频 API
│   │   │   └── files.py       # 文件 API
│   │   ├── services/          # 业务逻辑层
│   │   │   ├── script_service.py
│   │   │   ├── image_service.py
│   │   │   └── video_service.py
│   │   └── utils/             # 工具函数
│   ├── data/                  # SQLite 数据库目录
│   │   └── app.db
│   ├── output_tasks/          # 视频输出目录（符号链接到原项目）
│   ├── requirements.txt
│   └── run.py                 # 启动脚本
│
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/            # 路由配置
│   │   │   └── index.ts
│   │   ├── stores/            # Pinia 状态管理
│   │   │   ├── script.ts      # 剧本状态
│   │   │   ├── task.ts        # 任务状态
│   │   │   └── ui.ts          # UI 状态
│   │   ├── api/               # API 封装
│   │   │   ├── scripts.ts
│   │   │   ├── images.ts
│   │   │   └── videos.ts
│   │   ├── views/             # 页面组件
│   │   │   ├── ScriptGen.vue      # 步骤 1: 剧本生成
│   │   │   ├── ImageGen.vue       # 步骤 2: 分镜生成
│   │   │   ├── VideoGen.vue       # 步骤 3: 视频生成
│   │   │   ├── Showcase.vue       # 步骤 4: 成果展示
│   │   │   ├── History.vue        # 历史剧本
│   │   │   └── VideoHistory.vue   # 视频历史
│   │   ├── components/        # 通用组件
│   │   │   ├── ScriptPreview.vue
│   │   │   ├── ImageGrid.vue
│   │   │   ├── VideoPlayer.vue
│   │   │   └── StepProgress.vue
│   │   ├── hooks/             # 组合式函数
│   │   │   ├── usePolling.ts  # 轮询任务状态
│   │   │   └── useFileDownload.ts
│   │   └── types/             # TypeScript 类型定义
│   │       └── index.ts
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── start.sh                   # 一键启动脚本
└── README.md
```

## API 接口设计

### 剧本管理 API

```yaml
POST /api/v1/scripts/generate
  描述：生成新剧本（同步等待 AI 返回）
  请求：
    {
      "video_type": "文旅宣传",
      "theme": "西安大唐芙蓉园",
      "keywords": "古风，唐代，夜景",
      "num_shots": 5
    }
  响应：
    {
      "script_id": 12,
      "task_id": "task_1775801289_00000009",
      "script": {
        "id": 12,
        "title": "西安大唐芙蓉园 - 文旅宣传",
        "overview": "...",
        "shots": [...]
      }
    }

GET /api/v1/scripts/:id
  描述：获取剧本详情
  响应：
    {
      "id": 12,
      "title": "西安大唐芙蓉园 - 文旅宣传",
      "theme": "西安大唐芙蓉园",
      "video_type": "文旅宣传",
      "shots": [
        {
          "scene": "镜头 1: 开场全景",
          "visual": "...",
          "camera": "pull",
          "duration": 5,
          "prompt": "..."
        }
      ],
      "task_id": "task_1775801289_00000009"
    }

GET /api/v1/scripts
  描述：搜索剧本列表
  查询参数：?theme=西安&video_type=文旅宣传&limit=50
  响应：
    {
      "scripts": [...],
      "total": 10
    }

PUT /api/v1/scripts/:id/confirm
  描述：确认剧本，进入分镜生成步骤
  响应：
    {
      "success": true,
      "task_id": "task_1775801289_00000009"
    }

DELETE /api/v1/scripts/:id
  描述：删除剧本及相关文件
  响应：
    {
      "success": true,
      "deleted_files": [
        "output_tasks/task_xxx/frames/*",
        "output_tasks/task_xxx/videos/*"
      ]
    }
```

### 分镜图生成 API

```yaml
POST /api/v1/images/generate
  描述：生成单个分镜图（同步等待）
  请求：
    {
      "task_id": "task_1775801289_00000009",
      "shot_index": 0,
      "prompt": "wide establishing shot of ..."
    }
  响应：
    {
      "status": "completed",
      "image_id": 1,
      "url": "/api/v1/files/image/task_1775801289_00000009/shot_0.png"
    }

GET /api/v1/images/:task_id
  描述：获取任务所有分镜图
  响应：
    {
      "task_id": "task_1775801289_00000009",
      "images": [
        {
          "shot_index": 0,
          "url": "/api/v1/files/image/task_1775801289_00000009/shot_0.png",
          "status": "completed",
          "created_at": "2026-04-10T14:00:00Z"
        }
      ]
    }

POST /api/v1/images/regenerate
  描述：重新生成分镜图（创建新 task_id）
  请求：
    {
      "script_id": 12
    }
  响应：
    {
      "new_task_id": "task_1775801300_00000010",
      "status": "success"
    }
```

### 视频生成 API

```yaml
POST /api/v1/videos/generate
  描述：生成单个视频（同步等待，可能较慢）
  请求：
    {
      "task_id": "task_1775801289_00000009",
      "shot_index": 0,
      "duration": 5,
      "mode": "chain"
    }
  响应：
    {
      "status": "completed",
      "video_id": 1,
      "url": "/api/v1/files/video/task_1775801289_00000009/shot_1.mp4"
    }

GET /api/v1/videos/:task_id
  描述：获取任务所有视频
  响应：
    {
      "task_id": "task_1775801289_00000009",
      "videos": [
        {
          "shot_index": 0,
          "url": "/api/v1/files/video/task_1775801289_00000009/shot_1.mp4",
          "status": "completed",
          "duration": 5
        }
      ],
      "merged_video": {
        "url": "/api/v1/files/video/task_1775801289_00000009/merged_full_video.mp4",
        "status": "completed"
      } | null
    }

POST /api/v1/videos/merge
  描述：拼接所有视频为完整视频（同步等待）
  请求：
    {
      "task_id": "task_1775801289_00000009"
    }
  响应：
    {
      "status": "completed",
      "merged_url": "/api/v1/files/video/task_1775801289_00000009/merged_full_video.mp4"
    }
```

### 文件服务 API

```yaml
GET /api/v1/files/image/:task_id/:filename
  描述：下载分镜图片
  响应：图片文件流（image/png）

GET /api/v1/files/video/:task_id/:filename
  描述：下载视频文件
  响应：视频文件流（video/mp4）
```

## 数据库模型

### Script 模型
```python
class Script(db.Model):
    __tablename__ = 'scripts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    theme = db.Column(db.String(500))
    video_type = db.Column(db.String(50))
    keywords = db.Column(db.Text)
    overview = db.Column(db.Text)
    style = db.Column(db.Text)
    shots = db.Column(db.JSON)  # 存储分镜数组
    task_id = db.Column(db.String(50))  # 主 task_id
    search_source = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

### Task 模型
```python
class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.String(50), primary_key=True)  # task_id
    script_id = db.Column(db.Integer, db.ForeignKey('scripts.id'))
    status = db.Column(db.String(20), default='pending')
    step = db.Column(db.String(20))  # script, image, video
    progress = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    script = db.relationship('Script', backref='tasks')
```

### TaskImage 模型
```python
class TaskImage(db.Model):
    __tablename__ = 'task_images'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(50), db.ForeignKey('tasks.id'))
    shot_index = db.Column(db.Integer)
    file_path = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    task = db.relationship('Task', backref='images')
```

### TaskVideo 模型
```python
class TaskVideo(db.Model):
    __tablename__ = 'task_videos'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(50), db.ForeignKey('tasks.id'))
    shot_index = db.Column(db.Integer)
    file_path = db.Column(db.String(500))
    duration = db.Column(db.Integer)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    task = db.relationship('Task', backref='videos')
```

## 前端核心组件

### StepProgress.vue（步骤进度条）
```vue
<template>
  <el-steps :active="currentStep" finish-status="success" align-center>
    <el-step title="📝 智能剧本" />
    <el-step title="🎨 分镜生成" />
    <el-step title="🎬 视频生成" />
    <el-step title="📊 成果展示" />
  </el-steps>
</template>

<script setup lang="ts">
defineProps<{
  currentStep: number
}>()
</script>
```

### ScriptPreview.vue（剧本预览）
```vue
<template>
  <el-card class="script-preview">
    <template #header>
      <div class="card-header">
        <h3>{{ script.title }}</h3>
        <el-tag>{{ script.video_type }}</el-tag>
      </div>
    </template>
    
    <el-descriptions :column="2" border>
      <el-descriptions-item label="主题">{{ script.theme }}</el-descriptions-item>
      <el-descriptions-item label="分镜数">{{ script.shots?.length || 0 }}</el-descriptions-item>
      <el-descriptions-item label="关键词">{{ script.keywords }}</el-descriptions-item>
    </el-descriptions>
    
    <el-collapse>
      <el-collapse-item 
        v-for="(shot, i) in script.shots" 
        :key="i" 
        :title="shot.scene"
      >
        <p><strong>画面描述:</strong></p>
        <p>{{ shot.visual }}</p>
        <p><strong>运镜:</strong> {{ shot.camera }}</p>
        <p><strong>Prompt:</strong></p>
        <pre>{{ shot.prompt }}</pre>
      </el-collapse-item>
    </el-collapse>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{
  script: {
    id: number
    title: string
    theme: string
    video_type: string
    keywords: string
    shots: Array<any>
  }
}>()
</script>
```

### VideoPlayer.vue（视频播放器）
```vue
<template>
  <div class="video-player">
    <video :src="src" controls :poster="poster" class="video-element" />
    <div class="video-info" v-if="title">
      <h4>{{ title }}</h4>
      <p>{{ description }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  src: string
  poster?: string
  title?: string
  description?: string
}>()
</script>

<style scoped>
.video-element {
  width: 100%;
  max-height: 500px;
  border-radius: 8px;
}
</style>
```

## 状态管理（Pinia）

### script.ts
```typescript
import { defineStore } from 'pinia'

export const useScriptStore = defineStore('script', {
  state: () => ({
    currentScript: null as any | null,
    scriptList: [] as any[],
    isLoading: false
  }),
  
  actions: {
    async fetchScript(id: number) {
      this.isLoading = true
      try {
        const res = await fetch(`/api/v1/scripts/${id}`)
        this.currentScript = await res.json()
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchList(params?: any) {
      this.isLoading = true
      try {
        const query = new URLSearchParams(params).toString()
        const res = await fetch(`/api/v1/scripts?${query}`)
        this.scriptList = (await res.json()).scripts
      } finally {
        this.isLoading = false
      }
    }
  }
})
```

### task.ts
```typescript
import { defineStore } from 'pinia'

export const useTaskStore = defineStore('task', {
  state: () => ({
    taskId: null as string | null,
    currentStep: 1,
    genMode: 'single' as 'single' | 'chain',
    isChainMode: computed(() => state.genMode === 'chain')
  }),
  
  actions: {
    setTaskId(id: string) {
      this.taskId = id
    },
    
    setStep(step: number) {
      this.currentStep = step
    },
    
    setGenMode(mode: 'single' | 'chain') {
      this.genMode = mode
    }
  }
})
```

## 轮询方案（替代 WebSocket）

### usePolling.ts
```typescript
export function usePolling() {
  const intervals = new Map<string, number>()
  
  function startPolling(
    key: string,
    url: string,
    callback: (data: any) => void,
    intervalMs: number = 2000
  ) {
    const poll = async () => {
      try {
        const res = await fetch(url)
        const data = await res.json()
        callback(data)
        
        // 如果任务完成，停止轮询
        if (data.status === 'completed' || data.status === 'failed') {
          stopPolling(key)
        }
      } catch (error) {
        console.error('Polling error:', error)
      }
    }
    
    // 立即执行一次
    poll()
    
    // 设置定时轮询
    const intervalId = window.setInterval(poll, intervalMs)
    intervals.set(key, intervalId)
    
    return () => stopPolling(key)
  }
  
  function stopPolling(key: string) {
    const intervalId = intervals.get(key)
    if (intervalId) {
      window.clearInterval(intervalId)
      intervals.delete(key)
    }
  }
  
  function stopAll() {
    intervals.forEach((id) => window.clearInterval(id))
    intervals.clear()
  }
  
  return { startPolling, stopPolling, stopAll }
}
```

## 部署说明

### 1. 安装依赖

```bash
# 后端
cd backend
pip3 install -r requirements.txt

# 前端
cd frontend
npm install
```

### 2. 配置环境变量

```bash
# backend/.env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_PATH=./data/app.db
OUTPUT_DIR=./output_tasks
ALIYUN_BAILIAN_API_KEY=your-api-key
```

### 3. 启动服务

```bash
# 方式 1：使用启动脚本
./start.sh

# 方式 2：手动启动
# 终端 1：后端
cd backend
python3 run.py

# 终端 2：前端
cd frontend
npm run dev
```

### 4. 访问地址

- 前端开发：http://localhost:5173
- 后端 API：http://localhost:5000/api/v1

### 5. 生产部署（Nginx）

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端 API 代理
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # 文件下载
    location /files/ {
        proxy_pass http://localhost:5000/api/v1/files/;
        proxy_set_header Host $host;
    }
}
```

## 迁移计划

### 阶段 1：后端 API（5-7 天）
- [ ] 项目搭建、数据库模型
- [ ] 剧本 API（CRUD + AI 集成）
- [ ] 图片/视频 API（文件上传下载）
- [ ] 文件服务、单元测试

### 阶段 2：前端框架（3-4 天）
- [ ] Vue 项目搭建、路由配置
- [ ] Pinia 状态管理、Axios 封装
- [ ] 通用组件、UI 主题定制

### 阶段 3：核心页面（8-12 天）
- [ ] 步骤 1：剧本生成页面
- [ ] 步骤 2-3：分镜/视频生成页面
- [ ] 步骤 4：成果展示页面
- [ ] 历史剧本、视频历史页面
- [ ] 联调测试、Bug 修复

### 阶段 4：部署（1-2 天）
- [ ] Nginx 配置
- [ ] 启动脚本
- [ ] 部署文档

**总工期**: 18-25 天（单人开发）

## 与原始 skill 对比

| 特性 | 原始 skill (Streamlit) | 新 skill (Vue + Flask) |
|------|------------------------|------------------------|
| **前端框架** | Streamlit | Vue 3 + TypeScript |
| **状态管理** | st.session_state | Pinia |
| **路由** | st.navigation | Vue Router |
| **UI 组件** | Streamlit 内置 | Element Plus |
| **实时推送** | 轮询 + st.rerun | 轮询（可升级 WebSocket） |
| **数据库** | SQLite | SQLite（兼容） |
| **文件存储** | 本地 | 本地（兼容） |
| **部署** | streamlit run | Nginx + Gunicorn |
| **性能** | 一般 | 优秀 |
| **用户体验** | 一般 | 优秀 |
| **开发成本** | 低 | 中等 |
| **维护成本** | 低 | 中等 |

## 兼容性说明

1. **数据库兼容**: 直接使用现有 SQLite 数据库，无需迁移
2. **文件存储兼容**: 符号链接到现有 `output_tasks/` 目录
3. **API 兼容**: 保留现有 AI 调用逻辑（阿里云百炼）
4. **业务逻辑兼容**: 复用现有的剧本生成、图片生成、视频生成服务

## 注意事项

1. **同步 vs 异步**: 为简化部署，API 采用同步处理，视频生成时前端需要显示进度条
2. **轮询间隔**: 建议 2 秒轮询一次，避免频繁请求
3. **文件权限**: 确保 `output_tasks/` 目录有读写权限
4. **CORS 配置**: 开发环境需要启用 CORS
5. **生产环境**: 建议使用 Gunicorn 运行 Flask，Nginx 反向代理

## 相关文档

- 原始 skill: `/home/ubuntu/.openclaw/workspace-claw2/skills/txt-video-pipeline/SKILL.md`
- 前端目录：`/home/ubuntu/.openclaw/workspace-claw2/skills/vue-flask-frontend/frontend/`
- 后端目录：`/home/ubuntu/.openclaw/workspace-claw2/skills/vue-flask-frontend/backend/`

## 激活方式

当用户提到以下关键词时激活此 skill：
- "txt-to-video-pro"
- "Vue 前端"
- "Flask 后端"
- "前端迁移"
- "替换 Streamlit"
- "专业版"
