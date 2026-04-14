<template>
  <el-steps :active="currentStep" finish-status="success" align-center>
    <el-step title="📝 智能剧本" description="AI 生成视频剧本" />
    <el-step title="🎨 分镜生成" description="文生图创建分镜" />
    <el-step title="🎬 视频生成" description="图生视频动画" />
    <el-step title="📊 成果展示" description="查看完整视频" />
  </el-steps>
</template>

<script setup lang="ts">
defineProps<{
  currentStep: number
}>()
</script>

<style scoped>
.el-steps {
  margin: 20px 0;
}
</style>
