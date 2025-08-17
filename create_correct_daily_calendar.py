#!/usr/bin/env python3
"""
TradeIland.xlsx から正しい日次データを抽出してカレンダー形式のExcelを作成
日付と収益のペアを正しく抽出: 日付候補(1-31)の次の行が収益データ
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

def extract_daily_trading_data(excel_path, sheet_name):
    """シートから日次トレーディングデータを正しく抽出"""
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
        
        # 列内のデータを取得（行12以降）
        col_data = df[col].iloc[12:].reset_index(drop=True)
        
        # 日付と収益のペアを抽出
        trading_days = 0
        for i in range(len(col_data) - 1):
            current_val = col_data.iloc[i]
            next_val = col_data.iloc[i + 1]
            
            # 現在の値が日付候補（1-31）で、次の値が収益データかチェック
            if (pd.notna(current_val) and isinstance(current_val, (int, float)) and 
                1 <= current_val <= 31 and
                pd.notna(next_val) and isinstance(next_val, (int, float)) and
                abs(next_val) > 31):  # 収益データは31より大きい絶対値
                
                day = int(current_val)
                profit = next_val
                
                # 有効な日付かチェック
                try:
                    daily_date = date(year, month, day)
                    all_daily_data[daily_date] = profit
                    trading_days += 1
                except ValueError:
                    continue  # 無効な日付はスキップ
        
        print(f"    抽出したトレーディング日数: {trading_days}日")
    
    print(f"合計トレーディング日数: {len(all_daily_data)}日")
    return all_daily_data

def create_correct_daily_calendar():
    """正しい日次カレンダー形式のExcelシートを作成"""
    
    excel_path = Path("../data/TradeIland.xlsx")
    
    if not excel_path.exists():
        print(f"エラー: ファイルが見つかりません: {excel_path}")
        return
    
    print("=== 正しい日次カレンダー作成開始 ===")
    
    excel_file = pd.ExcelFile(excel_path)
    sheet_names = excel_file.sheet_names
    
    # 各トレーダーの日次トレーディングデータを抽出
    all_trader_data = {}
    all_dates = set()
    
    for sheet_name in sheet_names:
        trader_data = extract_daily_trading_data(excel_path, sheet_name)
        all_trader_data[sheet_name] = trader_data
        all_dates.update(trader_data.keys())
    
    # 日付をソート
    sorted_dates = sorted(all_dates)
    
    if not sorted_dates:
        print("エラー: トレーディングデータが見つかりませんでした")
        return
    
    print(f"\n=== 日次カレンダーデータ統計 ===")
    print(f"全期間: {sorted_dates[0]} 〜 {sorted_dates[-1]}")
    print(f"トレーディング日数: {len(sorted_dates)}日")
    
    # カレンダー形式のDataFrameを作成
    calendar_data = {
        'Date': [d.strftime('%Y-%m-%d') for d in sorted_dates]
    }
    
    # 各トレーダーの日次収益を追加
    for sheet_name in sheet_names:
        daily_profits = []
        for date_obj in sorted_dates:
            profit = all_trader_data[sheet_name].get(date_obj, np.nan)
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
            print(f"  トレーディング日数: {len(valid_profits)}日")
            print(f"  合計収益: ¥{total:,.0f}")
            print(f"  平均日次収益: ¥{avg:,.0f}")
            print(f"  勝率: {win_rate:.1f}% ({positive_days}/{len(valid_profits)}日)")
            if valid_profits:
                print(f"  最大収益: ¥{max(valid_profits):,.0f}")
                print(f"  最大損失: ¥{min(valid_profits):,.0f}")
    
    # DataFrameを作成
    df_daily_calendar = pd.DataFrame(calendar_data)
    
    print(f"\n=== 日次カレンダーシート作成完了 ===")
    print(f"行数: {len(df_daily_calendar)} (トレーディング日のみ)")
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
    output_path = Path("../data/TradeIland_Correct_Daily_Calendar.xlsx")
    df_daily_calendar.to_excel(output_path, sheet_name='Trading_Days_PL', index=False)
    
    print(f"\n=== 出力完了 ===")
    print(f"ファイル保存先: {output_path}")
    print("A列: 日付（YYYY-MM-DD形式）")
    print("B列以降: 各トレーダーの日次収益（トレーディング日のみ）")
    print("\n注意: トレードしなかった日は含まれていません")

def main():
    create_correct_daily_calendar()

if __name__ == "__main__":
    main()