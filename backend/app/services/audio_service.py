"""
AI 配音服务 - 基于 Edge TTS（免费）
"""
import os
import logging
import asyncio
import edge_tts
from datetime import datetime
from app import db
from app.models import TaskAudio, TaskVideo, TaskBGM, TaskSFX
from .token_service import TokenService

logger = logging.getLogger(__name__)


class AudioService:
    """AI 配音服务 - 基于 Edge TTS（微软免费服务）"""
    
    # Edge TTS 中文音色列表
    VOICES = {
        'xiaoxiao': 'zh-CN-XiaoxiaoNeural - 温柔女声（新闻、有声书）',
        'xiaoyi': 'zh-CN-XiaoyiNeural - 活泼女声（卡通、有声书）',
        'yunjian': 'zh-CN-YunjianNeural - 激情男声（体育、有声书）',
        'yunxi': 'zh-CN-YunxiNeural - 阳光男声（有声书）',
        'yunxia': 'zh-CN-YunxiaNeural - 可爱男声（卡通、有声书）',
        'yunyang': 'zh-CN-YunyangNeural - 专业男声（新闻）',
        'xiaobei': 'zh-CN-liaoning-XiaobeiNeural - 东北话（方言）',
        'xiaoni': 'zh-CN-shaanxi-XiaoniNeural - 陕西话（方言）',
    }
    
    def __init__(self, api_key: str = None, output_dir: str = None):
        """
        初始化 AudioService
        
        Args:
            api_key: 兼容原有接口，Edge TTS 不需要
            output_dir: 输出目录
        """
        self.output_dir = output_dir or './output_tasks'
        logger.info("Edge TTS 服务初始化完成（免费服务）")
    
    def generate_speech(self, task_id: str, shot_index: int, text: str,
                        voice_id: str = 'xiaoxiao', speed: int = 0,
                        volume: int = 50) -> TaskAudio:
        """
        生成单个分镜的配音
        
        Args:
            task_id: 任务 ID
            shot_index: 分镜索引
            text: 配音文本
            voice_id: 音色 ID（简化版，如 'xiaoxiao'）
            speed: 语速（-500~500，Edge TTS 使用 -1.0~1.0）
            volume: 音量（0~100，Edge TTS 使用 -100~100）
            
        Returns:
            TaskAudio 对象
        """
        # 查找或创建记录
        task_audio = TaskAudio.query.filter_by(
            task_id=task_id,
            shot_index=shot_index
        ).first()
        
        if task_audio:
            task_audio.status = 'running'
            task_audio.text = text
            task_audio.voice_id = voice_id
            task_audio.error_message = None
        else:
            task_audio = TaskAudio(
                task_id=task_id,
                shot_index=shot_index,
                text=text,
                voice_id=voice_id,
                status='running'
            )
            db.session.add(task_audio)
        
        db.session.commit()
        
        try:
            # 映射简化版 voice_id 到完整 Edge TTS 音色名
            voice_map = {
                'xiaoxiao': 'zh-CN-XiaoxiaoNeural',
                'xiaoyi': 'zh-CN-XiaoyiNeural',
                'yunjian': 'zh-CN-YunjianNeural',
                'yunxi': 'zh-CN-YunxiNeural',
                'yunxia': 'zh-CN-YunxiaNeural',
                'yunyang': 'zh-CN-YunyangNeural',
                'xiaobei': 'zh-CN-liaoning-XiaobeiNeural',
                'xiaoni': 'zh-CN-shaanxi-XiaoniNeural',
            }
            
            edge_voice = voice_map.get(voice_id, 'zh-CN-XiaoxiaoNeural')
            
            # 转换参数（Edge TTS 格式）
            # speed: -500~500 → rate: -50%~+50%
            rate = f"{int(speed / 10):+d}%" if speed != 0 else None
            # volume: 0~100 → +0dB~-50dB (50 是基准)
            vol = f"{int(volume - 50):+d}dB" if volume != 50 else None
            
            # 生成音频文件
            task_dir = os.path.join(self.output_dir, task_id, 'audios')
            os.makedirs(task_dir, exist_ok=True)
            
            filename = f'shot_{shot_index}_voice.wav'
            file_path = os.path.join(task_dir, filename)
            
            # 使用 Edge TTS 生成
            asyncio.run(self._generate_with_edge_tts(text, edge_voice, rate, vol, file_path))
            
            # 获取音频时长
            duration = self._get_audio_duration(file_path)
            
            # 更新记录
            task_audio.file_path = file_path
            task_audio.duration = duration
            task_audio.status = 'completed'
            db.session.commit()
            
            logger.info(f"配音生成成功：{file_path}, 时长：{duration:.2f}s")
            return task_audio
            
        except Exception as e:
            logger.error(f"配音生成异常：{str(e)}")
            task_audio.status = 'failed'
            task_audio.error_message = str(e)
            db.session.commit()
            raise
    
    async def _generate_with_edge_tts(self, text: str, voice: str, 
                                       rate: str, volume: str, 
                                       output_path: str):
        """使用 Edge TTS 生成音频"""
        try:
            # Edge TTS 参数为 None 时使用默认值
            kwargs = {}
            if rate:
                kwargs['rate'] = rate
            if volume:
                kwargs['volume'] = volume
            
            communicate = edge_tts.Communicate(text, voice, **kwargs)
            await communicate.save(output_path)
            logger.info(f"Edge TTS 生成完成：{output_path}")
        except Exception as e:
            logger.error(f"Edge TTS 生成失败：{e}")
            raise
    
    def _get_audio_duration(self, file_path: str) -> float:
        """使用 ffprobe 获取音频时长"""
        import subprocess
        
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
        return 0.0
    
    def generate_all_speech(self, task_id: str, shots: list, 
                            voice_id: str = 'xiaoxiao') -> list:
        """
        批量生成所有分镜的配音
        
        Args:
            task_id: 任务 ID
            shots: 分镜列表 [{index, text, duration}, ...]
            voice_id: 音色 ID
            
        Returns:
            生成结果列表
        """
        results = []
        
        for shot in shots:
            shot_index = shot.get('index')
            text = shot.get('text')
            
            if not text:
                results.append({
                    'shot_index': shot_index,
                    'status': 'failed',
                    'error': '配音文本为空'
                })
                continue
            
            try:
                task_audio = self.generate_speech(
                    task_id, shot_index, text, voice_id
                )
                results.append({
                    'shot_index': shot_index,
                    'status': 'completed',
                    'audio_id': task_audio.id,
                    'url': f'/api/v1/files/audio/{task_id}/shot_{shot_index}_voice.wav',
                    'duration': task_audio.duration
                })
            except Exception as e:
                results.append({
                    'shot_index': shot_index,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
    
    def merge_audio_with_video(self, task_id: str, 
                                output_filename: str = 'final_with_audio.mp4') -> str:
        """
        将配音、BGM、音效与视频合并
        
        Args:
            task_id: 任务 ID
            output_filename: 输出文件名
            
        Returns:
            合并后的视频路径
        """
        # 获取所有组件
        videos = TaskVideo.query.filter_by(
            task_id=task_id, 
            status='completed'
        ).order_by(TaskVideo.shot_index).all()
        
        audios = TaskAudio.query.filter_by(
            task_id=task_id, 
            status='completed'
        ).order_by(TaskAudio.shot_index).all()
        
        bgms = TaskBGM.query.filter_by(
            task_id=task_id, 
            status='completed'
        ).all()
        
        sfxs = TaskSFX.query.filter_by(
            task_id=task_id, 
            status='completed'
        ).all()
        
        if not videos:
            raise Exception("没有视频片段")
        
        task_dir = os.path.join(self.output_dir, task_id, 'videos')
        output_path = os.path.join(task_dir, output_filename)
        os.makedirs(task_dir, exist_ok=True)
        
        # 如果没有任何音频，直接返回原合并视频
        if not audios and not bgms and not sfxs:
            # 检查是否已有合并视频
            merged_path = os.path.join(task_dir, 'merged_full_video.mp4')
            if os.path.exists(merged_path):
                return merged_path
            else:
                # 调用原视频服务的合并功能
                from .video_service import VideoService
                video_service = VideoService(None, self.output_dir)
                return video_service.merge_videos(task_id)
        
        # ========== 两步合并法 ==========
        # Step 1: 先拼接所有视频片段
        # Step 2: 再拼接所有配音并与视频对齐
        
        # Step 1: 拼接视频
        video_list_file = os.path.join(task_dir, 'video_list.txt')
        with open(video_list_file, 'w') as f:
            for video in videos:
                f.write(f"file '{os.path.abspath(video.file_path)}'\n")
        
        temp_merged_video = os.path.join(task_dir, 'temp_merged_video.mp4')
        cmd_merge_video = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', video_list_file,
            '-c', 'copy',
            temp_merged_video
        ]
        
        logger.info("Step 1: 拼接视频片段...")
        result = subprocess.run(cmd_merge_video, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            logger.error(f"视频拼接失败：{result.stderr}")
            raise Exception(f"视频拼接失败：{result.stderr}")
        
        # Step 2: 拼接所有配音音频
        if audios:
            audio_list_file = os.path.join(task_dir, 'audio_list.txt')
            with open(audio_list_file, 'w') as f:
                for audio in audios:
                    f.write(f"file '{os.path.abspath(audio.file_path)}'\n")
            
            temp_merged_audio = os.path.join(task_dir, 'temp_merged_audio.aac')
            cmd_merge_audio = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', audio_list_file,
                '-c:a', 'aac',
                temp_merged_audio
            ]
            
            logger.info("Step 2: 拼接配音音频...")
            result = subprocess.run(cmd_merge_audio, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                logger.error(f"音频拼接失败：{result.stderr}")
                raise Exception(f"音频拼接失败：{result.stderr}")
        else:
            temp_merged_audio = None
        
        # Step 3: 将配音、BGM、音效与视频合并
        inputs = ['-i', temp_merged_video]
        filter_complex = []
        output_maps = ['-map', '0:v']
        
        audio_input_index = 1
        
        # 添加配音
        if temp_merged_audio and os.path.exists(temp_merged_audio):
            inputs.extend(['-i', temp_merged_audio])
            filter_complex.append(f"[{audio_input_index}:a]volume=1[audio_voice]")
            audio_input_index += 1
        
        # 添加 BGM
        if bgms:
            for i, bgm in enumerate(bgms):
                bgm_input_idx = audio_input_index
                inputs.extend(['-i', bgm.file_path])
                bgm_volume = bgm.volume if hasattr(bgm, 'volume') and bgm.volume else 0.3
                filter_complex.append(f"[{bgm_input_idx}:a]volume={bgm_volume}[audio_bgm_{i}]")
                audio_input_index += 1
            
            # 混合所有 BGM
            if len(bgms) == 1:
                if audios:
                    filter_complex.append("[audio_bgm_0][audio_voice]amix=inputs=2:duration=shortest[audio_out]")
                else:
                    filter_complex.append("[audio_bgm_0]amix=inputs=1:duration=shortest[audio_out]")
            else:
                bgm_mix_inputs = '+'.join([f'audio_bgm_{i}' for i in range(len(bgms))])
                if audios:
                    filter_complex.append(f"[{bgm_mix_inputs}]amix=inputs={len(bgms)}:duration=shortest[audio_bgm_mix]")
                    filter_complex.append("[audio_bgm_mix][audio_voice]amix=inputs=2:duration=shortest[audio_out]")
                else:
                    filter_complex.append(f"[{bgm_mix_inputs}]amix=inputs={len(bgms)}:duration=shortest[audio_out]")
            output_maps.append('[audio_out]')
        elif audios:
            # 仅有配音，无 BGM
            output_maps.append('[audio_voice]')
        
        cmd = ['ffmpeg', '-y'] + inputs
        
        if filter_complex:
            # 修正 filter_complex 格式
            filter_str = ';'.join(filter_complex)
            cmd.extend(['-filter_complex', filter_str])
        
        cmd.extend(output_maps if len(output_maps) > 1 else ['-map', '0:v', '-map', '0:a'])
        cmd.extend(['-c:v', 'copy', '-c:a', 'aac', '-shortest'])
        cmd.append(output_path)
        
        logger.info(f"Step 3: 最终合并，ffmpeg 命令：{' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                logger.error(f"ffmpeg 最终合并失败：{result.stderr}")
                # 如果复杂合并失败，尝试简单合并
                logger.info("尝试简单合并模式...")
                return self._simple_merge_audio_video(task_id, videos, audios, bgms, sfxs, output_path, temp_merged_video)
            
            logger.info(f"音视频合并成功：{output_path}")
            
            # 清理临时文件
            try:
                os.remove(temp_merged_video)
                if temp_merged_audio and os.path.exists(temp_merged_audio):
                    os.remove(temp_merged_audio)
            except:
                pass
            
            return output_path
            
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg 合并超时")
            raise Exception("合并超时")
        except FileNotFoundError:
            logger.error("ffmpeg 未安装")
            raise Exception("ffmpeg 未安装，请安装后重试")
    
    def _simple_merge_audio_video(self, task_id: str, videos: list, audios: list, 
                                   bgms: list, sfxs: list, output_path: str,
                                   temp_merged_video: str) -> str:
        """简单合并模式：仅添加第一个配音或 BGM"""
        inputs = ['-i', temp_merged_video]
        
        if audios and os.path.exists(audios[0].file_path):
            inputs.extend(['-i', audios[0].file_path])
            cmd = ['ffmpeg', '-y'] + inputs + [
                '-map', '0:v', '-map', '1:a',
                '-c:v', 'copy', '-c:a', 'aac', '-shortest',
                output_path
            ]
        elif bgms and os.path.exists(bgms[0].file_path):
            inputs.extend(['-i', bgms[0].file_path])
            cmd = ['ffmpeg', '-y'] + inputs + [
                '-map', '0:v', '-map', '1:a',
                '-c:v', 'copy', '-c:a', 'aac', '-shortest',
                output_path
            ]
        else:
            # 无任何音频，复制原视频
            import shutil
            shutil.copy(temp_merged_video, output_path)
            return output_path
        
        logger.info(f"简单合并：{' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            raise Exception(f"简单合并失败：{result.stderr}")
        
        return output_path
    
    def get_task_audios(self, task_id: str) -> list:
        """获取任务的所有配音"""
        audios = TaskAudio.query.filter_by(task_id=task_id).order_by(TaskAudio.shot_index).all()
        return [audio.to_dict() for audio in audios]
