from datetime import datetime
from app import db


class Script(db.Model):
    """剧本模型"""
    
    __tablename__ = 'scripts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    theme = db.Column(db.String(500), nullable=False)
    video_type = db.Column(db.String(50), nullable=False)
    keywords = db.Column(db.Text)
    overview = db.Column(db.Text)
    style = db.Column(db.Text)
    shots = db.Column(db.JSON, default=list)  # 存储分镜数组
    task_id = db.Column(db.String(50))  # 主 task_id
    search_source = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # 关联任务
    tasks = db.relationship('Task', backref='script', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'theme': self.theme,
            'video_type': self.video_type,
            'keywords': self.keywords,
            'overview': self.overview,
            'style': self.style,
            'shots': self.shots or [],
            'task_id': self.task_id,
            'search_source': self.search_source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Script {self.title}>'
