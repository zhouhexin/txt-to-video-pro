"""
背景音乐和音效管理服务
"""
import os
import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class BGMService:
    """背景音乐和音效管理服务"""
    
    def __init__(self, bgm_dir: str):
        self.bgm_dir = bgm_dir
        self.bgm_library = self._load_bgm_library()
        self.sfx_library = self._load_sfx_library()
    
    def _load_bgm_library(self) -> List[Dict]:
        """加载 BGM 库（从 JSON 配置文件）"""
        library_file = os.path.join(self.bgm_dir, 'bgm_library.json')
        
        if os.path.exists(library_file):
            try:
                with open(library_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载 BGM 库失败：{e}")
        
        # 默认 BGM 库（如果配置文件不存在）
        return []
    
    def _load_sfx_library(self) -> List[Dict]:
        """加载音效库"""
        library_file = os.path.join(self.bgm_dir, 'sfx_library.json')
        
        if os.path.exists(library_file):
            try:
                with open(library_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载音效库失败：{e}")
        
        # 默认音效库（如果配置文件不存在）
        return []
    
    def get_bgm_list(self, category: str = None, mood: str = None) -> List[Dict]:
        """获取 BGM 列表（支持筛选）"""
        results = self.bgm_library
        
        if category:
            results = [b for b in results if b.get('category') == category]
        if mood:
            results = [b for b in results if b.get('mood') == mood]
        
        return results
    
    def get_sfx_list(self, category: str = None, tags: List[str] = None) -> List[Dict]:
        """获取音效列表"""
        results = self.sfx_library
        
        if category:
            results = [s for s in results if s.get('category') == category]
        if tags:
            results = [s for s in results if any(tag in s.get('tags', []) for tag in tags)]
        
        return results
    
    def recommend_sfx(self, scene_description: str) -> List[Dict]:
        """根据场景描述推荐音效"""
        # 简单关键词匹配
        keywords = {
            '鸟': ['sfx_001'],
            '水': ['sfx_002'],
            '河': ['sfx_002'],
            '湖': ['sfx_002'],
            '海': ['sfx_007'],
            '风': ['sfx_003'],
            '人': ['sfx_004'],
            '街': ['sfx_004'],
            '城': ['sfx_004'],
            '雨': ['sfx_005'],
            '雷': ['sfx_006'],
            '火': ['sfx_008'],
            '钟': ['sfx_011'],
            '车': ['sfx_012'],
        }
        
        recommended = []
        for keyword, sfx_ids in keywords.items():
            if keyword in scene_description:
                for sfx_id in sfx_ids:
                    sfx = next((s for s in self.sfx_library if s['id'] == sfx_id), None)
                    if sfx and sfx not in recommended:
                        recommended.append(sfx)
        
        return recommended
    
    def get_bgm_file_path(self, bgm_id: str) -> Optional[str]:
        """获取 BGM 文件路径"""
        bgm = next((b for b in self.bgm_library if b['id'] == bgm_id), None)
        if bgm:
            return os.path.join(self.bgm_dir, bgm['file'])
        return None
    
    def get_sfx_file_path(self, sfx_id: str) -> Optional[str]:
        """获取音效文件路径"""
        sfx = next((s for s in self.sfx_library if s['id'] == sfx_id), None)
        if sfx:
            return os.path.join(self.bgm_dir, 'sfx', sfx['file'])
        return None
    
    def get_categories(self) -> Dict[str, List[str]]:
        """获取所有分类"""
        bgm_categories = list(set(b.get('category', '其他') for b in self.bgm_library))
        sfx_categories = list(set(s.get('category', '其他') for s in self.sfx_library))
        
        return {
            'bgm': bgm_categories,
            'sfx': sfx_categories
        }
