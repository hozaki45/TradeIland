"""セッション管理モジュール"""

import json
import time
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

from ..config.logger import get_logger
from ..config.settings import settings

logger = get_logger(__name__)


class SessionManager:
    """セッション管理クラス"""
    
    def __init__(self):
        self.session_dir = Path("scraping/session")
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.cookies_file = self.session_dir / "cookies.json"
        self.session_info_file = self.session_dir / "session_info.json"
        
    def save_session(self, cookies: list, user_info: Optional[Dict] = None) -> None:
        """セッション情報を保存"""
        try:
            # クッキー保存
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            
            # セッション情報保存
            session_info = {
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=settings.auth.session_timeout)).isoformat(),
                'user_info': user_info or {},
                'last_activity': datetime.now().isoformat()
            }
            
            with open(self.session_info_file, 'w', encoding='utf-8') as f:
                json.dump(session_info, f, ensure_ascii=False, indent=2)
            
            logger.info("セッション情報を保存しました")
            
        except Exception as e:
            logger.error("セッション保存でエラー", error=str(e))
            raise
    
    def load_session(self) -> Optional[Dict[str, Any]]:
        """セッション情報を読み込み"""
        try:
            if not self.is_session_valid():
                return None
            
            cookies = []
            session_info = {}
            
            # クッキー読み込み
            if self.cookies_file.exists():
                with open(self.cookies_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
            
            # セッション情報読み込み
            if self.session_info_file.exists():
                with open(self.session_info_file, 'r', encoding='utf-8') as f:
                    session_info = json.load(f)
            
            logger.info("セッション情報を読み込みました")
            
            return {
                'cookies': cookies,
                'session_info': session_info
            }
            
        except Exception as e:
            logger.error("セッション読み込みでエラー", error=str(e))
            return None
    
    def is_session_valid(self) -> bool:
        """セッションの有効性確認"""
        try:
            if not self.session_info_file.exists():
                return False
            
            with open(self.session_info_file, 'r', encoding='utf-8') as f:
                session_info = json.load(f)
            
            expires_at = datetime.fromisoformat(session_info.get('expires_at', ''))
            
            if datetime.now() > expires_at:
                logger.info("セッションが期限切れです")
                return False
            
            return True
            
        except Exception as e:
            logger.error("セッション有効性確認でエラー", error=str(e))
            return False
    
    def update_last_activity(self) -> None:
        """最終活動時刻を更新"""
        try:
            if not self.session_info_file.exists():
                return
            
            with open(self.session_info_file, 'r', encoding='utf-8') as f:
                session_info = json.load(f)
            
            session_info['last_activity'] = datetime.now().isoformat()
            
            with open(self.session_info_file, 'w', encoding='utf-8') as f:
                json.dump(session_info, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error("最終活動時刻更新でエラー", error=str(e))
    
    def clear_session(self) -> None:
        """セッション情報をクリア"""
        try:
            if self.cookies_file.exists():
                self.cookies_file.unlink()
            
            if self.session_info_file.exists():
                self.session_info_file.unlink()
            
            logger.info("セッション情報をクリアしました")
            
        except Exception as e:
            logger.error("セッションクリアでエラー", error=str(e))
    
    def get_session_status(self) -> Dict[str, Any]:
        """セッション状態を取得"""
        try:
            if not self.is_session_valid():
                return {
                    'is_valid': False,
                    'status': 'expired_or_missing'
                }
            
            with open(self.session_info_file, 'r', encoding='utf-8') as f:
                session_info = json.load(f)
            
            created_at = datetime.fromisoformat(session_info.get('created_at', ''))
            expires_at = datetime.fromisoformat(session_info.get('expires_at', ''))
            last_activity = datetime.fromisoformat(session_info.get('last_activity', ''))
            
            now = datetime.now()
            remaining_time = (expires_at - now).total_seconds()
            
            return {
                'is_valid': True,
                'status': 'active',
                'created_at': created_at.isoformat(),
                'expires_at': expires_at.isoformat(),
                'last_activity': last_activity.isoformat(),
                'remaining_seconds': max(0, remaining_time),
                'user_info': session_info.get('user_info', {})
            }
            
        except Exception as e:
            logger.error("セッション状態取得でエラー", error=str(e))
            return {
                'is_valid': False,
                'status': 'error',
                'error': str(e)
            }