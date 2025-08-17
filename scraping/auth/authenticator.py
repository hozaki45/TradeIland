"""Trade Island認証モジュール"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Optional, Any

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from ..config.logger import get_logger
from ..config.settings import settings

logger = get_logger(__name__)


class TradeIslandAuthenticator:
    """Trade Island認証クラス"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.session_file = Path("scraping/session/cookies.json")
        self.session_file.parent.mkdir(exist_ok=True)
        
    async def __aenter__(self):
        """非同期コンテキストマネージャ開始"""
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャ終了"""
        await self.close_browser()
    
    async def start_browser(self) -> None:
        """ブラウザ起動"""
        try:
            playwright = await async_playwright().start()
            
            self.browser = await playwright.chromium.launch(
                headless=settings.scraping.browser.headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            # ユーザーエージェント設定
            self.context = await self.browser.new_context(
                user_agent=settings.scraping.browser.user_agent,
                viewport={
                    'width': settings.scraping.browser.viewport_width,
                    'height': settings.scraping.browser.viewport_height
                },
                ignore_https_errors=True
            )
            
            # 既存セッションがあれば復元
            await self._load_session()
            
            self.page = await self.context.new_page()
            
            logger.info("ブラウザを起動しました")
            
        except Exception as e:
            logger.error("ブラウザ起動に失敗", error=str(e))
            raise
    
    async def close_browser(self) -> None:
        """ブラウザ終了"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("ブラウザを終了しました")
        except Exception as e:
            logger.error("ブラウザ終了時にエラー", error=str(e))
    
    async def login(self, email: str, password: str) -> bool:
        """ログイン実行"""
        try:
            # ログインページにアクセス
            await self.page.goto(settings.target_site.login_url)
            logger.info("ログインページにアクセス", url=settings.target_site.login_url)
            
            # ページ読み込み待機
            await self.page.wait_for_load_state('networkidle')
            
            # ログイン済みかチェック
            if await self._is_logged_in():
                logger.info("既にログイン済みです")
                return True
            
            # メールアドレス入力欄を探して入力
            email_selectors = [
                'input[type="email"]',
                'input[name*="email"]',
                'input[name*="mail"]',
                'input[id*="email"]',
                'input[id*="mail"]',
                'input[placeholder*="メール"]',
                'input[placeholder*="email"]'
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = await self.page.wait_for_selector(selector, timeout=2000)
                    if email_input:
                        break
                except:
                    continue
            
            if not email_input:
                logger.error("メールアドレス入力欄が見つかりません")
                return False
            
            await email_input.fill(email)
            logger.info("メールアドレスを入力")
            
            # パスワード入力欄を探して入力
            password_selectors = [
                'input[type="password"]',
                'input[name*="password"]',
                'input[name*="pass"]',
                'input[id*="password"]',
                'input[id*="pass"]',
                'input[placeholder*="パスワード"]',
                'input[placeholder*="password"]'
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = await self.page.wait_for_selector(selector, timeout=2000)
                    if password_input:
                        break
                except:
                    continue
            
            if not password_input:
                logger.error("パスワード入力欄が見つかりません")
                return False
            
            await password_input.fill(password)
            logger.info("パスワードを入力")
            
            # ログインボタンを探してクリック
            login_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("ログイン")',
                'button:has-text("login")',
                'input[value*="ログイン"]',
                'input[value*="login"]',
                '[class*="login"] button',
                '[class*="signin"] button'
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = await self.page.wait_for_selector(selector, timeout=2000)
                    if login_button:
                        break
                except:
                    continue
            
            if not login_button:
                logger.error("ログインボタンが見つかりません")
                return False
            
            # ログインボタンクリック
            await login_button.click()
            logger.info("ログインボタンをクリック")
            
            # ページ遷移待機
            await self.page.wait_for_load_state('networkidle')
            
            # ログイン成功チェック
            if await self._is_logged_in():
                logger.info("ログインに成功しました")
                await self._save_session()
                return True
            else:
                logger.error("ログインに失敗しました")
                return False
                
        except Exception as e:
            logger.error("ログイン処理でエラー", error=str(e))
            return False
    
    async def _is_logged_in(self) -> bool:
        """ログイン状態確認"""
        try:
            # URLベースでの判定
            current_url = self.page.url
            if "/login" not in current_url and settings.target_site.base_url in current_url:
                return True
            
            # ログイン後に表示される要素の確認
            login_indicators = [
                '[href*="logout"]',
                '[class*="user"]',
                '[class*="profile"]',
                'text="ユーザー検索"',
                'text="マイページ"'
            ]
            
            for indicator in login_indicators:
                try:
                    element = await self.page.wait_for_selector(indicator, timeout=2000)
                    if element:
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error("ログイン状態確認でエラー", error=str(e))
            return False
    
    async def _save_session(self) -> None:
        """セッション保存"""
        try:
            cookies = await self.context.cookies()
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            logger.info("セッションを保存しました", file=str(self.session_file))
        except Exception as e:
            logger.error("セッション保存でエラー", error=str(e))
    
    async def _load_session(self) -> None:
        """セッション復元"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                await self.context.add_cookies(cookies)
                logger.info("セッションを復元しました", file=str(self.session_file))
        except Exception as e:
            logger.error("セッション復元でエラー", error=str(e))
    
    async def navigate_to_user_search(self) -> bool:
        """ユーザー検索タブに移動"""
        try:
            # ユーザー検索タブを探してクリック
            search_selectors = [
                'text="ユーザー検索"',
                '[href*="user"]',
                '[href*="search"]',
                'a:has-text("ユーザー検索")',
                'button:has-text("ユーザー検索")'
            ]
            
            for selector in search_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=5000)
                    if element:
                        await element.click()
                        await self.page.wait_for_load_state('networkidle')
                        logger.info("ユーザー検索タブに移動しました")
                        return True
                except:
                    continue
            
            logger.error("ユーザー検索タブが見つかりません")
            return False
            
        except Exception as e:
            logger.error("ユーザー検索タブ移動でエラー", error=str(e))
            return False
    
    async def search_user_by_nickname(self, nickname: str) -> bool:
        """ニックネームでユーザー検索"""
        try:
            # 検索入力欄を探して入力
            search_selectors = [
                'input[placeholder*="ニックネーム"]',
                'input[placeholder*="nickname"]',
                'input[name*="nickname"]',
                'input[name*="search"]',
                'input[type="search"]',
                'input[class*="search"]'
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    search_input = await self.page.wait_for_selector(selector, timeout=3000)
                    if search_input:
                        break
                except:
                    continue
            
            if not search_input:
                logger.error("検索入力欄が見つかりません")
                return False
            
            await search_input.fill(nickname)
            logger.info("ニックネームを入力", nickname=nickname)
            
            # 検索ボタンクリックまたはEnterキー
            search_button_selectors = [
                'button:has-text("検索")',
                'button[type="submit"]',
                'input[type="submit"]'
            ]
            
            search_button = None
            for selector in search_button_selectors:
                try:
                    search_button = await self.page.wait_for_selector(selector, timeout=2000)
                    if search_button:
                        break
                except:
                    continue
            
            if search_button:
                await search_button.click()
            else:
                # ボタンが見つからない場合はEnterキー
                await search_input.press('Enter')
            
            # 検索結果待機
            await self.page.wait_for_load_state('networkidle')
            logger.info("ユーザー検索を実行しました")
            
            return True
            
        except Exception as e:
            logger.error("ユーザー検索でエラー", error=str(e))
            return False
    
    async def click_user_profile(self, nickname: str) -> bool:
        """ユーザープロフィールページに移動"""
        try:
            # ユーザー名のリンクを探してクリック
            user_selectors = [
                f'a:has-text("{nickname}")',
                f'[href*="{nickname}"]',
                f'text="{nickname}"',
                '.user-item a',
                '.search-result a'
            ]
            
            for selector in user_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        await element.click()
                        await self.page.wait_for_load_state('networkidle')
                        logger.info("ユーザープロフィールに移動", nickname=nickname)
                        return True
                except:
                    continue
            
            logger.error("ユーザープロフィールリンクが見つかりません", nickname=nickname)
            return False
            
        except Exception as e:
            logger.error("ユーザープロフィール移動でエラー", error=str(e))
            return False
    
    def get_page(self) -> Page:
        """現在のページオブジェクトを取得"""
        return self.page