import logging
import requests
from typing import Dict, Optional
import os
logger = logging.getLogger(__name__)
from openai import OpenAI, APIError
from .token_service import TokenService
from .conversation_manager import conversation_manager


class PromptOptimizer:
    """提示词优化服务 - 基于阿里云百炼千问"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        # self.chat_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        
        # 场景风格配置（6 个陕文投景点）
        self.scene_styles = {
            "大唐芙蓉园": {
                "style": "唐代宫殿建筑，红色灯笼，湖面倒影，飞檐斗拱",
                "camera_motion": "push",
                "duration": 6,
                "atmosphere": "神秘、中式美学、电影感光影"
            },
            "大唐不夜城": {
                "style": "古风商业街夜景，霓虹灯光与传统建筑融合，湿润石板路",
                "camera_motion": "pan",
                "duration": 5,
                "atmosphere": "赛博悬疑、青橙色色调、繁华"
            },
            "西安城墙": {
                "style": "古代城墙遗址，灰色砖墙纹理，宏伟规模",
                "camera_motion": "pull",
                "duration": 6,
                "atmosphere": "宏伟、黄昏剪影、戏剧性光影"
            },
            "华清宫": {
                "style": "皇家温泉宫殿，晨雾缭绕，传统中式亭台楼阁",
                "camera_motion": "tilt",
                "duration": 5,
                "atmosphere": "神秘浪漫、柔焦效果、层次丰富"
            },
            "法门寺": {
                "style": "佛教寺庙建筑，佛塔庄严，香火烟雾",
                "camera_motion": "orbit",
                "duration": 8,
                "atmosphere": "spiritual 神秘、庄严肃穆"
            },
            "陕西历史博物馆": {
                "style": "博物馆展厅，文物展品，青铜器，聚光灯",
                "camera_motion": "push",
                "duration": 5,
                "atmosphere": "悬疑、浅景深、历史厚重感"
            }
        }
        
        # 镜头运动描述
        self.camera_motions = {
            "push": "缓慢的镜头推进，靠近主体，展示细节",
            "pull": "镜头缓缓拉远，展现更广阔的场景",
            "pan": "水平摇摄镜头，从左到右平滑移动",
            "tilt": "垂直倾斜镜头，从上到下缓慢移动",
            "zoom": "变焦效果，聚焦关键细节",
            "orbit": "环绕拍摄，360 度展示主体"
        }
    
    def get_scene_styles(self) -> Dict:
        """获取所有场景风格配置"""
        return self.scene_styles
    
    def get_camera_motions(self) -> Dict:
        """获取所有镜头运动描述"""
        return self.camera_motions
    
    def optimize_prompt(self, prompt: str, scene_type: Optional[str] = None, 
                       model: str = "qwen3.5-plus", task_id: str = None, keywords: str = None,
                       video_type: str = None) -> Dict:
        """
        优化提示词
        
        Args:
            prompt: 原始提示词
            scene_type: 场景类型（可选）
            model: AI 模型
            task_id: 关联的任务ID（可选）
            keywords: 关键词（可选）
            video_type: 视频类型（可选）
            
        Returns:
            优化结果字典
        """
        logger.info(f"优化提示词：{prompt[:50]}...")
        
        # 关键词和视频类型补充
        keywords_note = f"\n关键词参考：{keywords}" if keywords else ""
        video_type_note = f"\n视频类型：{video_type}" if video_type else ""
        
        # 构建系统提示词
#         if scene_type and scene_type in self.scene_styles:
#             style_info = self.scene_styles[scene_type]
#             system_prompt = f"""你是专业 AI 视频提示词优化专家，精通{scene_type}场景创作。
# 优化用户的提示词，适配视频生成模型，内容更精细生动。
# {video_type_note}
# 风格参考：{keywords_note}
# - 场景：{style_info['style']}
# - 氛围：{style_info['atmosphere']}
# - 镜头：{self.camera_motions.get(style_info['camera_motion'], '')}
# 要求：
# 1. 补充光影、色彩、构图等细节
# 2. 写明镜头运动和光影效果
# 3. 字数约 150 字，详细描述
# 4. 仅输出优化后提示词，无额外内容"""
#         else:
        if video_type=="文旅宣传":
