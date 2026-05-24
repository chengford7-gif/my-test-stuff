import sys
import traceback

def run_pipeline():
    try:
        print("🚀 正在初始化环境...")
        import requests
        import json
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        import os
        
        # 强制切换 matplotlib 为 Headless 模式
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from matplotlib.ticker import FixedLocator, FixedFormatter
        print("✅ 环境初始化成功")
        
        # --- [ 这里放入你原本的核心绘图逻辑代码 ] ---
        # (请确保此处代码完整，包括 get_macro_weekly_data, generate_calibrated_tradingview_chart 等函数)
        # ...
        
        print("✅ 脚本运行成功，准备同步...")

    except Exception:
        # 💥 侦探逻辑：把所有错误详细记录到日志
        print("❌ 脚本崩溃，现场诊断信息如下：")
        traceback.print_exc()
        sys.exit(1) # 强制以非正常状态退出，以触发 Action 报错

if __name__ == "__main__":
    run_pipeline()
