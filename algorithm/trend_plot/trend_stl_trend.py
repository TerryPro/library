import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.seasonal import STL
import mplfinance.original_flavor as mpf

def trend_stl_trend(df, y_columns=None, seasonal=7, robust=True, title="STL 趋势分量图", figsize=None) -> None:
    """
    Plot STL (Seasonal-Trend decomposition using LOESS) trend component for a DataFrame.

    Algorithm:
        name: STL 趋势分量
        category: trend_plot
        prompt: 请对{VAR_NAME} 执行 STL 分解并提取趋势分量。使用 statsmodels.tsa.seasonal.STL 提取趋势，绘制趋势曲线并与原始数据对比显示。
        imports: from statsmodels.tsa.seasonal import STL, import matplotlib.pyplot as plt, import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
    y_columns (list): Columns to decompose.
        label: Y轴列名
        widget: column-selector
        priority: critical
    seasonal (int): Seasonal period.
        label: 季节周期
        min: 3
        max: 100
        priority: non-critical
    robust (bool): Whether to use robust estimation.
        label: 稳健估计
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
    stl_data = result[y_columns].copy()
    
    # Handle frequency for DatetimeIndex
    if isinstance(stl_data.index, pd.DatetimeIndex):
        if stl_data.index.freq is None:
            inferred_freq = pd.infer_freq(stl_data.index)
            if inferred_freq:
                stl_data = stl_data.asfreq(inferred_freq).interpolate()
    
    # Plot STL trend for each column
    for col in y_columns:
        try:
            res = STL(stl_data[col], seasonal=seasonal, robust=robust).fit()
            
            # Create plot
            plt.figure(figsize=figsize)
            plt.plot(stl_data.index, stl_data[col], label='原始数据', alpha=0.4)
            plt.plot(stl_data.index, res.trend, label='STL 趋势分量', linewidth=2, color='brown')
            
            plt.title(f"STL 趋势分量: {col}" if title == "STL 趋势分量图" else title)
            plt.xlabel('时间' if isinstance(stl_data.index, pd.DatetimeIndex) else '索引')
            plt.ylabel(col)
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"{col} 的 STL 分解失败: {e}")
