import os
import logging
import subprocess
import requests
import time
from datetime import datetime
from app import db
from app.models import Task, TaskVideo
from .token_service import TokenService
import mimetypes
import base64


logger = logging.getLogger(__name__)


class VideoService:
    """视频生成服务 - 基于阿里云百炼 wan2.2-kf2v-flash"""
    
    def __init__(self, api_key: str, output_dir: str):
        self.api_key = api_key
        self.output_dir = output_dir
        
        # API 端点
        self.video_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis"
        self.task_url = "https://dashscope.aliyuncs.com/api/v1/tasks"

    # --- 辅助函数：用于 Base64 编码 ---
    # 格式为 data:{MIME_type};base64,{base64_data}
    def encode_file(self,file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type or not mime_type.startswith("image/"):
            raise ValueError("不支持或无法识别的图像格式")
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:{mime_type};base64,{encoded_string}"

    def generate_video(self, task_id: str, shot_index: int, image_path: str, 
                       duration: int = 5, mode: str = 'single',
                       last_frame_path: str = None,
                       resolution: str = '480P',
                       camera_motion: str = 'push',
                       visual_desc: str = None) -> TaskVideo:
        """
        生成单个视频片段
        
        Args:
            task_id: 任务 ID
            shot_index: 分镜索引
            image_path: 输入图片路径
            duration: 视频时长（秒）
            mode: 模式（single/chain）
            last_frame_path: 尾帧图片路径（可选）
            resolution: 分辨率（480P/720P/1080P）
            camera_motion: 镜头运动方式（push/pull/pan/tilt/zoom/orbit）
            visual_desc: 分镜的视觉描述（用于增强prompt）
            
        Returns:
            TaskVideo 对象
        """
        # 查找或创建任务记录（避免重复记录）
        task_video = TaskVideo.query.filter_by(
            task_id=task_id,
            shot_index=shot_index
        ).first()
        
        if task_video:
            # 更新现有记录
            task_video.duration = duration
            task_video.status = 'running'
            task_video.file_path = None
            task_video.error_message = None
        else:
            # 创建新记录
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
            
            video_result = self._call_video_api(image_url, shot_index, last_frame_url, 
                                                 resolution=resolution, 
                                                 camera_motion=camera_motion,
                                                 task_id=task_id,
                                                 visual_desc=visual_desc)
            
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
        return self.encode_file(image_path)
        # return "file://" + f"{image_path}"
    
    def _call_video_api(self, first_frame_url: str, shot_index: int, 
                        last_frame_url: str = None,
                        model: str = "wan2.2-kf2v-flash",
                        resolution: str = "480P",
                        camera_motion: str = "push",
                        task_id: str = None,
                        visual_desc: str = None) -> dict:
        """调用阿里云万相视频生成 API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
            "Referer": "https://dashscope.aliyuncs.com"
        }
        
        # 构建增强的视频prompt
        prompt = self._build_video_prompt(camera_motion, last_frame_url is not None, visual_desc)
        
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
            api_task_id = task_result.get("output", {}).get("task_id")
            
            if not api_task_id:
                return {"success": False, "error": "未获取到任务 ID"}
            
            logger.info(f"API 任务 ID: {api_task_id}")
            
            # 轮询任务状态
            status_url = f"{self.task_url}/{api_task_id}"
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
                            
                            # 记录 token 使用情况
                            try:
                                usage = status_result.get("usage", {})
                                # 判断API是否返回了精确的token信息
                                has_exact_usage = usage.get("input_tokens") is not None and usage.get("output_tokens") is not None
                                
                                if has_exact_usage:
                                    input_tokens = usage.get("input_tokens", 0)
                                    output_tokens = usage.get("output_tokens", 0)
                                    is_estimated = False
                                    logger.info(f"API返回精确token: input={input_tokens}, output={output_tokens}")
                                else:
                                    # API未返回精确token信息，使用估算值
                                    input_tokens = 200  # 视频生成输入token估算
                                    output_tokens = 100  # 视频生成输出token估算
                                    is_estimated = True
                                    logger.info(f"API未返回token信息，使用估算值: input={input_tokens}, output={output_tokens}")
                                
                                TokenService.record_usage(
                                    model_type='video_generate',
                                    input_tokens=input_tokens,
                                    output_tokens=output_tokens,
                                    model_name=model,
                                    task_id=task_id,
                                    prompt_text=prompt,
                                    response_text=f"Generated video: {video_url}",
                                    scene='video_generation',
                                    is_estimated=is_estimated
                                )
                            except Exception as token_error:
                                logger.warning(f"Token 记录失败：{token_error}")
                            
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
    
    def _build_video_prompt(self, camera_motion: str, has_last_frame: bool = False, 
                            visual_desc: str = None) -> str:
        """
        构建增强的视频生成prompt
        
        Args:
            camera_motion: 镜头运动方式
            has_last_frame: 是否有尾帧（首尾帧模式）
            visual_desc: 分镜的视觉描述
            
        Returns:
            增强后的视频prompt
        """
        # 增强的镜头运动描述（更详细、更自然）
        motion_desc = {
            "push": "slow and smooth camera push-in, gradually approaching the subject from wide shot to close-up, revealing fine details and textures, cinematic depth change, gentle dolly forward movement",
            "pull": "smooth camera pull-back, slowly revealing the broader scene from close-up to wide shot, showing the relationship between subject and environment, expanding spatial perspective, gentle dolly backward movement",
            "pan": "horizontal pan shot, smooth left-to-right camera movement, revealing the lateral extension of the scene, maintaining stable and fluid motion, tracking the landscape horizontally",
            "tilt": "vertical tilt shot, smooth top-to-bottom camera movement, revealing the vertical layers of the scene, natural and fluid descent, showcasing height and depth",
            "zoom": "smooth zoom effect, gradual transition from wide angle to close-up, focusing on key details, natural depth of field change, cinematic focus shift",
            "orbit": "orbit shot, 360-degree circular camera movement around the subject, keeping subject centered while background flows naturally, dynamic perspective change",
            "static": "static shot with subtle natural motion, gentle wind effects, flowing water, or ambient movement, peaceful and stable composition"
        }
        
        # 获取镜头运动描述
        motion_text = motion_desc.get(camera_motion, motion_desc["push"])
        
        # 构建基础prompt
        base_prompt = "High quality video, cinematic lighting and color grading, professional cinematography, 4K resolution, smooth motion"
        
        # 添加镜头运动
        prompt_parts = [base_prompt, motion_text]
        
        # 首尾帧模式：添加过渡描述
        if has_last_frame:
            transition_desc = "seamless transition between first and last frame, natural motion flow, smooth ease-in ease-out movement, coherent action continuity, perfect frame blending"
            prompt_parts.append(transition_desc)
        else:
            # 单帧模式：添加自然运动描述
            natural_motion = "natural ambient motion, subtle environmental dynamics, lifelike movement, organic scene evolution"
            prompt_parts.append(natural_motion)
        
        # 添加视觉描述（如果有）
        if visual_desc:
            # 将中文视觉描述转换为英文风格
            visual_en = self._translate_visual_desc(visual_desc)
            prompt_parts.append(visual_en)
        
        # 添加电影感增强
        cinematic_enhance = "film-like quality, professional color grading, subtle motion blur for cinematic feel, natural lighting transition"
        prompt_parts.append(cinematic_enhance)
        
        # 组合最终prompt
        final_prompt = ", ".join(prompt_parts)
        
        logger.info(f"构建视频prompt: {final_prompt[:100]}...")
        
        return final_prompt
    
    def _translate_visual_desc(self, visual_desc: str) -> str:
        """
        将中文视觉描述转换为英文风格描述
        
        Args:
            visual_desc: 中文视觉描述
            
        Returns:
            英文风格描述
        """
        # 常见场景关键词映射
        scene_keywords = {
            '湖': 'lake scenery with calm water reflection',
            '山': 'mountain landscape with majestic peaks',
            '河': 'river flowing gently through the landscape',
            '桥': 'bridge architecture spanning across',
            '塔': 'tower architecture standing tall',
            '亭': 'traditional pavilion with elegant design',
            '楼': 'building architecture with detailed structure',
            '树': 'trees with natural foliage and branches',
            '花': 'flowers blooming with vibrant colors',
            '草': 'grass field with natural green texture',
            '水': 'water surface with gentle ripples',
            '天': 'sky with natural cloud formations',
            '云': 'clouds drifting slowly across the sky',
            '日': 'sunlight casting warm golden rays',
            '月': 'moonlight creating soft ambient glow',
            '人': 'people with natural posture and movement',
            '船': 'boat floating gently on water',
            '鸟': 'birds flying naturally in the sky',
            '风': 'wind creating gentle motion effects',
            '雨': 'rain falling with natural droplets',
            '雪': 'snow falling gently with winter atmosphere',
            '雾': 'fog creating mysterious atmospheric depth',
            '晨': 'morning light with soft dawn colors',
            '暮': 'twilight with warm sunset tones',
            '夜': 'night scene with ambient lighting',
            '古': 'ancient historical atmosphere with traditional elements',
            '现': 'modern contemporary style with clean aesthetics',
            '城': 'cityscape with urban architecture',
            '村': 'village scenery with rural charm',
            '园': 'garden landscape with manicured beauty',
            '林': 'forest with dense natural vegetation',
            '石': 'stone elements with natural texture',
            '路': 'path or road leading through the scene',
            '街': 'street scene with urban atmosphere',
            '窗': 'window view with perspective depth',
            '门': 'doorway with architectural detail',
            '墙': 'wall with texture and depth',
            '屋': 'house or building structure',
            '寺': 'temple architecture with spiritual atmosphere',
            '庙': 'traditional shrine with cultural elements',
            '宫': 'palace architecture with grandeur',
            '殿': 'hall architecture with majestic interior',
        }
        
        # 尝试匹配关键词
        matched_desc = []
        for keyword, en_desc in scene_keywords.items():
            if keyword in visual_desc:
                matched_desc.append(en_desc)
        
        # 如果有匹配的关键词，使用匹配的描述
        if matched_desc:
            return f"scene featuring {', '.join(matched_desc[:3])}"
        
        # 如果没有匹配，使用通用描述
        return f"scene with {visual_desc} atmosphere and natural elements"
