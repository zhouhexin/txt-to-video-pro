#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博热点关键词推荐 API
通过 HTTP 调用 social-hotspot-monitor 服务
"""

from flask import Blueprint, request, jsonify
from app.services.weibo_recommender import WeiboKeywordRecommender
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
weibo_bp = Blueprint('weibo', __name__)

# 推荐器实例（单例）
recommender = WeiboKeywordRecommender()


@weibo_bp.route('/api/v1/weibo/recommend', methods=['POST'])
def recommend_keywords():
    """
    推荐微博热点关键词
    
    Request:
    {
        "video_type": "文旅宣传",
        "theme": "华山"
    }
    
    Response:
    {
        "success": true,
        "keywords": [
            {"word": "打卡", "hot_score": 95},
            {"word": "攻略", "hot_score": 90}
        ],
        "source": "social_hotspot_monitor"  # 或 "fallback"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'}), 400
        
        video_type = data.get('video_type', '文旅宣传')
        theme = data.get('theme', '')
        
        if not theme:
            return jsonify({'success': False, 'message': '主题为空'}), 400
        
        logger.info(f"🔍 推荐微博热点关键词：{theme} ({video_type})")
        
        # 推荐关键词
        result = recommender.recommend(theme, video_type)
        
        logger.info(f"✅ 推荐 {len(result['keywords'])} 个关键词")
        
        return jsonify({
            'success': True,
            'keywords': result['keywords'],
            'theme': theme,
            'video_type': video_type,
            'source': 'social_hotspot_monitor' if not result.get('fallback') else 'fallback'
        })
    
    except Exception as e:
        logger.error(f"❌ 推荐失败：{e}")
        return jsonify({
            'success': False,
            'message': f'推荐失败：{str(e)}',
            'keywords': []
        }), 500
