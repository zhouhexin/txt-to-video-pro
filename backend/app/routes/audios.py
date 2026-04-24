"""
音频相关 API 路由 - 配音、BGM、音效
"""
import os
import logging
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Task, TaskAudio, TaskBGM, TaskSFX, Script
from app.services.audio_service import AudioService
from app.services.bgm_service import BGMService

audios_bp = Blueprint('audios', __name__)


@audios_bp.route('/audios/generate', methods=['POST'])
def generate_audio():
    """生成单个分镜的配音"""
    try:
        data = request.get_json()
        
        task_id = data.get('task_id')
        shot_index = data.get('shot_index', 0)
        text = data.get('text')
        voice_id = data.get('voice_id', 'xiaoyun')
        
        if not task_id or not text:
            return jsonify({'error': 'task_id 和 text 不能为空'}), 400
        
        api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
        output_dir = current_app.config['OUTPUT_DIR']
        audio_service = AudioService(api_key, output_dir)
        
        task_audio = audio_service.generate_speech(
            task_id, shot_index, text, voice_id
        )
        
        return jsonify({
            'status': 'completed',
            'audio_id': task_audio.id,
            'url': f'/api/v1/files/audio/{task_id}/shot_{shot_index}_voice.wav',
            'duration': task_audio.duration,
            'voice_id': task_audio.voice_id
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"生成配音失败：{e}")
        return jsonify({'error': str(e)}), 500


@audios_bp.route('/audios/generate-all', methods=['POST'])
def generate_all_audios():
    """批量生成所有分镜的配音"""
    try:
        data = request.get_json()
        
        task_id = data.get('task_id')
        voice_id = data.get('voice_id', 'xiaoyun')
        script_id = data.get('script_id')
        
        if not task_id:
            return jsonify({'error': 'task_id 不能为空'}), 400
        
        # 从剧本获取旁白文本
        shots = []
        if script_id:
            script = Script.query.get(script_id)
            if script and script.shots:
                for i, shot in enumerate(script.shots):
                    # 使用 visual 字段作为配音文本，或者可以添加 narration 字段
                    text = shot.get('narration') or shot.get('visual', '')
                    if text:
                        shots.append({
                            'index': i,
                            'text': text
                        })
        
        if not shots:
            return jsonify({'error': '没有可生成配音的分镜'}), 400
        
        api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
        output_dir = current_app.config['OUTPUT_DIR']
        audio_service = AudioService(api_key, output_dir)
        
        results = audio_service.generate_all_speech(task_id, shots, voice_id)
        
        success_count = sum(1 for r in results if r['status'] == 'completed')
        fail_count = sum(1 for r in results if r['status'] == 'failed')
        
        return jsonify({
            'status': 'completed',
            'results': results,
            'success_count': success_count,
            'fail_count': fail_count
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"批量生成配音失败：{e}")
        return jsonify({'error': str(e)}), 500


@audios_bp.route('/audios/<task_id>', methods=['GET'])
def get_task_audios(task_id):
    """获取任务所有配音"""
    api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
    output_dir = current_app.config['OUTPUT_DIR']
    audio_service = AudioService(api_key, output_dir)
    
    audios = audio_service.get_task_audios(task_id)
    
    # 添加 URL
    for audio in audios:
        if audio['status'] == 'completed':
            audio['url'] = f'/api/v1/files/audio/{task_id}/shot_{audio["shot_index"]}_voice.wav'
    
    return jsonify({
        'task_id': task_id,
        'audios': audios
    })


@audios_bp.route('/bgm/list', methods=['GET'])
def list_bgm():
    """获取 BGM 列表"""
    category = request.args.get('category')
    mood = request.args.get('mood')
    
    bgm_dir = os.path.join(current_app.config['OUTPUT_DIR'], '../bgm_library')
    bgm_service = BGMService(bgm_dir)
    
    bgm_list = bgm_service.get_bgm_list(category, mood)
    
    return jsonify({'bgm_list': bgm_list})


@audios_bp.route('/sfx/list', methods=['GET'])
def list_sfx():
    """获取音效列表"""
    category = request.args.get('category')
    tags = request.args.getlist('tags')
    
    bgm_dir = os.path.join(current_app.config['OUTPUT_DIR'], '../bgm_library')
    bgm_service = BGMService(bgm_dir)
    
    sfx_list = bgm_service.get_sfx_list(category, tags)
    
    return jsonify({'sfx_list': sfx_list})


@audios_bp.route('/sfx/recommend', methods=['POST'])
def recommend_sfx():
    """根据场景描述推荐音效"""
    try:
        data = request.get_json()
        scene_description = data.get('description', '')
        
        if not scene_description:
            return jsonify({'error': '场景描述不能为空'}), 400
        
        bgm_dir = os.path.join(current_app.config['OUTPUT_DIR'], '../bgm_library')
        bgm_service = BGMService(bgm_dir)
        
        recommendations = bgm_service.recommend_sfx(scene_description)
        
        return jsonify({'recommendations': recommendations})
        
    except Exception as e:
        logger.error(f"推荐音效失败：{e}")
        return jsonify({'error': str(e)}), 500


@audios_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取 BGM 和音效分类"""
    bgm_dir = os.path.join(current_app.config['OUTPUT_DIR'], '../bgm_library')
    bgm_service = BGMService(bgm_dir)
    
    categories = bgm_service.get_categories()
    
    return jsonify({'categories': categories})


@audios_bp.route('/bgm/set', methods=['POST'])
def set_bgm():
    """为任务设置背景音乐"""
    try:
        data = request.get_json()
        
        task_id = data.get('task_id')
        bgm_id = data.get('bgm_id')
        bgm_name = data.get('bgm_name')
        volume = data.get('volume', 0.3)
        
        if not task_id or not bgm_id:
            return jsonify({'error': 'task_id 和 bgm_id 不能为空'}), 400
        
        # 查找现有记录
        task_bgm = TaskBGM.query.filter_by(task_id=task_id).first()
        
        if task_bgm:
            # 更新现有记录
            task_bgm.bgm_id = bgm_id
            task_bgm.bgm_name = bgm_name
            task_bgm.volume = volume
        else:
            # 创建新记录
            task_bgm = TaskBGM(
                task_id=task_id,
                bgm_id=bgm_id,
                bgm_name=bgm_name,
                volume=volume,
                status='pending'
            )
            db.session.add(task_bgm)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'bgm_id': bgm_id,
            'bgm_name': bgm_name,
            'volume': volume
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"设置 BGM 失败：{e}")
        return jsonify({'error': str(e)}), 500


@audios_bp.route('/audios/merge', methods=['POST'])
def merge_audio_video():
    """将配音、BGM、音效与视频合并"""
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        
        if not task_id:
            return jsonify({'error': 'task_id 不能为空'}), 400
        
        api_key = current_app.config['ALIYUN_BAILIAN_API_KEY']
        output_dir = current_app.config['OUTPUT_DIR']
        audio_service = AudioService(api_key, output_dir)
        
        final_path = audio_service.merge_audio_with_video(task_id)
        
        return jsonify({
            'status': 'completed',
            'final_url': f'/api/v1/files/video/{task_id}/final_with_audio.mp4'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"合并音视频失败：{e}")
        return jsonify({'error': str(e)}), 500
