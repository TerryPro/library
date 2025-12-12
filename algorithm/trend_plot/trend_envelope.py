import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.seasonal import STL
import mplfinance.original_flavor as mpf

def trend_envelope(df, y_columns=None, window_duration="1min", title="数据包络线图", figsize=None) -> None:
    """
    Plot data envelope for a DataFrame.

    Algorithm:
        name: 数据包络线绘制
        category: trend_plot
        prompt: 请对{VAR_NAME} 绘制数据包络线。使用滚动窗口的最大值和最小值计算上、下包络线，并与原始曲线一起绘制。
        imports: import pandas as pd, import matplotlib.pyplot as plt, import numpy as np
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    y_columns (list): Columns to plot envelope for.
        label: Y轴列名
        widget: column-selector
        priority: critical
    window_duration (str): Time window duration.
        label: 窗口时长
        widget: select
        options: ["10s", "30s", "1min", "5min", "15min", "30min", "1h", "2h", "6h", "12h", "1D"]
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
    envelope_data = result[y_columns].copy()
    
    # Check if the index is a DatetimeIndex
    is_time_series = isinstance(envelope_data.index, pd.DatetimeIndex)
    
    # Calculate window size based on time duration
    window_size = 60  # Default window size if not time series
    if is_time_series:
        # Calculate time difference between consecutive points
        time_diff = envelope_data.index.to_series().diff().median()
        if pd.isna(time_diff):
            time_diff = pd.Timedelta(seconds=1)  # Default to 1 second if no valid difference
        
        # Convert window duration to Timedelta
        window_timedelta = pd.Timedelta(window_duration)
        
        # Calculate window size in points
        window_size = int(window_timedelta / time_diff)
        
        # Ensure minimum window size
        window_size = max(5, window_size)
    
    # Plot envelope for each column
    for col in y_columns:
        # Calculate upper and lower envelopes
        upper_envelope = envelope_data[col].rolling(window=window_size, center=True).max()
        lower_envelope = envelope_data[col].rolling(window=window_size, center=True).min()
        
        # Create plot
        plt.figure(figsize=figsize)
        plt.plot(envelope_data.index, envelope_data[col], label='原始数据', alpha=0.7)
        plt.plot(envelope_data.index, upper_envelope, label=f'上包络线 (窗口={window_duration})', color='red', linestyle='--')
        plt.plot(envelope_data.index, lower_envelope, label=f'下包络线 (窗口={window_duration})', color='green', linestyle='--')
        
        plt.title(f"数据包络线: {col}")
        plt.xlabel('时间' if is_time_series else '索引')
        plt.ylabel(col)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()