#             system_prompt = f"""你是文旅短片提示词优化专员，专注城市、古镇、山水、乡村文旅创作。
# 请按规则将{keywords_note}优化成专业剧本提示词：
# 1. 保留原有地点、特色、氛围、季节、主题，不额外加无关景点；
# 2. 自动补齐人文特色、风景质感、光影时段、色调氛围、叙事调性、4K电影画质；
# 3. 统一慢节奏、沉浸式治愈风，主打风景+人文，无多余剧情；
# 4. 文案精炼饱满，适配生成文旅分镜剧本；
# 只输出优化后完整提示词，无多余话术与解释。"""
           system_prompt = f"""You are a prompt optimization specialist for cultural tourism short videos, focusing on urban, ancient town, landscape and rural cultural tourism creation.
Optimize {keywords_note} into a professional script prompt following the rules below:
1. Retain the original location, features, atmosphere, season and theme; do not add irrelevant scenic spots arbitrarily.
2. Automatically supplement humanistic characteristics, landscape texture, light & time period, color tone atmosphere, narrative style, and 4K cinematic image quality.
3. Adopt a unified slow-paced, immersive healing style, focusing on scenery and humanistic vibes with no redundant plots.
4. Keep the wording concise and substantial, suitable for generating cultural tourism storyboard scripts.
Only output the complete optimized prompt, without extra remarks or explanations.(output chinese)"""
        else:
            system_prompt = f"""专业的 AI 视频文案与镜头提示词精修专家。擅长适配主流视频生成模型。
{video_type_note}
基于原始文案做精细化升级：{keywords_note} 
保持原意不变、逻辑连贯；
整体精简打磨至约150字，严格只输出优化完成的提示词，不附加任何解释、多余文字 """
            # 补足场景视觉细节，仅专注画面内容、环境细节、人物动态与情绪氛围描写，

        try:
            # 使用会话管理器优化token
            # if task_id:
            #     # 首次调用：设置系统提示词
            #     # if not conversation_manager.get_system_prompt(task_id):
            #     #     conversation_manager.set_system_prompt(task_id, system_prompt)
            #
            #     # 后续调用：只传用户消息
            #     conversation_manager.add_message(task_id, "user", f"优化提示词：{prompt}")
            #     messages = conversation_manager.get_messages(task_id)
            # else:
            #     # 无task_id时使用传统方式
            #     messages = [
            #         {"role": "system", "content": system_prompt},
            #         {"role": "user", "content": f"优化提示词：{prompt}"}
            #     ]
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"优化提示词：{prompt}"}
            ]

            import time
            start_time = time.time()
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=500
            )
            duration = time.time() - start_time
            logger.info(f"API调用耗时: {duration:.2f}秒")
            
            optimized_prompt = completion.choices[0].message.content
            logger.info(f"优化成功：{optimized_prompt[:50]}...")
            
            # 记录会话
            if task_id:
                conversation_manager.add_message(task_id, "assistant", optimized_prompt)
                logger.info(f"会话 {task_id} 已保存，当前消息数: {conversation_manager.get_session_size(task_id)}")

            # 记录 token 使用情况
            try:
                usage = completion.usage
                input_tokens = usage.prompt_tokens if usage else 0
                output_tokens = usage.completion_tokens if usage else 0
                
                TokenService.record_usage(
                    model_type='prompt_optimize',
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    model_name=model,
                    task_id=task_id,
                    prompt_text=f"优化提示词：{prompt}",
                    response_text=optimized_prompt,
                    scene='optimization'
                )
            except Exception as token_error:
                logger.warning(f"Token 记录失败：{token_error}")

            return {
                "success": True,
                "original": prompt,
                "optimized": optimized_prompt,
                "scene_type": scene_type,
                "model": model
            }

        except APIError as e:
            return {
                "success": False,
                "error": str(e),
                "original": prompt,
                "optimized": prompt
            }
    
    def optimize_with_custom_prompt(self, prompt: str, system_prompt: str,
                                   model: str = "qwen3.5-plus", 
                                   user_template: str = None,
                                   task_id: str = None) -> Dict:
        """
        使用自定义提示词优化
        
        Args:
            prompt: 原始提示词
            system_prompt: 系统提示词（外部传入）
            model: AI 模型
            user_template: 用户消息模板，如 "优化提示词：{prompt}"
            task_id: 关联的任务ID
            
        Returns:
            优化结果字典
        """
        logger.info(f"自定义提示词优化：{prompt[:50]}...")
        
        if not user_template:
            user_template = "优化提示词：{prompt}"
        
        user_message = user_template.format(prompt=prompt)
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            import time
            start_time = time.time()
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=500
            )
            duration = time.time() - start_time
            logger.info(f"API调用耗时: {duration:.2f}秒")
            
            optimized_prompt = completion.choices[0].message.content
            logger.info(f"优化成功：{optimized_prompt[:50]}...")
            
            # 记录token使用
            try:
                usage = completion.usage
                input_tokens = usage.prompt_tokens if usage else 0
                output_tokens = usage.completion_tokens if usage else 0
                
                TokenService.record_usage(
                    model_type='prompt_optimize',
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    model_name=model,
                    task_id=task_id,
                    prompt_text=prompt,
                    response_text=optimized_prompt,
                    scene='custom_optimization'
                )
            except Exception as token_error:
                logger.warning(f"Token 记录失败：{token_error}")
            
            return {
                "success": True,
                "original": prompt,
                "optimized": optimized_prompt,
                "duration": duration,
                "input_tokens": input_tokens if usage else 0,
                "output_tokens": output_tokens if usage else 0,
                "model": model
            }
            
        except APIError as e:
            return {
                "success": False,
                "error": str(e),
                "original": prompt,
                "optimized": prompt
            }
    
    def generate_shot_prompt(self, shot_description: str, scene_type: Optional[str] = None,
                            camera_motion: Optional[str] = None,
                            theme: str = None, video_type: str = None, 
                            style: str = None) -> Dict:
        """
        生成分镜提示词

        Args:
            shot_description: 分镜描述（中文）
            scene_type: 场景类型
            camera_motion: 镜头运动
            theme: 主题（用于上下文）
            video_type: 视频类型（用于上下文）
            style: 风格（用于上下文）

        Returns:
            英文提示词
        """
        logger.info(f"生成分镜提示词：{shot_description[:50]}...")

        # 获取场景风格
        style_info = {}
        if scene_type and scene_type in self.scene_styles:
            style_info = self.scene_styles[scene_type]

        # 镜头运动描述
        motion_desc = ""
        if camera_motion and camera_motion in self.camera_motions:
            motion_desc = self.camera_motions[camera_motion]
        elif style_info.get('camera_motion'):
            motion_desc = self.camera_motions.get(style_info['camera_motion'], '')

        # 构建包含上下文信息的 system prompt
        system_prompt = f"""You are a professional AI prompt engineer for video generation.

CONTEXT INFORMATION (use these consistently throughout the prompt):
- Theme: {theme or 'general content'}
- Video Type: {video_type or 'cinematic video'}
- Scene Style: {scene_type or 'default'}
- Camera Motion: {motion_desc if motion_desc else 'smooth camera movement'}
- Current Shot Description: {shot_description}

TASK:
Convert the above shot description into a detailed English prompt for AI video/image generation.

REQUIREMENTS:
1. Output in pure English only
2. Incorporate the theme and video type naturally into the scene description
3. Include detailed subjects, background, lighting, and color details
4. Add cinematic, high quality, 4K style keywords
5. Keep the prompt 100-150 words
6. Only output the prompt text, no extra explanation"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "qwen3.5-plus",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate the English prompt for this shot: {shot_description}"}
            ]
        }

        try:
            response = requests.post(self.chat_url, headers=headers, json=data, timeout=60)

            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"API 调用失败：{response.status_code}",
                    "prompt": shot_description
                }

            result = response.json()
            prompt = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

            return {
                "success": True,
                "prompt": prompt,
                "scene_type": scene_type,
                "camera_motion": camera_motion or style_info.get('camera_motion', 'push')
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "prompt": shot_description
            }
