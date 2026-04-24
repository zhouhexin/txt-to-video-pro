<template>
  <el-card class="audio-config">
    <template #header>
      <div class="card-header">
        <h3>🎵 配音与音效配置</h3>
      </div>
    </template>
    
    <el-form :model="config" label-width="120px" size="default">
      <!-- 配音设置 -->
      <el-form-item label="启用配音">
        <el-switch v-model="config.enableVoice" />
      </el-form-item>
      
      <template v-if="config.enableVoice">
        <el-form-item label="选择音色">
          <el-select v-model="config.voiceId" placeholder="选择音色" style="width: 100%">
            <el-option
              v-for="(voice, key) in voices"
              :key="key"
              :label="voice"
              :value="key"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="试听音色">
          <el-button 
            @click="handlePreviewVoice" 
            :loading="playingVoice"
          >
            {{ playingVoice ? '停止播放' : '🔊 试听' }}
          </el-button>
          <span v-if="playingVoice" style="margin-left: 10px; color: #67c23a">
            播放中...
          </span>
        </el-form-item>
      </template>
      
      <el-divider />
      
      <!-- BGM 设置 -->
      <el-form-item label="启用 BGM">
        <el-switch v-model="config.enableBGM" />
      </el-form-item>
      
      <template v-if="config.enableBGM">
        <el-form-item label="选择 BGM">
          <el-select 
            v-model="config.bgmId" 
            placeholder="选择背景音乐" 
            filterable
            style="width: 100%"
          >
            <el-option-group
              v-for="group in bgmGroups"
              :key="group.category"
              :label="group.category"
            >
              <el-option
                v-for="bgm in group.items"
                :key="bgm.id"
                :label="bgm.name"
                :value="bgm.id"
              >
                <span style="float: left">{{ bgm.name }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px">{{ bgm.mood }}</span>
              </el-option>
            </el-option-group>
          </el-select>
        </el-form-item>
        
        <el-form-item label="BGM 音量">
          <el-slider v-model="config.bgmVolume" :min="0" :max="1" :step="0.1" style="width: 80%" />
          <span style="margin-left: 10px">{{ Math.round(config.bgmVolume * 100) }}%</span>
        </el-form-item>
        
        <el-form-item label="试听 BGM">
          <el-button 
            @click="handlePreviewBGM" 
            :loading="playingBGM"
          >
            {{ playingBGM ? '停止播放' : '🔊 试听' }}
          </el-button>
          <span v-if="playingBGM" style="margin-left: 10px; color: #67c23a">
            播放中...
          </span>
        </el-form-item>
      </template>
      
      <el-divider />
      
      <!-- 音效设置 -->
      <el-form-item label="启用音效">
        <el-switch v-model="config.enableSFX" />
      </el-form-item>
      
      <template v-if="config.enableSFX">
        <el-form-item label="自动推荐">
          <el-switch v-model="config.autoSFX" />
          <span style="margin-left: 10px; color: #999; font-size: 13px">
            根据场景描述自动推荐音效
          </span>
        </el-form-item>
        
        <el-form-item v-if="!config.autoSFX" label="选择音效">
          <el-select 
            v-model="config.sfxIds" 
            multiple 
            placeholder="选择音效" 
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="sfx in sfxList"
              :key="sfx.id"
              :label="sfx.name"
              :value="sfx.id"
            />
          </el-select>
        </el-form-item>
      </template>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { getBGMList, getSFXList, getCategories } from '@/api/audios'

interface AudioConfig {
  enableVoice: boolean
  voiceId: string
  enableBGM: boolean
  bgmId: string
  bgmVolume: number
  enableSFX: boolean
  autoSFX: boolean
  sfxIds: string[]
}

const config = reactive<AudioConfig>({
  enableVoice: true,
  voiceId: 'xiaoxiao',
  enableBGM: true,
  bgmId: '',
  bgmVolume: 0.3,
  enableSFX: false,
  autoSFX: true,
  sfxIds: []
})

const voices = {
  xiaoxiao: 'zh-CN-XiaoxiaoNeural - 温柔女声（新闻、有声书）',
  xiaoyi: 'zh-CN-XiaoyiNeural - 活泼女声（卡通、有声书）',
  yunjian: 'zh-CN-YunjianNeural - 激情男声（体育、有声书）',
  yunxi: 'zh-CN-YunxiNeural - 阳光男声（有声书）',
  yunxia: 'zh-CN-YunxiaNeural - 可爱男声（卡通、有声书）',
  yunyang: 'zh-CN-YunyangNeural - 专业男声（新闻）',
  xiaobei: 'zh-CN-liaoning-XiaobeiNeural - 东北话（方言）',
  xiaoni: 'zh-CN-shaanxi-XiaoniNeural - 陕西话（方言）'
}

const bgmList = ref<any[]>([])
const sfxList = ref<any[]>([])
const categories = ref<any>({ bgm: [], sfx: [] })

// 音频播放状态
const playingVoice = ref(false)
const playingBGM = ref(false)
const currentAudio = ref<HTMLAudioElement | null>(null)

const bgmGroups = computed(() => {
  const groups: Record<string, any[]> = {}
  bgmList.value.forEach((bgm) => {
    const category = bgm.category || '其他'
    if (!groups[category]) groups[category] = []
    groups[category].push(bgm)
  })
  return Object.entries(groups).map(([category, items]) => ({
    category,
    items
  }))
})

onMounted(async () => {
  await loadBGM()
  await loadSFX()
  await loadCategories()
})

onUnmounted(() => {
  // 清理音频播放
  stopCurrentAudio()
})

const loadBGM = async () => {
  try {
    const result = await getBGMList()
    bgmList.value = result.bgm_list || []
  } catch (error) {
    console.error('加载 BGM 列表失败:', error)
  }
}

const loadSFX = async () => {
  try {
    const result = await getSFXList()
    sfxList.value = result.sfx_list || []
  } catch (error) {
    console.error('加载音效列表失败:', error)
  }
}

const loadCategories = async () => {
  try {
    const result = await getCategories()
    categories.value = result.categories || {}
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

// 停止当前播放
const stopCurrentAudio = () => {
  if (currentAudio.value) {
    currentAudio.value.pause()
    currentAudio.value.currentTime = 0
    currentAudio.value = null
  }
  playingVoice.value = false
  playingBGM.value = false
}

// 播放音频
const playAudio = (url: string, type: 'voice' | 'bgm') => {
  // 如果正在播放，先停止
  if (currentAudio.value) {
    stopCurrentAudio()
  }
  
  // 创建新的 Audio 对象
  const audio = new Audio(url)
  audio.preload = 'auto'
  
  // 设置事件监听
  audio.onended = () => {
    if (type === 'voice') {
      playingVoice.value = false
    } else {
      playingBGM.value = false
    }
    currentAudio.value = null
  }
  
  audio.onerror = (e) => {
    console.error('音频播放失败:', e)
    if (type === 'voice') {
      playingVoice.value = false
    } else {
      playingBGM.value = false
    }
    currentAudio.value = null
    alert('音频播放失败，请检查文件是否存在')
  }
  
  currentAudio.value = audio
  
  // 开始播放
  audio.play().catch(err => {
    console.error('播放错误:', err)
    alert('播放失败：' + err.message)
    stopCurrentAudio()
  })
  
  // 更新状态
  if (type === 'voice') {
    playingVoice.value = true
  } else {
    playingBGM.value = true
  }
}

const handlePreviewVoice = () => {
  // 如果正在播放此音色，停止
  if (playingVoice.value) {
    stopCurrentAudio()
    return
  }
  
  // Edge TTS 不支持在线试听，显示提示
  // 实际项目中可以预先录制好每个音色的示例音频
  const voiceName = voices[config.voiceId as keyof typeof voices]
  alert(`音色：${voiceName}\n\n注意：Edge TTS 需要生成后才能试听。\n您可以在生成配音后，在成果展示页面播放完整视频。`)
}

const handlePreviewBGM = () => {
  if (!config.bgmId) {
    alert('请先选择 BGM')
    return
  }
  
  // 如果正在播放此 BGM，停止
  if (playingBGM.value) {
    stopCurrentAudio()
    return
  }
  
  const bgm = bgmList.value.find(b => b.id === config.bgmId)
  if (bgm) {
    const url = `/api/v1/files/bgm/${bgm.file}`
    playAudio(url, 'bgm')
  }
}

defineExpose({
  config
})
</script>

<style scoped>
.audio-config {
  max-width: 800px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-divider) {
  margin: 20px 0;
}
</style>
