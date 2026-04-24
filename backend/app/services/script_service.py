import json
import logging
from datetime import datetime
from app import db
from app.models import Script, Task
from .prompt_optimizer import PromptOptimizer
from .token_service import TokenService
import dashscope
from dashscope import Generation

logger = logging.getLogger(__name__)


class ScriptService:
    """剧本生成服务"""
    
    def __init__(self, api_key: str):
        dashscope.api_key = api_key
        self.prompt_optimizer = PromptOptimizer(api_key)
    
    def generate_script(self, video_type: str, theme: str, keywords: str = "", 
                       num_shots: int = 5, scene_type: str = None, task_id: str = None) -> dict:
        """
        生成剧本
        
        Args:
            video_type: 视频类型（文旅宣传、产品展示、教程等）
            theme: 主题
            keywords: 关键词
            num_shots: 分镜数量
            task_id: 关联的任务ID（可选）
            
        Returns:
            生成的剧本字典
        """
        prompt = self._build_prompt(video_type, theme, keywords, num_shots)
        
        try:
            response = Generation.call(
                model='qwen-max',
                prompt=prompt,
                result_format='message'
            )
            
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                
                # 记录 token 使用情况
                try:
                    usage = response.usage
                    input_tokens = usage.input_tokens if hasattr(usage, 'input_tokens') else 0
                    output_tokens = usage.output_tokens if hasattr(usage, 'output_tokens') else 0
                    
                    TokenService.record_usage(
                        model_type='script_generate',
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        model_name='qwen-max',
                        task_id=task_id,
                        prompt_text=prompt,
                        response_text=content,
                        scene='script_creation'
                    )
                except Exception as token_error:
                    logger.warning(f"Token 记录失败：{token_error}")
                
                script_data = self._parse_script_response(content, video_type, theme, keywords)
                return script_data
            else:
                logger.error(f"AI API 调用失败：{response.code} - {response.message}")
                raise Exception(f"AI 服务调用失败：{response.message}")
                
        except Exception as e:
            logger.error(f"剧本生成异常：{str(e)}")
            raise
    
    def _build_prompt(self, video_type: str, theme: str, keywords: str, num_shots: int, 
                     scene_type: str = None) -> str:
        """构建 AI 提示词"""
        # 如果有场景类型，添加场景风格描述
        style_note = ""
        if scene_type and scene_type in self.prompt_optimizer.scene_styles:
            style_info = self.prompt_optimizer.scene_styles[scene_type]
            style_note = f"""

场景风格参考：
- 场景特点：{style_info['style']}
- 氛围：{style_info['atmosphere']}
- 推荐运镜：{style_info['camera_motion']}"""
        
        return f"""专业视频剧本创作专家，按以下要求创作完整{video_type}剧本：
主题：{theme}
关键词：{keywords}
分镜数量：{num_shots} 个镜头{style_note}

格式：严格按指定 JSON 输出（仅 JSON，无其他文字），包含 title、overview（≤200 字）、style、shots（含 scene/visual/camera/duration/prompt）
要求：{num_shots}个镜头，每个镜头 3-8 秒，
运镜从 push/pull/pan/tilt/zoom/orbit 选，画面描述具体适配 AI 视频生成，
每个镜头配详细英文 AI 绘图提示词（prompt），整体风格统一，符合{video_type}特点
除prompt外，所有字段中文
"""

    # 请按照以下 JSON 格式输出剧本（只输出 JSON，不要其他文字）：
    # {{
    #     "title": "剧本标题",
    #     "overview": "200 字以内的视频概述",
    #     "style": "视频风格描述",
    #     "shots": [
    #         {{
    #             "scene": "镜头 1: 场景名称",
    #             "visual": "详细的画面描述，包括场景、人物、动作、道具等",
    #             "camera": "运镜方式（push/pull/pan/tilt/zoom/orbit）",
    #             "duration": 5,
    #             "prompt": "用于 AI 绘图的英文 prompt，详细描述画面内容、风格、光影、构图等"
    #         }}
    #     ]
    # }}
    def _parse_script_response(self, content: str, video_type: str, theme: str, keywords: str) -> dict:
        """解析 AI 返回的剧本"""
        try:
            # 尝试提取 JSON 内容
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                script_data = json.loads(json_str)
            else:
                script_data = json.loads(content)
            
            return {
                'title': script_data.get('title', f'{theme} - {video_type}'),
                'overview': script_data.get('overview', ''),
                'style': script_data.get('style', ''),
                'shots': script_data.get('shots', [])
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败：{str(e)}")
            # 返回基础结构
            return {
                'title': f'{theme} - {video_type}',
                'overview': content[:500],
                'style': '',
                'shots': []
            }
    
    def save_script(self, video_type: str, theme: str, keywords: str, script_data: dict) -> Script:
        """保存剧本到数据库"""
        script = Script(
            title=script_data['title'],
            theme=theme,
            video_type=video_type,
            keywords=keywords,
            overview=script_data.get('overview', ''),
            style=script_data.get('style', ''),
            shots=script_data.get('shots', []),
            search_source='qwen-max'
        )
        db.session.add(script)
        db.session.commit()
        return script
    
    def get_script_by_id(self, script_id: int) -> Script:
        """根据 ID 获取剧本"""
        return Script.query.get(script_id)
    
    def search_scripts(self, theme: str = None, video_type: str = None, limit: int = 50) -> list:
        """搜索剧本"""
        query = Script.query
        
        if theme:
            query = query.filter(Script.theme.contains(theme))
        if video_type:
            query = query.filter(Script.video_type == video_type)
        
        query = query.order_by(Script.created_at.desc()).limit(limit)
        return query.all()
    
    def delete_script(self, script_id: int) -> bool:
        """删除剧本"""
        script = Script.query.get(script_id)
        if script:
            db.session.delete(script)
            db.session.commit()
            return True
        return False
