<template>
  <el-card class="voiceover-config">
    <template #header>
      <div class="card-header">
        <h3>🎙️ 添加配音</h3>
        <el-tag type="warning">最后一步</el-tag>
      </div>
    </template>
    
    <el-alert
      title="配音生成说明"
      type="info"
      :closable="false"
      style="margin-bottom: 20px"
    >
      <p>• 请为每个分镜输入配音文本</p>
      <p>• 生成时间：约 2-5 秒/100 字</p>
      <p>• 完全免费（Edge TTS）</p>
    </el-alert>
    
    <!-- 配音文本输入 -->
    <el-card shadow="hover" style="margin-bottom: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <h4 style="margin: 0">📝 配音文本</h4>
          <el-button size="small" @click="handleFillFromVisual">
            🔄 从画面描述填充
          </el-button>
        </div>
      </template>
      
      <div v-for="(shot, index) in shots" :key="index" class="shot-input">
        <div class="shot-label">镜头 {{ index + 1 }}</div>
        <el-input
          v-model="shot.text"
          type="textarea"
          :rows="2"
          placeholder="请输入该分镜的配音文本..."
          resize="vertical"
        />
      </div>
    </el-card>
    
    <el-form :model="config" label-width="120px">
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
        <el-button @click="handlePreviewVoice">
          🔊 试听示例
        </el-button>
        <span style="margin-left: 10px; color: #909399; font-size: 13px">
          点击播放音色示例
        </span>
      </el-form-item>
      
      <el-divider />
      
      <el-form-item>
        <el-button 
          type="primary" 
          size="large"
          :loading="generating"
          @click="handleGenerateVoiceover"
          style="width: 100%"
        >
          {{ generating ? '正在生成配音...' : '🎙️ 生成所有分镜配音' }}
        </el-button>
      </el-form-item>
      
      <el-form-item v-if="generatedCount > 0">
        <el-progress 
          :percentage="Math.round((generatedCount / totalCount) * 100)" 
          :status="generating ? undefined : 'success'"
        />
        <p style="margin-top: 10px; font-size: 13px; color: #909399">
          已生成 {{ generatedCount }} / {{ totalCount }} 个分镜配音
        </p>
      </el-form-item>
      
      <el-form-item v-if="allCompleted">
        <el-button 
          type="success" 
          size="large"
          :loading="merging"
          @click="handleMergeWithVoiceover"
          style="width: 100%"
        >
          {{ merging ? '合并中...' : '🎬 合并配音到视频' }}
        </el-button>
      </el-form-item>
    </el-form>
    
    <!-- 配音列表预览 -->
    <el-divider v-if="voiceovers.length > 0">配音预览</el-divider>
    
    <div v-if="voiceovers.length > 0" class="voiceover-list">
      <el-collapse accordion>
        <el-collapse-item 
          v-for="(vo, index) in voiceovers" 
          :key="index"
          :title="`镜头 ${index + 1}`"
        >
          <div class="voiceover-item">
            <p style="margin: 0 0 10px 0; font-size: 13px; color: #606266">
              {{ vo.text }}
            </p>
            <audio v-if="vo.url" :src="vo.url" controls style="width: 100%" />
            <el-tag v-else size="small" type="info">生成中...</el-tag>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, reactive, computed, defineExpose, onMounted } from 'vue'
import { generateAllAudios, getTaskAudios, mergeAudioVideo } from '@/api/audios'
import { useUIStore } from '@/stores/ui'

interface VoiceoverConfig {
  voiceId: string
}

