import os
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
        first_last_mode = data.get('first_last_mode', False)
        total_shots = data.get('total_shots', 0)  # 总分镜数，用于判断是否是最后一个
        visual_desc = data.get('visual_desc', '')  # 分镜的视觉描述
        
        if not task_id:
            return jsonify({'error': 'task_id 不能为空'}), 400
        
        # 获取图片路径
        output_dir = current_app.config['OUTPUT_DIR']
        image_path = f"{output_dir}/{task_id}/frames/shot_{shot_index}.png"
        
        # 首尾帧模式：获取下一个分镜的图片作为尾帧
        last_frame_path = None
        if first_last_mode and total_shots > 0:
            next_shot_index = shot_index + 1
            if next_shot_index < total_shots:
                last_frame_path = f"{output_dir}/{task_id}/frames/shot_{next_shot_index}.png"
                if not os.path.exists(last_frame_path):
                    last_frame_path = None
        
        # 初始化服务
        api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
        video_service = VideoService(api_key, output_dir)
        
        # 生成视频（带分辨率、镜头运动和视觉描述参数）
        task_video = video_service.generate_video(
            task_id, shot_index, image_path, duration, mode, 
            last_frame_path, resolution, camera_motion, visual_desc
        )
        
        return jsonify({
            'status': 'completed',
            'video_id': task_video.id,
            'url': f'/api/v1/files/video/{task_id}/shot_{shot_index}.mp4',
            'first_last_mode': last_frame_path is not None
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


@videos_bp.route('/videos/generate-all', methods=['POST'])
def generate_all_videos():
    """批量生成所有视频片段"""
    try:
        data = request.get_json()
        
        task_id = data.get('task_id')
        shots = data.get('shots', [])  # [{index, duration, camera_motion}, ...]
        resolution = data.get('resolution', '480P')
        first_last_mode = data.get('first_last_mode', False)
        
        if not task_id:
            return jsonify({'error': 'task_id 不能为空'}), 400
        
        # 初始化服务
        api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
        output_dir = current_app.config['OUTPUT_DIR']
        video_service = VideoService(api_key, output_dir)
        
        # 获取总分镜数
        total_shots = len(shots)
        
        results = []
        for shot in shots:
            shot_index = shot.get('index')
            duration = shot.get('duration', 5)
            camera_motion = shot.get('camera_motion', 'push')
            visual_desc = shot.get('visual', '')  # 分镜的视觉描述
            
            # 检查图片是否存在
            image_path = f"{output_dir}/{task_id}/frames/shot_{shot_index}.png"
            if not os.path.exists(image_path):
                results.append({
                    'shot_index': shot_index,
                    'status': 'failed',
                    'error': '分镜图不存在'
                })
                continue
            
            # 首尾帧模式：获取下一个分镜的图片作为尾帧
            last_frame_path = None
            if first_last_mode:
                next_shot_index = shot_index + 1
                if next_shot_index < total_shots:
                    last_frame_path = f"{output_dir}/{task_id}/frames/shot_{next_shot_index}.png"
                    if not os.path.exists(last_frame_path):
                        last_frame_path = None
            
            try:
                task_video = video_service.generate_video(
                    task_id, shot_index, image_path, duration, 'single', 
                    last_frame_path, resolution, camera_motion, visual_desc
                )
                results.append({
                    'shot_index': shot_index,
                    'status': 'completed',
                    'video_id': task_video.id,
                    'url': f'/api/v1/files/video/{task_id}/shot_{shot_index}.mp4',
                    'first_last_mode': last_frame_path is not None
                })
            except Exception as e:
                results.append({
                    'shot_index': shot_index,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return jsonify({
            'task_id': task_id,
            'results': results,
            'first_last_mode': first_last_mode
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


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
