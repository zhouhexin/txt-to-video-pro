/**
 * 轮询 Hook - 用于任务状态轮询
 */

export function usePolling() {
  const intervals = new Map<string, number>()
  
  function startPolling(
    key: string,
    url: string,
    callback: (data: any) => void,
    intervalMs: number = 2000
  ): () => void {
    const poll = async () => {
      try {
        const res = await fetch(url)
        const data = await res.json()
        callback(data)
        
        // 如果任务完成或失败，停止轮询
        if (data.status === 'completed' || data.status === 'failed') {
          stopPolling(key)
        }
      } catch (error) {
        console.error('Polling error:', error)
      }
    }
    
    // 立即执行一次
    poll()
    
    // 设置定时轮询
    const intervalId = window.setInterval(poll, intervalMs)
    intervals.set(key, intervalId)
    
    // 返回停止函数
    return () => stopPolling(key)
  }
  
  function stopPolling(key: string) {
    const intervalId = intervals.get(key)
    if (intervalId) {
      window.clearInterval(intervalId)
      intervals.delete(key)
    }
  }
  
  function stopAll() {
    intervals.forEach((id) => window.clearInterval(id))
    intervals.clear()
  }
  
  return { startPolling, stopPolling, stopAll }
}
