import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sys

SYMBOL = "IREN"
OUTPUT_FILE = "iren_quantum_v5.png"
RPF = 0.28


def get_data(symbol):
    print("\ud83d\udd04 Fetching latest data...")
    df = yf.download(symbol, period="18mo", interval="1wk", progress=False)
    if df.empty:
        print("\u274c Failed to fetch data")
        sys.exit(1)
    df = df.reset_index()
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df


def generate_projection_chart(df, current_price):
    print("\ud83c\udfa8 Generating forward-looking Quantum Projection chart...")
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot recent price
    ax.plot(df['Date'], df['Close'], color='black', linewidth=2.0, label='IREN Weekly Close')
    ax.set_yscale('log')
    
    # Current price marker
    ax.axhline(y=current_price, color='red', linestyle='--', linewidth=1.2, alpha=0.7)
    ax.text(df['Date'].iloc[-1] + timedelta(days=10), current_price * 1.08, 
            f'Current: ${current_price}', fontsize=10, color='red', fontweight='bold')
    
    # --- Forward Projection (from now) ---
    last_date = df['Date'].iloc[-1]
    future_weeks = 52  # ~12 months
    
    future_dates = [last_date + timedelta(weeks=i) for i in range(1, future_weeks + 1)]
    
    # Simple but structured projection (you can replace with real model later)
    # Assume Wave (3) extension
    wave3_target = 133.0
    wave3_mid = 105.0
    
    # Create a smooth projection curve
    proj_prices = []
    for i in range(future_weeks):
        progress = i / future_weeks
        # S-curve like impulsive move
        price = current_price + (wave3_target - current_price) * (progress ** 0.7)
        proj_prices.append(price)
    
    ax.plot(future_dates, proj_prices, color='#FF6B00', linewidth=2.5, linestyle='--', label='Projected Impulsive Wave (3)')
    
    # Key Targets
    ax.axhline(y=105, color='#1E88E5', linestyle=':', linewidth=1.8, alpha=0.85)
    ax.text(future_dates[15], 108, 'HPQ Zone $105', fontsize=10, color='#1E88E5', fontweight='bold')
    
    ax.axhline(y=133, color='#D32F2F', linestyle=':', linewidth=2.0, alpha=0.9)
    ax.text(future_dates[30], 138, 'HPQ-Target $133.33', fontsize=11, color='#D32F2F', fontweight='bold')
    
    # Q-Structure reference levels
    ax.axhline(y=44.5, color='#43A047', linestyle='--', linewidth=1.3, alpha=0.6)
    ax.text(df['Date'].iloc[-20], 46, 'Q-Structure \u03bb\u2084 Support (~$44.5)', fontsize=9, color='#2E7D32')
    
    # Wave structure labels on projection
    ax.annotate('Int Wave (3)\nImpulsive Extension', xy=(future_dates[18], 85), fontsize=9.5, 
                color='#E65100', fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFF3E0", edgecolor='#FF6B00', alpha=0.9))
    
    ax.annotate('Potential Wave (5)\nExtension Zone', xy=(future_dates[42], 160), fontsize=9, 
                color='#B71C1C', style='italic')
    
    # Title and Info
    ax.set_title("IREN — Quantum Reality Model | Forward Projection (May 2026 → May 2027)", 
                 fontsize=14, fontweight='bold', pad=12)
    
    info = (
        f"Current: ${current_price}   |   RPF = {RPF}\n"
        "Structure: Primary ⑤ Extension → Int Wave (3) in progress\n"
        "Timeframe: Next 12 months | Log Scale"
    )
    ax.text(0.02, 0.97, info, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.95))
    
    ax.set_ylabel("Price (USD, log scale)")
    ax.grid(True, which="both", linestyle="--", alpha=0.35)
    ax.legend(loc='upper left', fontsize=9)
    
    # X-axis formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"\u2705 Projection chart saved: {OUTPUT_FILE}")


# Run
df = get_data(SYMBOL)
current_price = round(float(df['Close'].iloc[-1].item()), 2)
generate_projection_chart(df, current_price)
