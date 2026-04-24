import logging
import requests
from typing import Dict, Optional
import os
logger = logging.getLogger(__name__)
from openai import OpenAI, APIError
from .token_service import TokenService


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
                       model: str = "qwen3.5-plus", task_id: str = None) -> Dict:
        """
        优化提示词
        
        Args:
            prompt: 原始提示词
            scene_type: 场景类型（可选）
            model: AI 模型
            task_id: 关联的任务ID（可选）
            
        Returns:
            优化结果字典
        """
        logger.info(f"优化提示词：{prompt[:50]}...")
        
        # 构建系统提示词
        if scene_type and scene_type in self.scene_styles:
            style_info = self.scene_styles[scene_type]
            system_prompt = f"""你是专业 AI 视频提示词优化专家，精通{scene_type}场景创作。
优化用户的提示词，适配视频生成模型，内容更精细生动。

风格参考：
- 场景：{style_info['style']}
- 氛围：{style_info['atmosphere']}
- 镜头：{self.camera_motions.get(style_info['camera_motion'], '')}

要求：
1. 补充光影、色彩、构图等细节
2. 写明镜头运动和光影效果
3. 字数约 150 字，详细描述
4. 仅输出优化后提示词，无额外内容"""
        else:
            system_prompt = """你是专业的 AI 视频提示词优化专家。
优化用户提示词，适配视频生成模型，内容更精细生动。

要求：
1. 补充视觉细节、镜头运动
2. 描述光影与整体氛围
3. 字数约 150 字
4. 仅输出优化后提示词，无额外内容"""

        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"优化提示词：{prompt}"}
                ],
                max_tokens=500  # 限制输出token数量，约200-300个中文字
            )
            optimized_prompt = completion.choices[0].message.content
            logger.info(f"优化成功：{optimized_prompt[:50]}...")
            
            # 检查实际输出内容长度
            actual_length = len(optimized_prompt)
            logger.info(f"实际输出内容长度: {actual_length} 字符")

            print("输入Token:", completion.usage.prompt_tokens)
            print("输出Token:", completion.usage.completion_tokens)
            print("总计Token:", completion.usage.total_tokens)
            print("实际输出字符数:", actual_length)
            
            # 如果token数异常高，使用估算值代替
            # 中文约1.5-2字符/token，英文约4字符/token
            estimated_output_tokens = min(actual_length // 2, 500)  # 估算，上限500
            if completion.usage.completion_tokens > 1000:
                logger.warning(f"Token计数异常({completion.usage.completion_tokens})，使用估算值: {estimated_output_tokens}")

            # 记录 token 使用情况
            try:
                usage = completion.usage
                input_tokens = usage.prompt_tokens if usage else 0
                output_tokens = usage.completion_tokens if usage else 0
                
                full_prompt = f"{system_prompt}\n\n请优化这个提示词：{prompt}"
                
                TokenService.record_usage(
                    model_type='prompt_optimize',
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    model_name=model,
                    task_id=task_id,
                    prompt_text=full_prompt,
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
            e = "错误：请求超时，请检查网络后重试"
            logger.error(f"API调用失败：{e.message}")
            return {
                "success": False,
                "error": str(e),
                "original": prompt,
                "optimized": prompt
            }
    
    def generate_shot_prompt(self, shot_description: str, scene_type: Optional[str] = None,
                            camera_motion: Optional[str] = None) -> Dict:
        """
        生成分镜提示词
        
        Args:
            shot_description: 分镜描述
            scene_type: 场景类型
            camera_motion: 镜头运动
            
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
        
        system_prompt = f"""You are a professional AI prompt engineer.
Convert Chinese storyboard descriptions into detailed English prompts for AI video generation.

Requirements:
1. Output in pure English
2. Include detailed subjects, background, lighting, and color details
3. Add camera movement: {motion_desc if motion_desc else 'smooth camera movement'}
4. Add cinematic, high quality, 4K style keywords
5. 100-150 words in total
6. Only output the prompt, no extra text"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "qwen3.5-plus",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"将这个分镜描述转换为英文提示词：{shot_description}"}
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
