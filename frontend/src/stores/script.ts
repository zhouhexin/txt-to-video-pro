import { defineStore } from 'pinia'
import type { Script } from '@/types'
import { getScript, searchScripts, generateScript } from '@/api/scripts'

export const useScriptStore = defineStore('script', {
  state: () => ({
    currentScript: null as Script | null,
    scriptList: [] as Script[],
    isLoading: false,
    error: null as string | null
  }),
  
  getters: {
    hasCurrentScript: (state) => !!state.currentScript,
    scriptCount: (state) => state.scriptList.length
  },
  
  actions: {
    async fetchScript(id: number) {
      this.isLoading = true
      this.error = null
      try {
        this.currentScript = await getScript(id)
      } catch (err: any) {
        this.error = err.message
        throw err
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchList(params?: any) {
      this.isLoading = true
      this.error = null
      try {
        const result = await searchScripts(params)
        this.scriptList = result.scripts
      } catch (err: any) {
        this.error = err.message
        throw err
      } finally {
        this.isLoading = false
      }
    },
    
    async createScript(scriptParams: any) {
      this.isLoading = true
      this.error = null
      try {
        const result = await generateScript(scriptParams)
        this.currentScript = result.script
        return result
      } catch (err: any) {
        this.error = err.message
        throw err
      } finally {
        this.isLoading = false
      }
    },
    
    setCurrentScript(script: Script | null) {
      this.currentScript = script
    },
    
    clearError() {
      this.error = null
    }
  }
})
