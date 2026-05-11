#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博热点关键词推荐服务
通过 HTTP 调用 social-hotspot-monitor 服务
"""

import requests
from typing import Dict, List


class WeiboKeywordRecommender:
    """微博热点关键词推荐器"""
    
    def __init__(self, api_url: str = 'http://localhost:5001'):
        self.api_url = api_url
        self.timeout = 5  # 5 秒超时
    
    def recommend(self, theme: str, video_type: str = '文旅宣传') -> Dict:
        """
        推荐热点关键词
        
        Args:
            theme: 主题（如"华山"）
            video_type: 视频类型（如"文旅宣传"）
        
        Returns:
            {
                "keywords": [{"word": "夜爬", "hot_score": 95}, ...],
                "hot_topics": ["热门话题 1", ...]
            }
        """
        try:
            # 调用 social-hotspot-monitor API
            response = requests.get(
                f'{self.api_url}/api/v1/hotspot/topics/by-type',
                params={
                    'video_type': video_type,
                    'limit': 10
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    topics = data.get('data', {}).get('topics', [])
                    # 转换为关键词格式
                    keywords = self._format_topics(topics)
                    hot_topics = self._generate_hot_topics(theme, video_type)
                    
                    return {
                        'keywords': keywords,
                        'hot_topics': hot_topics,
                        'theme': theme,
                        'video_type': video_type
                    }
            
            # API 调用失败，返回预定义关键词
            return self._fallback_recommend(theme, video_type)
        
        except requests.exceptions.RequestException as e:
            print(f"⚠️ 热点服务调用失败：{e}")
            # 降级方案：返回预定义关键词
            return self._fallback_recommend(theme, video_type)
    
    def _format_topics(self, topics: List[str]) -> List[Dict]:
        """格式化话题列表为关键词格式"""
        return [
            {'word': topic, 'hot_score': max(100 - i * 10, 50)}
            for i, topic in enumerate(topics[:10])
        ]
    
    def _generate_hot_topics(self, theme: str, video_type: str) -> List[str]:
        """生成热门话题"""
        return [
            f'{theme}旅游攻略',
            f'{theme}必去景点',
            '周末去哪儿玩'
        ]
    
    def _fallback_recommend(self, theme: str, video_type: str) -> Dict:
        """降级方案：预定义关键词"""
        fallback_keywords = {
            '文旅宣传': [
                {'word': '打卡', 'hot_score': 95},
                {'word': '攻略', 'hot_score': 90},
                {'word': '必去', 'hot_score': 85},
                {'word': '拍照', 'hot_score': 80},
                {'word': '周末', 'hot_score': 75},
            ],
            '历史故事': [
                {'word': '文物', 'hot_score': 95},
                {'word': '古代', 'hot_score': 90},
                {'word': '历史', 'hot_score': 85},
                {'word': '文化', 'hot_score': 80},
            ],
        }
        
        keywords = fallback_keywords.get(video_type, fallback_keywords['文旅宣传'])
        
        return {
            'keywords': keywords,
            'hot_topics': [f'{theme}旅游攻略', f'{theme}必去景点'],
            'theme': theme,
            'video_type': video_type,
            'fallback': True  # 标记使用了降级方案
        }


# 测试
if __name__ == '__main__':
    recommender = WeiboKeywordRecommender()
    
    print("测试微博关键词推荐...")
    result = recommender.recommend('华山', '文旅宣传')
    
    print(f"\n主题：{result['theme']}")
    print("推荐关键词:")
    for kw in result['keywords'][:5]:
        print(f"  • {kw['word']} ({kw['hot_score']})")
    
    print("热门话题:")
    for topic in result['hot_topics'][:3]:
        print(f"  • {topic}")
