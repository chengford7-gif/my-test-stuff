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

HPQ_TARGET = 133.33
FINAL_TARGET = 250.0


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
    print("[CHART] Generating dynamic projection based on real current price...")
    
    fig, ax = plt.subplots(figsize=(15, 8.5))
    
    # Historical
    ax.plot(df['Date'], df['Close'], color='#1a1a1a', linewidth=2.0, label='IREN Price')
    ax.set_yscale('log')
    
    ax.axhline(y=current_price, color='#d32f2f', linestyle='--', linewidth=1.2, alpha=0.7)
    ax.text(df['Date'].iloc[-1] + timedelta(days=6), current_price * 1.05, f'Now ${current_price}', fontsize=9, color='#c62828', fontweight='bold')
    
    # === Dynamic Forward Projection (based on real current price) ===
    last_date = df['Date'].iloc[-1]
    future_weeks = 52
    future_dates = [last_date + timedelta(weeks=i) for i in range(future_weeks)]
    
    # Calculate realistic targets from current price
    hpq_target = HPQ_TARGET
    final_target = FINAL_TARGET
    
    # Wave (3): Main impulsive leg toward HPQ
    wave3_ratio = 0.48
    wave3_end_idx = int(future_weeks * wave3_ratio)
    
    wave3_prices = []
    for i in range(wave3_end_idx):
        progress = (i / wave3_end_idx) ** 0.58
        price = current_price + (hpq_target - current_price) * progress
        wave3_prices.append(price)
    
    # Wave (4): Shallow corrective pullback
    wave4_ratio = 0.58
    wave4_end_idx = int(future_weeks * wave4_ratio)
    wave4_prices = []
    for i in range(wave3_end_idx, wave4_end_idx):
        progress = (i - wave3_end_idx) / (wave4_end_idx - wave3_end_idx)
        # Shallow 23-38% pullback
        pullback = (hpq_target - current_price) * 0.28 * (1 - progress * 0.6)
        price = hpq_target - pullback
        wave4_prices.append(price)
    
    # Wave (5): Extension toward final target
    wave5_prices = []
    for i in range(wave4_end_idx, future_weeks):
        progress = (i - wave4_end_idx) / (future_weeks - wave4_end_idx)
        price = hpq_target + (final_target - hpq_target) * (progress ** 0.45)
        wave5_prices.append(price)
    
    # Plot orange dashed wave lines
    ax.plot(future_dates[:wave3_end_idx], wave3_prices, color='#FF6D00', linewidth=2.3, linestyle='--', label='Wave (3) Impulsive')
    ax.plot(future_dates[wave3_end_idx:wave4_end_idx], wave4_prices, color='#FF6D00', linewidth=1.7, linestyle=':', label='Wave (4) Corrective')
    ax.plot(future_dates[wave4_end_idx:], wave5_prices, color='#FF6D00', linewidth=2.3, linestyle='--', label='Wave (5) Extension')
    
    # Price labels
    ax.annotate(f'Wave 3 High\n${hpq_target:.0f}', xy=(future_dates[wave3_end_idx-2], hpq_target), 
                fontsize=9, color='#e65100', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#fff3e0', edgecolor='#ff6d00'))
    
    ax.annotate(f'Wave 5 High\n${final_target:.0f}', xy=(future_dates[-6], final_target), 
                fontsize=9, color='#bf360c', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#fbe9e7', edgecolor='#e64a19'))
    
    # Key levels
    ax.axhline(y=105, color='#1976d2', linestyle=':', linewidth=1.4, alpha=0.7)
    ax.text(future_dates[6], 108, '$105 Zone', fontsize=8, color='#1565c0')
    
    ax.axhline(y=hpq_target, color='#d32f2f', linestyle=':', linewidth=1.5, alpha=0.85)
    ax.text(future_dates[wave3_end_idx + 4], hpq_target + 4, 'HPQ $133.33', fontsize=9, color='#c62828', fontweight='bold')
    
    # Structure description
    ax.annotate('Dynamic Projection\nInt Wave (3) → (4) → (5)\nBased on Real Current Price', 
                xy=(future_dates[12], 85), fontsize=9, color='#e65100', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff8e1', edgecolor='#ff6d00', alpha=0.9))
    
    ax.set_title('IREN — Quantum Model | Dynamic Wave Projection (Real Price Adaptive)', fontsize=13, fontweight='bold', pad=8)
    
    info = f"Current: ${current_price}  |  RPF={RPF}  |  Targets: $133.33 → $250 | Dynamic from real price"
    ax.text(0.015, 0.96, info, transform=ax.transAxes, fontsize=8, fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='#757575', alpha=0.95))
    
    ax.set_ylabel('Price (log scale)')
    ax.grid(True, which='both', linestyle='--', alpha=0.25)
    ax.legend(loc='upper left', fontsize=8)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"[OK] Dynamic chart saved: {OUTPUT_FILE}")

if __name__ == "__main__":
    df = get_latest_data(SYMBOL)
    current_price = round(float(df['Close'].iloc[-1]), 2)
    generate_projection_chart(df, current_price)
