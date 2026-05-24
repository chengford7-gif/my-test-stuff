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


def find_recent_swing_low(df, lookback=30):
    recent = df['Close'].iloc[-lookback:]
    min_idx = recent.idxmin()
    return df.loc[min_idx, 'Date'], df.loc[min_idx, 'Close']


def generate_projection_chart(df, current_price):
    print("[CHART] Generating chart with clear prediction curve...")
    
    fig, ax = plt.subplots(figsize=(15, 8.5))
    
    # Historical price (solid)
    ax.plot(df['Date'], df['Close'], color='#1a1a1a', linewidth=2.2, label='Historical Price')
    ax.set_yscale('log')
    
    # Current price
    ax.axhline(y=current_price, color='#d32f2f', linestyle='--', linewidth=1.2, alpha=0.7)
    ax.text(df['Date'].iloc[-1] + timedelta(days=6), current_price * 1.05, f'Now ${current_price}', fontsize=9, color='#c62828', fontweight='bold')
    
    # Reference swing low
    swing_date, swing_low = find_recent_swing_low(df, lookback=30)
    measured_move = current_price - swing_low
    
    last_date = df['Date'].iloc[-1]
    future_weeks = 52
    future_dates = [last_date + timedelta(weeks=i) for i in range(future_weeks)]
    
    # === Dynamic Targets ===
    wave3_target = current_price + measured_move * 1.85
    wave4_low = wave3_target - (wave3_target - current_price) * 0.30
    wave5_target = wave3_target + (wave3_target - current_price) * 0.75
    
    wave3_end_idx = int(future_weeks * 0.42)
    wave4_end_idx = int(future_weeks * 0.55)
    
    # Build segments
    wave3_prices = [current_price + (wave3_target - current_price) * ((i / wave3_end_idx) ** 0.55) for i in range(wave3_end_idx)]
    wave4_prices = []
    for i in range(wave3_end_idx, wave4_end_idx):
        progress = (i - wave3_end_idx) / (wave4_end_idx - wave3_end_idx)
        price = wave3_target - (wave3_target - current_price) * 0.30 * (1 - progress * 0.4)
        wave4_prices.append(price)
    wave5_prices = []
    for i in range(wave4_end_idx, future_weeks):
        progress = (i - wave4_end_idx) / (future_weeks - wave4_end_idx)
        price = wave4_low + (wave5_target - wave4_low) * (progress ** 0.5)
        wave5_prices.append(price)
    
    # === Main Prediction Curve (prominent) ===
    all_future_prices = wave3_prices + wave4_prices + wave5_prices
    ax.plot(future_dates, all_future_prices, color='#FF6D00', linewidth=2.8, linestyle='--', 
            label='Main Prediction Curve (Dynamic)', alpha=0.85)
    
    # Sub wave lines (lighter)
    ax.plot(future_dates[:wave3_end_idx], wave3_prices, color='#FF6D00', linewidth=1.8, linestyle='--', alpha=0.6)
    ax.plot(future_dates[wave3_end_idx:wave4_end_idx], wave4_prices, color='#FF6D00', linewidth=1.4, linestyle=':', alpha=0.6)
    ax.plot(future_dates[wave4_end_idx:], wave5_prices, color='#FF6D00', linewidth=1.8, linestyle='--', alpha=0.6)
    
    # Target labels
    ax.annotate(f'Wave 3\n${wave3_target:.1f}', xy=(future_dates[wave3_end_idx-2], wave3_target), fontsize=9, color='#e65100', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#fff3e0', edgecolor='#ff6d00'))
    ax.annotate(f'Wave 5\n${wave5_target:.1f}', xy=(future_dates[-5], wave5_target), fontsize=9, color='#bf360c', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#fbe9e7', edgecolor='#e64a19'))
    
    # Fib reference
    fib_1618 = current_price + measured_move * 1.618
    ax.axhline(y=fib_1618, color='#1976d2', linestyle=':', linewidth=1.3, alpha=0.65)
    ax.text(future_dates[8], fib_1618 * 1.03, f'1.618x ~${fib_1618:.1f}', fontsize=8, color='#1565c0')
    
    # Annotation
    ax.annotate('Main Prediction Curve\nDynamic Fib Projection\nInt Wave (3) → (4) → (5)', 
                xy=(future_dates[12], wave3_target * 0.82), fontsize=9, color='#e65100', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff8e1', edgecolor='#ff6d00', alpha=0.9))
    
    ax.set_title('IREN — Quantum Model | Clear Prediction Curve (Dynamic Fibonacci)', fontsize=13, fontweight='bold', pad=8)
    
    info = f"Current: ${current_price}  |  RPF={RPF}  |  Dynamic Targets from Real Price + Fib"
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
    print(f"[OK] Chart with prominent prediction curve saved: {OUTPUT_FILE}")

if __name__ == "__main__":
    df = get_latest_data(SYMBOL)
    current_price = round(float(df['Close'].iloc[-1]), 2)
    generate_projection_chart(df, current_price)
