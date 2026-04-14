import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """应用配置类"""
    
    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # 数据库配置
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _db_path_env = os.getenv('DATABASE_PATH', os.path.join('data', 'app.db'))
    # 如果是相对路径，则相对于 BASE_DIR 解析
    if not os.path.isabs(_db_path_env):
        DATABASE_PATH = os.path.join(BASE_DIR, _db_path_env)
    else:
        DATABASE_PATH = _db_path_env
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件存储配置
    _output_dir_env = os.getenv('OUTPUT_DIR', 'output_tasks')
    # 如果是相对路径，则相对于 BASE_DIR 解析
    if not os.path.isabs(_output_dir_env):
        OUTPUT_DIR = os.path.join(BASE_DIR, _output_dir_env)
    else:
        OUTPUT_DIR = _output_dir_env
    
    # 阿里云百炼 API 配置
    ALIYUN_BAILIAN_API_KEY = os.getenv('ALIYUN_BAILIAN_API_KEY', '')
    
    # 上传配置
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB 最大上传
    
    # API 配置
    API_PREFIX = '/api/v1'
