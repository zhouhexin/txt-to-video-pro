<template>
  <div class="video-player">
    <video 
      :src="src" 
      :poster="poster" 
      controls 
      class="video-element"
      preload="metadata"
    />
    <div v-if="title || description" class="video-info">
      <h4 v-if="title">{{ title }}</h4>
      <p v-if="description">{{ description }}</p>
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
.video-player {
  width: 100%;
}

.video-element {
  width: 100%;
  max-height: 500px;
  border-radius: 8px;
  background: #000;
}

.video-info {
  margin-top: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
}

.video-info h4 {
  margin: 0 0 5px;
  color: #333;
}

.video-info p {
  margin: 0;
  font-size: 13px;
  color: #666;
}
</style>
