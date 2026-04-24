from flask import Blueprint, send_file, abort, current_app
import os

files_bp = Blueprint('files', __name__)


@files_bp.route('/files/image/<task_id>/<filename>')
def get_image(task_id, filename):
    """下载分镜图片"""
    from flask import current_app
    
    output_dir = current_app.config['OUTPUT_DIR']
    file_path = os.path.join(output_dir, task_id, 'frames', filename)
    
    if not os.path.exists(file_path):
        abort(404)
    
    return send_file(file_path, mimetype='image/png')


@files_bp.route('/files/video/<task_id>/<filename>')
def get_video(task_id, filename):
    """下载视频文件"""
    output_dir = current_app.config['OUTPUT_DIR']
    file_path = os.path.join(output_dir, task_id, 'videos', filename)
    
    if not os.path.exists(file_path):
        abort(404)
    
    return send_file(file_path, mimetype='video/mp4')


@files_bp.route('/files/audio/<task_id>/<filename>')
def get_audio(task_id, filename):
    """下载配音文件"""
    output_dir = current_app.config['OUTPUT_DIR']
    file_path = os.path.join(output_dir, task_id, 'audios', filename)
    
    if not os.path.exists(file_path):
        abort(404)
    
    return send_file(file_path, mimetype='audio/wav')


@files_bp.route('/files/bgm/<filename>')
def get_bgm(filename):
    """下载背景音乐文件"""
    bgm_dir = os.path.join(current_app.config['OUTPUT_DIR'], '../bgm_library')
    file_path = os.path.join(bgm_dir, filename)
    
    if not os.path.exists(file_path):
        abort(404)
    
    return send_file(file_path, mimetype='audio/mpeg')


@files_bp.route('/files/sfx/<filename>')
def get_sfx(filename):
    """下载音效文件"""
    bgm_dir = os.path.join(current_app.config['OUTPUT_DIR'], '../bgm_library/sfx')
    file_path = os.path.join(bgm_dir, filename)
    
    if not os.path.exists(file_path):
        abort(404)
    
    return send_file(file_path, mimetype='audio/wav')
