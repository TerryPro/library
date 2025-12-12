import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.seasonal import STL
import mplfinance.original_flavor as mpf

def trend_ewma(df, y_columns=None, span=60, title="指数加权趋势图", figsize=None) -> None:
    """
    Plot EWMA (Exponentially Weighted Moving Average) trend chart for a DataFrame.

    Algorithm:
        name: 指数加权趋势
        category: trend_plot
        prompt: 请对{VAR_NAME} 绘制 EWMA（指数加权移动平均）趋势线。使用 pandas 的 ewm(span=...).mean() 计算趋势，并使用 matplotlib 将原始数据与 EWMA 趋势曲线叠加展示。
        imports: import pandas as pd, import matplotlib.pyplot as plt
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    y_columns (list): Columns to plot EWMA for.
        label: Y轴列名
        widget: column-selector
        priority: critical
    span (int): Smoothing span.
        label: 平滑跨度
        min: 5
        max: 300
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
    
    # Set Chinese font support
    plt.rcParams['font.sans-serif'] = ['SimHei']  # Use SimHei for Chinese
    plt.rcParams['axes.unicode_minus'] = False   # Fix minus sign display
    
    # Filter to selected columns
    ewma_data = result[y_columns].copy()
    
    # Plot EWMA for each column
    for col in y_columns:
        # Calculate EWMA
        ewma_data[f'{col}_EWMA'] = ewma_data[col].ewm(span=span).mean()
        
        # Create plot
        plt.figure(figsize=figsize)
        plt.plot(ewma_data.index, ewma_data[col], label='原始数据', alpha=0.4)
        plt.plot(ewma_data.index, ewma_data[f'{col}_EWMA'], label=f'指数加权平均线 (span={span})', linewidth=2, color='orange')
        
        plt.title(f"指数加权趋势: {col}" if title == "指数加权趋势图" else title)
        plt.xlabel('时间' if isinstance(ewma_data.index, pd.DatetimeIndex) else '索引')
        plt.ylabel(col)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()
