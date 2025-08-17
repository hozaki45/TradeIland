#!/usr/bin/env python3
"""
TradeIland.xlsx の正しいデータ構造を詳細検証
各列（月）内で、日付情報と収益データのペアを正しく特定する
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

def convert_excel_date(excel_date):
    """Excelの日付シリアル値を日付に変換"""
    try:
        base_date = datetime(1899, 12, 30)
        return base_date + timedelta(days=int(excel_date))
    except:
        return None

def analyze_column_structure():
    """各列内の構造を詳細に分析"""
    
    excel_path = Path("../data/TradeIland.xlsx")
    excel_file = pd.ExcelFile(excel_path)
    
    # BGSシートで詳細分析（サンプル）
    df = pd.read_excel(excel_path, sheet_name='BGS')
    
    print("=== BGSシート - 列内構造の詳細分析 ===")
    
    # 最初の2列（4月と5月）を詳細分析
    target_cols = list(df.columns)[:2]
    
    for col_idx, col in enumerate(target_cols):
        print(f"\n--- 列 {col} ({col_idx+1}列目) の詳細分析 ---")
        
        # 列名を日付に変換
        month_date = convert_excel_date(float(str(col).replace('.1', '')))
        if month_date:
            print(f"対象月: {month_date.strftime('%Y年%m月')}")
        
        # 列内の全データを表示
        col_data = df[col]
        
        print("行番号 | データ型 | 値")
        print("-" * 40)
        
        for row_idx, value in enumerate(col_data):
            if pd.notna(value):
                data_type = type(value).__name__
                
                # 値の内容を分析
                if isinstance(value, (int, float)):
                    if abs(value) > 1000000:
                        category = "大額収益"
                    elif abs(value) > 1000:
                        category = "収益データ"
                    elif 1 <= value <= 31:
                        category = "日付候補"
                    else:
                        category = "小額/その他"
                    print(f"{row_idx:6d} | {data_type:8s} | {value:>12} ({category})")
                else:
                    str_val = str(value)[:30]
                    if '位/' in str_val:
                        category = "順位"
                    elif '収益' in str_val:
                        category = "ラベル"
                    elif '円' in str_val:
                        category = "通貨"
                    elif str_val in ['日', '月', '火', '水', '木', '金', '土']:
                        category = "曜日"
                    else:
                        category = "その他"
                    print(f"{row_idx:6d} | {data_type:8s} | {str_val:>30} ({category})")
            else:
                print(f"{row_idx:6d} | NaN      | {'':>30}")
        
        print(f"\n統計:")
        numeric_data = []
        for val in col_data:
            if pd.notna(val) and isinstance(val, (int, float)):
                numeric_data.append(val)
        
        if numeric_data:
            print(f"  数値データ数: {len(numeric_data)}個")
            print(f"  大額収益データ(>100万): {len([x for x in numeric_data if abs(x) > 1000000])}個")
            print(f"  収益データ(>1000): {len([x for x in numeric_data if abs(x) > 1000])}個") 
            print(f"  日付候補(1-31): {len([x for x in numeric_data if 1 <= x <= 31])}個")

def main():
    analyze_column_structure()

if __name__ == "__main__":
    main()