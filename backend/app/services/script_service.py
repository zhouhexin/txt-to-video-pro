import json
import logging
from datetime import datetime
from app import db
from app.models import Script, Task
from .prompt_optimizer import PromptOptimizer
from .token_service import TokenService
from .conversation_manager import conversation_manager
from openai import OpenAI

logger = logging.getLogger(__name__)


class ScriptService:
    """剧本生成服务"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
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
        system_prompt = self._build_system_prompt(video_type, num_shots)
        user_prompt = self._build_user_prompt(theme, keywords, scene_type)
        
        try:
            # 使用会话管理器优化token
            if task_id:
                # 检查会话是否存在
                session_exists = conversation_manager.get_session_size(task_id) > 0
                
                # 首次调用：设置系统提示词
                if not conversation_manager.get_system_prompt(task_id):
                    conversation_manager.set_system_prompt(task_id, system_prompt)
                
                # 如果会话存在，添加之前的用户消息作为上下文
                if session_exists:
                    # 获取之前的用户消息（主题）
                    previous_messages = conversation_manager.get_user_messages(task_id)
                    themes = [m.get('content', '').split('主题：')[1].split('\n')[0] for m in previous_messages if '主题：' in m.get('content', '')]
                    if themes:
                        user_prompt = f"【历史主题】{', '.join(themes)}\n\n" + user_prompt
                    logger.info(f"会话 {task_id} 存在，包含 {len(previous_messages)} 条历史消息")
                
                # 添加当前用户消息
                conversation_manager.add_message(task_id, "user", user_prompt)
                messages = conversation_manager.get_messages(task_id)
            else:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            
            import time
            start_time = time.time()
            response = self.client.chat.completions.create(
                model='qwen-max',
                messages=messages
            )
            duration = time.time() - start_time
            logger.info(f"剧本生成API调用耗时: {duration:.2f}秒")
            
            content = response.choices[0].message.content
            logger.info(f"剧本生成成功，内容长度: {len(content)}")
            
            # 记录会话
            if task_id:
                conversation_manager.add_message(task_id, "assistant", content)
                logger.info(f"会话 {task_id} 已保存")
            
            # 记录 token 使用情况
            try:
                usage = response.usage
                input_tokens = usage.prompt_tokens if usage else 0
                output_tokens = usage.completion_tokens if usage else 0
                
                TokenService.record_usage(
                    model_type='script_generate',
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    model_name='qwen-max',
                    task_id=task_id,
                    prompt_text=user_prompt,
                    response_text=content,
                    scene='script_creation'
                )
            except Exception as token_error:
                logger.warning(f"Token 记录失败：{token_error}")
            
            script_data = self._parse_script_response(content, video_type, theme, keywords)
            return script_data
            
        except Exception as e:
            logger.error(f"剧本生成异常：{str(e)}")
            raise
    
    def _build_system_prompt(self, video_type: str, num_shots: int) -> str:
        """构建系统提示词"""
        return f"""你是专业影视分镜编剧与AI视频剧本创作专家。
按以下要求创作{video_type}剧本：

格式要求：
1. 严格按指定 JSON 输出（仅 JSON，无其他文字）
2. 包含 title、overview（≤200字）、style、shots（含 scene/visual/camera/duration/prompt）
3. {num_shots}个镜头，每个镜头 5 秒
4. 运镜从 push/pull/pan/tilt/zoom/orbit 选
5. 每个镜头配详细英文 AI 绘图提示词（prompt）
6. 除prompt外，所有字段中文"""
    
    def _build_user_prompt(self, theme: str, keywords: str, scene_type: str = None) -> str:
        """构建用户提示词"""
        style_note = ""
        if scene_type and scene_type in self.prompt_optimizer.scene_styles:
            style_info = self.prompt_optimizer.scene_styles[scene_type]
            style_note = f"""
场景风格参考：
- 场景特点：{style_info['style']}
- 氛围：{style_info['atmosphere']}
- 推荐运镜：{style_info['camera_motion']}"""
        
        return f"""创作剧本：
主题：{theme}
关键词：{keywords}{style_note}

画面描述具体适配 AI 视频生成，整体风格统一。"""
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
    
    def save_script(self, video_type: str, theme: str, keywords: str, script_data: dict, original_theme: str = None) -> Script:
        """保存剧本到数据库
        
        Args:
            theme: 优化后的主题（存入 theme 字段）
            original_theme: 原始主题（存入 original_theme 字段）
        """
        script = Script(
            title=script_data['title'],
            theme=theme,  # 优化后的主题
            original_theme=original_theme or theme,  # 原始主题
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
