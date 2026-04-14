import { defineStore } from 'pinia'

export const useTaskStore = defineStore('task', {
  state: () => ({
    taskId: null as string | null,
    currentStep: 1,
    genMode: 'single' as 'single' | 'chain'
  }),
  
  getters: {
    isChainMode: (state) => state.genMode === 'chain',
    hasTask: (state) => !!state.taskId
  },
  
  actions: {
    setTaskId(id: string) {
      this.taskId = id
    },
    
    setStep(step: number) {
      this.currentStep = step
    },
    
    setGenMode(mode: 'single' | 'chain') {
      this.genMode = mode
    },
    
    nextStep() {
      if (this.currentStep < 4) {
        this.currentStep++
      }
    },
    
    prevStep() {
      if (this.currentStep > 1) {
        this.currentStep--
      }
    },
    
    reset() {
      this.taskId = null
      this.currentStep = 1
      this.genMode = 'single'
    }
  }
})
