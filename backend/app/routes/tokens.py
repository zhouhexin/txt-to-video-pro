from flask import Blueprint, request, jsonify
from app.services.token_service import TokenService

tokens_bp = Blueprint('tokens', __name__)


@tokens_bp.route('/tokens/overview', methods=['GET'])
def get_overview():
    """获取 Token 使用概览"""
    try:
        service = TokenService()
        stats = service.get_overview()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tokens_bp.route('/tokens/daily', methods=['GET'])
def get_daily_stats():
    """获取每日 Token 使用统计"""
    try:
        days = request.args.get('days', 7, type=int)
        service = TokenService()
        stats = service.get_daily_stats(days)
        return jsonify({'stats': stats, 'days': days})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tokens_bp.route('/tokens/by-model', methods=['GET'])
def get_by_model_stats():
    """按模型类型获取统计"""
    try:
        service = TokenService()
        stats = service.get_by_model_stats()
        return jsonify({'stats': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tokens_bp.route('/tokens/records', methods=['GET'])
def get_records():
    """获取 Token 使用记录列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        model_type = request.args.get('model_type')
        task_id = request.args.get('task_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        service = TokenService()
        result = service.get_records(
            page=page,
            per_page=per_page,
            model_type=model_type,
            task_id=task_id,
            start_date=start_date,
            end_date=end_date
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tokens_bp.route('/tokens/records/<int:record_id>', methods=['GET'])
def get_record_detail(record_id):
    """获取单条记录详情"""
    try:
        service = TokenService()
        record = service.get_record_detail(record_id)
        if record:
            return jsonify(record)
        return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500