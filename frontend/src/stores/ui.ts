import { defineStore } from 'pinia'

export const useUIStore = defineStore('ui', {
  state: () => ({
    loading: false,
    loadingText: '',
    message: null as { type: 'success' | 'warning' | 'info' | 'error'; content: string } | null
  }),
  
  actions: {
    showLoading(text: string = '加载中...') {
      this.loading = true
      this.loadingText = text
    },
    
    hideLoading() {
      this.loading = false
      this.loadingText = ''
    },
    
    showMessage(type: 'success' | 'warning' | 'info' | 'error', content: string) {
      this.message = { type, content }
      setTimeout(() => {
        this.message = null
      }, 3000)
    },
    
    showSuccess(content: string) {
      this.showMessage('success', content)
    },
    
    showError(content: string) {
      this.showMessage('error', content)
    },
    
    showInfo(content: string) {
      this.showMessage('info', content)
    },
    
    showWarning(content: string) {
      this.showMessage('warning', content)
    },
    
    clearMessage() {
      this.message = null
    }
  }
})
