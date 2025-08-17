"""設定管理モジュール"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field
from dotenv import load_dotenv


class AuthSettings(BaseModel):
    """認証設定"""
    username: str = Field(default="", description="ログインユーザー名")
    password: str = Field(default="", description="ログインパスワード")
    session_timeout: int = Field(default=3600, description="セッションタイムアウト（秒）")


class BrowserSettings(BaseModel):
    """ブラウザ設定"""
    headless: bool = Field(default=True, description="ヘッドレスモード")
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        description="ユーザーエージェント"
    )
    viewport_width: int = Field(default=1920, description="ビューポート幅")
    viewport_height: int = Field(default=1080, description="ビューポート高さ")


class ScrapingSettings(BaseModel):
    """スクレイピング設定"""
    request_delay: float = Field(default=1.0, description="リクエスト間隔（秒）")
    request_timeout: int = Field(default=30, description="リクエストタイムアウト（秒）")
    max_retries: int = Field(default=3, description="最大リトライ回数")
    concurrent_requests: int = Field(default=1, description="並列リクエスト数")
    browser: BrowserSettings = Field(default_factory=BrowserSettings)


class DataProcessingSettings(BaseModel):
    """データ処理設定"""
    remove_duplicates: bool = Field(default=True, description="重複データの除去")
    normalize_dates: bool = Field(default=True, description="日付の正規化")
    validate_data: bool = Field(default=True, description="データ検証")
    fill_missing_values: bool = Field(default=False, description="欠損値の補完")


class ExcelSettings(BaseModel):
    """Excel設定"""
    include_index: bool = Field(default=False, description="インデックスを含める")
    sheet_name: str = Field(default="ScrapedData", description="シート名")


class ExportSettings(BaseModel):
    """エクスポート設定"""
    format: str = Field(default="excel", description="出力フォーマット")
    output_dir: str = Field(default="output", description="出力ディレクトリ")
    filename_template: str = Field(
        default="scraped_data_{date}_{person}.{ext}",
        description="ファイル名テンプレート"
    )
    excel: ExcelSettings = Field(default_factory=ExcelSettings)


class LoggingSettings(BaseModel):
    """ログ設定"""
    level: str = Field(default="INFO", description="ログレベル")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="ログフォーマット"
    )
    file_enabled: bool = Field(default=True, description="ファイル出力有効")
    file_path: str = Field(default="logs/scraping.log", description="ログファイルパス")
    max_file_size: str = Field(default="10MB", description="最大ファイルサイズ")
    backup_count: int = Field(default=5, description="バックアップファイル数")


class TargetSiteSettings(BaseModel):
    """ターゲットサイト設定"""
    base_url: str = Field(default="", description="ベースURL")
    login_url: str = Field(default="", description="ログインURL")
    data_url: str = Field(default="", description="データURL")


class DefaultPeriodSettings(BaseModel):
    """期間設定"""
    days: int = Field(default=30, description="デフォルト取得期間（日数）")
    max_days: int = Field(default=365, description="最大取得期間（日数）")


class Settings(BaseModel):
    """メイン設定クラス"""
    target_site: TargetSiteSettings = Field(default_factory=TargetSiteSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    scraping: ScrapingSettings = Field(default_factory=ScrapingSettings)
    data_processing: DataProcessingSettings = Field(default_factory=DataProcessingSettings)
    export: ExportSettings = Field(default_factory=ExportSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    default_period: DefaultPeriodSettings = Field(default_factory=DefaultPeriodSettings)

    @classmethod
    def load_from_file(cls, config_path: Optional[Path] = None) -> "Settings":
        """設定ファイルから読み込み"""
        if config_path is None:
            config_path = Path(__file__).parent / "settings.yaml"
        
        # 環境変数を読み込み
        load_dotenv()
        
        # YAML設定ファイルを読み込み
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
        else:
            config_data = {}
        
        # 環境変数で上書き
        cls._override_with_env_vars(config_data)
        
        return cls(**config_data)
    
    @staticmethod
    def _override_with_env_vars(config: Dict[str, Any]) -> None:
        """環境変数で設定を上書き"""
        env_mappings = {
            "SCRAPING_USERNAME": ["auth", "username"],
            "SCRAPING_PASSWORD": ["auth", "password"],
            "TARGET_SITE_BASE_URL": ["target_site", "base_url"],
            "TARGET_SITE_LOGIN_URL": ["target_site", "login_url"],
            "TARGET_SITE_DATA_URL": ["target_site", "data_url"],
            "LOG_LEVEL": ["logging", "level"],
            "OUTPUT_DIR": ["export", "output_dir"],
            "BROWSER_HEADLESS": ["scraping", "browser", "headless"],
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # 設定辞書の深い階層にアクセス
                current = config
                for key in config_path[:-1]:
                    current = current.setdefault(key, {})
                
                # 型変換
                if env_var == "BROWSER_HEADLESS":
                    value = value.lower() == "true"
                
                current[config_path[-1]] = value


# グローバル設定インスタンス
settings = Settings.load_from_file()