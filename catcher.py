import os
import sys
import pandas as pd
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
    # 强制重新获取数据，确保数据完整性
    iren_data = yf.download(SYMBOL, period="2y", interval="1d", progress=False)
    if iren_data.empty:
        raise ValueError("数据抓取失败")
    
    # 提取最新价格并确保是标量 float
    current_price = float(iren_data['Close'].iloc[-1].item())
    return iren_data, current_price

def generate_calibrated_chart(iren_data, current_price):
    # 创建画布
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), gridspec_kw={'height_ratios': [3.5, 1]}, sharex=True)
    
    # 1. 价格曲线
    ax1.plot(iren_data.index, iren_data['Close'], color='black', linewidth=2.5, label='IREN Price')
    
    # 2. 标注处理 (加入空值检查防止报错)
    idx_last = iren_data.index[-1]
    ax1.annotate(f'Now: ${current_price:.2f}', xy=(idx_last, current_price), 
                 xytext=(20, -30), textcoords='offset points', fontsize=12, 
                 color='red', bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.9))
    
    # 辅助线
    ax1.axhline(y=81.5, color='orange', linestyle='--', linewidth=1.5, alpha=0.8)
    ax1.axhline(y=105, color='orange', linestyle='--', linewidth=1.5, alpha=0.8)
    ax1.set_title(f'IREN Quantum Model', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 3. 成交量图 (【核心修复】：使用 fill_between 彻底弃用 bar，绕过 patches.py)
    # 将 NaN 替换为 0，确保绘图函数不会因为空值崩溃
    vol_data = iren_data['Volume'].fillna(0).values
    ax2.fill_between(iren_data.index, 0, vol_data, color='lightgreen', alpha=0.6)
    ax2.set_ylabel('Volume')
    ax2.grid(True, alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    plt.close()

def run_pipeline():
    try:
        iren_data, current_price = fetch_latest_data()
        generate_calibrated_chart(iren_data, current_price)
        
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# IREN Quantum Model\n\n- **Current Price**: ${current_price:.2f}\n![Dashboard]({OUTPUT_FILE})")
    except Exception:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
