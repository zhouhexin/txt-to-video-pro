# AI 视频生成平台 - 专业版 (txt-to-video-pro)

基于 Vue 3 + Flask 的 AI 视频生成平台，从剧本到成片的全流程自动化。

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3.4 + TypeScript + Element Plus + Pinia |
| **后端** | Flask 3.0 + SQLite |
| **AI 服务** | 阿里云百炼（通义千问 + 通义万相） |

## 快速开始

### 1. 配置 API Key

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入你的阿里云百炼 API Key
```

### 2. 一键启动

```bash
./start.sh
```

或手动启动：

```bash
# 终端 1：后端
cd backend
pip3 install -r requirements.txt
python run.py

# 终端 2：前端
cd frontend
npm install
npm run dev
```

### 3. 访问应用

- 前端：http://localhost:5173
- 后端 API：http://localhost:5000

## 功能模块

### 1. 智能剧本生成
- 支持多种视频类型（文旅宣传、产品展示、教程等）
- AI 自动生成完整剧本和分镜描述
- 支持自定义分镜数量

### 2. 分镜图生成
- 批量/单个生成分镜图
- 支持重新生成
- 实时预览

### 3. 视频生成
- 单镜头/链式连续两种模式
- 自定义视频时长
- 自动合并为完整视频

### 4. 成果展示
- 完整视频播放
- 分镜预览
- 下载功能

## API 接口

### 剧本管理
- `POST /api/v1/scripts/generate` - 生成剧本
- `GET /api/v1/scripts/:id` - 获取剧本详情
- `GET /api/v1/scripts` - 搜索剧本
- `PUT /api/v1/scripts/:id/confirm` - 确认剧本
- `DELETE /api/v1/scripts/:id` - 删除剧本

### 分镜图
- `POST /api/v1/images/generate` - 生成单个分镜
- `GET /api/v1/images/:task_id` - 获取所有分镜
- `POST /api/v1/images/regenerate` - 重新生成

### 视频
- `POST /api/v1/videos/generate` - 生成单个视频
- `GET /api/v1/videos/:task_id` - 获取所有视频
- `POST /api/v1/videos/merge` - 合并视频

### 文件
- `GET /api/v1/files/image/:task_id/:filename` - 下载图片
- `GET /api/v1/files/video/:task_id/:filename` - 下载视频

## 目录结构

```
txt-to-video-pro/
├── backend/
│   ├── app/
│   │   ├── models/        # 数据库模型
│   │   ├── routes/        # API 路由
│   │   ├── services/      # 业务逻辑
│   │   └── utils/         # 工具函数
│   ├── data/              # SQLite 数据库
│   ├── output_tasks/      # 视频输出
│   └── run.py             # 启动脚本
├── frontend/
│   ├── src/
│   │   ├── api/           # API 封装
│   │   ├── components/    # 通用组件
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── views/         # 页面组件
│   │   └── types/         # TypeScript 类型
│   └── package.json
└── start.sh               # 一键启动
```

## 生产部署

### Nginx 配置

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
}
```

### 构建前端

```bash
cd frontend
npm run build
```

### 使用 Gunicorn 运行后端

```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## 注意事项

1. **API Key**: 需要阿里云百炼 API Key 才能使用 AI 功能
2. **ffmpeg**: 视频合并需要安装 ffmpeg
3. **端口**: 默认使用 5000（后端）和 5173（前端）
4. **数据库**: SQLite 数据库自动创建在 `backend/data/app.db`

## 开发计划

- [ ] WebSocket 实时进度推送
- [ ] 用户认证系统
- [ ] 视频编辑功能
- [ ] 配音合成集成
- [ ] 字幕自动生成

## License

MIT
