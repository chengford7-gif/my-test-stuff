import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# 💥 强制切换 matplotlib 为 Headless 静态渲染模式
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FixedLocator, FixedFormatter

# 🎯 目标资产
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
    
    # 💥 建立主副双图布局
    fig, (ax, ax_vol) = plt.subplots(2, 1, figsize=(14, 8.5), facecolor='#ffffff', 
                                    gridspec_kw={'height_ratios': [5.8, 1.2]})
    fig.subplots_adjust(hspace=0.05)
    
    # ---- 【主图：价格时空矩阵】 ----
    ax.set_facecolor('#ffffff')
    ax.set_yscale('log')
    ax.yaxis.tick_right() # 坐标轴严格右置
    ax.yaxis.set_label_position("right")
    
    # 绘制历史真实黑色粗价格K线趋势
    ax.plot(df['date'], df['close'], color='#111111', linewidth=1.5, label='IREN Close', zorder=3)
    
    # ⏱️ 时间轴核心锚点
    latest_date = df['date'].iloc[-1]
    w3_date = pd.to_datetime('2025-10-15')
    w4_date = pd.to_datetime('2026-04-15')
    
    # 历史大浪黄金锚点
    w3_val = 76.87
    w4_val = 30.76
    
    ax.text(w3_date, w3_val * 1.06, f"③\n${w3_val:.2f}", color='#1A365D', fontsize=10, fontweight='bold', ha='center', va='bottom')
    ax.text(w4_date, w4_val * 0.90, f"④ ${w4_val:.2f}", color='#1A365D', fontsize=10, fontweight='bold', ha='center', va='top')

    # 【固定元素】：右侧 Now 实时标签
    current_price = 56.83
    ax.text(latest_date + timedelta(weeks=1), current_price, f" Now: $56.83 ", color='#ffffff', zorder=5,
            bbox=dict(facecolor='#E74C3C', edgecolor='none', boxstyle='square,pad=0.3'), fontsize=9, fontweight='bold', va='center')
    
    # 未来时空预测点（月份映射锚点）
    future_weeks = 52 # 进一步拓宽右侧时间轴，留足画虚线的空档
    forecast_dates = [latest_date + timedelta(weeks=i) for i in range(0, future_weeks + 1)]
    x_min = df['date'].iloc[20]
    x_max = forecast_dates[-1] + timedelta(weeks=4)
    
    t_w3 = latest_date + timedelta(weeks=10)   # 2026年7月 (子浪3)
    t_w4 = latest_date + timedelta(weeks=18)   # 2026年9月 (子浪4)
    t_w5 = latest_date + timedelta(weeks=42)   # 2027年1月-2月 (最终浪5)
    
    # 💥 【重磅物理分流一】：将所有斐波那契浅灰小字挪动到画布左侧半场，彻底跟右侧大标签隔离
    wave_range = w3_val - w4_val
    fib_levels = [0.0, 0.236, 0.382, 0.500, 0.618, 0.786, 1.0]
    fib_colors = ['#7F8C8D', '#95A5A6', '#BDC3C7', '#BDC3C7', '#95A5A6', '#7F8C8D', '#7F8C8D']
    
    for level, color in zip(fib_levels, fib_colors):
        fib_price = w3_val - (level * wave_range)
        ax.axhline(y=fib_price, color=color, linestyle=':', linewidth=0.5, alpha=0.4, zorder=1)
        fib_text = f"Fib {level:.3f} (${fib_price:.2f})"
        # 挪到历史大浪 ④ 的左侧空白处（Jul 25附近），避开未来的主升浪线
        ax.text(pd.to_datetime('2025-08-01'), fib_price * 1.03, fib_text, 
                color='#95A5A6', fontsize=7.5, va='bottom', ha='left', alpha=0.6)

    # 绘制等价射线群（Q-Structure 纯细几何线矩阵）
    all_dates = list(df['date']) + forecast_dates[1:]
    x_idx = np.arange(len(all_dates))
    ray_base_idx = 15
    ray_top = 1.2 + 0.015 * (x_idx - ray_base_idx)
    ray_mid = 1.2 + 0.011 * (x_idx - ray_base_idx)
    ray_bot = 1.2 + 0.007 * (x_idx - ray_base_idx)
    
    ax.plot(all_dates, np.exp(ray_top), color='#9B59B6', linestyle=':', linewidth=0.8, alpha=0.3)
    ax.plot(all_dates, np.exp(ray_mid), color='#27AE60', linestyle='--', linewidth=0.8, alpha=0.3)
    ax.plot(all_dates, np.exp(ray_bot), color='#9B59B6', linestyle='-.', linewidth=0.8, alpha=0.2)
    
    # 💥 【重磅物理分流二】：微观子浪标签错位微调，防止被价格粗线横穿
    ax.text(t_w3, 81.50 * 1.12, "(3)\n$81.50\n~Est: Jul 26", color='#2980B9', fontsize=8.5, fontweight='bold', ha='center', va='bottom')
    ax.text(t_w4, 64.80 * 0.82, "(4)\n$64.80\n~Est: Sep 26", color='#2980B9', fontsize=8.5, fontweight='bold', ha='center', va='top')
    
    # 💥 【重磅物理分流三】：右侧三大目标卡片「时间轴阶梯化平移」阻断粘连！
    # 不再让它们站在同一条垂直线上。价格越高的标签，在时间轴上越往右靠，利用斜率自然错开空间！
    x_hpq = t_w5 + timedelta(weeks=2)     # $105 放在前段
    x_133 = t_w5 + timedelta(weeks=12)    # $133 往右挪 12 周
    x_qtg = t_w5 + timedelta(weeks=22)    # $172 往右挪 22 周
    
    # 对应绘制非对称的目标指导横向虚线
    ax.plot([latest_date, x_hpq], [105.00, 105.00], color='#1F4E79', linestyle='--', linewidth=0.8, alpha=0.6)
    ax.plot([latest_date, x_133], [133.33, 133.33], color='#2980B9', linestyle='--', linewidth=0.8, alpha=0.6)
    ax.plot([latest_date, x_qtg], [172.00, 172.00], color='#34495E', linestyle='--', linewidth=0.8, alpha=0.6)

    # 1. 核心 HPQ 校准目标位（最先落位）
    ax.text(x_hpq, 105.00, " HPQ: $105.00 \n(Est: Nov-Dec 2026) ", color='#ffffff', zorder=5, ha='left',
            bbox=dict(facecolor='#1F4E79', edgecolor='none', boxstyle='square,pad=0.3'), fontsize=8.5, fontweight='bold', va='center')
    
    # 2. 原版经典大浪目标回归位（中段落位）
    ax.text(x_133, 133.33, " HPQ-Target: $133.33 \n(Est: Jan 2027 Window) ", color='#ffffff', zorder=5, ha='left',
            bbox=dict(facecolor='#2980B9', edgecolor='none', boxstyle='square,pad=0.3'), fontsize=8.5, fontweight='bold', va='center')
    
    # 3. 终极宏观大目标位（末端最高位落位）
    ax.text(x_qtg, 172.00, " Q-Target: $172.00 \n(Est: Q1 2027 Peak) ", color='#ffffff', zorder=5, ha='left',
            bbox=dict(facecolor='#34495E', edgecolor='none', boxstyle='square,pad=0.3'), fontsize=8.5, fontweight='bold', va='center')

    # 绘制微观五浪上升路径
    wave_x = [mdates.date2num(latest_date), mdates.date2num(t_w3), mdates.date2num(t_w4), mdates.date2num(t_w5)]
    wave_y_log = [np.log(current_price), np.log(81.50), np.log(64.80), np.log(105.00)]
    poly = np.poly1d(np.polyfit(wave_x, wave_y_log, 2))
    px = np.linspace(mdates.date2num(latest_date), mdates.date2num(t_w5), 50)
    ax.plot(mdates.num2date(px), np.exp(poly(px)), color='#00A3E0', linewidth=2.0, zorder=4)

    # 顶部中央大标题
    title_text = "$IREN — Calibrated Quantum Elliott Model (RPF=0.28)\n2026.5.24 Update | Int Wave (3) Impulsive"
    ax.text(0.5, 0.95, title_text, transform=ax.transAxes, fontsize=11, fontweight='bold', color='#111111',
            bbox=dict(facecolor='#ffffff', edgecolor='#333333', linewidth=1.0, boxstyle='square,pad=0.4'),
            ha='center', va='top', zorder=5)

    # 纵坐标轴标准对数刻度清洗
    log_ticks = [1.00, 2.30, 5.50, 13.00, 32.00, 56.83, 76.87, 105.00, 133.33, 172.00, 250.00]
    ax.yaxis.set_major_locator(FixedLocator(log_ticks))
    ax.yaxis.set_major_formatter(FixedFormatter([f"${t:.2f}" if t in [56.83, 105.00, 133.33, 172.00] else f"{t:.2f}" if t == 76.87 else f"{int(t)}" for t in log_ticks]))
    
    ax.grid(True, which="both", linestyle=':', color='#E5E5E5', linewidth=0.7)
    ax.set_xticklabels([])
    ax.set_xlim(x_min, x_max + timedelta(weeks=36)) # 给阶梯化平移后的三大卡片留出绝对充足的右侧画布
    ax.set_ylim(0.8, 420.0)
    
    # ---- 【副图：底部红绿相间真实成交量】 ----
    ax_vol.set_facecolor('#ffffff')
    ax_vol.yaxis.tick_right()
    
    colors = ['#2ECC71' if df['close'].iloc[i] >= df['open'].iloc[i] else '#E74C3C' for i in range(len(df))]
    ax_vol.bar(df['date'], df['volume'], width=5.0, color=colors, alpha=0.7, zorder=2)
    
    ax_vol.grid(True, linestyle=':', color='#E5E5E5', linewidth=0.7)
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
    ax_vol.set_xlim(x_min, x_max + timedelta(weeks=36))
    ax_vol.set_ylim(0, df['volume'].max() * 1.1)
    
    ax.text(0.85, 0.05, "Elliott Chart", transform=ax.transAxes, fontsize=14, color='#333333', alpha=0.8, fontweight='bold')
    
    fig.autofmt_xdate()
    plt.savefig('iren_quantum_v5.png', dpi=150, bbox_inches='tight')
    plt.close()

