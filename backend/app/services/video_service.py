import os
import logging
import subprocess
import requests
import time
from datetime import datetime
from app import db
from app.models import Task, TaskVideo

logger = logging.getLogger(__name__)


class VideoService:
    """视频生成服务 - 基于阿里云百炼 wan2.2-kf2v-flash"""
    
    def __init__(self, api_key: str, output_dir: str):
        self.api_key = api_key
        self.output_dir = output_dir
        
        # API 端点
        self.video_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis"
        self.task_url = "https://dashscope.aliyuncs.com/api/v1/tasks"
    
    def generate_video(self, task_id: str, shot_index: int, image_path: str, 
                       duration: int = 5, mode: str = 'single',
                       last_frame_path: str = None) -> TaskVideo:
        """
        生成单个视频片段
        
        Args:
            task_id: 任务 ID
            shot_index: 分镜索引
            image_path: 输入图片路径
            duration: 视频时长（秒）
            mode: 模式（single/chain）
            
        Returns:
            TaskVideo 对象
        """
        # 创建任务记录
        task_video = TaskVideo(
            task_id=task_id,
            shot_index=shot_index,
            duration=duration,
            status='running'
        )
        db.session.add(task_video)
        db.session.commit()
        
        try:
            # 上传图片获取 URL（这里假设图片已有 URL，实际需要从本地路径上传）
            # 简化实现：使用本地文件路径转换为 URL
            image_url = self._get_image_url(image_path)
            
            # 调用阿里云万相视频生成 API（支持首尾帧）
            last_frame_url = None
            if last_frame_path:
                last_frame_url = self._get_image_url(last_frame_path)
            
            video_result = self._call_video_api(image_url, shot_index, last_frame_url)
            
            if video_result.get('success'):
                # 下载视频
                video_url = video_result['video_url']
                video_data = self._download_video(video_url)
                
                # 保存视频到本地
                task_dir = os.path.join(self.output_dir, task_id, 'videos')
                os.makedirs(task_dir, exist_ok=True)
                
                filename = f'shot_{shot_index}.mp4'
                file_path = os.path.join(task_dir, filename)
                
                with open(file_path, 'wb') as f:
                    f.write(video_data)
                
                # 更新记录
                task_video.file_path = file_path
                task_video.status = 'completed'
                db.session.commit()
                
                logger.info(f"视频生成成功：{file_path}")
                return task_video
            else:
                logger.error(f"视频 API 调用失败：{video_result.get('error')}")
                task_video.status = 'failed'
                task_video.error_message = video_result.get('error')
                db.session.commit()
                raise Exception(f"视频服务调用失败：{video_result.get('error')}")
                
        except Exception as e:
            logger.error(f"视频生成异常：{str(e)}")
            task_video.status = 'failed'
            db.session.commit()
            raise
    
    def _get_image_url(self, image_path: str) -> str:
        """获取图片 URL（简化实现，实际需要上传到 OSS 或返回 file:// URL）"""
        # 这里简化处理，实际应该上传图片到云存储
        # 对于本地开发，可以使用 file:// 协议或本地 HTTP 服务器
        return f"file://{image_path}"
    
    def _call_video_api(self, first_frame_url: str, shot_index: int, 
                        last_frame_url: str = None,
                        model: str = "wan2.2-kf2v-flash",
                        resolution: str = "480P",
                        camera_motion: str = "push") -> dict:
        """调用阿里云万相视频生成 API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
            "Referer": "https://dashscope.aliyuncs.com"
        }
        
        # 镜头运动描述
        motion_desc = {
            "push": "缓慢的镜头推进，靠近主体，展示细节",
            "pull": "镜头缓缓拉远，展现更广阔的场景",
            "pan": "水平摇摄镜头，从左到右平滑移动",
            "tilt": "垂直倾斜镜头，从上到下缓慢移动",
            "zoom": "变焦效果，聚焦关键细节",
            "orbit": "环绕拍摄，360 度展示主体"
        }
        
        prompt = f"高质量视频，电影感光影，{motion_desc.get(camera_motion, '平滑的镜头运动')}，4K 画质"
        
        # 构建输入参数（支持首尾帧模式）
        input_data = {
            "first_frame_url": first_frame_url,
            "prompt": prompt
        }
        
        if last_frame_url:
            input_data["last_frame_url"] = last_frame_url
            logger.info(f"使用首尾帧模式生成视频")
        
        data = {
            "model": model,
            "input": input_data,
            "parameters": {
                "resolution": resolution,
                "prompt_extend": True
            }
        }
        
        try:
            logger.info("提交视频生成任务...")
            response = requests.post(self.video_url, headers=headers, json=data, timeout=60)
            
            if response.status_code != 200:
                return {"success": False, "error": f"API 请求失败：{response.status_code}"}
            
            task_result = response.json()
            task_id = task_result.get("output", {}).get("task_id")
            
            if not task_id:
                return {"success": False, "error": "未获取到任务 ID"}
            
            logger.info(f"任务 ID: {task_id}")
            
            # 轮询任务状态
            status_url = f"{self.task_url}/{task_id}"
            timeout = 900  # 15 分钟
            poll_interval = 15
            waited = 0
            
            while waited < timeout:
                time.sleep(poll_interval)
                waited += poll_interval
                
                if waited % 60 == 0:
                    logger.info(f"等待生成中... ({waited//60}分钟)")
                
                status_response = requests.get(status_url, headers=headers, timeout=60)
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    task_status = status_result.get("output", {}).get("task_status", "")
                    
                    if task_status == "SUCCEEDED":
                        video_url = status_result.get("output", {}).get("video_url")
                        if video_url:
                            logger.info(f"视频生成成功！")
                            return {"success": True, "video_url": video_url}
                        else:
                            return {"success": False, "error": "未获取到视频 URL"}
                    
                    elif task_status == "FAILED":
                        error_msg = status_result.get("output", {}).get("error", {}).get("message", "未知错误")
                        return {"success": False, "error": f"任务失败：{error_msg}"}
            
            return {"success": False, "error": "任务超时"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _download_video(self, url: str) -> bytes:
        """下载视频"""
        response = requests.get(url, timeout=300)
        response.raise_for_status()
        return response.content
    
    def merge_videos(self, task_id: str, output_filename: str = 'merged_full_video.mp4') -> str:
        """
        合并所有视频片段为完整视频
        
        Args:
            task_id: 任务 ID
            output_filename: 输出文件名
            
        Returns:
            合并后的视频路径
        """
        # 获取所有视频
        videos = TaskVideo.query.filter_by(
            task_id=task_id, 
            status='completed'
        ).order_by(TaskVideo.shot_index).all()
        
        if not videos:
            raise Exception("没有找到已完成的视频片段")
        
        task_dir = os.path.join(self.output_dir, task_id, 'videos')
        output_path = os.path.join(task_dir, output_filename)
        
        # 创建视频列表文件
        list_file = os.path.join(task_dir, 'video_list.txt')
        with open(list_file, 'w') as f:
            for video in videos:
                # ffmpeg 需要相对路径或绝对路径
                f.write(f"file '{os.path.abspath(video.file_path)}'\n")
        
        # 使用 ffmpeg 合并视频
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file,
            '-c', 'copy',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                logger.error(f"ffmpeg 合并失败：{result.stderr}")
                raise Exception(f"视频合并失败：{result.stderr}")
            
            logger.info(f"视频合并成功：{output_path}")
            return output_path
            
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg 合并超时")
            raise Exception("视频合并超时")
        except FileNotFoundError:
            logger.error("ffmpeg 未安装")
            raise Exception("ffmpeg 未安装，请安装后重试")
    
    def get_task_videos(self, task_id: str) -> list:
        """获取任务的所有视频"""
        videos = TaskVideo.query.filter_by(task_id=task_id).order_by(TaskVideo.shot_index).all()
        return [vid.to_dict() for vid in videos]
    
    def check_merged_video(self, task_id: str) -> dict:
        """检查合并视频是否存在"""
        task_dir = os.path.join(self.output_dir, task_id, 'videos')
        merged_path = os.path.join(task_dir, 'merged_full_video.mp4')
        
        if os.path.exists(merged_path):
            return {
                'url': f'/api/v1/files/video/{task_id}/merged_full_video.mp4',
                'status': 'completed'
            }
        return None
