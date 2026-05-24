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
    print("🔄 正在抓取最新数据...")
    iren_data = yf.download(SYMBOL, period="2y", interval="1d", progress=False)
    btc_data = yf.download("BTC-USD", period="2y", interval="1d", progress=False)
    
    if iren_data.empty:
        raise ValueError("无法获取数据")

    # 确保数值纯净
    current_price = float(iren_data['Close'].iloc[-1])
    return iren_data, current_price

def generate_calibrated_chart(iren_data, current_price):
    print("🎨 正在生成校准图表...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), gridspec_kw={'height_ratios': [3.5, 1]}, sharex=True)
    
    # 1. 价格曲线
    ax1.plot(iren_data.index, iren_data['Close'], color='black', linewidth=2.5, label='IREN Price')
    
    # 标注处理 (使用安全索引)
    idx_300 = iren_data.index[-300] if len(iren_data) > 300 else iren_data.index[0]
    idx_150 = iren_data.index[-150] if len(iren_data) > 150 else iren_data.index[0]
    idx_last = iren_data.index[-1]
    
    ax1.annotate('③ $76.87', xy=(idx_300, 76.87), xytext=(10, 10), textcoords='offset points', arrowprops=dict(arrowstyle='->'), fontsize=11, color='blue')
    ax1.annotate('④ $30.76', xy=(idx_150, 30.76), xytext=(10, -20), textcoords='offset points', arrowprops=dict(arrowstyle='->'), fontsize=11, color='blue')
    ax1.annotate(f'Now: ${current_price:.2f}', xy=(idx_last, current_price), xytext=(20, -30), textcoords='offset points', fontsize=12, color='red', bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.9))
    
    # 水平线
    ax1.axhline(y=81.5, color='orange', linestyle='--', linewidth=1.5, alpha=0.8)
    ax1.axhline(y=105, color='orange', linestyle='--', linewidth=1.5, alpha=0.8)
    ax1.axhline(y=133, color='orange', linestyle='--', linewidth=1.5, alpha=0.6)
    
    ax1.set_title(f'$IREN — Calibrated Quantum Elliott Model (RPF={RPF})\n({CURRENT_WAVE})', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price ($)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # 【终极方案】：弃用 bar，改用 fill_between，彻底绕过 patches.py 的报错
    # 这将绘制成交量区域，视觉效果和 bar 一样，但逻辑简单得多，不触发图形对象转换错误
    volumes = iren_data['Volume'].fillna(0)
    ax2.fill_between(iren_data.index, 0, volumes, color='lightgreen', alpha=0.5)
    
    ax2.set_ylabel('Volume')
    ax2.grid(True, alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ 图表生成完成 → {OUTPUT_FILE}")

def run_pipeline():
    try:
        iren_data, current_price = fetch_latest_data()
        generate_calibrated_chart(iren_data, current_price)
        
        # 更新 README
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# IREN Quantum Calibrated Predictor\n\n**实时状态** ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC)\n\n"
                    f"- **当前价格**: **${current_price:.2f}**\n\n"
                    f"![Dashboard]({OUTPUT_FILE})")
        print("🎉 全部任务完成！")
    except Exception:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
