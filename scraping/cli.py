"""CLIメインモジュール"""

import asyncio
import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from .config.logger import get_logger
from .config.settings import settings
from .auth.authenticator import TradeIslandAuthenticator
from .auth.session_manager import SessionManager

logger = get_logger(__name__)


@click.group()
@click.option('--debug', is_flag=True, help='デバッグモードで実行')
def cli(debug):
    """Trade Island スクレイピングツール"""
    if debug:
        os.environ['LOG_LEVEL'] = 'DEBUG'
        logger.info("デバッグモードで実行中")


@cli.command()
@click.option('--email', prompt='メールアドレス', help='ログイン用メールアドレス')
@click.option('--password', prompt='パスワード', hide_input=True, help='ログイン用パスワード')
def login(email, password):
    """ログインテスト"""
    async def _login():
        async with TradeIslandAuthenticator() as auth:
            success = await auth.login(email, password)
            if success:
                click.echo("✅ ログインに成功しました")
                
                # ユーザー検索タブに移動テスト
                if await auth.navigate_to_user_search():
                    click.echo("✅ ユーザー検索タブに移動しました")
                else:
                    click.echo("❌ ユーザー検索タブに移動できませんでした")
            else:
                click.echo("❌ ログインに失敗しました")
    
    asyncio.run(_login())


@cli.command()
@click.option('--email', prompt='メールアドレス', help='ログイン用メールアドレス')
@click.option('--password', prompt='パスワード', hide_input=True, help='ログイン用パスワード')
@click.option('--nickname', prompt='ニックネーム', help='検索するユーザーのニックネーム')
def search_user(email, password, nickname):
    """ユーザー検索テスト"""
    async def _search_user():
        async with TradeIslandAuthenticator() as auth:
            # ログイン
            if not await auth.login(email, password):
                click.echo("❌ ログインに失敗しました")
                return
            
            click.echo("✅ ログインに成功しました")
            
            # ユーザー検索タブに移動
            if not await auth.navigate_to_user_search():
                click.echo("❌ ユーザー検索タブに移動できませんでした")
                return
            
            click.echo("✅ ユーザー検索タブに移動しました")
            
            # ユーザー検索
            if await auth.search_user_by_nickname(nickname):
                click.echo(f"✅ ユーザー '{nickname}' を検索しました")
                
                # ユーザープロフィールに移動
                if await auth.click_user_profile(nickname):
                    click.echo(f"✅ ユーザー '{nickname}' のプロフィールに移動しました")
                else:
                    click.echo(f"❌ ユーザー '{nickname}' のプロフィールに移動できませんでした")
            else:
                click.echo(f"❌ ユーザー '{nickname}' の検索に失敗しました")
    
    asyncio.run(_search_user())


@cli.command()
def session_status():
    """セッション状態確認"""
    session_manager = SessionManager()
    status = session_manager.get_session_status()
    
    if status['is_valid']:
        click.echo("✅ セッションは有効です")
        click.echo(f"作成日時: {status['created_at']}")
        click.echo(f"有効期限: {status['expires_at']}")
        click.echo(f"最終活動: {status['last_activity']}")
        click.echo(f"残り時間: {status['remaining_seconds']:.0f}秒")
    else:
        click.echo(f"❌ セッションは無効です: {status['status']}")


@cli.command()
def clear_session():
    """セッション情報をクリア"""
    session_manager = SessionManager()
    session_manager.clear_session()
    click.echo("✅ セッション情報をクリアしました")


@cli.command()
def test_browser():
    """ブラウザ起動テスト"""
    async def _test_browser():
        try:
            async with TradeIslandAuthenticator() as auth:
                page = auth.get_page()
                await page.goto("https://www.trade-island.jp/")
                title = await page.title()
                click.echo(f"✅ ブラウザテスト成功: {title}")
        except Exception as e:
            click.echo(f"❌ ブラウザテスト失敗: {e}")
    
    asyncio.run(_test_browser())


@cli.command()
def config():
    """設定情報表示"""
    click.echo("=== Trade Island スクレイピング設定 ===")
    click.echo(f"ベースURL: {settings.target_site.base_url}")
    click.echo(f"ログインURL: {settings.target_site.login_url}")
    click.echo(f"ログレベル: {settings.logging.level}")
    click.echo(f"ヘッドレスモード: {settings.scraping.browser.headless}")
    click.echo(f"リクエスト間隔: {settings.scraping.request_delay}秒")
    click.echo(f"出力ディレクトリ: {settings.export.output_dir}")


def main():
    """メイン関数"""
    # 環境変数を読み込み
    load_dotenv()
    
    # 設定ファイルの存在チェック
    config_file = Path("scraping/config/settings.yaml")
    if not config_file.exists():
        click.echo("❌ 設定ファイルが見つかりません: scraping/config/settings.yaml")
        sys.exit(1)
    
    # .envファイルの存在チェック
    env_file = Path("scraping/.env")
    if not env_file.exists():
        click.echo("⚠️  .envファイルが見つかりません。.env.templateをコピーして.envファイルを作成してください。")
    
    cli()


if __name__ == '__main__':
    main()