import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from .config import Config

# 初始化扩展
db = SQLAlchemy()

def create_app(config_class=Config):
    """Flask 应用工厂函数"""
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(app.config['DATABASE_PATH']), exist_ok=True)
    os.makedirs(app.config['OUTPUT_DIR'], exist_ok=True)
    
    # 初始化扩展
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册路由蓝图
    from .routes.scripts import scripts_bp
    from .routes.images import images_bp
    from .routes.videos import videos_bp
    from .routes.files import files_bp
    from .routes.prompts import prompts_bp
    from .routes.tasks import tasks_bp
    from .routes.statistics import statistics_bp
    
    app.register_blueprint(scripts_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(images_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(videos_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(files_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(prompts_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(tasks_bp, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(statistics_bp, url_prefix=app.config['API_PREFIX'])
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 健康检查端点
    @app.route('/health')
    def health():
        return {'status': 'ok'}
    
    return app
