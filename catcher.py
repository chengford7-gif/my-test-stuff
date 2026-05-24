import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import yfinance as yf
import traceback

# ==================== 配置 ====================
SYMBOL = "IREN"
OUTPUT_FILE = "iren_quantum_v5.png"
RPF = 0.28
CURRENT_WAVE = "Int Wave (3) impulsive | 2026.10-11 BTC喇叭口共振"

def fetch_latest_data():
    print("🔄 正在抓取最新数据...")
    iren_data = yf.download(SYMBOL, period="2y", interval="1d", progress=False)
    if iren_data.empty:
        raise ValueError("无法获取数据")
    
    # 提取最新价格并确保是标量 float
    current_price = float(iren_data['Close'].iloc[-1].item())
    return iren_data, current_price

def generate_calibrated_chart(iren_data, current_price):
    print("🎨 正在生成校准图表...")
    # 使用 numpy 数组作为 x 轴，防止 Matplotlib 识别错误
    x_axis = np.array(iren_data.index)
    price_data = iren_data['Close'].values.flatten()
    vol_data = iren_data['Volume'].fillna(0).values.flatten()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), gridspec_kw={'height_ratios': [3.5, 1]}, sharex=True)
    
    # 1. 价格曲线
    ax1.plot(x_axis, price_data, color='black', linewidth=2.5, label='IREN Price')
    
    # 2. 标注
    idx_last = x_axis[-1]
    ax1.annotate(f'Now: ${current_price:.2f}', xy=(idx_last, current_price), 
                 xytext=(20, -30), textcoords='offset points', fontsize=12, 
                 color='red', bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.9))
    
    ax1.axhline(y=81.5, color='orange', linestyle='--', linewidth=1.5, alpha=0.8)
    ax1.axhline(y=105, color='orange', linestyle='--', linewidth=1.5, alpha=0.8)
    ax1.set_title(f'IREN Quantum Model', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 3. 成交量图 (【强制转换】：使用 fill_between 并显式传入 numpy 一维数组)
    ax2.fill_between(x_axis, 0, vol_data, color='lightgreen', alpha=0.6)
    ax2.set_ylabel('Volume')
    ax2.grid(True, alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ 图表已保存")

def run_pipeline():
    try:
        iren_data, current_price = fetch_latest_data()
        generate_calibrated_chart(iren_data, current_price)
        
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# IREN Quantum Model\n\n- **Current Price**: ${current_price:.2f}\n![Dashboard]({OUTPUT_FILE})")
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
