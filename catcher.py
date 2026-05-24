import requests
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # 强制使用无头模式，避免 Action 环境报错
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import sys

# 🎯 目标资产
SYMBOL = "IREN"
OUTPUT_FILE = "iren_quantum_v5.png"

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
        return df.dropna().reset_index(drop=True)
    except Exception as e:
        print(f"❌ 数据抓取失败: {e}")
        sys.exit(1)

def generate_tradingview_replica_chart(df, current_price):
    # 强制将数据转为一维 numpy 数组，彻底解决 ValueError: 'y2' is not 1-dimensional
    dates = df['date'].to_numpy()
    closes = df['close'].to_numpy().flatten()
    volumes = df['volume'].to_numpy().flatten()
    
    fig, (ax, ax_vol) = plt.subplots(2, 1, figsize=(13, 8.5), gridspec_kw={'height_ratios': [5.5, 1.5]})
    fig.subplots_adjust(hspace=0.08)
    
    # 主图
    ax.plot(dates, closes, color='#333333', linewidth=1.2)
    ax.set_yscale('log')
    
    # 修复日期计算错误：确保使用 Pandas Timestamp 进行 timedelta 加法
    last_date = pd.to_datetime(dates[-1])
    forecast_dates = [last_date + timedelta(weeks=i) for i in range(1, 25)]
    
    # 填充成交量 - 确保传入的是一维数组
    ax_vol.bar(dates, volumes, color='gray', alpha=0.3)
    
    plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ 图表生成成功")

# 主执行逻辑
df = get_macro_weekly_data(SYMBOL)
if df is not None:
    current_price = float(df['close'].iloc[-1])
    generate_tradingview_replica_chart(df, current_price)
