#!/usr/bin/env python3
"""
配音功能测试脚本
测试配音生成、加载和合并功能
"""
import os
import sys

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_app, db
from backend.app.models import Task, TaskVideo, TaskAudio, Script, TaskBGM
import subprocess

def create_test_task():
    """创建测试任务"""
    app = create_app()
    with app.app_context():
        # 创建任务
        task_id = "test_voiceover_20260427"
        task = Task(
            id=task_id,
            status='completed',
            progress=100,
            step='video_generated'
        )
        db.session.add(task)
        
        # 创建测试剧本
        script = Script(
            title="测试配音功能",
            theme="测试",
            video_type="test",
            shots=[
                {"visual": "清晨的阳光洒在湖面上", "narration": "这是一个美丽的清晨"},
                {"visual": "微风吹过，带来阵阵花香", "narration": "微风吹过，带来阵阵花香"},
                {"visual": "鸟儿在枝头欢快地歌唱", "narration": "鸟儿在枝头欢快地歌唱"},
                {"visual": "人们在公园里悠闲地散步", "narration": "人们在公园里悠闲地散步"},
                {"visual": "美好的一天开始了", "narration": "美好的一天开始了"}
            ]
        )
        db.session.add(script)
        db.session.commit()
        
        task.script_id = script.id
        db.session.commit()
        
        print(f"✓ 创建测试任务：{task_id}")
        print(f"✓ 剧本 ID: {script.id}")
        print(f"✓ 分镜数：{len(script.shots)}")
        
        return task_id, script.id, script.shots

def create_test_videos(task_id, shots):
    """创建测试视频（使用静态图片生成短视频）"""
    frames_dir = f"backend/output_tasks/{task_id}/frames"
    videos_dir = f"backend/output_tasks/{task_id}/videos"
    os.makedirs(videos_dir, exist_ok=True)
    
    app = create_app()
    with app.app_context():
        for i, shot in enumerate(shots):
            # 创建测试视频（5 秒黑屏视频）
            video_path = os.path.join(videos_dir, f"shot_{i}.mp4")
            
            # 使用 ffmpeg 生成测试视频
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'color=c=blue:s=640x360:d=5',
                '-f', 'lavfi',
                '-i', f'anullsrc=r=44100:cl=stereo',
                '-vf', f'drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text="Shot {i+1}":fontsize=48:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2',
                '-t', '5',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                video_path
            ]
            
            try:
                subprocess.run(cmd, capture_output=True, timeout=30)
                
                # 创建数据库记录
                video = TaskVideo(
                    task_id=task_id,
                    shot_index=i,
                    file_path=video_path,
                    duration=5.0,
                    status='completed'
                )
                db.session.add(video)
                print(f"✓ 创建测试视频：镜头 {i+1}")
            except Exception as e:
                print(f"✗ 创建视频失败：{e}")
        
        db.session.commit()

def test_audio_generation(task_id, shots):
    """测试配音生成"""
    from backend.app.services.audio_service import AudioService
    
    app = create_app()
    with app.app_context():
        audio_service = AudioService(output_dir='backend/output_tasks')
        
        # 准备分镜数据
        shot_data = [
            {"index": i, "text": shot.get("narration", "")}
            for i, shot in enumerate(shots)
        ]
        
        print("\n🎙️ 开始生成配音...")
        results = audio_service.generate_all_speech(
            task_id=task_id,
            shots=shot_data,
            voice_id='xiaoxiao'
        )
        
        success = sum(1 for r in results if r['status'] == 'completed')
        failed = sum(1 for r in results if r['status'] == 'failed')
        
        print(f"✓ 配音生成完成：{success} 成功，{failed} 失败")
        
        for result in results:
            if result['status'] == 'completed':
                print(f"  ✓ 镜头 {result['shot_index']+1}: {result.get('duration', 0):.2f}s")
            else:
                print(f"  ✗ 镜头 {result['shot_index']+1}: {result.get('error', '未知错误')}")
        
        return success > 0

def test_audio_merge(task_id):
    """测试音视频合并"""
    from backend.app.services.audio_service import AudioService
    
    app = create_app()
    with app.app_context():
        audio_service = AudioService(output_dir='backend/output_tasks')
        
        print("\n🎬 开始合并音视频...")
        try:
            output_path = audio_service.merge_audio_with_video(task_id)
            print(f"✓ 合并成功：{output_path}")
            
            # 检查文件是否存在
            if os.path.exists(output_path):
                size = os.path.getsize(output_path) / 1024 / 1024  # MB
                print(f"✓ 文件大小：{size:.2f} MB")
                
                # 检查是否有音频轨道
                cmd = ['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type', 
                       '-of', 'default=noprint_wrappers=1', output_path]
                result = subprocess.run(cmd, capture_output=True, text=True)
                streams = result.stdout.strip().split('\n')
                has_audio = 'audio' in streams
                print(f"{'✓' if has_audio else '✗'} {'包含音频轨道' if has_audio else '缺少音频轨道'}")
                
                return True
            else:
                print(f"✗ 输出文件不存在：{output_path}")
                return False
                
        except Exception as e:
            print(f"✗ 合并失败：{e}")
            return False

def test_audio_api(task_id):
    """测试配音 API 接口"""
    import requests
    
    print("\n📡 测试 API 接口...")
    
    # 测试获取配音列表
    try:
        response = requests.get(f'http://localhost:5001/api/v1/audios/{task_id}')
        if response.status_code == 200:
            data = response.json()
            audios = data.get('audios', [])
            print(f"✓ API 获取配音列表：{len(audios)} 个")
            for audio in audios:
                print(f"  - 镜头 {audio['shot_index']+1}: {audio['status']} 时长={audio.get('duration', 0):.2f}s")
        else:
            print(f"✗ API 请求失败：{response.status_code}")
    except Exception as e:
        print(f"✗ API 测试失败：{e}")

def main():
    print("=" * 60)
    print("🎙️ 配音功能测试")
    print("=" * 60)
    
    # Step 1: 创建测试任务
    print("\n📝 Step 1: 创建测试任务")
    task_id, script_id, shots = create_test_task()
    
    # Step 2: 创建测试视频
    print("\n🎬 Step 2: 创建测试视频")
    create_test_videos(task_id, shots)
    
    # Step 3: 生成配音
    print("\n🎙️ Step 3: 生成配音")
    has_audio = test_audio_generation(task_id, shots)
    
    if not has_audio:
        print("\n✗ 配音生成失败，终止测试")
        return
    
    # Step 4: 测试 API
    print("\n📡 Step 4: 测试 API")
    test_audio_api(task_id)
    
    # Step 5: 合并音视频
    print("\n🎬 Step 5: 合并音视频")
    merge_success = test_audio_merge(task_id)
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    print(f"任务 ID: {task_id}")
    print(f"分镜数：{len(shots)}")
    print(f"配音生成：{'✓ 成功' if has_audio else '✗ 失败'}")
    print(f"音视频合并：{'✓ 成功' if merge_success else '✗ 失败'}")
    print("=" * 60)

if __name__ == '__main__':
    main()
