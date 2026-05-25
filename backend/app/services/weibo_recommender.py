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
    
    # 低权重词（通用词、泛义词）
    LOW_WEIGHT_WORDS = {'打卡', '白天', '周末', '拍照', '推荐', '热门', '最美', '必去'}
    
    def __init__(self, api_url: str = 'http://212.64.14.158:5001'):
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
            }
        """
        try:
            # 调用 social-hotspot-monitor API
            response = requests.get(
                f'{self.api_url}/api/v1/hotspot/search',
                params={
                    'keyword': theme,
                    'limit': 10
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    topics = data.get('data', {}).get('topics', [])
                    keywords = []
                    seen = set()  # 去重
                    
                    for topic in topics:
                        # keywords 是空格分隔的字符串："古风 唐代 夜景"
                        topic_keywords = topic.get('keywords', '')
                        for kw in topic_keywords.split(' '):
                            kw = kw.strip()
                            if not kw or kw in seen:
                                continue
                            
                            seen.add(kw)
                            # 低权重词降低分数
                            score = 60 if kw in self.LOW_WEIGHT_WORDS else 90
                            keywords.append({'word': kw, 'hot_score': score})
                    
                    # 按权重排序，最多7个
                    keywords = sorted(keywords, key=lambda x: x['hot_score'], reverse=True)[:7]
                    
                    if keywords:
                        return {
                            'keywords': keywords,
                            'theme': theme,
                            'video_type': video_type
                        }
            
            # API 调用失败或没有关键词，返回预定义关键词
            return self._fallback_recommend(theme, video_type)
        
        except requests.exceptions.RequestException as e:
            print(f"⚠️ 热点服务调用失败：{e}")
            # 降级方案：返回预定义关键词
            return self._fallback_recommend(theme, video_type)
    
    def _fallback_recommend(self, theme: str, video_type: str) -> Dict:
        """降级方案：预定义关键词"""
        fallback_keywords = {
            '文旅宣传': [
                {'word': '攻略', 'hot_score': 95},
                {'word': '夜爬', 'hot_score': 90},
                {'word': '日出', 'hot_score': 85},
                {'word': '云海', 'hot_score': 80},
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
            'theme': theme,
            'video_type': video_type,
            'fallback': True  # 标记使用了降级方案
        }
