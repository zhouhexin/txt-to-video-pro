<template>
  <div class="script-gen">
    <el-card class="form-card">
      <template #header>
        <h2>📝 智能剧本生成</h2>
      </template>
      
      <el-form :model="form" label-width="100px" label-position="top">
        <el-form-item label="视频类型" required>
          <el-select v-model="form.video_type" placeholder="请选择视频类型" style="width: 100%">
            <el-option label="文旅宣传" value="文旅宣传" />
            <el-option label="产品展示" value="产品展示" />
            <el-option label="教程视频" value="教程视频" />
            <el-option label="故事短片" value="故事短片" />
            <el-option label="企业宣传片" value="企业宣传片" />
            <el-option label="社交媒体" value="社交媒体" />
          </el-select>
        </el-form-item>
        
        <!-- 场景选择器 (暂时禁用) -->
        
        <el-form-item label="主题" required>
          <el-input 
            v-model="form.theme" 
            placeholder="例如：西安大唐芙蓉园、新款智能手机发布"
            :disabled="generating"
            @blur="fetchHotKeywords"
          />
        </el-form-item>
        
        <!-- 微博热点关键词推荐 -->
        <el-form-item v-if="hotKeywords.length > 0" label="🔥 热点推荐">
          <div class="hot-keywords-container">
            <el-tag
              v-for="kw in hotKeywords"
              :key="kw.word"
              size="large"
              effect="plain"
              class="hot-keyword-tag"
              @click="addKeyword(kw.word)"
            >
              {{ kw.word }}
              <span class="hot-score">{{ kw.hot_score }}</span>
            </el-tag>
            <el-button size="small" @click="refreshKeywords" style="margin-left: 8px">
              🔄 刷新
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="关键词">
          <el-input 
            v-model="form.keywords" 
            placeholder="例如：古风，唐代，夜景、科技感、简约"
            :disabled="generating"
          />
        </el-form-item>
        
        <el-form-item label="分镜数量">
          <el-slider v-model="form.num_shots" :min="1" :max="10" :step="1" show-input />
        </el-form-item>
        
        <!-- 提示词优化 -->
        <PromptOptimizer 
          :original-prompt="form.theme"
          v-model:optimized-prompt="form.optimized_theme"
          :scene-type="form.scene_type"
          :task-id="tempTaskId"
          :keywords="form.keywords"
          :video-type="form.video_type"
        />
        
        <el-form-item style="margin-top: 20px">
          <el-button 
            type="primary" 
            size="large" 
            :loading="generating"
            @click="handleGenerate"
            style="width: 100%"
          >
            {{ generating ? 'AI 创作中...' : '✨ 开始生成剧本' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 剧本预览 -->
    <ScriptPreview v-if="scriptStore.currentScript" :script="scriptStore.currentScript" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useScriptStore } from '@/stores/script'
import { useTaskStore } from '@/stores/task'
import { useUIStore } from '@/stores/ui'
import ScriptPreview from '@/components/ScriptPreview.vue'
import PromptOptimizer from '@/components/PromptOptimizer.vue'

const router = useRouter()
const scriptStore = useScriptStore()
const taskStore = useTaskStore()
const uiStore = useUIStore()

const generating = ref(false)

// 临时 taskId（用于提示词优化的 token 统计，后续会更新为真实 task_id）
const tempTaskId = ref(`task_${Date.now()}_00000000`)

// 热点关键词
const hotKeywords = ref<Array<{ word: string; hot_score: number }>>([])

// 页面加载时清空当前剧本，避免显示历史剧本
onMounted(() => {
  scriptStore.setCurrentScript(null)
  tempTaskId.value = `task_${Date.now()}_00000000`
})

const form = reactive({
  video_type: '文旅宣传',
  theme: '',
  optimized_theme: '',
  scene_type: '',
  keywords: '',
  num_shots: 5
})

// 监听主题变化，自动清空优化结果
watch(() => form.theme, () => {
  form.optimized_theme = ''
})

// 获取热点关键词
const fetchHotKeywords = async () => {
  if (!form.theme || !form.video_type) return
  
  try {
    const res = await fetch('/api/v1/weibo/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        video_type: form.video_type,
        theme: form.theme
      })
    })
    
    const data = await res.json()
    if (data.success) {
      hotKeywords.value = data.keywords || []
    }
  } catch (error) {
    console.error('获取热点关键词失败:', error)
  }
}

// 添加关键词到输入框
const addKeyword = (word: string) => {
  if (form.keywords) {
    if (!form.keywords.includes(word)) {
      form.keywords += `, ${word}`
    }
  } else {
    form.keywords = word
  }
}

// 刷新关键词
const refreshKeywords = () => {
  hotKeywords.value = []
  fetchHotKeywords()
}

const handleGenerate = async () => {
  if (!form.theme) {
    uiStore.showError('请输入主题')
    return
  }
  
  generating.value = true
  try {
    // 使用优化后的主题（如果有）
    const themeToUse = form.optimized_theme || form.theme
    
    console.log('开始生成剧本...', themeToUse)
    
    const result = await scriptStore.createScript({
      video_type: form.video_type,
      theme: themeToUse,  // 优化后的主题
      original_theme: form.theme,  // 原始主题
      keywords: form.keywords,
      num_shots: form.num_shots,
      scene_type: form.scene_type || undefined
    })
    
    console.log('剧本生成成功，result:', result)
    uiStore.showSuccess('剧本生成成功！')
    
    // 设置任务 ID
    taskStore.setTaskId(result.task_id)
    console.log('任务 ID 已设置:', result.task_id, ', currentScript:', scriptStore.currentScript)
    
    // 确保 currentScript 已设置
    if (!scriptStore.currentScript) {
      scriptStore.setCurrentScript(result.script)
    }
    
    // 使用 replace 跳转，避免回退
    console.log('准备跳转到 /image...')
    setTimeout(() => {
      console.log('执行跳转，使用 replace 模式')
      router.replace('/image')
    }, 800)
  } catch (err: any) {
    console.error('生成失败:', err)
    uiStore.showError(err.message || '生成失败')
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.script-gen {
  max-width: 900px;
  margin: 0 auto;
}

.form-card {
  margin-bottom: 20px;
}

h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.hot-keywords-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  padding: 8px 0;
}

.hot-keyword-tag {
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
  padding: 4px 12px;
}

.hot-keyword-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(245, 101, 101, 0.3);
  border-color: #f56565;
}

.hot-score {
  margin-left: 4px;
  font-size: 12px;
  color: #f56565;
  font-weight: bold;
}
</style>
