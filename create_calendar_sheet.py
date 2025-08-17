#!/usr/bin/env python3
"""
TradeIland.xlsx データをカレンダー形式に変換
A列に日付、B列以降に各トレーダーの日次収益を配置した新しいExcelシートを作成
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

def convert_excel_date(excel_date):
    """Excelの日付シリアル値を日付に変換"""
    try:
        # Excelの基準日: 1900年1月1日（実際は1900年1月0日として計算）
        base_date = datetime(1899, 12, 30)  # Excelのエラーを補正
        return base_date + timedelta(days=int(excel_date))
    except:
        return None

def extract_trader_data(excel_path, sheet_name):
    """各トレーダーの収益データを抽出"""
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    
    # 日付と収益のマッピングを作成
    date_profit_map = {}
    
    # 収益データの行を特定（通常は行2）
    profit_row = df.iloc[2]
    
    for col in df.columns:
        try:
            # 列名を日付に変換
            col_clean = str(col).replace('.1', '')  # 重複列名の処理
            if col_clean.replace('.', '').isdigit():
                date_val = convert_excel_date(float(col_clean))
                profit_val = profit_row[col]
                
                if date_val and pd.notna(profit_val) and isinstance(profit_val, (int, float)):
                    date_profit_map[date_val] = profit_val
        except:
            continue
    
    return date_profit_map

def create_calendar_sheet():
    """カレンダー形式のExcelシートを作成"""
    
    excel_path = Path("../data/TradeIland.xlsx")
    
    if not excel_path.exists():
        print(f"エラー: ファイルが見つかりません: {excel_path}")
        return
    
    print("=== カレンダー形式データ変換開始 ===")
    
    # 全シート名を取得
    excel_file = pd.ExcelFile(excel_path)
    sheet_names = excel_file.sheet_names
    
    print(f"対象シート: {sheet_names}")
    
    # 各トレーダーのデータを抽出
    all_trader_data = {}
    all_dates = set()
    
    for sheet_name in sheet_names:
        print(f"データ抽出中: {sheet_name}")
        trader_data = extract_trader_data(excel_path, sheet_name)
        all_trader_data[sheet_name] = trader_data
        all_dates.update(trader_data.keys())
        print(f"  抽出データ数: {len(trader_data)}件")
    
    # 日付をソート
    sorted_dates = sorted(all_dates)
    print(f"\n全期間: {len(sorted_dates)}件")
    print(f"開始日: {sorted_dates[0].strftime('%Y-%m-%d')}")
    print(f"終了日: {sorted_dates[-1].strftime('%Y-%m-%d')}")
    
    # カレンダー形式のDataFrameを作成
    calendar_data = {
        'Date': sorted_dates
    }
    
    # 各トレーダーの収益を追加
    for sheet_name in sheet_names:
        profits = []
        for date in sorted_dates:
            profit = all_trader_data[sheet_name].get(date, np.nan)
            profits.append(profit)
        calendar_data[sheet_name] = profits
    
    # DataFrameを作成
    df_calendar = pd.DataFrame(calendar_data)
    
    # 日付を文字列形式に変換
    df_calendar['Date'] = df_calendar['Date'].dt.strftime('%Y-%m-%d')
    
    print("\n=== カレンダーデータ作成完了 ===")
    print(f"行数: {len(df_calendar)}")
    print(f"列数: {len(df_calendar.columns)}")
    print("\n列名:")
    for i, col in enumerate(df_calendar.columns):
        print(f"  {chr(65+i)}: {col}")
    
    # 最初の5行を表示
    print(f"\n最初の5行:")
    print(df_calendar.head())
    
    # 各トレーダーの統計
    print(f"\n=== トレーダー別統計 ===")
    for sheet_name in sheet_names:
        col_data = df_calendar[sheet_name].dropna()
        if len(col_data) > 0:
            total = col_data.sum()
            avg = col_data.mean()
            positive_count = (col_data > 0).sum()
            win_rate = positive_count / len(col_data) * 100
            
            print(f"{sheet_name}:")
            print(f"  データ数: {len(col_data)}件")
            print(f"  合計収益: ¥{total:,.0f}")
            print(f"  平均収益: ¥{avg:,.0f}")
            print(f"  勝率: {win_rate:.1f}%")
    
    # Excelファイルに保存
    output_path = Path("../data/TradeIland_Calendar.xlsx")
    df_calendar.to_excel(output_path, sheet_name='Daily_PL_Calendar', index=False)
    
    print(f"\n=== 出力完了 ===")
    print(f"ファイル保存先: {output_path}")
    print("A列: 日付")
    print("B列以降: 各トレーダーの日次収益")

def main():
    create_calendar_sheet()

if __name__ == "__main__":
    main()