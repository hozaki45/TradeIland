# TradeIland スクレイピング機能

ウェブサイトからのデータ自動取得システム

## 📁 プロジェクト構造

```
scraping/
├── auth/              # 認証モジュール
├── scrapers/          # スクレイピングエンジン  
├── processors/        # データ処理モジュール
├── exporters/         # データエクスポート機能
├── config/            # 設定管理
│   ├── settings.yaml  # メイン設定ファイル
│   ├── settings.py    # 設定管理クラス
│   └── logger.py      # ログ設定
├── tests/             # テストモジュール
├── logs/              # ログファイル出力先
├── .env.template      # 環境変数テンプレート
├── pyproject.toml     # プロジェクト設定
└── README.md          # このファイル
```

## 🚀 セットアップ

### 1. 依存関係のインストール

```bash
cd scraping
uv sync
```

### 2. 環境変数の設定

```bash
cp .env.template .env
# .env ファイルを編集して認証情報等を設定
```

### 3. 設定ファイルの編集

`config/settings.yaml` を編集してターゲットサイトやスクレイピング設定を調整

## ⚙️ 設定項目

### 主要設定

- **target_site**: ターゲットサイトのURL設定
- **auth**: 認証情報（環境変数で上書き推奨）
- **scraping**: スクレイピングの動作設定
- **export**: データ出力設定
- **logging**: ログ設定

### 環境変数

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `SCRAPING_USERNAME` | ログインユーザー名 | `user@example.com` |
| `SCRAPING_PASSWORD` | ログインパスワード | `password123` |
| `TARGET_SITE_BASE_URL` | ターゲットサイトURL | `https://example.com` |
| `LOG_LEVEL` | ログレベル | `INFO` |

## 🛠️ 開発

### テストの実行

```bash
uv run pytest
```

### コード品質チェック

```bash
uv run black .
uv run isort .
uv run flake8 .
uv run mypy .
```

## 📝 使用例

```python
from scraping.config.settings import settings
from scraping.config.logger import get_logger

logger = get_logger(__name__)

# 設定の取得
logger.info("スクレイピング開始", url=settings.target_site.base_url)
```

## 🔧 開発状況

- [x] プロジェクト基盤構築
- [ ] 認証システム実装
- [ ] スクレイピングエンジン実装  
- [ ] データ処理機能実装
- [ ] エクスポート機能実装

## 📋 次のステップ

1. ISSUE #4: 認証システムの実装
2. ISSUE #5: スクレイピングエンジンの実装
3. ISSUE #6: データ処理機能の実装