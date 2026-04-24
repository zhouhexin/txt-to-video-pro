"""
音频相关模型 - 配音、BGM、音效
"""
from datetime import datetime
from app import db


class TaskAudio(db.Model):
    """配音记录表"""
    __tablename__ = 'task_audios'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(50), db.ForeignKey('tasks.id'), nullable=False)
    shot_index = db.Column(db.Integer, nullable=False)  # 分镜索引
    file_path = db.Column(db.String(500))  # 配音文件路径
    duration = db.Column(db.Float)  # 音频时长（秒）
    voice_id = db.Column(db.String(50))  # 音色 ID
    text = db.Column(db.Text)  # 配音文本
    status = db.Column(db.String(20), default='pending')  # pending/running/completed/failed
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    task = db.relationship('Task', backref='audios')
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'shot_index': self.shot_index,
            'file_path': self.file_path,
            'duration': self.duration,
            'voice_id': self.voice_id,
            'text': self.text,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TaskBGM(db.Model):
    """背景音乐记录表"""
    __tablename__ = 'task_bgm'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(50), db.ForeignKey('tasks.id'), nullable=False)
    bgm_id = db.Column(db.String(50))  # BGM 库中的 ID
    bgm_name = db.Column(db.String(200))  # BGM 名称
    file_path = db.Column(db.String(500))  # BGM 文件路径
    volume = db.Column(db.Float, default=0.3)  # 音量（0-1）
    start_time = db.Column(db.Float, default=0)  # 开始时间
    end_time = db.Column(db.Float)  # 结束时间
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    task = db.relationship('Task', backref='bgms')
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'bgm_id': self.bgm_id,
            'bgm_name': self.bgm_name,
            'file_path': self.file_path,
            'volume': self.volume,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TaskSFX(db.Model):
    """音效记录表"""
    __tablename__ = 'task_sfx'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(50), db.ForeignKey('tasks.id'), nullable=False)
    shot_index = db.Column(db.Integer)  # 音效应用的分镜索引
    sfx_id = db.Column(db.String(50))  # 音效库中的 ID
    sfx_name = db.Column(db.String(200))  # 音效名称
    file_path = db.Column(db.String(500))  # 音效文件路径
    volume = db.Column(db.Float, default=0.5)  # 音量
    start_offset = db.Column(db.Float, default=0)  # 相对于分镜的开始偏移
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    task = db.relationship('Task', backref='sfxs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'shot_index': self.shot_index,
            'sfx_id': self.sfx_id,
            'sfx_name': self.sfx_name,
            'file_path': self.file_path,
            'volume': self.volume,
            'start_offset': self.start_offset,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
