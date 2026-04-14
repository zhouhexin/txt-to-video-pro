from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Task
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """获取任务列表"""
    try:
        # 获取查询参数
        status = request.args.get('status')
        script_id = request.args.get('script_id', type=int)
        limit = request.args.get('limit', 50, type=int)
        
        query = Task.query
        
        if status:
            query = query.filter(Task.status == status)
        if script_id:
            query = query.filter(Task.script_id == script_id)
        
        query = query.order_by(Task.created_at.desc()).limit(limit)
        tasks = query.all()
        
        return jsonify({
            'tasks': [t.to_dict() for t in tasks],
            'total': len(tasks)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tasks_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """获取任务详情"""
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': '任务不存在'}), 404
        
        return jsonify(task.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tasks_bp.route('/tasks/<task_id>/confirm', methods=['PUT'])
def confirm_task(task_id):
    """确认任务继续（用于确认模式）"""
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': '任务不存在'}), 404
        
        # 允许在 waiting_confirm 或 completed 状态下确认
        if task.status not in ['waiting_confirm', 'completed', 'running']:
            return jsonify({'error': f'当前状态不能确认：{task.status}'}), 400
        
        # 更新状态
        task.status = 'running'
        task.confirmed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'status': 'running'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tasks_bp.route('/tasks/<task_id>/retry', methods=['PUT'])
def retry_task(task_id):
    """重试任务"""
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': '任务不存在'}), 404
        
        # 重置状态
        task.status = 'pending'
        task.progress = 0
        task.error_message = None
        db.session.commit()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'status': 'pending'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tasks_bp.route('/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """取消任务"""
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': '任务不存在'}), 404
        
        # 更新状态
        task.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'status': 'cancelled'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
