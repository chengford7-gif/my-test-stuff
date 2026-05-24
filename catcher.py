import os
import sys
import requests
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # GitHub Actions 无界面环境必须
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# ==================== 配置 ====================
SYMBOL = "IREN"
OUTPUT_FILE = "iren_quantum_vs.png"
RPF = 0.28  # Reality Pull-Back Factor
CURRENT_WAVE = "Primary ⑨ Extension → Int Wave (3) impulsive"

def fetch_latest_data():
    """实时抓取 IREN 和 BTC 数据"""
    print("🔄 正在抓取最新数据...")
    iren = pd.read_csv('https://query1.finance.yahoo.com/v8/finance/chart/IREN?interval=1d&range=2y', storage_options={'User-Agent': 'Mozilla/5.0'})
    # 简化版 yfinance 替代（Actions 环境更稳）
    # 实际使用 yfinance（已安装）
    import yfinance as yf
    iren_data = yf.download(SYMBOL, period="2y", interval="1d")
    btc_data = yf.download("BTC-USD", period="2y", interval="1d")
    
    current_price = round(float(iren_data['Close'].iloc[-1]), 2)
    btc_price = round(float(btc_data['Close'].iloc[-1]), 0)
    
    print(f"✅ IREN 当前价: ${current_price} | BTC: ${btc_price}")
    return iren_data, btc_data, current_price, btc_price

def generate_calibrated_chart(iren_data, current_price, btc_price):
    """生成校准后专业图表（完全复刻 ElliottChart 风格）"""
    print("🎨 正在生成校准图表...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), gridspec_kw={'height_ratios': [3.5, 1]}, sharex=True)
    
    # 主价格图
    ax1.plot(iren_data.index, iren_data['Close'], color='black', linewidth=2.5, label='IREN Price')
    
    # 关键历史标注（复刻你之前的图）
    ax1.annotate('③ $76.87', xy=(iren_data.index[-300], 76.87), xytext=(10, 10),
                 textcoords='offset points', arrowprops=dict(arrowstyle='->'), fontsize=11, color='blue')
    ax1.annotate('④ $30.76', xy=(iren_data.index[-150], 30.76), xytext=(10, -20),
                 textcoords='offset points', arrowprops=dict(arrowstyle='->'), fontsize=11, color='blue')
    
    # 当前价格
    ax1.annotate(f'Now: ${current_price}', xy=(iren_data.index[-1], current_price),
                 xytext=(20, -30), textcoords='offset points', fontsize=12, color='red',
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.9))
    
    # 校准后目标（RPF=0.28）
    ax1.axhline(y=105, color='orange', linestyle='--', linewidth=1.5, alpha=0.8)
    ax1.annotate('(3) $81.50\n(校准后)', xy=(iren_data.index[-1], 81.5), xytext=(20, 10),
                 textcoords='offset points', fontsize=11, color='darkorange')
    
    ax1.axhline(y=105, color='orange', linestyle='--', linewidth=1.5, alpha=0.8)
    ax1.annotate('HPQ: $105 (RPF=0.28)', xy=(iren_data.index[-1], 105), xytext=(20, 40),
                 textcoords='offset points', fontsize=12, color='blue', fontweight='bold')
    
    ax1.axhline(y=133, color='orange', linestyle='--', linewidth=1.5, alpha=0.6)
    ax1.annotate('极限区 $133', xy=(iren_data.index[-1], 133), xytext=(20, 70),
                 textcoords='offset points', fontsize=11, color='darkred')
    
    # Q-Structure 模拟射线
    ax1.plot([iren_data.index[-200], iren_data.index[-1]], [44, 105], color='green', linestyle='-', linewidth=1.5, alpha=0.7, label='Q-Structure λ₄ → λ₁')
    
    ax1.set_title(f'$IREN — Calibrated Quantum Elliott Model (RPF={RPF})\n{Int Wave (3) impulsive | 2026.10-11 BTC喇叭口共振}', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Price ($)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # 成交量
    ax2.bar(iren_data.index, iren_data['Volume'], color='lightgreen', alpha=0.7, width=0.8)
    ax2.set_ylabel('Volume')
    ax2.grid(True, alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ 图表生成完成 → {OUTPUT_FILE}")

def update_readme(current_price):
    """更新 README.md"""
    content = f"""# IREN Quantum Calibrated Predictor

**实时状态**（{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC+8）

- **当前价格**：**${current_price}**
- **模型**：Calibrated Quantum Elliott Model (RPF=0.28)
- **波浪结构**：Primary ⑨ Extension → Int Wave (3) impulsive
- **共振窗口**：**2026年10月–11月**（$105–133 + BTC 130k+ 喇叭口顶）
- **校准目标**：HPQ $105（原$133.33）

![IREN Quantum Dashboard](iren_quantum_vs.png)

---
由 GitHub Actions 每日自动更新 | 基于 @ElliottChart + tradermige 周期共振
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ README.md 更新完成")

def run_pipeline():
    try:
        iren_data, btc_data, current_price, btc_price = fetch_latest_data()
        generate_calibrated_chart(iren_data, current_price, btc_price)
        update_readme(current_price)
        print("🎉 全部任务完成！")
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
