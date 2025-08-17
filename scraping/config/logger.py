"""ログ設定モジュール"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional

import structlog
from rich.console import Console
from rich.logging import RichHandler

from .settings import settings


class LoggerConfig:
    """ログ設定クラス"""
    
    def __init__(self):
        self.console = Console()
        self._setup_directories()
        self._setup_logging()
    
    def _setup_directories(self) -> None:
        """ログディレクトリの作成"""
        log_dir = Path(settings.logging.file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self) -> None:
        """ログ設定の初期化"""
        # ルートロガーの設定
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.logging.level.upper()))
        
        # 既存のハンドラをクリア
        root_logger.handlers.clear()
        
        # コンソールハンドラ（Rich使用）
        console_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=True,
            markup=True,
            rich_tracebacks=True
        )
        console_handler.setLevel(getattr(logging, settings.logging.level.upper()))
        
        # ファイルハンドラ（ローテーション付き）
        if settings.logging.file_enabled:
            file_handler = self._create_file_handler()
            root_logger.addHandler(file_handler)
        
        root_logger.addHandler(console_handler)
        
        # structlogの設定
        self._setup_structlog()
    
    def _create_file_handler(self) -> logging.handlers.RotatingFileHandler:
        """ローテーションファイルハンドラの作成"""
        # ファイルサイズの変換（例: "10MB" -> 10485760）
        max_bytes = self._parse_file_size(settings.logging.max_file_size)
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=settings.logging.file_path,
            maxBytes=max_bytes,
            backupCount=settings.logging.backup_count,
            encoding="utf-8"
        )
        
        file_handler.setLevel(getattr(logging, settings.logging.level.upper()))
        
        # ファイル用フォーマッター
        file_formatter = logging.Formatter(
            fmt=settings.logging.format,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        
        return file_handler
    
    def _parse_file_size(self, size_str: str) -> int:
        """ファイルサイズ文字列をバイト数に変換"""
        size_str = size_str.upper()
        if size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith("GB"):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def _setup_structlog(self) -> None:
        """structlogの設定"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    def get_logger(self, name: str) -> structlog.BoundLogger:
        """構造化ロガーの取得"""
        return structlog.get_logger(name)


# グローバルロガー設定
logger_config = LoggerConfig()


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """ロガーの取得（便利関数）"""
    if name is None:
        # 呼び出し元のモジュール名を取得
        frame = sys._getframe(1)
        name = frame.f_globals.get("__name__", "unknown")
    
    return logger_config.get_logger(name)


# プロジェクト共通ロガー
logger = get_logger("tradeiland.scraping")