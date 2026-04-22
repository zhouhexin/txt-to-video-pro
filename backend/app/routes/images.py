from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Script, Task, TaskImage
from app.services import ImageService

images_bp = Blueprint('images', __name__)


@images_bp.route('/images/generate', methods=['POST'])
def generate_image():
    """生成单个分镜图"""
    try:
        data = request.get_json()
        
        task_id = data.get('task_id')
        shot_index = data.get('shot_index', 0)
        prompt = data.get('prompt', '')
        theme = data.get('theme', '')  # 主题
        video_type = data.get('video_type', '')  # 视频类型
        style = data.get('style', '')  # 风格
        
        if not task_id or not prompt:
            return jsonify({'error': 'task_id 和 prompt 不能为空'}), 400
        
        # 初始化服务
        api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
        output_dir = current_app.config['OUTPUT_DIR']
        image_service = ImageService(api_key, output_dir)
        
        # 生成图片（带主题增强）
        task_image = image_service.generate_image(
            task_id, shot_index, prompt, 
            theme=theme, video_type=video_type, style=style
        )
        
        return jsonify({
            'status': 'completed',
            'image_id': task_image.id,
            'url': f'/api/v1/files/image/{task_id}/shot_{shot_index}.png'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@images_bp.route('/images/<task_id>', methods=['GET'])
def get_task_images(task_id):
    """获取任务所有分镜图"""
    api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
    output_dir = current_app.config['OUTPUT_DIR']
    image_service = ImageService(api_key, output_dir)
    
    images = image_service.get_task_images(task_id)
    
    # 添加 URL
    for img in images:
        if img['status'] == 'completed':
            img['url'] = f'/api/v1/files/image/{task_id}/shot_{img["shot_index"]}.png'
    
    return jsonify({
        'task_id': task_id,
        'images': images
    })


@images_bp.route('/images/regenerate', methods=['POST'])
def regenerate_images():
    """重新生成分镜图（创建新 task_id）"""
    try:
        data = request.get_json()
        
        script_id = data.get('script_id')
        
        if not script_id:
            return jsonify({'error': 'script_id 不能为空'}), 400
        
        script = Script.query.get(script_id)
        if not script:
            return jsonify({'error': '剧本不存在'}), 404
        
        # 初始化服务
        api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
        output_dir = current_app.config['OUTPUT_DIR']
        image_service = ImageService(api_key, output_dir)
        
        # 创建新任务
        new_task_id = image_service.regenerate_images(script_id, script.shots)
        
        return jsonify({
            'new_task_id': new_task_id,
            'status': 'success'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
