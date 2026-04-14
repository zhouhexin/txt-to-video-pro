from flask import Blueprint, send_file, abort
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
    from flask import current_app
    
    output_dir = current_app.config['OUTPUT_DIR']
    file_path = os.path.join(output_dir, task_id, 'videos', filename)
    
    if not os.path.exists(file_path):
        abort(404)
    
    return send_file(file_path, mimetype='video/mp4')
