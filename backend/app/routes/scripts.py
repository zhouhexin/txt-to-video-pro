from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Script, Task
from app.services import ScriptService
from datetime import datetime

scripts_bp = Blueprint('scripts', __name__)


@scripts_bp.route('/scripts/generate', methods=['POST'])
def generate_script():
    """生成新剧本"""
    try:
        data = request.get_json()
        
        video_type = data.get('video_type', '文旅宣传')
        theme = data.get('theme', '')  # 优化后的主题
        original_theme = data.get('original_theme', theme)  # 原始主题
        keywords = data.get('keywords', '')
        num_shots = data.get('num_shots', 5)
        scene_type = data.get('scene_type')
        
        if not theme:
            return jsonify({'error': '主题不能为空'}), 400
        
        # 先创建 task_id（用于 token 统计）
        temp_task_id = f"task_{int(datetime.now().timestamp())}_00000000"
        
        # 初始化服务
        api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
        script_service = ScriptService(api_key)
        
        # 生成剧本（带 task_id 用于统计）
        script_data = script_service.generate_script(video_type, theme, keywords, num_shots, scene_type, task_id=temp_task_id)
        
        # 保存到数据库（保存原始主题）
        script = script_service.save_script(video_type, theme, keywords, script_data, original_theme)
        
        # 创建任务（使用正确的 task_id 包含 script.id）
        task_id = f"task_{int(datetime.now().timestamp())}_{script.id:08d}"
        task = Task(
            id=task_id,
            script_id=script.id,
            status='completed',
            step='script',
            progress=100
        )
        db.session.add(task)
        script.task_id = task_id
        db.session.commit()
        
        # 更新 token_usage 表中的 task_id
        from app.models import TokenUsage
        TokenUsage.query.filter(TokenUsage.task_id == temp_task_id).update({'task_id': task_id})
        db.session.commit()
        
        return jsonify({
            'script_id': script.id,
            'task_id': task_id,
            'script': script.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@scripts_bp.route('/scripts/<int:script_id>', methods=['GET'])
def get_script(script_id):
    """获取剧本详情"""
    script = Script.query.get(script_id)
    
    if not script:
        return jsonify({'error': '剧本不存在'}), 404
    
    return jsonify(script.to_dict())


@scripts_bp.route('/scripts', methods=['GET'])
def search_scripts():
    """搜索剧本列表"""
    theme = request.args.get('theme')
    video_type = request.args.get('video_type')
    limit = request.args.get('limit', 50, type=int)
    
    api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
    script_service = ScriptService(api_key)
    
    scripts = script_service.search_scripts(theme, video_type, limit)
    
    return jsonify({
        'scripts': [s.to_dict() for s in scripts],
        'total': len(scripts)
    })


@scripts_bp.route('/scripts/<int:script_id>/confirm', methods=['PUT'])
def confirm_script(script_id):
    """确认剧本，进入分镜生成步骤"""
    script = Script.query.get(script_id)
    
    if not script:
        return jsonify({'error': '剧本不存在'}), 404
    
    # 如果还没有 task_id，创建一个新的
    if not script.task_id:
        task_id = f"task_{int(datetime.now().timestamp())}_{script.id:08d}"
        task = Task(
            id=task_id,
            script_id=script.id,
            status='pending',
            step='image',
            progress=0
        )
        db.session.add(task)
        script.task_id = task_id
        db.session.commit()
    
    return jsonify({
        'success': True,
        'task_id': script.task_id
    })


@scripts_bp.route('/scripts/<int:script_id>', methods=['DELETE'])
def delete_script(script_id):
    """删除剧本及相关文件"""
    import os
    
    script = Script.query.get(script_id)
    
    if not script:
        return jsonify({'error': '剧本不存在'}), 404
    
    deleted_files = []
    
    # 删除相关文件
    if script.task_id:
        output_dir = current_app.config['OUTPUT_DIR']
        task_dir = os.path.join(output_dir, script.task_id)
        
        if os.path.exists(task_dir):
            import shutil
            shutil.rmtree(task_dir)
            deleted_files.append(task_dir)
    
    # 删除数据库记录
    db.session.delete(script)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'deleted_files': deleted_files
    })
