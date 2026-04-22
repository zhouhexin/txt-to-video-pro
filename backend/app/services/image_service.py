import os
import logging
import requests
from datetime import datetime
from app import db
from app.models import Task, TaskImage
from .token_service import TokenService

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
                       size: str = "1024*1024",
                       theme: str = None,
                       video_type: str = None,
                       style: str = None) -> TaskImage:
        """
        生成单个分镜图
        
        Args:
            task_id: 任务 ID
            shot_index: 分镜索引
            prompt: 绘图提示词
            model: AI 模型
            size: 图片尺寸
            theme: 主题（用于增强prompt）
            video_type: 视频类型（用于增强prompt）
            style: 风格（用于增强prompt）
            
        Returns:
            TaskImage 对象
        """
        # 增强prompt（添加主题、视频类型、风格信息）
        enhanced_prompt = self._enhance_prompt(prompt, theme, video_type, style)
        logger.info(f"原始prompt: {prompt[:100]}...")
        logger.info(f"增强后prompt: {enhanced_prompt[:100]}...")
        
        # 查找或创建任务记录（避免重复记录）
        task_image = TaskImage.query.filter_by(
            task_id=task_id,
            shot_index=shot_index
        ).first()
        
        if task_image:
            # 更新现有记录
            task_image.prompt = enhanced_prompt  # 保存增强后的prompt
            task_image.status = 'running'
            task_image.file_path = None
        else:
            # 创建新记录
            task_image = TaskImage(
                task_id=task_id,
                shot_index=shot_index,
                prompt=enhanced_prompt,  # 保存增强后的prompt
                status='running'
            )
            db.session.add(task_image)
        
        db.session.commit()
        
        try:
            # 调用阿里云万相 API（使用增强后的prompt）
            image_result = self._call_image_api(enhanced_prompt, model, size, task_id)
            
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
                        size: str = "1024*1024", task_id: str = None) -> dict:
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
            
            # 记录 token 使用情况
            try:
                usage = result.get("usage", {})
                # 判断API是否返回了精确的token信息
                has_exact_usage = usage.get("input_tokens") is not None and usage.get("output_tokens") is not None
                
                if has_exact_usage:
                    input_tokens = usage.get("input_tokens", 0)
                    output_tokens = usage.get("output_tokens", 0)
                    is_estimated = False
                    logger.info(f"API返回精确token: input={input_tokens}, output={output_tokens}")
                else:
                    # API未返回精确token信息，使用估算值
                    input_tokens = len(prompt) // 4  # 按字符数估算
                    output_tokens = 100  # 图片生成输出token估算
                    is_estimated = True
                    logger.info(f"API未返回token信息，使用估算值: input={input_tokens}, output={output_tokens}")
                
                TokenService.record_usage(
                    model_type='image_generate',
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    model_name=model,
                    task_id=task_id,
                    prompt_text=prompt,
                    response_text=f"Generated image: {image_urls[0]}",
                    scene='image_prompt',
                    is_estimated=is_estimated
                )
            except Exception as token_error:
                logger.warning(f"Token 记录失败：{token_error}")
            
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
    
    def _enhance_prompt(self, prompt: str, theme: str = None, video_type: str = None, style: str = None) -> str:
        """
        增强绘图prompt，添加主题、视频类型、风格信息
        
        Args:
            prompt: 原始prompt
            theme: 主题
            video_type: 视频类型
            style: 风格
            
        Returns:
            增强后的prompt
        """
        enhancements = []
        
        # 主题增强
        if theme:
            # 将中文主题转换为英文描述
            theme_en_map = {
                '西湖': 'West Lake scenery',
                '黄山': 'Yellow Mountain landscape',
                '故宫': 'Forbidden City architecture',
                '长城': 'Great Wall of China',
                '桂林': 'Guilin landscape and karst mountains',
                '九寨沟': 'Jiuzhaigou valley colorful waters',
                '张家界': 'Zhangjiajie towering peaks',
                '丽江': 'Lijiang ancient town',
                '苏州': 'Suzhou classical gardens',
                '北京': 'Beijing cityscape',
                '上海': 'Shanghai modern city',
                '成都': 'Chengdu city life',
                '杭州': 'Hangzhou scenery',
                '西安': 'Xi\'an historical city',
                '南京': 'Nanjing cultural heritage',
            }
            # 尝试匹配已知主题，否则使用原主题
            theme_en = theme_en_map.get(theme, f'{theme} themed')
            enhancements.append(f'{theme_en}, consistent with main theme')
        
        # 视频类型增强
        if video_type:
            video_type_en_map = {
                '文旅宣传': 'tourism promotional style, cinematic travel video aesthetic',
                '产品展示': 'product showcase style, commercial photography quality',
                '教程': 'educational video style, clear and informative visuals',
                '企业宣传': 'corporate promotional style, professional business aesthetic',
                '短视频': 'short video style, engaging social media content',
                '纪录片': 'documentary style, authentic and realistic visuals',
                '广告': 'commercial advertising style, high-end production quality',
                '微电影': 'short film style, narrative cinematic quality',
            }
            video_type_en = video_type_en_map.get(video_type, f'{video_type} style')
            enhancements.append(video_type_en)
        
        # 风格增强
        if style:
            style_en_map = {
                '唯美风光': 'beautiful scenic style, soft lighting, elegant composition',
                '动感活力': 'dynamic and energetic style, vibrant colors, motion blur',
                '温馨治愈': 'warm and healing style, soft pastel colors, cozy atmosphere',
                '科技未来': 'futuristic tech style, neon lights, cyber aesthetic',
                '复古怀旧': 'retro vintage style, film grain, nostalgic colors',
                '简约现代': 'minimalist modern style, clean lines, contemporary design',
                '大气磅礴': 'grand and majestic style, epic scale, dramatic lighting',
                '清新自然': 'fresh natural style, bright colors, organic elements',
            }
            style_en = style_en_map.get(style, f'{style} aesthetic')
            enhancements.append(style_en)
        
        # 组合增强内容
        if enhancements:
            enhanced_prompt = f"{prompt}, {', '.join(enhancements)}, consistent visual style throughout the series"
        else:
            enhanced_prompt = prompt
        
        return enhanced_prompt
