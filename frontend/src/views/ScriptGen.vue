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
        
        <!-- 场景选择器 -->
        <SceneSelector v-model="form.scene_type" @change="handleSceneChange" />
        
        <el-form-item label="主题" required>
          <el-input 
            v-model="form.theme" 
            placeholder="例如：西安大唐芙蓉园、新款智能手机发布"
            :disabled="generating"
          />
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
          v-model:original-prompt="form.theme"
          v-model:optimized-prompt="form.optimized_theme"
          :scene-type="form.scene_type"
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
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useScriptStore } from '@/stores/script'
import { useTaskStore } from '@/stores/task'
import { useUIStore } from '@/stores/ui'
import ScriptPreview from '@/components/ScriptPreview.vue'
import SceneSelector from '@/components/SceneSelector.vue'
import PromptOptimizer from '@/components/PromptOptimizer.vue'

const router = useRouter()
const scriptStore = useScriptStore()
const taskStore = useTaskStore()
const uiStore = useUIStore()

const generating = ref(false)

const form = reactive({
  video_type: '文旅宣传',
  theme: '',
  optimized_theme: '',
  scene_type: '',
  keywords: '',
  num_shots: 5
})

// 监听场景变化，自动更新推荐参数
const handleSceneChange = (sceneType: string | null) => {
  if (sceneType) {
    // 场景选择后，可以自动设置推荐的分镜数量等
    uiStore.showSuccess(`已选择场景：${sceneType}`)
  }
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
      theme: themeToUse,
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
</style>
