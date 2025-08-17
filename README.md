# TradeIland - トレーディングデータ分析プロジェクト

## 概要

TradeIlandは複数トレーダーの日次損益（P&L）データを分析し、パフォーマンス評価を行うPythonプロジェクトです。

## プロジェクト構造

```
TradeIland/
├── data/                          # データファイル
│   ├── TradeIland.xlsx           # 元データ（複数シート形式）
│   └── TradeIland_*_Calendar.xlsx # 変換後データ
├── tradeiland-analysis/          # 分析スクリプト
│   ├── pyproject.toml            # uv プロジェクト設定
│   └── *.py                      # 分析・変換スクリプト
└── docs/                         # ドキュメント
    ├── memos/                    # 作業メモ
    ├── specifications/           # 仕様書
    ├── analysis/                 # 分析結果
    └── development/              # 開発ノート
```

## 技術スタック

- **言語**: Python 3.10+
- **パッケージ管理**: uv
- **主要ライブラリ**: pandas, numpy, matplotlib, seaborn, openpyxl

## 開発環境セットアップ

```bash
# 依存関係のインストール
cd tradeiland-analysis
uv sync

# 分析実行
uv run python main.py
```

## 機能

- 複数トレーダーの日次P&Lデータ分析
- Excelファイルからの日次カレンダー形式への変換
- パフォーマンス指標の計算（勝率、平均収益等）
- 統計的可視化

## ドキュメント

詳細なドキュメントは `docs/` ディレクトリ内にあります：

- [作業メモ](docs/memos/) - 日々の作業記録とアイデア
- [仕様書](docs/specifications/) - 機能仕様と要件
- [分析結果](docs/analysis/) - データ分析の結果とレポート
- [開発ノート](docs/development/) - 技術的な実装メモ