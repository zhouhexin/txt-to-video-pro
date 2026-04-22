import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ScriptGen from '../views/ScriptGen.vue'
import ImageGen from '../views/ImageGen.vue'
import VideoGen from '../views/VideoGen.vue'
import Showcase from '../views/Showcase.vue'
import History from '../views/History.vue'
import TaskHistory from '../views/TaskHistory.vue'
import Statistics from '../views/Statistics.vue'
import TokenStatistics from '../views/TokenStatistics.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/script',
    name: 'ScriptGen',
    component: ScriptGen
  },
  {
    path: '/image',
    name: 'ImageGen',
    component: ImageGen
  },
  {
    path: '/video',
    name: 'VideoGen',
    component: VideoGen
  },
  {
    path: '/showcase',
    name: 'Showcase',
    component: Showcase
  },
  {
    path: '/history',
    name: 'History',
    component: History
  },
  {
    path: '/task-history',
    name: 'TaskHistory',
    component: TaskHistory
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: Statistics
  },
  {
    path: '/token-statistics',
    name: 'TokenStatistics',
    component: TokenStatistics
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
