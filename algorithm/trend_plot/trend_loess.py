import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.seasonal import STL
import mplfinance.original_flavor as mpf

def trend_loess(df: pd.DataFrame, y_columns: list = None, frac: float = 0.1, title: str = "LOESS趋势图", figsize: tuple = None) -> None:
    """
    Plot LOESS (Locally Weighted Scatterplot Smoothing) trend chart for a DataFrame.

    Algorithm:
        name: LOESS 趋势
        category: trend_plot
        prompt: 请对{VAR_NAME} 绘制 LOESS 平滑趋势。使用 statsmodels.nonparametric.smoothers_lowess.lowess 进行平滑并绘制趋势曲线；若缺少该库，可退化为 rolling().mean()。

    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    y_columns (list): Columns to plot LOESS for.
        label: Y轴列名
        widget: column-selector
        priority: critical
    frac (float): Smoothing fraction.
        label: 平滑因子
        min: 0.05
        max: 0.5
        step: 0.05
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
    loess_data = result[y_columns].dropna().copy()
    
    # Plot LOESS for each column
    for col in y_columns:
        try:
            # Lowess requires numeric x-axis
            x = np.arange(len(loess_data))
            y = loess_data[col].values
            
            # Calculate LOESS
            lowess = sm.nonparametric.lowess(y, x, frac=frac)
            
            # Create plot
            plt.figure(figsize=figsize)
            plt.plot(loess_data.index, y, label='原始数据', alpha=0.4)
            plt.plot(loess_data.index, lowess[:, 1], label=f'LOESS 趋势 (平滑因子={frac})', linewidth=2, color='green')
            
            plt.title(f"LOESS 趋势: {col}" if title == "LOESS趋势图" else title)
            plt.xlabel('时间' if isinstance(loess_data.index, pd.DatetimeIndex) else '索引')
            plt.ylabel(col)
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"LOESS计算失败，尝试使用移动平均线替代: {e}")
            # Fallback to moving average if LOESS fails
            window_size = max(5, int(len(loess_data) * frac))
            loess_data[f'{col}_MA'] = loess_data[col].rolling(window=window_size, center=True).mean()
            
            plt.figure(figsize=figsize)
            plt.plot(loess_data.index, loess_data[col], label='原始数据', alpha=0.4)
            plt.plot(loess_data.index, loess_data[f'{col}_MA'], label=f'移动平均线 (窗口={window_size})', linewidth=2, color='green')
            
            plt.title(f"LOESS 趋势: {col}" if title == "LOESS趋势图" else title)
            plt.xlabel('时间' if isinstance(loess_data.index, pd.DatetimeIndex) else '索引')
            plt.ylabel(col)
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.show()
