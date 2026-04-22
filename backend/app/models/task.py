from datetime import datetime
from app import db


class Task(db.Model):
    """任务模型"""
    
    __tablename__ = 'tasks'
    
    id = db.Column(db.String(50), primary_key=True)  # task_id
    script_id = db.Column(db.Integer, db.ForeignKey('scripts.id'), nullable=False)
    status = db.Column(db.String(30), default='pending')  # pending, waiting_confirm, running, completed, failed, cancelled
    step = db.Column(db.String(20))  # script, image, video
    mode = db.Column(db.String(20))  # single, first_last  # 生成模式
    camera_motion = db.Column(db.String(20))  # push/pull/pan/tilt/zoom/orbit
    resolution = db.Column(db.String(10))  # 480P/720P/1080P
    progress = db.Column(db.Integer, default=0)  # 0-100
    error_message = db.Column(db.Text)
    confirmed_at = db.Column(db.DateTime)  # 确认时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # 关联图片和视频
    images = db.relationship('TaskImage', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    videos = db.relationship('TaskVideo', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'script_id': self.script_id,
            'status': self.status,
            'step': self.step,
            'progress': self.progress,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Task {self.id}>'


class TaskImage(db.Model):
    """任务分镜图模型"""
    
    __tablename__ = 'task_images'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(50), db.ForeignKey('tasks.id'), nullable=False)
    shot_index = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    prompt = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'shot_index': self.shot_index,
            'file_path': self.file_path,
            'status': self.status,
            'prompt': self.prompt,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<TaskImage {self.task_id}_shot_{self.shot_index}>'


class TaskVideo(db.Model):
    """任务视频模型"""
    
    __tablename__ = 'task_videos'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(50), db.ForeignKey('tasks.id'), nullable=False)
    shot_index = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(500))
    duration = db.Column(db.Integer, default=5)
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    error_message = db.Column(db.Text)  # 错误信息
    prompt = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'shot_index': self.shot_index,
            'file_path': self.file_path,
            'duration': self.duration,
            'status': self.status,
            'error_message': self.error_message,
            'prompt': self.prompt,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<TaskVideo {self.task_id}_shot_{self.shot_index}>'
