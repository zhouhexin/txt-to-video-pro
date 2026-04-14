import logging
from datetime import datetime, timedelta
from app import db
from app.models import Script, Task, TaskImage, TaskVideo
from sqlalchemy import func

logger = logging.getLogger(__name__)


class StatisticsService:
    """统计服务"""
    
    def get_overview(self) -> dict:
        """获取概览统计"""
        # 总剧本数
        total_scripts = Script.query.count()
        
        # 总任务数
        total_tasks = Task.query.count()
        
        # 各状态任务数
        tasks_by_status = db.session.query(
            Task.status, 
            func.count(Task.id)
        ).group_by(Task.status).all()
        
        status_counts = {status: count for status, count in tasks_by_status}
        
        # 总图片数
        total_images = TaskImage.query.count()
        
        # 总视频数
        total_videos = TaskVideo.query.count()
        
        # 成功率
        completed_tasks = status_counts.get('completed', 0) + status_counts.get('waiting_confirm', 0)
        success_rate = round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0
        
        # 平均生成耗时（估算）
        avg_duration = 5  # 默认 5 秒
        
        return {
            'total_scripts': total_scripts,
            'total_tasks': total_tasks,
            'total_images': total_images,
            'total_videos': total_videos,
            'tasks_by_status': status_counts,
            'success_rate': success_rate,
            'avg_duration': avg_duration
        }
    
    def get_daily_stats(self, days: int = 7) -> list:
        """获取每日统计（最近 N 天）"""
        today = datetime.utcnow().date()
        stats = []
        
        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            start_date = datetime.combine(date, datetime.min.time())
            end_date = start_date + timedelta(days=1)
            
            # 查询当天的任务数
            task_count = Task.query.filter(
                Task.created_at >= start_date,
                Task.created_at < end_date
            ).count()
            
            # 查询当天的图片数
            image_count = TaskImage.query.join(Task).filter(
                Task.created_at >= start_date,
                Task.created_at < end_date
            ).count()
            
            # 查询当天的视频数
            video_count = TaskVideo.query.join(Task).filter(
                Task.created_at >= start_date,
                Task.created_at < end_date
            ).count()
            
            stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'tasks': task_count,
                'images': image_count,
                'videos': video_count
            })
        
        return stats
    
    def get_usage_stats(self) -> dict:
        """获取用量统计"""
        # 本月任务数
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        tasks_this_month = Task.query.filter(Task.created_at >= month_start).count()
        images_this_month = TaskImage.query.join(Task).filter(Task.created_at >= month_start).count()
        videos_this_month = TaskVideo.query.join(Task).filter(Task.created_at >= month_start).count()
        
        # 估算 API 调用次数
        api_calls_estimate = tasks_this_month + images_this_month * 2 + videos_this_month * 3
        
        return {
            'tasks_this_month': tasks_this_month,
            'images_this_month': images_this_month,
            'videos_this_month': videos_this_month,
            'api_calls_estimate': api_calls_estimate
        }
