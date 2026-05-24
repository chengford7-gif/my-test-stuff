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
    """Fetch weekly data with robust column handling for different yfinance versions."""
    print("[INFO] Fetching latest weekly data...")
    try:
        df = yf.download(
            symbol,
            period="18mo",
            interval="1wk",
            progress=False,
            auto_adjust=True
        )
        if df.empty:
            raise ValueError("Empty data returned")

        df = df.reset_index()

        # Step 1: Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if isinstance(col, tuple) else str(col) for col in df.columns]

        # Step 2: Rename first column to 'Date' (handles 'index', 'Date', etc.)
        df = df.rename(columns={df.columns[0]: 'Date'})

        # Step 3: Find and standardize 'Close' column
        close_col = None
        for col in df.columns:
            if str(col).lower() in ['close', 'adj close', 'adjclose']:
                close_col = col
                break
        
        if close_col and close_col != 'Close':
            df = df.rename(columns={close_col: 'Close'})

        # Final safety check
        if 'Date' not in df.columns or 'Close' not in df.columns:
            print("[WARNING] Columns after processing:", list(df.columns))
            # Last resort: assume standard order
            if len(df.columns) >= 2:
                df.columns = ['Date', 'Close'] + list(df.columns[2:])

        return df

    except Exception as e:
        print(f"[ERROR] Data fetch failed: {e}")
        sys.exit(1)


def generate_projection_chart(df, current_price):
    """Clean forward projection chart for next 12 months."""
    print("[CHART] Generating forward 12-month Quantum Projection chart...")
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    ax.plot(df['Date'], df['Close'], color='black', linewidth=1.8, label='IREN Weekly Close')
    ax.set_yscale('log')
    
    ax.axhline(y=current_price, color='#E53935', linestyle='--', linewidth=1.3, alpha=0.8)
    ax.text(df['Date'].iloc[-1] + timedelta(days=8), current_price * 1.06, 
            f'Current: ${current_price}', fontsize=10, color='#C62828', fontweight='bold')
    
    # Forward projection
    last_date = df['Date'].iloc[-1]
    future_weeks = 52
    future_dates = [last_date + timedelta(weeks=i) for i in range(1, future_weeks + 1)]
    
    hpq_target = 133.0
    proj_prices = []
    for i in range(future_weeks):
        progress = (i / future_weeks) ** 0.65
        price = current_price + (hpq_target - current_price) * progress
        proj_prices.append(price)
    
    ax.plot(future_dates, proj_prices, color='#FF6D00', linewidth=2.4, linestyle='--', 
            label='Projected Path (Int Wave 3 Extension)')
    
    ax.axhline(y=105, color='#1E88E5', linestyle=':', linewidth=1.6, alpha=0.85)
    ax.text(future_dates[12], 108, 'HPQ Zone ~$105', fontsize=9.5, color='#1565C0', fontweight='bold')
    
    ax.axhline(y=133, color='#D32F2F', linestyle=':', linewidth=1.8, alpha=0.9)
    ax.text(future_dates[28], 138, 'HPQ-Target $133.33', fontsize=10.5, color='#B71C1C', fontweight='bold')
    
    ax.axhline(y=44.5, color='#43A047', linestyle='--', linewidth=1.2, alpha=0.6)
    ax.text(df['Date'].iloc[-18], 46, 'Q-Structure Support Zone', fontsize=8.5, color='#2E7D32')
    
    ax.annotate('Currently in Int Wave (3)\nof Primary Wave 5 Extension', 
                xy=(future_dates[10], 78), fontsize=9, color='#E65100', fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.4", facecolor='#FFF8E1', edgecolor='#FF6D00', alpha=0.92))
    
    ax.set_title("IREN Quantum Reality Model | Forward Projection (May 2026 - May 2027)", 
                 fontsize=13, fontweight='bold', pad=10)
    
    info_text = (
        f"Current Price: ${current_price}     RPF = {RPF}\n"
        "Structure: Primary Wave (5) Extension | Int Wave (3) in progress\n"
        "Projection: Next 12 months | Log Scale"
    )
    ax.text(0.015, 0.96, info_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#616161", alpha=0.96))
    
    ax.set_ylabel("Price (USD, log scale)")
    ax.grid(True, which="both", linestyle="--", alpha=0.3)
    ax.legend(loc='upper left', fontsize=8.5)
    
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
