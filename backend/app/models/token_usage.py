from datetime import datetime
from app import db


class TokenUsage(db.Model):
    """Token 使用记录模型"""
    
    __tablename__ = 'token_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(50), db.ForeignKey('tasks.id'), nullable=True)  # 关联任务ID
    model_type = db.Column(db.String(50), nullable=False)  # script_generate, image_generate, video_generate, prompt_optimize
    model_name = db.Column(db.String(100))  # gpt-4, claude-3, etc.
    input_tokens = db.Column(db.Integer, default=0)
    output_tokens = db.Column(db.Integer, default=0)
    total_tokens = db.Column(db.Integer, default=0)
    is_estimated = db.Column(db.Boolean, default=False)  # 是否为估算值（API未返回精确token信息时为True）
    prompt_text = db.Column(db.Text)  # 发送的提示词
    response_text = db.Column(db.Text)  # 返回的信息
    scene = db.Column(db.String(50))  # 调用场景：script_creation, image_prompt, video_prompt, optimization
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联任务（多对一关系，不能使用 dynamic 加载器）
    task = db.relationship('Task', backref='token_usages', lazy='select')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'model_type': self.model_type,
            'model_name': self.model_name,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.total_tokens,
            'is_estimated': self.is_estimated,
            'prompt_text': self.prompt_text[:500] + '...' if self.prompt_text and len(self.prompt_text) > 500 else self.prompt_text,
            'response_text': self.response_text[:500] + '...' if self.response_text and len(self.response_text) > 500 else self.response_text,
            'scene': self.scene,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def to_dict_full(self):
        """转换为完整字典（包含完整提示词和返回信息）"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'model_type': self.model_type,
            'model_name': self.model_name,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.total_tokens,
            'is_estimated': self.is_estimated,
            'prompt_text': self.prompt_text,
            'response_text': self.response_text,
            'scene': self.scene,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<TokenUsage {self.id} - {self.model_type} - {self.total_tokens} tokens>'
