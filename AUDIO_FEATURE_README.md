# 🎵 配音/音效功能实施完成

## ✅ 已完成的工作

### 1. 数据库模型（Backend）

**文件**: `backend/app/models/audio.py`

创建了 3 个新表：
- `task_audios` - 配音记录表
- `task_bgm` - 背景音乐记录表
- `task_sfx` - 音效记录表

**迁移状态**: ✅ 已执行 `python3 migrate.py`

### 2. 后端服务（Backend Services）

**文件**: 
- `backend/app/services/audio_service.py` - AI 配音服务（阿里云 TTS）
- `backend/app/services/bgm_service.py` - BGM/音效管理服务

**功能**:
- ✅ 生成单个/批量配音
- ✅ 音视频合并（ffmpeg）
- ✅ BGM/音效库管理
- ✅ 音效智能推荐

### 3. API 路由（Backend Routes）

**文件**: `backend/app/routes/audios.py`

**接口列表**:
| 接口 | 方法 | 说明 |
|------|------|------|
| `/audios/generate` | POST | 生成单个配音 |
| `/audios/generate-all` | POST | 批量生成配音 |
| `/audios/:task_id` | GET | 获取配音列表 |
| `/bgm/list` | GET | 获取 BGM 列表 |
| `/sfx/list` | GET | 获取音效列表 |
| `/sfx/recommend` | POST | 推荐音效 |
| `/categories` | GET | 获取分类 |
| `/bgm/set` | POST | 设置 BGM |
| `/audios/merge` | POST | 合并音视频 |

### 4. BGM/音效库配置

**文件**:
- `backend/bgm_library/bgm_library.json` - 10 首 BGM
- `backend/bgm_library/sfx_library.json` - 12 个音效

**分类**:
- BGM: 自然、古风、现代、生活、史诗
- SFX: 自然、环境、人物、建筑、城市

### 5. 前端 API（Frontend API）

**文件**: `frontend/src/api/audios.ts`

封装了所有音频相关的 API 调用。

### 6. 前端组件（Frontend Components）

**文件**: `frontend/src/components/AudioConfig.vue`

**功能**:
- ✅ 音色选择（7 种阿里云音色）
- ✅ BGM 选择（分组显示）
- ✅ 音量调节滑块
- ✅ 音效自动推荐开关
- ✅ 试听功能（待实现音频播放）

### 7. 页面集成（Page Integration）

**文件**: `frontend/src/views/VideoGen.vue`

**修改**:
- ✅ 导入 AudioConfig 组件
- ✅ 添加音频配置区域
- ✅ 合并时自动生成配音
- ✅ 支持带配音的视频合并

---

## 📋 待完成的工作

### 1. BGM/音效文件准备 ⚠️

**位置**: `backend/bgm_library/`

需要添加实际的音频文件：
- BGM 文件：`bgm_001.mp3` ~ `bgm_010.mp3`
- SFX 文件：`sfx_001.wav` ~ `sfx_012.wav`

**建议**:
- 使用免版权音乐（推荐：[FreePD](https://freepd.com/)、[Bensound](https://www.bensound.com/)）
- 或使用 AI 生成音乐（Suno/Udio）

### 2. 阿里云 TTS API Key 配置 ⚠️

需要在 `backend/.env` 中添加：

```bash
ALIYUN_NLS_TOKEN=your-nls-token
```

**获取方式**: 
1. 登录 [阿里云控制台](https://nls-portal.console.aliyun.com/)
2. 创建项目获取 Token

### 3. 前端音频播放功能

`AudioConfig.vue` 中的试听功能需要实现：
```typescript
const handlePreviewVoice = () => {
  // TODO: 播放试听音频
}

const handlePreviewBGM = () => {
  // TODO: 播放 BGM 试听
}
```

### 4. ffmpeg 验证

确保服务器已安装 ffmpeg：
```bash
ffmpeg -version
ffprobe -version
```

如未安装：
```bash
sudo apt update && sudo apt install ffmpeg
```

---

## 🚀 如何使用

### 后端启动

```bash
cd backend
source venv/bin/activate
python3 run.py
```

### 前端启动

```bash
cd frontend
npm run dev
```

### 使用流程

1. **生成剧本和分镜图**（正常流程）
2. **进入视频生成页面**
3. **配置音频**:
   - 启用配音 → 选择音色
   - 启用 BGM → 选择背景音乐 → 调节音量
   - 启用音效 → 自动推荐
4. **生成视频**（正常流程）
5. **合并视频** → 自动包含配音/BGM/音效

---

## 📊 成本估算

### 阿里云 TTS

| 项目 | 单价 | 说明 |
|------|------|------|
| 智能语音 TTS | ¥0.08/100 字 | 按字符数计费 |

**示例**: 
- 1000 字配音 = ¥0.8
- 5 个分镜 × 200 字 = ¥0.8

### BGM/音效

- **免版权音乐**: 免费
- **AI 生成音乐**: Suno ¥10/月（可选）

---

## 🔧 技术栈

| 模块 | 技术 |
|------|------|
| TTS | 阿里云智能语音 |
| 音频处理 | ffmpeg |
| BGM 库 | JSON 配置 + 本地文件 |
| 前端组件 | Vue 3 + Element Plus |
| 状态管理 | Pinia |

---

## 📝 下一步建议

1. **测试配音生成** - 准备阿里云 NLS Token
2. **收集 BGM 文件** - 下载免版权音乐
3. **实现音频播放** - 前端添加音频播放器
4. **优化合并逻辑** - 精确对齐时间轴
5. **添加音频编辑** - 剪辑、淡入淡出

---

## 🎯 功能演示

### 配音生成
```bash
curl -X POST http://localhost:5000/api/v1/audios/generate \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task_xxx",
    "shot_index": 0,
    "text": "这是一个美丽的清晨",
    "voice_id": "xiaoyun"
  }'
```

### 批量生成配音
```bash
curl -X POST http://localhost:5000/api/v1/audios/generate-all \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task_xxx",
    "script_id": 1,
    "voice_id": "xiaoyun"
  }'
```

### 获取 BGM 列表
```bash
curl http://localhost:5000/api/v1/bgm/list
```

---

**实施完成时间**: 2026-04-24  
**状态**: ✅ 后端完成 | ✅ 前端完成 | ⚠️ 待配置 API Key | ⚠️ 待添加音频文件
