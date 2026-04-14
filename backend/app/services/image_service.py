import os
import logging
import requests
from datetime import datetime
from app import db
from app.models import Task, TaskImage

logger = logging.getLogger(__name__)


class ImageService:
    """分镜图生成服务 - 基于阿里云百炼 qwen-image-2.0-pro"""
    
    def __init__(self, api_key: str, output_dir: str):
        self.api_key = api_key
        self.output_dir = output_dir
        
        # API 端点
        self.image_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    
    def generate_image(self, task_id: str, shot_index: int, prompt: str,
                       model: str = "qwen-image-2.0-pro",
                       size: str = "1024*1024") -> TaskImage:
        """
        生成单个分镜图
        
        Args:
            task_id: 任务 ID
            shot_index: 分镜索引
            prompt: 绘图提示词
            model: AI 模型
            size: 图片尺寸
            
        Returns:
            TaskImage 对象
        """
        # 创建任务记录
        task_image = TaskImage(
            task_id=task_id,
            shot_index=shot_index,
            prompt=prompt,
            status='running'
        )
        db.session.add(task_image)
        db.session.commit()
        
        try:
            # 调用阿里云万相 API
            image_result = self._call_image_api(prompt, model, size)
            
            if image_result.get('success'):
                # 下载图片
                image_url = image_result['image_urls'][0]
                image_data = self._download_image(image_url)
                
                # 保存图片到本地
                task_dir = os.path.join(self.output_dir, task_id, 'frames')
                os.makedirs(task_dir, exist_ok=True)
                
                filename = f'shot_{shot_index}.png'
                file_path = os.path.join(task_dir, filename)
                
                with open(file_path, 'wb') as f:
                    f.write(image_data)
                
                # 更新记录
                task_image.file_path = file_path
                task_image.status = 'completed'
                db.session.commit()
                
                logger.info(f"分镜图生成成功：{file_path}")
                return task_image
            else:
                logger.error(f"AI 绘图 API 调用失败：{image_result.get('error')}")
                task_image.status = 'failed'
                task_image.error_message = image_result.get('error')
                db.session.commit()
                raise Exception(f"AI 绘图服务调用失败：{image_result.get('error')}")
                
        except Exception as e:
            logger.error(f"分镜图生成异常：{str(e)}")
            task_image.status = 'failed'
            db.session.commit()
            raise
    
    def _call_image_api(self, prompt: str, model: str = "qwen-image-2.0-pro",
                        size: str = "1024*1024") -> dict:
        """调用阿里云万相图片生成 API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        data = {
            "model": model,
            "input": {
                "messages": [{"role": "user", "content": [{"text": prompt}]}]
            },
            "parameters": {
                "size": size,
                "negative_prompt": "低分辨率，低画质，肢体畸形，模糊",
                "prompt_extend": True,
                "watermark": False
            }
        }
        
        try:
            logger.info(f"生成图片：{prompt[:50]}...")
            response = requests.post(self.image_url, headers=headers, json=data, timeout=120)
            
            if response.status_code != 200:
                return {"success": False, "error": f"API 请求失败：{response.status_code}"}
            
            result = response.json()
            choices = result.get("output", {}).get("choices", [])
            
            if not choices:
                return {"success": False, "error": "未获取到图片结果"}
            
            content = choices[0].get("message", {}).get("content", [])
            image_urls = [item.get("image") for item in content if item.get("image")]
            
            if not image_urls:
                return {"success": False, "error": "未获取到图片 URL"}
            
            logger.info(f"图片生成成功！")
            
            return {
                "success": True,
                "image_urls": image_urls,
                "prompt": prompt
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _download_image(self, url: str) -> bytes:
        """下载图片"""
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        return response.content
    
    def get_task_images(self, task_id: str) -> list:
        """获取任务的所有分镜图"""
        images = TaskImage.query.filter_by(task_id=task_id).order_by(TaskImage.shot_index).all()
        return [img.to_dict() for img in images]
    
    def complete_image_generation(self, task_id: str, wait_confirm: bool = False):
        """
        完成分镜图生成，更新任务状态
        
        Args:
            task_id: 任务 ID
            wait_confirm: 是否等待确认
        """
        task = Task.query.get(task_id)
        if task:
            if wait_confirm:
                task.status = 'waiting_confirm'
            else:
                task.status = 'completed'
            task.progress = 100
            db.session.commit()
    
    def regenerate_images(self, script_id: int, shots: list) -> str:
        """
        重新生成分镜图（创建新 task）
        
        Args:
            script_id: 剧本 ID
            shots: 分镜列表
            
        Returns:
            新 task_id
        """
        new_task_id = f"task_{int(datetime.now().timestamp())}_{script_id:08d}"
        
        # 创建新任务
        task = Task(
            id=new_task_id,
            script_id=script_id,
            status='pending',
            step='image',
            progress=0
        )
        db.session.add(task)
        db.session.commit()
        
        return new_task_id
    
    def generate_first_frame(self, task_id: str, prompt: str, shot_index: int = 0) -> TaskImage:
        """
        生成首帧图片
        
        Args:
            task_id: 任务 ID
            prompt: 提示词
            shot_index: 分镜索引
            
        Returns:
            TaskImage 对象
        """
        return self.generate_image(task_id, shot_index, prompt)
    
    def generate_last_frame(self, task_id: str, first_prompt: str, shot_index: int = 0) -> TaskImage:
        """
        生成尾帧图片（基于首帧提示词的延续）
        
        Args:
            task_id: 任务 ID
            first_prompt: 首帧提示词
            shot_index: 分镜索引
            
        Returns:
            TaskImage 对象
        """
        # 生成尾帧提示词（场景的延续和过渡）
        last_prompt = f"{first_prompt}, continuation and transition of the scene, smooth visual flow, consistent style and lighting"
        
        return self.generate_image(task_id, shot_index, last_prompt)
