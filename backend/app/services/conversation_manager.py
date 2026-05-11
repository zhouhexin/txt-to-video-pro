"""
会话管理器 - 持久化到数据库
"""
import logging
from typing import Dict, List, Optional
from app import db
from app.models import Conversation, ConversationMessage

logger = logging.getLogger(__name__)


class ConversationManager:
    """会话管理器，持久化存储到数据库"""
    
    def get_or_create_session(self, task_id: str) -> Conversation:
        """获取或创建会话"""
        conversation = Conversation.query.filter_by(task_id=task_id).first()
        if not conversation:
            conversation = Conversation(task_id=task_id)
            db.session.add(conversation)
            db.session.commit()
        return conversation
    
    def set_system_prompt(self, task_id: str, system_prompt: str):
        """设置系统提示词（只设置一次）"""
        conversation = self.get_or_create_session(task_id)
        if not conversation.system_prompt:
            conversation.system_prompt = system_prompt
            db.session.commit()
    
    def get_system_prompt(self, task_id: str) -> Optional[str]:
        """获取系统提示词"""
        conversation = Conversation.query.filter_by(task_id=task_id).first()
        return conversation.system_prompt if conversation else None
    
    def add_message(self, task_id: str, role: str, content: str):
        """添加消息到会话"""
        conversation = self.get_or_create_session(task_id)
        message = ConversationMessage(
            conversation_id=conversation.id,
            role=role,
            content=content
        )
        db.session.add(message)
        db.session.commit()
    
    def get_messages(self, task_id: str, include_system: bool = True) -> List[Dict]:
        """获取会话消息"""
        messages = []
        
        conversation = Conversation.query.filter_by(task_id=task_id).first()
        if not conversation:
            return messages
        
        # 添加系统提示词
        if include_system and conversation.system_prompt:
            messages.append({"role": "system", "content": conversation.system_prompt})
        
        # 添加对话历史
        for msg in conversation.messages.order_by(ConversationMessage.created_at).all():
            messages.append({"role": msg.role, "content": msg.content})
        
        return messages
    
    def get_user_messages(self, task_id: str) -> List[Dict]:
        """只获取用户消息"""
        messages = []
        conversation = Conversation.query.filter_by(task_id=task_id).first()
        if conversation:
            for msg in conversation.messages.order_by(ConversationMessage.created_at).all():
                if msg.role == "user":
                    messages.append({"role": msg.role, "content": msg.content})
        return messages
    
    def clear_session(self, task_id: str):
        """清除会话"""
        conversation = Conversation.query.filter_by(task_id=task_id).first()
        if conversation:
            db.session.delete(conversation)
            db.session.commit()
    
    def get_session_size(self, task_id: str) -> int:
        """获取会话消息数量"""
        conversation = Conversation.query.filter_by(task_id=task_id).first()
        return conversation.messages.count() if conversation else 0
    
    def get_all_session_ids(self) -> List[str]:
        """获取所有会话ID"""
        return [c.task_id for c in Conversation.query.all()]


# 全局单例
conversation_manager = ConversationManager()
