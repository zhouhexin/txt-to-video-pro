from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Task, TaskVideo
from app.services import VideoService

videos_bp = Blueprint('videos', __name__)


@videos_bp.route('/videos/generate', methods=['POST'])
def generate_video():
    """生成单个视频片段"""
    try:
        data = request.get_json()
        
        task_id = data.get('task_id')
        shot_index = data.get('shot_index', 0)
        duration = data.get('duration', 5)
        mode = data.get('mode', 'single')
        resolution = data.get('resolution', '480P')
        camera_motion = data.get('camera_motion', 'push')
        
        if not task_id:
            return jsonify({'error': 'task_id 不能为空'}), 400
        
        # 获取图片路径
        output_dir = current_app.config['OUTPUT_DIR']
        image_path = f"{output_dir}/{task_id}/frames/shot_{shot_index}.png"
        
        # 初始化服务
        api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
        video_service = VideoService(api_key, output_dir)
        
        # 生成视频（带分辨率和镜头运动参数）
        task_video = video_service.generate_video(task_id, shot_index, image_path, duration, mode, None, resolution, camera_motion)
        
        return jsonify({
            'status': 'completed',
            'video_id': task_video.id,
            'url': f'/api/v1/files/video/{task_id}/shot_{shot_index}.mp4'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@videos_bp.route('/videos/<task_id>', methods=['GET'])
def get_task_videos(task_id):
    """获取任务所有视频"""
    api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
    output_dir = current_app.config['OUTPUT_DIR']
    video_service = VideoService(api_key, output_dir)
    
    videos = video_service.get_task_videos(task_id)
    
    # 添加 URL
    for vid in videos:
        if vid['status'] == 'completed':
            vid['url'] = f'/api/v1/files/video/{task_id}/shot_{vid["shot_index"]}.mp4'
    
    # 检查合并视频
    merged_video = video_service.check_merged_video(task_id)
    
    response = {
        'task_id': task_id,
        'videos': videos
    }
    
    if merged_video:
        response['merged_video'] = merged_video
    
    return jsonify(response)


@videos_bp.route('/videos/merge', methods=['POST'])
def merge_videos():
    """合并所有视频为完整视频"""
    try:
        data = request.get_json()
        
        task_id = data.get('task_id')
        
        if not task_id:
            return jsonify({'error': 'task_id 不能为空'}), 400
        
        # 初始化服务
        api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
        output_dir = current_app.config['OUTPUT_DIR']
        video_service = VideoService(api_key, output_dir)
        
        # 合并视频
        merged_path = video_service.merge_videos(task_id)
        
        return jsonify({
            'status': 'completed',
            'merged_url': f'/api/v1/files/video/{task_id}/merged_full_video.mp4'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
