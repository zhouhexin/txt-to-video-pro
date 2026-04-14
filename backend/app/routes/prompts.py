from flask import Blueprint, request, jsonify, current_app
from app.services import PromptOptimizer

prompts_bp = Blueprint('prompts', __name__)


@prompts_bp.route('/prompts/optimize', methods=['POST'])
def optimize_prompt():
    """优化提示词"""
    try:
        data = request.get_json()
        
        prompt = data.get('prompt', '')
        scene_type = data.get('scene_type')
        model = data.get('model', 'qwen3.5-plus')
        
        if not prompt:
            return jsonify({'error': '提示词不能为空'}), 400
        
        # 初始化服务
        api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
        optimizer = PromptOptimizer(api_key)
        
        # 优化提示词
        result = optimizer.optimize_prompt(prompt, scene_type, model)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prompts_bp.route('/prompts/scenes', methods=['GET'])
def get_scene_styles():
    """获取场景风格列表"""
    try:
        api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
        optimizer = PromptOptimizer(api_key)
        
        scenes = optimizer.get_scene_styles()
        motions = optimizer.get_camera_motions()
        
        return jsonify({
            'scenes': scenes,
            'camera_motions': motions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prompts_bp.route('/prompts/generate-shot', methods=['POST'])
def generate_shot_prompt():
    """生成分镜提示词"""
    try:
        data = request.get_json()
        
        shot_description = data.get('shot_description', '')
        scene_type = data.get('scene_type')
        camera_motion = data.get('camera_motion')
        
        if not shot_description:
            return jsonify({'error': '分镜描述不能为空'}), 400
        
        # 初始化服务
        api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
        optimizer = PromptOptimizer(api_key)
        
        # 生成提示词
        result = optimizer.generate_shot_prompt(shot_description, scene_type, camera_motion)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
