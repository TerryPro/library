import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.seasonal import STL
import mplfinance.original_flavor as mpf

def trend_ma(df: pd.DataFrame, y_columns: list = None, window_size: int = 60, center: bool = True, title: str = "移动平均趋势图", figsize: tuple = None) -> None:
    """
    Plot moving average trend chart for a DataFrame.

    Algorithm:
        name: 移动平均趋势
        category: trend_plot
        prompt: 请对{VAR_NAME} 绘制移动平均趋势线。使用 pandas 的 rolling().mean() 计算趋势线，并用 matplotlib 绘制原始曲线与趋势线，添加网格、图例与中文标签。

    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    y_columns (list): Columns to plot moving average for.
        label: Y轴列名
        widget: column-selector
        priority: critical
    window_size (int): Moving average window size.
        label: 窗口大小
        min: 5
        max: 300
        priority: critical
    center (bool): Whether to center the moving average.
        label: 居中对齐
        priority: non-critical
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
    
    # Set Chinese font support
    plt.rcParams['font.sans-serif'] = ['SimHei']  # Use SimHei for Chinese
    plt.rcParams['axes.unicode_minus'] = False   # Fix minus sign display
    
    # Filter to selected columns
    ma_data = result[y_columns].copy()
    
    # Plot moving average for each column
    for col in y_columns:
        # Calculate moving average
        ma_data[f'{col}_MA'] = ma_data[col].rolling(window=window_size, center=center).mean()
        
        # Create plot
        plt.figure(figsize=figsize)
        plt.plot(ma_data.index, ma_data[col], label='原始数据', alpha=0.4)
        plt.plot(ma_data.index, ma_data[f'{col}_MA'], label=f'移动平均线 (窗口={window_size})', linewidth=2, color='red')
        
        plt.title(f"移动平均趋势: {col}" if title == "移动平均趋势图" else title)
        plt.xlabel('时间' if isinstance(ma_data.index, pd.DatetimeIndex) else '索引')
        plt.ylabel(col)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()
