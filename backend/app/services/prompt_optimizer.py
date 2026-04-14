import logging
import requests
from typing import Dict, Optional
import os
logger = logging.getLogger(__name__)
from openai import OpenAI, APIError


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
                       model: str = "qwen3.5-plus") -> Dict:
        """
        优化提示词
        
        Args:
            prompt: 原始提示词
            scene_type: 场景类型（可选）
            model: AI 模型
            
        Returns:
            优化结果字典
        """
        logger.info(f"优化提示词：{prompt[:50]}...")
        
        # 构建系统提示词
        if scene_type and scene_type in self.scene_styles:
            style_info = self.scene_styles[scene_type]
            system_prompt = f"""你是一位专业的 AI 视频提示词优化专家，擅长{scene_type}场景的描述。
请优化用户的提示词，使其更加详细、生动，适合视频生成模型。

风格参考：
- 场景特点：{style_info['style']}
- 氛围：{style_info['atmosphere']}
- 推荐镜头：{self.camera_motions.get(style_info['camera_motion'], '')}

要求：
1. 添加详细的视觉细节（建筑、光影、色彩、构图）
2. 描述镜头运动和光影效果
3. 输出 150 字左右的详细描述
4. 只输出优化后的提示词，不要其他内容"""
        else:
            system_prompt = """你是一位专业的 AI 视频提示词优化专家。
请优化用户的提示词，使其更加详细、生动，适合视频生成模型。

要求：
1. 添加详细的视觉细节和镜头运动描述
2. 描述光影效果和氛围
3. 输出 150 字左右的详细描述
4. 只输出优化后的提示词，不要其他内容"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请优化这个提示词：{prompt}"}
            ]
        }
        
        try:
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请优化这个提示词：{prompt}"}
                ]
            )
            # response = completion.model_dump_json()
            optimized_prompt = completion.choices[0].message.content

            logger.info(f"优化成功：{optimized_prompt[:50]}...")

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
        
        system_prompt = f"""你是一位专业的 AI 绘画提示词工程师。
请将中文分镜描述转换为详细的英文提示词，用于 AI 视频生成。

要求：
1. 使用英文输出
2. 包含详细的视觉元素（主体、背景、光影、色彩）
3. 包含镜头运动描述：{motion_desc if motion_desc else '平滑的镜头运动'}
4. 包含风格关键词：电影感、高质量、4K
5. 输出 100-150 个单词
6. 只输出提示词，不要其他内容"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "qwen3.5-plus",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请将这个分镜描述转换为英文提示词：{shot_description}"}
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
