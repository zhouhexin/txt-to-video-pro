import logging
from datetime import datetime, timedelta
from app import db
from app.models import TokenUsage
from sqlalchemy import func

logger = logging.getLogger(__name__)


class TokenService:
    """Token 使用统计服务"""
    
    @staticmethod
    def record_usage(
        model_type: str,
        input_tokens: int,
        output_tokens: int,
        model_name: str = None,
        task_id: str = None,
        prompt_text: str = None,
        response_text: str = None,
        scene: str = None,
        is_estimated: bool = False
    ) -> TokenUsage:
        """
        记录 Token 使用情况
        
        Args:
            model_type: 模型类型 (script_generate, image_generate, video_generate, prompt_optimize)
            input_tokens: 输入 token 数
            output_tokens: 输出 token 数
            model_name: 模型名称
            task_id: 关联的任务ID
            prompt_text: 发送的提示词
            response_text: 返回的信息
            scene: 调用场景
            is_estimated: 是否为估算值（API未返回精确token信息时为True）
        
        Returns:
            TokenUsage 实例
        """
        try:
            # 截取 response_text 避免过长
            if response_text and len(response_text) > 5000:
                response_text = response_text[:5000] + '...'
            
            token_usage = TokenUsage(
                task_id=task_id,
                model_type=model_type,
                model_name=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                is_estimated=is_estimated,
                prompt_text=prompt_text,
                response_text=response_text,
                scene=scene
            )
            
            db.session.add(token_usage)
            db.session.commit()
            
            est_text = " (估算)" if is_estimated else ""
            logger.info(f"Token usage recorded: {model_type} - {input_tokens + output_tokens} tokens{est_text}")
            return token_usage
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to record token usage: {e}")
            raise
    
    def get_overview(self) -> dict:
        """获取 Token 使用概览"""
        # 总 token 数
        total_result = db.session.query(
            func.sum(TokenUsage.input_tokens).label('total_input'),
            func.sum(TokenUsage.output_tokens).label('total_output'),
            func.sum(TokenUsage.total_tokens).label('total_tokens')
        ).first()
        
        total_input = total_result.total_input or 0
        total_output = total_result.total_output or 0
        total_tokens = total_result.total_tokens or 0
        
        # 今日统计
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        
        today_result = db.session.query(
            func.sum(TokenUsage.total_tokens).label('today_tokens')
        ).filter(TokenUsage.created_at >= today_start).first()
        
        today_tokens = today_result.today_tokens or 0
        
        # 本月统计
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        month_result = db.session.query(
            func.sum(TokenUsage.total_tokens).label('month_tokens')
        ).filter(TokenUsage.created_at >= month_start).first()
        
        month_tokens = month_result.month_tokens or 0
        
        # 按模型类型分组统计
        by_model_result = db.session.query(
            TokenUsage.model_type,
            func.sum(TokenUsage.total_tokens).label('total')
        ).group_by(TokenUsage.model_type).all()
        
        by_model = {row.model_type: row.total for row in by_model_result}
        
        # 计算平均每日消耗（最近30天）
        thirty_days_ago = now - timedelta(days=30)
        total_last_30_days = db.session.query(
            func.sum(TokenUsage.total_tokens)
        ).filter(TokenUsage.created_at >= thirty_days_ago).scalar() or 0
        
        avg_daily = round(total_last_30_days / 30, 2) if total_last_30_days > 0 else 0
        
        return {
            'total_tokens': total_tokens,
            'total_input': total_input,
            'total_output': total_output,
            'today_tokens': today_tokens,
            'month_tokens': month_tokens,
            'avg_daily': avg_daily,
            'by_model': by_model
        }
    
    def get_daily_stats(self, days: int = 7) -> list:
        """获取每日 Token 使用统计"""
        today = datetime.utcnow().date()
        stats = []
        
        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            start_date = datetime.combine(date, datetime.min.time())
            end_date = start_date + timedelta(days=1)
            
            # 查询当天的 token 使用情况
            result = db.session.query(
                func.sum(TokenUsage.input_tokens).label('input'),
                func.sum(TokenUsage.output_tokens).label('output'),
                func.sum(TokenUsage.total_tokens).label('total'),
                func.count(TokenUsage.id).label('count')
            ).filter(
                TokenUsage.created_at >= start_date,
                TokenUsage.created_at < end_date
            ).first()
            
            stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'input_tokens': result.input or 0,
                'output_tokens': result.output or 0,
                'total_tokens': result.total or 0,
                'call_count': result.count or 0
            })
        
        return stats
    
    def get_by_model_stats(self) -> list:
        """按模型类型获取统计"""
        result = db.session.query(
            TokenUsage.model_type,
            TokenUsage.model_name,
            func.sum(TokenUsage.input_tokens).label('total_input'),
            func.sum(TokenUsage.output_tokens).label('total_output'),
            func.sum(TokenUsage.total_tokens).label('total_tokens'),
            func.count(TokenUsage.id).label('call_count')
        ).group_by(TokenUsage.model_type, TokenUsage.model_name).all()
        
        return [{
            'model_type': row.model_type,
            'model_name': row.model_name,
            'total_input': row.total_input,
            'total_output': row.total_output,
            'total_tokens': row.total_tokens,
            'call_count': row.call_count
        } for row in result]
    
    def get_records(
        self,
        page: int = 1,
        per_page: int = 20,
        model_type: str = None,
        task_id: str = None,
        start_date: str = None,
        end_date: str = None
    ) -> dict:
        """获取 Token 使用记录列表"""
        query = TokenUsage.query
        
        # 筛选条件
        if model_type:
            query = query.filter(TokenUsage.model_type == model_type)
        
        if task_id:
            query = query.filter(TokenUsage.task_id == task_id)
        
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(TokenUsage.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(TokenUsage.created_at < end_dt)
        
        # 按时间倒序
        query = query.order_by(TokenUsage.created_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'records': [record.to_dict() for record in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    
    def get_record_detail(self, record_id: int) -> dict:
        """获取单条记录详情（包含完整提示词和返回信息）"""
        record = TokenUsage.query.get(record_id)
        if record:
            return record.to_dict_full()
        return None