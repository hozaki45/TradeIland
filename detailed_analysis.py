#!/usr/bin/env python3
"""
TradeIland.xlsx の詳細分析
日次PL（損益）データの構造を詳しく理解します。
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

def analyze_data_structure():
    """データ構造の詳細分析"""
    
    excel_path = Path("../data/TradeIland.xlsx")
    
    if not excel_path.exists():
        print(f"エラー: ファイルが見つかりません: {excel_path}")
        return
    
    print("=== TradeIland.xlsx 詳細分析 ===\n")
    
    excel_file = pd.ExcelFile(excel_path)
    sheet_names = excel_file.sheet_names
    
    # 各シートの詳細分析
    for sheet_name in sheet_names:
        print(f"=== シート: {sheet_name} ===")
        
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        # 列名（日付）の変換と分析
        print("列名分析（日付変換）:")
        date_columns = []
        for col in df.columns:
            try:
                if str(col).replace('.', '').isdigit():
                    date_val = convert_excel_date(float(str(col).replace('.1', '')))
                    if date_val:
                        date_columns.append((col, date_val))
                        print(f"  {col} → {date_val.strftime('%Y-%m-%d')}")
            except:
                print(f"  {col} → 変換不可")
        
        print(f"\n期間: {len(date_columns)}日間")
        if date_columns:
            sorted_dates = sorted(date_columns, key=lambda x: x[1])
            start_date = sorted_dates[0][1]
            end_date = sorted_dates[-1][1]
            print(f"開始日: {start_date.strftime('%Y-%m-%d')}")
            print(f"終了日: {end_date.strftime('%Y-%m-%d')}")
        
        print(f"\nデータ行分析:")
        print(f"総行数: {len(df)}")
        
        # 各行の内容を分析
        for i in range(min(10, len(df))):
            row_desc = []
            for j, val in enumerate(df.iloc[i]):
                if pd.notna(val):
                    if isinstance(val, str):
                        if '位/' in str(val):
                            row_desc.append("順位情報")
                        elif '収益額' in str(val):
                            row_desc.append("収益額ラベル")
                        elif '円' in str(val):
                            row_desc.append("通貨単位")
                        else:
                            row_desc.append(f"文字列: {str(val)[:20]}")
                    elif isinstance(val, (int, float)) and abs(val) > 1000:
                        row_desc.append("金額データ")
                    else:
                        row_desc.append(f"数値: {val}")
                else:
                    row_desc.append("空白")
                
                if j >= 2:  # 最初の3列のみ表示
                    break
            
            print(f"  行{i}: {' | '.join(row_desc)}")
        
        # 収益額データの抽出と分析
        print(f"\n収益額データ分析:")
        profit_data = []
        
        # 収益額の行を特定（通常は行2または行3あたり）
        for row_idx in range(len(df)):
            row_data = df.iloc[row_idx]
            numeric_count = 0
            for val in row_data:
                if pd.notna(val) and isinstance(val, (int, float)) and abs(val) > 1000:
                    numeric_count += 1
            
            if numeric_count >= len(date_columns) * 0.5:  # 半数以上が数値データ
                print(f"  収益額データ行: {row_idx}")
                
                daily_profits = []
                for col in df.columns:
                    val = row_data[col]
                    if pd.notna(val) and isinstance(val, (int, float)):
                        daily_profits.append(val)
                
                if daily_profits:
                    print(f"    日次収益数: {len(daily_profits)}日")
                    print(f"    最大収益: ¥{max(daily_profits):,}")
                    print(f"    最小収益: ¥{min(daily_profits):,}")
                    print(f"    平均収益: ¥{np.mean(daily_profits):,.0f}")
                    print(f"    合計収益: ¥{sum(daily_profits):,}")
                    
                    # 勝率計算
                    positive_days = sum(1 for x in daily_profits if x > 0)
                    win_rate = positive_days / len(daily_profits) * 100
                    print(f"    勝率: {win_rate:.1f}% ({positive_days}/{len(daily_profits)}日)")
                
                break
        
        print("-" * 60)
        print()

def main():
    analyze_data_structure()

if __name__ == "__main__":
    main()