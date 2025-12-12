import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.seasonal import STL
import mplfinance.original_flavor as mpf

def trend_ohlc(df, y_columns=None, resample_freq="5T", title="OHLC蜡烛图", figsize=None) -> None:
    """
    Plot OHLC (Open-High-Low-Close) candlestick chart for a DataFrame.

    Algorithm:
        name: OHLC重采样
        category: trend_plot
        prompt: 请对{VAR_NAME} 进行OHLC重采样。将时间序列数据重采样为指定频率的开盘价(Open)、最高价(High)、最低价(Low)和收盘价(Close)，并绘制蜡烛图。
        imports: import pandas as pd, import matplotlib.pyplot as plt, import mplfinance.original_flavor as mpf
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
    y_columns (list): Columns to resample.
        label: Y轴列名
        widget: column-selector
        priority: critical
    resample_freq (str): Resampling frequency.
        label: 重采样频率
        priority: critical
    title (str): Chart title.
        label: 图表标题
        priority: non-critical
    figsize (tuple): Figure size tuple.
        label: 图像尺寸
        priority: non-critical
    
    Returns:
    None
    """
    result = df.copy()
    
    if y_columns is None:
        y_columns = []
    
    # Parse figsize
    if figsize is None:
        figsize = (15, 8)
    elif isinstance(figsize, str):
        try:
            figsize = eval(figsize)
        except:
            figsize = (15, 8)
    
    # Determine Y columns
    if not y_columns:
        # Use all numeric columns if none specified
        y_columns = result.select_dtypes(include=['number']).columns.tolist()
    
    # Check if the index is a DatetimeIndex
    if not isinstance(result.index, pd.DatetimeIndex):
        print("错误: 数据索引不是时间索引，无法进行OHLC重采样。")
        return
    else:
        # Filter to selected columns
        ohlc_data = result[y_columns].copy()
        
        # Perform OHLC resampling for each column
        for col in y_columns:
            # Resample to OHLC
            ohlc = ohlc_data[col].resample(resample_freq).ohlc()
            
            # Plot OHLC chart using mplfinance
            plt.figure(figsize=figsize)
            mpf.candlestick2_ochl(plt.gca(), ohlc['open'], ohlc['high'], ohlc['low'], ohlc['close'], width=0.6, colorup='green', colordown='red', alpha=0.8)
            
            plt.title(f"OHLC Chart for {col} (Resampled to {resample_freq})")
            plt.xlabel('时间')
            plt.ylabel(col)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
