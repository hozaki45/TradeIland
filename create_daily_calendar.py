#!/usr/bin/env python3
"""
TradeIland.xlsx から日次データを抽出して日次カレンダー形式のExcelを作成
各月の日次収益データを全て抽出し、A列に日付、B列以降に各トレーダーの日次収益を配置
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from pathlib import Path
from calendar import monthrange

def convert_excel_date(excel_date):
    """Excelの日付シリアル値を日付に変換"""
    try:
        base_date = datetime(1899, 12, 30)
        return base_date + timedelta(days=int(excel_date))
    except:
        return None

def extract_daily_data_from_sheet(excel_path, sheet_name):
    """シートから日次データを抽出"""
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    
    print(f"\n--- {sheet_name} シートからの日次データ抽出 ---")
    
    # 列名（月）と日付のマッピングを作成
    month_columns = {}
    for col in df.columns:
        try:
            col_clean = str(col).replace('.1', '')
            if col_clean.replace('.', '').isdigit():
                date_val = convert_excel_date(float(col_clean))
                if date_val:
                    month_columns[col] = date_val
        except:
            continue
    
    print(f"対象月数: {len(month_columns)}月")
    
    # 各月の日次データを抽出
    all_daily_data = {}
    
    for col, month_date in month_columns.items():
        year = month_date.year
        month = month_date.month
        
        print(f"  {year}年{month}月 処理中...")
        
        # その月の日数を取得
        _, days_in_month = monthrange(year, month)
        
        # 列内のデータを取得（行13以降が日次データ）
        col_data = df[col].iloc[13:].dropna()
        
        # 数値データのみを抽出（収益データ）
        daily_profits = []
        for val in col_data:
            if isinstance(val, (int, float)) and not pd.isna(val):
                daily_profits.append(val)
        
        print(f"    抽出した日次データ数: {len(daily_profits)}件")
        
        # 各日の日付を生成して収益を割り当て
        for day in range(1, min(days_in_month + 1, len(daily_profits) + 1)):
            if day - 1 < len(daily_profits):
                daily_date = date(year, month, day)
                profit = daily_profits[day - 1]
                all_daily_data[daily_date] = profit
    
    print(f"合計日次データ: {len(all_daily_data)}件")
    return all_daily_data

def create_daily_calendar_sheet():
    """日次カレンダー形式のExcelシートを作成"""
    
    excel_path = Path("../data/TradeIland.xlsx")
    
    if not excel_path.exists():
        print(f"エラー: ファイルが見つかりません: {excel_path}")
        return
    
    print("=== 日次カレンダー作成開始 ===")
    
    excel_file = pd.ExcelFile(excel_path)
    sheet_names = excel_file.sheet_names
    
    # 各トレーダーの日次データを抽出
    all_trader_daily_data = {}
    all_dates = set()
    
    for sheet_name in sheet_names:
        trader_daily_data = extract_daily_data_from_sheet(excel_path, sheet_name)
        all_trader_daily_data[sheet_name] = trader_daily_data
        all_dates.update(trader_daily_data.keys())
    
    # 日付をソート
    sorted_dates = sorted(all_dates)
    
    if not sorted_dates:
        print("エラー: 日次データが見つかりませんでした")
        return
    
    print(f"\n=== 日次カレンダーデータ統計 ===")
    print(f"全期間: {len(sorted_dates)}日間")
    print(f"開始日: {sorted_dates[0]}")
    print(f"終了日: {sorted_dates[-1]}")
    
    # カレンダー形式のDataFrameを作成
    calendar_data = {
        'Date': [d.strftime('%Y-%m-%d') for d in sorted_dates]
    }
    
    # 各トレーダーの日次収益を追加
    for sheet_name in sheet_names:
        daily_profits = []
        for date_obj in sorted_dates:
            profit = all_trader_daily_data[sheet_name].get(date_obj, np.nan)
            daily_profits.append(profit)
        calendar_data[sheet_name] = daily_profits
        
        # 統計情報を表示
        valid_profits = [p for p in daily_profits if not pd.isna(p)]
        if valid_profits:
            total = sum(valid_profits)
            avg = np.mean(valid_profits)
            positive_days = sum(1 for p in valid_profits if p > 0)
            win_rate = positive_days / len(valid_profits) * 100
            
            print(f"\n{sheet_name}:")
            print(f"  日次データ数: {len(valid_profits)}日")
            print(f"  合計収益: ¥{total:,.0f}")
            print(f"  平均日次収益: ¥{avg:,.0f}")
            print(f"  勝率: {win_rate:.1f}% ({positive_days}/{len(valid_profits)}日)")
            print(f"  最大収益: ¥{max(valid_profits):,.0f}")
            print(f"  最大損失: ¥{min(valid_profits):,.0f}")
    
    # DataFrameを作成
    df_daily_calendar = pd.DataFrame(calendar_data)
    
    print(f"\n=== 日次カレンダーシート作成完了 ===")
    print(f"行数: {len(df_daily_calendar)}")
    print(f"列数: {len(df_daily_calendar.columns)}")
    
    # 列名を表示
    print("\n列名:")
    for i, col in enumerate(df_daily_calendar.columns):
        print(f"  {chr(65+i)}: {col}")
    
    # 最初と最後の5行を表示
    print(f"\n最初の5行:")
    print(df_daily_calendar.head())
    
    print(f"\n最後の5行:")
    print(df_daily_calendar.tail())
    
    # Excelファイルに保存
    output_path = Path("../data/TradeIland_Daily_Calendar.xlsx")
    df_daily_calendar.to_excel(output_path, sheet_name='Daily_PL_Calendar', index=False)
    
    print(f"\n=== 出力完了 ===")
    print(f"ファイル保存先: {output_path}")
    print("A列: 日付（YYYY-MM-DD形式）")
    print("B列以降: 各トレーダーの日次収益")
    print("\n日次データを使った詳細な分析が可能になります。")

def main():
    create_daily_calendar_sheet()

if __name__ == "__main__":
    main()