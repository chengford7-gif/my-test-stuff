import requests
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import sys

SYMBOL = "IREN"
OUTPUT_FILE = "iren_quantum_v5.png"
RPF = 0.28


def get_macro_weekly_data(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=3y&interval=1wk"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        result = data['chart']['result'][0]
        df = pd.DataFrame({
            'date': pd.to_datetime(result['timestamp'], unit='s'),
            'close': result['indicators']['quote'][0]['close'],
            'high': result['indicators']['quote'][0]['high'],
            'low': result['indicators']['quote'][0]['low'],
            'volume': result['indicators']['quote'][0]['volume']
        })
        return df.dropna().reset_index(drop=True)
    except Exception as e:
        print(f"❌ 数据获取失败: {e}")
        sys.exit(1)


def generate_calibrated_chart(df, current_price):
    print("🎨 正在生成专业版校准图表（接近ElliottChart风格）...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), 
                                    gridspec_kw={'height_ratios': [4, 1]}, 
                                    sharex=True)
    
    # 主图 - 价格
    ax1.plot(df['date'], df['close'], color='black', linewidth=1.8, label='IREN Price')
    ax1.set_yscale('log')
    
    # Q-Structure 射线模拟（可后续替换为真实模型值）
    ax1.axhline(y=44.5, color='#00AA00', linestyle='--', linewidth=1.3, alpha=0.75, label='Q-Structure λ₄ Support')
    ax1.axhline(y=105, color='#FF8800', linestyle='--', linewidth=1.6, alpha=0.85)
    ax1.axhline(y=133.33, color='#0066FF', linestyle='--', linewidth=1.8, alpha=0.9)
    
    # Elliott Wave 标注
    ax1.annotate('① Leading Diagonal', xy=(df['date'].iloc[25], 8.5), fontsize=9, color='#006600', fontweight='bold')
    ax1.annotate('② Zigzag', xy=(df['date'].iloc[75], 5.8), fontsize=9, color='#006600')
    ax1.annotate('③', xy=(df['date'].iloc[135], 76), fontsize=12, color='blue', fontweight='bold')
    ax1.annotate('④ Double Zigzag', xy=(df['date'].iloc[155], 31), fontsize=9, color='#006600')
    ax1.annotate('⑤', xy=(df['date'].iloc[-8], current_price * 1.15), fontsize=13, color='red', fontweight='bold')
    
    # HPQ & Q-Target 醒目标注
    ax1.annotate('HPQ-Target $133.33\n(Early July | RPF Calibrated)', 
                 xy=(df['date'].iloc[-1], 133.33), 
                 xytext=(25, 45), textcoords='offset points',
                 fontsize=10, color='#0033AA', fontweight='bold',
                 bbox=dict(boxstyle="round,pad=0.45", facecolor="#fffde7", edgecolor="#1565C0", alpha=0.95),
                 arrowprops=dict(arrowstyle="->", color='#1565C0', lw=1.2))
    
    ax1.annotate('Q-Target $249.99\n(Mid Oct | Potential Extension)', 
                 xy=(df['date'].iloc[-1], 250), 
                 xytext=(25, 70), textcoords='offset points',
                 fontsize=10, color='#B71C1C', fontweight='bold',
                 bbox=dict(boxstyle="round,pad=0.45", facecolor="#ffebee", edgecolor="#C62828", alpha=0.95),
                 arrowprops=dict(arrowstyle="->", color='#C62828', lw=1.2))
    
    # 当前结构高亮区域
    ax1.axvspan(df['date'].iloc[-35], df['date'].iloc[-1], alpha=0.07, color='blue')
    
    # 左上信息框（模仿ElliottChart）
    info_text = (
        "IREN — Quantum Model Projection\n"
        "Bullish Outlook | Primary Wave⑤ Extension\n"
        f"HPQ-Target → $133.33 | RPF={RPF}\n"
        f"Current: ${current_price} | {datetime.now().strftime('%Y-%m-%d')}"
    )
    ax1.text(0.015, 0.97, info_text, transform=ax1.transAxes, fontsize=9.5,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle="round,pad=0.6", facecolor="white", edgecolor="#424242", alpha=0.97))
    
    ax1.set_title("IREN LIMITED - Weekly | Calibrated ElliottChart Style", fontsize=13, fontweight='bold', pad=15)
    ax1.set_ylabel("Price (log)")
    ax1.grid(True, which="both", linestyle="--", alpha=0.35)
    ax1.legend(loc='upper left', fontsize=8)
    
    # 成交量
    ax2.bar(df['date'], df['volume'], color='#90EE90', alpha=0.55, width=6)
    ax2.set_ylabel("Volume")
    ax2.grid(True, alpha=0.3)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ 专业版图表已生成: {OUTPUT_FILE}")


# 执行
df = get_macro_weekly_data(SYMBOL)
if df is not None and not df.empty:
    current_price = round(float(df['close'].iloc[-1].item()), 2)
    generate_calibrated_chart(df, current_price)
