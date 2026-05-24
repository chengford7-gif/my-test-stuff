import yfinance as yf
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


def get_latest_data(symbol):
    print("[INFO] Fetching latest weekly data...")
    try:
        df = yf.download(symbol, period="18mo", interval="1wk", progress=False, auto_adjust=True)
        if df.empty:
            raise ValueError("Empty data")
        df = df.reset_index()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if isinstance(col, tuple) else str(col) for col in df.columns]
        df = df.rename(columns={df.columns[0]: 'Date'})
        for col in df.columns:
            if str(col).lower() in ['close', 'adj close']:
                if col != 'Close':
                    df = df.rename(columns={col: 'Close'})
                break
        return df
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


def generate_projection_chart(df, current_price):
    print("[CHART] Generating improved projection chart with orange wave lines...")
    
    fig, ax = plt.subplots(figsize=(15, 8.5))
    
    # Historical price
    ax.plot(df['Date'], df['Close'], color='#1a1a1a', linewidth=2.0, label='IREN Price')
    ax.set_yscale('log')
    
    # Current price
    ax.axhline(y=current_price, color='#d32f2f', linestyle='--', linewidth=1.2, alpha=0.7)
    ax.text(df['Date'].iloc[-1] + timedelta(days=6), current_price * 1.05, f'Now ${current_price}', fontsize=9, color='#c62828', fontweight='bold')
    
    # === Forward Projection with Orange Wave Lines ===
    last_date = df['Date'].iloc[-1]
    future_weeks = 52
    future_dates = [last_date + timedelta(weeks=i) for i in range(future_weeks)]
    
    # Create segmented projection (more wave-like)
    hpq_target = 133.0
    final_target = 250.0
    
    # Wave (3) projection
    wave3_end = int(future_weeks * 0.45)
    wave3_prices = [current_price + (hpq_target - current_price) * ((i / wave3_end) ** 0.6) for i in range(wave3_end)]
    
    # Wave (4) shallow pullback
    wave4_end = int(future_weeks * 0.55)
    wave4_prices = [hpq_target - (hpq_target - current_price) * 0.25 * ((i - wave3_end) / (wave4_end - wave3_end)) for i in range(wave3_end, wave4_end)]
    
    # Wave (5) extension
    wave5_prices = []
    for i in range(wave4_end, future_weeks):
        progress = (i - wave4_end) / (future_weeks - wave4_end)
        price = hpq_target + (final_target - hpq_target) * (progress ** 0.5)
        wave5_prices.append(price)
    
    # Plot orange dashed wave lines
    ax.plot(future_dates[:wave3_end], wave3_prices, color='#FF6D00', linewidth=2.2, linestyle='--', label='Wave (3) Extension')
    ax.plot(future_dates[wave3_end:wave4_end], wave4_prices, color='#FF6D00', linewidth=1.8, linestyle=':', label='Wave (4) Pullback')
    ax.plot(future_dates[wave4_end:], wave5_prices, color='#FF6D00', linewidth=2.2, linestyle='--', label='Wave (5) Extension')
    
    # Price labels on key points
    ax.annotate(f'${hpq_target:.0f}', xy=(future_dates[wave3_end-3], hpq_target), fontsize=10, color='#e65100', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#fff3e0', edgecolor='#ff6d00'))
    ax.annotate(f'${final_target:.0f}', xy=(future_dates[-5], final_target), fontsize=10, color='#bf360c', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#fbe9e7', edgecolor='#e64a19'))
    
    # Key horizontal levels
    ax.axhline(y=105, color='#1976d2', linestyle=':', linewidth=1.5, alpha=0.7)
    ax.text(future_dates[8], 107, '$105 Zone', fontsize=8.5, color='#1565c0')
    
    ax.axhline(y=133, color='#d32f2f', linestyle=':', linewidth=1.5, alpha=0.8)
    ax.text(future_dates[wave3_end+3], 136, 'HPQ $133.33', fontsize=9, color='#c62828', fontweight='bold')
    
    # Structure label
    ax.annotate('Int Wave (3) → (4) → (5)\nPrimary Wave ⑤ Extension', xy=(future_dates[15], 90), fontsize=9, color='#e65100', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff8e1', edgecolor='#ff6d00', alpha=0.9))
    
    # Title
    ax.set_title('IREN — Quantum Model Forward Projection (May 2026 → May 2027) | Orange Wave Lines', fontsize=13, fontweight='bold', pad=8)
    
    info = f"Current: ${current_price}  |  RPF={RPF}  |  Structure: Int Wave (3) of Primary ⑤"
    ax.text(0.015, 0.96, info, transform=ax.transAxes, fontsize=8.5, fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='#757575', alpha=0.95))
    
    ax.set_ylabel('Price (log)')
    ax.grid(True, which='both', linestyle='--', alpha=0.25)
    ax.legend(loc='upper left', fontsize=8)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] Chart saved: {OUTPUT_FILE}")

if __name__ == "__main__":
    df = get_latest_data(SYMBOL)
    current_price = round(float(df['Close'].iloc[-1]), 2)
    generate_projection_chart(df, current_price)
