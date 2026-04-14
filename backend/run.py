#!/usr/bin/env python3
"""Flask 应用启动脚本"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.config import Config

if __name__ == '__main__':
    app = create_app(Config)
    
    print("=" * 50)
    print("🎬 AI 视频生成平台 - 后端服务")
    print("=" * 50)
    print(f"📍 运行模式：{'开发' if app.config['DEBUG'] else '生产'}")
    print(f"🔗 API 地址：http://localhost:5001")
    print(f"📁 输出目录：{app.config['OUTPUT_DIR']}")
    print(f"💾 数据库：{app.config['DATABASE_PATH']}")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=app.config['DEBUG'],
        threaded=True
    )
