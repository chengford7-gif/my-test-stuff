import requests
import json
import pandas as pd
import numpy as np
import os
import sys
import traceback
from datetime import datetime, timedelta

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FixedLocator, FixedFormatter

SYMBOL = "IREN"

def get_macro_weekly_data(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=3y&interval=1wk"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        result = data['chart']['result'][0]
        df = pd.DataFrame({
            'date': pd.to_datetime(result['timestamp'], unit='s'),
            'open': result['indicators']['quote'][0]['open'],
            'high': result['indicators']['quote'][0]['high'],
            'low': result['indicators']['quote'][0]['low'],
            'close': result['indicators']['quote'][0]['close'],
            'volume': result['indicators']['quote'][0]['volume']
        })
        df.dropna(inplace=True)
        return df
    except Exception as e:
        print(f"❌ 数据抓取失败: {e}")
        return None

def generate_calibrated_tradingview_chart(df):
    df = df.reset_index(drop=True)
    fig, (ax, ax_vol) = plt.subplots(2, 1, figsize=(14, 8.5), facecolor='#ffffff', 
                                    gridspec_kw={'height_ratios': [5.8, 1.2]})
    fig.subplots_adjust(hspace=0.05)
    
    ax.set_facecolor('#ffffff')
    ax.set_yscale('log')
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    ax.plot(df['date'], df['close'], color='#111111', linewidth=1.5, zorder=3)
    
    # 绘图逻辑保持你原有的设置
    latest_date = df['date'].iloc[-1]
    w3_date, w4_date = pd.to_datetime('2025-10-15'), pd.to_datetime('2026-04-15')
    w3_val, w4_val = 76.87, 30.76
    
    ax.text(w3_date, w3_val * 1.06, f"③\n${w3_val:.2f}", color='#1A365D', fontsize=10, fontweight='bold', ha='center')
    ax.text(w4_date, w4_val * 0.90, f"④ ${w4_val:.2f}", color='#1A365D', fontsize=10, fontweight='bold', ha='center')

    # 逻辑结束，保存图片
    plt.savefig('iren_quantum_v5.png', dpi=150, bbox_inches='tight')
    plt.close()

def main():
    try:
        df = get_macro_weekly_data(SYMBOL)
        if df is not None and not df.empty:
            generate_calibrated_tradingview_chart(df)
            
            # 生成 README，通过加入时间戳强制 Git 提交
            report = f"# ⚠️ $IREN 周期性牛熊时空转换警告看板\n\n"
            report += f"> **最后更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} \n\n"
            report += f"![Quantum Elliott Chart](iren_quantum_v5.png)\n\n"
            report += f"--- \n免责声明: 此看板内容为自动生成的模拟推演，不构成投资建议。"
            
            with open('README.md', 'w', encoding='utf-8') as f:
                f.write(report)
            print("✅ 图片与 README 已更新，准备推送。")
    except Exception:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
