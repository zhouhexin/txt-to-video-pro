#!/usr/bin/env python3
"""数据库迁移脚本"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.config import Config
from sqlalchemy import text

app = create_app(Config)

def migrate():
    """执行数据库迁移"""
    with app.app_context():
        # 检查表是否存在
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        print(f"当前数据库表：{tables}")
        
        # 迁移 Task 表
        if 'tasks' in tables:
            print("\n迁移 tasks 表...")
            
            # 先删除旧的备份表（如果存在）
            if 'tasks_old' in tables:
                print("  - 删除旧的备份表 tasks_old")
                with db.engine.connect() as conn:
                    conn.execute(text("DROP TABLE tasks_old"))
                    conn.commit()
            
            # 添加新列（如果不存在）
            columns = [col['name'] for col in inspector.get_columns('tasks')]
            
            if 'mode' not in columns:
                print("  - 添加 mode 列")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE tasks ADD COLUMN mode VARCHAR(20)"))
                    conn.commit()
            
            if 'camera_motion' not in columns:
                print("  - 添加 camera_motion 列")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE tasks ADD COLUMN camera_motion VARCHAR(20)"))
                    conn.commit()
            
            if 'resolution' not in columns:
                print("  - 添加 resolution 列")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE tasks ADD COLUMN resolution VARCHAR(10)"))
                    conn.commit()
            
            if 'confirmed_at' not in columns:
                print("  - 添加 confirmed_at 列")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE tasks ADD COLUMN confirmed_at DATETIME"))
                    conn.commit()
            
            # 更新 status 列长度
            print("  - 更新 status 列长度")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE tasks RENAME TO tasks_old"))
                conn.execute(text("""
                    CREATE TABLE tasks (
                        id VARCHAR(50) PRIMARY KEY,
                        script_id INTEGER NOT NULL,
                        status VARCHAR(30) DEFAULT 'pending',
                        step VARCHAR(20),
                        mode VARCHAR(20),
                        camera_motion VARCHAR(20),
                        resolution VARCHAR(10),
                        progress INTEGER DEFAULT 0,
                        error_message TEXT,
                        confirmed_at DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME,
                        FOREIGN KEY (script_id) REFERENCES scripts(id)
                    )
                """))
                conn.execute(text("""
                    INSERT INTO tasks 
                    SELECT id, script_id, status, step, mode, camera_motion, resolution, progress, error_message, confirmed_at, created_at, updated_at
                    FROM tasks_old
                """))
                conn.execute(text("DROP TABLE tasks_old"))
                conn.commit()
            
            print("✅ tasks 表迁移完成")
        
        # 迁移 task_videos 表
        if 'task_videos' in tables:
            print("\n迁移 task_videos 表...")
            
            columns = [col['name'] for col in inspector.get_columns('task_videos')]
            
            if 'error_message' not in columns:
                print("  - 添加 error_message 列")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE task_videos ADD COLUMN error_message TEXT"))
                    conn.commit()
            
            print("✅ task_videos 表迁移完成")
        
        # 迁移 token_usage 表
        if 'token_usage' in tables:
            print("\n迁移 token_usage 表...")
            
            columns = [col['name'] for col in inspector.get_columns('token_usage')]
            
            if 'is_estimated' not in columns:
                print("  - 添加 is_estimated 列")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE token_usage ADD COLUMN is_estimated BOOLEAN DEFAULT 0"))
                    conn.commit()
            
            print("✅ token_usage 表迁移完成")
        
        print("\n✅ 数据库迁移完成！")

if __name__ == '__main__':
    migrate()