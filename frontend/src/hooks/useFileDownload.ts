/**
 * 文件下载 Hook
 */

export function useFileDownload() {
  /**
   * 下载文件
   */
  function download(url: string, filename: string = 'download') {
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }
  
  /**
   * 下载图片
   */
  function downloadImage(url: string, filename: string = 'image.png') {
    download(url, filename)
  }
  
  /**
   * 下载视频
   */
  function downloadVideo(url: string, filename: string = 'video.mp4') {
    download(url, filename)
  }
  
  return { download, downloadImage, downloadVideo }
}
