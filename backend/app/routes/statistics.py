from flask import Blueprint, request, jsonify, current_app
from app.services import StatisticsService

statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/statistics/overview', methods=['GET'])
def get_overview():
    """获取概览统计"""
    try:
        service = StatisticsService()
        stats = service.get_overview()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@statistics_bp.route('/statistics/daily', methods=['GET'])
def get_daily_stats():
    """获取每日统计"""
    try:
        days = request.args.get('days', 7, type=int)
        service = StatisticsService()
        stats = service.get_daily_stats(days)
        return jsonify({'stats': stats, 'days': days})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@statistics_bp.route('/statistics/usage', methods=['GET'])
def get_usage_stats():
    """获取用量统计"""
    try:
        service = StatisticsService()
        stats = service.get_usage_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