const config = reactive<VoiceoverConfig>({
  voiceId: 'xiaoxiao'
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

const props = defineProps<{
  taskId: string
  scriptId?: number
  totalShots: number
}>()

const emit = defineEmits<{
  (e: 'complete', voiceovers: any[]): void
  (e: 'merged', videoUrl: string): void
}>()

const hasVoiceover = computed(() => voiceovers.value.length > 0)
const allCompleted = computed(() => {
  return voiceovers.value.length > 0 && 
         voiceovers.value.every((v: any) => v.status === 'completed')
})

const uiStore = useUIStore()
const generating = ref(false)
const generatedCount = ref(0)
const merging = ref(false)
const voiceovers = ref<any[]>([])
const totalCount = ref(props.totalShots)

// 用户输入的配音文本
const shots = ref<any[]>([])

// 初始化 shots 数组
const initShots = () => {
  shots.value = []
  for (let i = 0; i < props.totalShots; i++) {
    shots.value.push({ shot_index: i, text: '' })
  }
}

// 从已有配音加载文本
const loadTextFromVoiceovers = () => {
  if (voiceovers.value.length > 0) {
    voiceovers.value.forEach((vo: any) => {
      if (shots.value[vo.shot_index]) {
        shots.value[vo.shot_index].text = vo.text
      }
    })
  }
}

// 从画面描述填充
const handleFillFromVisual = async () => {
  try {
    const response = await fetch(`/api/v1/scripts/${props.scriptId}`)
    if (response.ok) {
      const data = await response.json()
      const scriptShots = data.shots || []
      scriptShots.forEach((shot: any, index: number) => {
        if (shots.value[index]) {
          // 优先使用 voiceover 字段，其次 narration，最后 visual
          shots.value[index].text = shot.voiceover || shot.narration || shot.visual || ''
        }
      })
      uiStore.showSuccess('已从画面描述填充配音文本')
    }
  } catch (error) {
    uiStore.showError('加载剧本失败')
  }
}

const handlePreviewVoice = () => {
  const voiceName = voices[config.voiceId as keyof typeof voices]
  alert(`音色：${voiceName}\n\n这是 Edge TTS 免费服务，生成配音后才能试听实际效果。`)
}

const handleGenerateVoiceover = async () => {
  if (!props.taskId) return
  
  // 验证配音文本
  const voiceoverInputs = shots.value.filter(s => s.text && s.text.trim())
  if (voiceoverInputs.length === 0) {
    uiStore.showWarning('请至少输入一个分镜的配音文本')
    return
  }
  
  generating.value = true
  generatedCount.value = 0
  
  try {
    // 生成所有配音，使用用户输入的文本
    const result = await generateAllAudios({
      task_id: props.taskId,
      script_id: props.scriptId,
      voice_id: config.voiceId,
      voiceovers: shots.value.map(s => ({
        shot_index: s.shot_index,
        text: s.text.trim()
      }))
    })
    
    generatedCount.value = result.success_count || 0
    
    // 获取配音列表
    const audioResult = await getTaskAudios(props.taskId)
    voiceovers.value = audioResult.audios || []
    
    emit('complete', voiceovers.value)
    
    if (result.success_count > 0) {
      uiStore.showSuccess(`配音生成成功！${result.success_count}个分镜`)
    }
    if (result.fail_count > 0) {
      uiStore.showWarning(`${result.success_count}个成功，${result.fail_count}个失败`)
    }
    
  } catch (err: any) {
    console.error('生成配音失败:', err)
    uiStore.showError('生成配音失败：' + err.message)
    throw err
  } finally {
    generating.value = false
  }
}

const handleMergeWithVoiceover = async () => {
  if (!props.taskId) return
  
  merging.value = true
  
  try {
    uiStore.showInfo('正在合并配音到视频...')
    
    const result = await mergeAudioVideo({
      task_id: props.taskId
    })
    
    emit('merged', result.final_url)
    uiStore.showSuccess('配音合并成功！')
    
  } catch (err: any) {
    console.error('合并配音失败:', err)
    uiStore.showError('合并失败：' + err.message)
  } finally {
    merging.value = false
  }
}

// 组件挂载时自动加载已有配音
onMounted(async () => {
  if (props.taskId) {
    initShots()
    await loadVoiceovers()
  }
})

const loadVoiceovers = async () => {
  try {
    const result = await getTaskAudios(props.taskId)
    voiceovers.value = result.audios?.filter((a: any) => a.status === 'completed') || []
    generatedCount.value = voiceovers.value.length
    if (voiceovers.value.length > 0) {
      totalCount.value = Math.max(props.totalShots, voiceovers.value.length)
      // 从已有配音加载文本
      loadTextFromVoiceovers()
    }
  } catch (error) {
    console.error('加载配音失败:', error)
  }
}

defineExpose({
  config,
  loadVoiceovers
})
</script>

<style scoped>
.voiceover-config {
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
}

.shot-input {
  margin-bottom: 15px;
}

.shot-input:last-child {
  margin-bottom: 0;
}

.shot-label {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  font-size: 14px;
}

.voiceover-list {
  margin-top: 15px;
}

.voiceover-item {
  padding: 10px 0;
}

:deep(.el-alert__content) {
  font-size: 13px;
}

:deep(.el-alert__content p) {
  margin: 5px 0;
}
</style>