# 执行同步覆盖刷新流程
df = get_macro_weekly_data(SYMBOL)
if df is not None and not df.empty:
    generate_calibrated_tradingview_chart(df)
    
    w3_val, w4_val = 76.87, 30.76
    wave_range = w3_val - w4_val
    
    report = f"# $IREN — Calibrated Quantum Elliott Model 看板\n\n"
    report += f"> 📐 **排版引擎深度校准**: 已通过时空不匀称平移算法（Staggered Offset）彻底解决右侧对数坐标轴标签粘连、覆盖的视觉 Bug。\n\n"
    report += f"### 📊 现实强化校准因子\n"
    report += f"* **更新时间**：`2026-05-24`\n"
    report += f"* **校准核心引力系数 (Calibrated RPF)**：`0.28`\n"
    report += f"* **当前波段状态**：`Int Wave (3) Impulsive`\n\n"
    report += f"### 🌊 极致清晰的时空量化主图\n"
    report += f"![Quantum Elliott Chart](iren_quantum_v5.png?v={int(datetime.now().timestamp())})\n\n"
    report += f"--- \n"
    report += f"### 📊 动态斐波那契及战略预期矩阵\n"
    report += f"| 结构坐标点 | 价格位 | 交易战术参考中枢 | 🎯 预期达成时间窗 |\n"
    report += f"| :--- | :--- | :--- | :--- |\n"
    report += f"| **校准 Q-Target** | `$172.00` | 施加现实拉回模型后的长线扩展终点 | **2027 年 第一季度 (Q1 Peak)** |\n"
    report += f"| **原版波五扩展目标** | `$133.33` | 经典艾略特 5 浪时空强共振压力位 | **2027 年 1 月 前后窗口** |\n"
    report += f"| **核心 HPQ-Target** | `$105.00` | 经 RPF=0.28 压制修正后的第一波段清算点 | **2026 年 11 月 - 12 月** |\n"
    report += f"| **微观子浪 (3) 高点** | `$81.50` | 内部冲顶清算位，多头加速赶顶目标 | **2026 年 7 月 期间** |\n"
    report += f"| **微观子浪 (4) 低点** | `$64.80` | 蓄势换手期，允许的极限回踩支撑中枢 | **2026 年 9 月 期间** |\n"
    report += f"| **Fib 0.618 黄金坑** | `${w3_val - 0.618 * wave_range:.2f}` | **大周期绝对防御带**，针对 250,000 USD 新主仓的机械加仓区 | **宏观结构核心强支撑** |\n\n"
    report += f"📜 *免责声明: All content reflects personal Elliott Wave + Quantum Model analysis and is not intended to serve as financial advice.*\n"
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(report)
    print("✅ 终极防粘连错位编排代码已 100% 部署就绪！")
