#!/usr/bin/env python3
"""
TradeIland.xlsx の日次データ構造を詳細調査
各行に日次データが含まれているかを徹底的に調べる
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

def investigate_daily_structure():
    """各シートの全行を詳細調査して日次データを探す"""
    
    excel_path = Path("../data/TradeIland.xlsx")
    
    if not excel_path.exists():
        print(f"エラー: ファイルが見つかりません: {excel_path}")
        return
    
    print("=== 日次データ構造の詳細調査 ===\n")
    
    excel_file = pd.ExcelFile(excel_path)
    sheet_names = excel_file.sheet_names
    
    for sheet_name in sheet_names:
        print(f"=== シート: {sheet_name} ===")
        
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        # 列名（日付）の確認
        print("列名分析:")
        date_columns = []
        for col in df.columns:
            try:
                col_clean = str(col).replace('.1', '')
                if col_clean.replace('.', '').isdigit():
                    date_val = convert_excel_date(float(col_clean))
                    if date_val:
                        date_columns.append((col, date_val))
                        print(f"  {col} → {date_val.strftime('%Y-%m-%d')}")
            except:
                print(f"  {col} → 変換不可")
        
        print(f"\n全行分析 (行数: {len(df)}):")
        print("-" * 80)
        
        # 各行を詳細分析
        for row_idx in range(len(df)):
            row_data = df.iloc[row_idx]
            
            # 数値データの数をカウント
            numeric_values = []
            string_values = []
            
            for col_idx, (col, val) in enumerate(row_data.items()):
                if pd.notna(val):
                    if isinstance(val, (int, float)):
                        # 大きな数値（収益っぽい）かどうか判定
                        if abs(val) > 100:
                            numeric_values.append((col_idx, col, val))
                        else:
                            # 小さな数値は日付や順番かもしれない
                            pass
                    else:
                        string_values.append((col_idx, col, str(val)[:30]))
            
            # 行の特徴を分析
            row_type = "不明"
            if len(numeric_values) >= len(date_columns) * 0.5:
                if any(abs(val) > 1000000 for _, _, val in numeric_values):
                    row_type = "収益データ（高額）"
                elif any(abs(val) > 1000 for _, _, val in numeric_values):
                    row_type = "収益データ（低額）または日次データ"
                else:
                    row_type = "小額データ"
            elif any("位/" in val for _, _, val in string_values):
                row_type = "順位情報"
            elif any("収益" in val for _, _, val in string_values):
                row_type = "収益ラベル"
            elif any("円" in val for _, _, val in string_values):
                row_type = "通貨単位"
            elif any(val in ["日", "月", "火", "水", "木", "金", "土"] for _, _, val in string_values):
                row_type = "曜日情報"
            elif len(string_values) > 0:
                row_type = f"文字列データ"
            
            print(f"行{row_idx:2d}: {row_type}")
            print(f"      数値データ: {len(numeric_values)}個")
            if numeric_values:
                # 最初の3つの数値を表示
                for i, (col_idx, col, val) in enumerate(numeric_values[:3]):
                    print(f"        [{col_idx}] {col}: {val:,}")
                if len(numeric_values) > 3:
                    print(f"        ... 他 {len(numeric_values)-3}個")
            
            if string_values:
                print(f"      文字データ: {len(string_values)}個")
                for i, (col_idx, col, val) in enumerate(string_values[:3]):
                    print(f"        [{col_idx}] {col}: {val}")
                if len(string_values) > 3:
                    print(f"        ... 他 {len(string_values)-3}個")
            
            print()
        
        print("=" * 80)
        print()

def main():
    investigate_daily_structure()

if __name__ == "__main__":
    main()