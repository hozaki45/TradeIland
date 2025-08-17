# 開発環境セットアップガイド

## 前提条件

- Python 3.10以上
- Git
- uvパッケージマネージャー

## 初期セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/[username]/TradeIland.git
cd TradeIland
```

### 2. 仮想環境の構築

```bash
cd tradeiland-analysis
uv sync
```

### 3. 依存関係の確認

```bash
uv run python -c "import pandas, numpy, matplotlib; print('Dependencies OK')"
```

## 開発ワークフロー

### 1. 新機能開発

```bash
# 新しいブランチを作成
git checkout -b feature/new-analysis

# 開発
uv run python main.py

# テスト実行（将来的）
uv run pytest

# コミット
git add .
git commit -m "Add new analysis feature"
git push origin feature/new-analysis
```

### 2. データ分析ワークフロー

```bash
# データ構造の確認
uv run python explore_excel.py

# 詳細分析
uv run python detailed_analysis.py

# 日次カレンダー作成
uv run python create_daily_calendar.py
```

## ディレクトリ構造

```
tradeiland-analysis/
├── main.py                    # メインエントリーポイント
├── explore_excel.py           # データ構造探索
├── detailed_analysis.py       # 詳細分析
├── create_daily_calendar.py   # カレンダー作成
├── investigate_daily_data.py  # データ調査
├── pyproject.toml            # プロジェクト設定
└── uv.lock                   # 依存関係ロック
```

## コーディング規約

### 1. ファイル命名
- スクリプト: `snake_case.py`
- 関数: `snake_case()`
- クラス: `PascalCase`
- 定数: `UPPER_CASE`

### 2. コメント
- 日本語コメント推奨（プロジェクトの性質上）
- docstring は日本語で記述
- 複雑な処理には詳細な説明を追加

### 3. インポート順序
```python
# 標準ライブラリ
import os
from pathlib import Path

# サードパーティ
import pandas as pd
import numpy as np

# ローカル
from .utils import helper_function
```

## トラブルシューティング

### 1. uv 関連
```bash
# uvが見つからない場合
pip install uv

# 依存関係の再インストール
uv sync --reinstall
```

### 2. Excel読み込みエラー
```bash
# openpyxlの再インストール
uv add openpyxl
```

### 3. 日本語文字化け
```python
# pandasでの文字化け対策
pd.read_excel(file_path, encoding='utf-8')
```

## 開発ツール推奨設定

### VS Code 拡張機能
- Python
- Pylance
- Python Docstring Generator
- GitLens

### VS Code 設定
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true
}
```

## データファイル管理

### 1. データファイルの配置
```
data/
├── TradeIland.xlsx              # 元データ（Git管理対象外）
├── TradeIland_Daily_Calendar.xlsx
└── sample/                      # サンプルデータ（Git管理対象）
```

### 2. 大容量ファイルの取り扱い
- Git LFS の使用を検討
- データファイルは .gitignore に追加
- サンプルデータのみバージョン管理

---

*更新日: 2025-08-17*