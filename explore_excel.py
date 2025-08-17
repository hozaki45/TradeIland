#!/usr/bin/env python3
"""
TradeIland.xlsx ファイルの構造を分析するスクリプト
各シートの内容と構造を理解します。
"""

import pandas as pd
import os
from pathlib import Path

def explore_excel_structure():
    """Excelファイルの構造を探索する"""
    
    # ファイルパス
    excel_path = Path("../data/TradeIland.xlsx")
    
    if not excel_path.exists():
        print(f"エラー: ファイルが見つかりません: {excel_path}")
        return
    
    print(f"=== TradeIland.xlsx ファイル分析 ===")
    print(f"ファイルサイズ: {excel_path.stat().st_size / 1024:.2f} KB")
    print()
    
    try:
        # Excelファイル全体を読み取り、シート名を取得
        excel_file = pd.ExcelFile(excel_path)
        sheet_names = excel_file.sheet_names
        
        print(f"シート数: {len(sheet_names)}")
        print("シート名一覧:")
        for i, sheet_name in enumerate(sheet_names, 1):
            print(f"  {i}. {sheet_name}")
        print()
        
        # 各シートの詳細を分析
        print("=== 各シートの詳細分析 ===")
        
        for sheet_name in sheet_names:
            print(f"\n--- シート: {sheet_name} ---")
            
            try:
                # シートを読み込み
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                
                print(f"行数: {len(df)}")
                print(f"列数: {len(df.columns)}")
                
                # 列名を表示
                print("列名:")
                for i, col in enumerate(df.columns, 1):
                    print(f"  {i}. {col}")
                
                # 最初の5行を表示
                print("\n最初の5行:")
                print(df.head())
                
                # データ型情報
                print("\nデータ型:")
                print(df.dtypes)
                
                # 欠損値情報
                null_counts = df.isnull().sum()
                if null_counts.sum() > 0:
                    print("\n欠損値:")
                    for col, count in null_counts.items():
                        if count > 0:
                            print(f"  {col}: {count}")
                else:
                    print("\n欠損値: なし")
                
                # 数値列の基本統計
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    print(f"\n数値列の基本統計 ({len(numeric_cols)}列):")
                    print(df[numeric_cols].describe())
                
                print("-" * 50)
                
            except Exception as e:
                print(f"エラー: シート '{sheet_name}' の読み込みに失敗: {e}")
                continue
                
    except Exception as e:
        print(f"エラー: Excelファイルの読み込みに失敗: {e}")

if __name__ == "__main__":
    explore_excel_structure()