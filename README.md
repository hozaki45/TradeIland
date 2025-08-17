# TradeIland

## これは何？

トレーダーの売買データを分析するツールです。

## フォルダ構成

```
TradeIland/
├── data/                    # データ
├── tradeiland-analysis/     # 分析プログラム
└── docs/                    # 説明書
```

## 使い方

```bash
cd tradeiland-analysis
uv sync
uv run python main.py
```

## できること

- トレーダーの損益データ分析
- Excelファイルの変換
- 勝率などの計算
- グラフ作成
