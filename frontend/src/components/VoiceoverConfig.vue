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
      <p>• 系统将使用分镜的画面描述作为配音文本</p>
      <p>• 生成时间：约 2-5 秒/100 字</p>
      <p>• 完全免费（Edge TTS）</p>
    </el-alert>
    
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
import { ref, reactive, computed, defineExpose } from 'vue'
import { generateAllAudios, getTaskAudios } from '@/api/audios'

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
}>()

const generating = ref(false)
const generatedCount = ref(0)
const voiceovers = ref<any[]>([])

const totalCount = computed(() => props.totalShots)

const handlePreviewVoice = () => {
  const voiceName = voices[config.voiceId as keyof typeof voices]
  alert(`音色：${voiceName}\n\n这是 Edge TTS 免费服务，生成配音后才能试听实际效果。`)
}

const handleGenerateVoiceover = async () => {
  if (!props.taskId) return
  
  generating.value = true
  generatedCount.value = 0
  
  try {
    // 生成所有配音
    const result = await generateAllAudios({
      task_id: props.taskId,
      script_id: props.scriptId,
      voice_id: config.voiceId
    })
    
    generatedCount.value = result.success_count || 0
    
    // 获取配音列表
    const audioResult = await getTaskAudios(props.taskId)
    voiceovers.value = audioResult.audios || []
    
    emit('complete', voiceovers.value)
    
  } catch (err: any) {
    console.error('生成配音失败:', err)
    throw err
  } finally {
    generating.value = false
  }
}

const loadVoiceovers = async () => {
  try {
    const result = await getTaskAudios(props.taskId)
    voiceovers.value = result.audios || []
    generatedCount.value = voiceovers.value.filter((v: any) => v.status === 'completed').length
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
