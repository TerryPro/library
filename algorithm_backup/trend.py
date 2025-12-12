import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.seasonal import STL
import mplfinance.original_flavor as mpf


def trend_plot(df, x_column="", y_columns=None, plot_type="叠加显示", title="趋势图", xlabel="", ylabel="", grid=True, figsize=None) -> None:
    """
    Plot trend chart for a DataFrame.

    Algorithm:
        name: 通用趋势图 (Trend)
        category: trend_plot
        prompt: 请根据配置绘制 {VAR_NAME} 的趋势图。支持自定义 X 轴、Y 轴列、标题、网格等设置。
        imports: import matplotlib.pyplot as plt, import pandas as pd, import math
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    x_column (str): Column to use as X-axis.
        label: X轴列名
        widget: column-selector
        priority: critical
    y_columns (list): Columns to plot on Y-axis.
        label: Y轴列名
        widget: column-selector
        priority: critical
    plot_type (str): Plot type (叠加显示, 堆叠显示, 分栏显示, 网格显示).
        label: 绘图方式
        options: ["叠加显示", "堆叠显示", "分栏显示", "网格显示"]
        priority: critical
    title (str): Chart title.
        label: 图表标题
        priority: non-critical
    xlabel (str): X-axis label.
        label: X轴标签
        priority: non-critical
    ylabel (str): Y-axis label.
        label: Y轴标签
        priority: non-critical
    grid (bool): Whether to show grid.
        label: 显示网格
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
    
    print(f"Plotting trend chart using {plot_type}")
    
    # Parse figsize
    if figsize is None:
        figsize = (15, 8)
    elif isinstance(figsize, str):
        try:
            figsize = eval(figsize)
        except:
            figsize = (15, 8)
    
    # Convert Chinese plot_type to English for code logic
    plot_type_en = plot_type
    if plot_type == '叠加显示':
        plot_type_en = 'overlay'
    elif plot_type == '堆叠显示':
        plot_type_en = 'stacked'
    elif plot_type == '分栏显示':
        plot_type_en = 'subplots'
    elif plot_type == '网格显示':
        plot_type_en = 'grid'
    
    # Determine if the DataFrame is a time series
    is_time_series = False
    x_data = None
    
    # Check if index is a DatetimeIndex (most common case for time series)
    if isinstance(result.index, pd.DatetimeIndex):
        is_time_series = True
        x_data = result.index
    
    # If x_column is specified, use it instead of index
    if x_column and x_column in result.columns:
        # Check if the specified column is datetime-like
        if pd.api.types.is_datetime64_any_dtype(result[x_column]):
            is_time_series = True
            x_data = result[x_column]
        else:
            # Try to convert to datetime if it's not already
            try:
                x_data = pd.to_datetime(result[x_column])
                is_time_series = True
                print(f"Converted column '{x_column}' to datetime")
            except Exception as e:
                print(f"Warning: Could not convert column '{x_column}' to datetime. Using original values.")
                x_data = result[x_column]
    elif x_column:
        # x_column specified but not found, use index
        print(f"Warning: X column '{x_column}' not found, using index.")
        if isinstance(result.index, pd.DatetimeIndex):
            is_time_series = True
        x_data = result.index
    
    # If x_data is still None (shouldn't happen), use index
    if x_data is None:
        x_data = result.index
        if isinstance(x_data, pd.DatetimeIndex):
            is_time_series = True
    
    if not y_columns:
        # If empty (or parsed as empty), fallback to numeric columns only
        y_columns = result.select_dtypes(include=['number']).columns.tolist()
    
    # Remove x_col from y_cols if present to avoid plotting time/index on Y-axis
    if x_column and x_column in y_columns:
        y_columns.remove(x_column)
    
    # Support Chinese characters in title and labels if needed
    plt.rcParams['font.sans-serif'] = ['SimHei'] # Use SimHei for Chinese
    plt.rcParams['axes.unicode_minus'] = False   # Fix minus sign
    
    # Create plot based on plot_type_en
    if plot_type_en == 'overlay':
        # Overlay plot (default) - all lines on same axes
        plt.figure(figsize=figsize)
        for col in y_columns:
            if col in result.columns:
                plt.plot(x_data, result[col], label=col)
            else:
                print(f"Warning: Y column '{col}' not found.")
        plt.title(title)
        plt.xlabel(xlabel if xlabel else ('时间' if is_time_series else '索引'))
        plt.ylabel(ylabel if ylabel else '')
        plt.grid(grid)
        plt.legend()
        plt.tight_layout()
    
    elif plot_type_en == 'stacked':
        # Stacked plot
        plt.figure(figsize=figsize)
        # Calculate cumulative sum for stacking
        df_stacked = result[y_columns].cumsum(axis=1)
        for i, col in enumerate(y_columns):
            if i == 0:
                plt.fill_between(x_data, 0, df_stacked[col], label=col, alpha=0.7)
            else:
                plt.fill_between(x_data, df_stacked[y_columns[i-1]], df_stacked[col], label=col, alpha=0.7)
        plt.title(title)
        plt.xlabel(xlabel if xlabel else ('时间' if is_time_series else '索引'))
        plt.ylabel(ylabel if ylabel else '')
        plt.grid(grid)
        plt.legend()
        plt.tight_layout()
    
    elif plot_type_en == 'subplots':
        # Subplots - each line in its own subplot, stacked vertically
        n_cols = len(y_columns)
        fig, axes = plt.subplots(n_cols, 1, figsize=(15, 3*n_cols), sharex=False)
        if len(y_columns) == 1: axes = [axes]
        
        for i, col in enumerate(y_columns):
            if col in result.columns:
                axes[i].plot(x_data, result[col], label=col)
                axes[i].set_title(col)
                axes[i].grid(grid)
                axes[i].legend()
            else:
                print(f"Warning: Y column '{col}' not found.")
        
        plt.suptitle(title, y=0.99, fontsize=16)
        plt.xlabel(xlabel if xlabel else ('时间' if is_time_series else '索引'))
        plt.tight_layout()
    
    elif plot_type_en == 'grid':
        # Grid plot - each line in its own subplot, arranged in a grid
        n_cols = len(y_columns)
        if n_cols > 0:
            # Calculate grid size
            n_rows = int(np.ceil(np.sqrt(n_cols)))
            n_cols_grid = int(np.ceil(n_cols / n_rows))
            
            fig, axes = plt.subplots(n_rows, n_cols_grid, figsize=(18, 4*n_rows))
            axes = axes.flatten()
            
            for i in range(len(axes)):
                if i < n_cols:
                    col = y_columns[i]
                    if col in result.columns:
                        axes[i].plot(x_data, result[col], label=col)
                        axes[i].set_title(col)
                        axes[i].grid(grid)
                        axes[i].legend()
                    else:
                        print(f"Warning: Y column '{col}' not found.")
                else:
                    # Hide unused subplots
                    axes[i].axis('off')
            
            plt.suptitle(title, y=0.99, fontsize=16)
            plt.tight_layout()
    
    plt.show()



def trend_ma(df, y_columns=None, window_size=60, center=True, title="移动平均趋势图", figsize=None) -> None:
    """
    Plot moving average trend chart for a DataFrame.

    Algorithm:
        name: 移动平均趋势
        category: trend_plot
        prompt: 请对{VAR_NAME} 绘制移动平均趋势线。使用 pandas 的 rolling().mean() 计算趋势线，并用 matplotlib 绘制原始曲线与趋势线，添加网格、图例与中文标签。
        imports: import pandas as pd, import matplotlib.pyplot as plt
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
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



def trend_loess(df, y_columns=None, frac=0.1, title="LOESS趋势图", figsize=None) -> None:
    """
    Plot LOESS (Locally Weighted Scatterplot Smoothing) trend chart for a DataFrame.

    Algorithm:
        name: LOESS 趋势
        category: trend_plot
        prompt: 请对{VAR_NAME} 绘制 LOESS 平滑趋势。使用 statsmodels.nonparametric.smoothers_lowess.lowess 进行平滑并绘制趋势曲线；若缺少该库，可退化为 rolling().mean()。
        imports: import statsmodels.api as sm, import matplotlib.pyplot as plt, import numpy as np, import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
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



def trend_polyfit(df, y_columns=None, degree=2, title="多项式趋势拟合图", figsize=None) -> None:
    """
    Plot polynomial trend fit for a DataFrame.

    Algorithm:
        name: 多项式趋势拟合
        category: trend_plot
        prompt: 请对{VAR_NAME} 进行多项式趋势拟合并绘制趋势。使用 numpy.polyfit 对指定阶数进行拟合，绘制拟合曲线与原始数据，并计算与输出拟合优度（R²）。
        imports: import numpy as np, import matplotlib.pyplot as plt, import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
    y_columns (list): Columns to perform polynomial fitting on.
        label: Y轴列名
        widget: column-selector
        priority: critical
    degree (int): Polynomial degree.
        label: 多项式阶数
        min: 1
        max: 5
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
    poly_data = result[y_columns].dropna().copy()
    
    # Plot polynomial fit for each column
    for col in y_columns:
        # Prepare data
        y = poly_data[col].values
        x = np.arange(len(y))

        # Fit polynomial
        coefs = np.polyfit(x, y, deg=degree)
        trend_poly = np.polyval(coefs, x)
        
        # Calculate R-squared
        ss_res = np.sum((y - trend_poly) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        # Create plot
        plt.figure(figsize=figsize)
        plt.plot(poly_data.index, y, label='原始数据', alpha=0.4)
        plt.plot(poly_data.index, trend_poly, label=f'{degree}阶多项式拟合 (R²={r_squared:.4f})', linewidth=2, color='purple')
        
        plt.title(f"多项式趋势拟合: {col}" if title == "多项式趋势拟合图" else title)
        plt.xlabel('时间' if isinstance(poly_data.index, pd.DatetimeIndex) else '索引')
        plt.ylabel(col)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()
        
        # Print R-squared
        print(f"{col} 的 {degree}阶多项式拟合优度 R² = {r_squared:.4f}")



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
    y_columns (list): Columns to plot envelope for.
        label: Y轴列名
        widget: column-selector
        priority: critical
    window_duration (str): Time window duration.
        label: 窗口时长
        options: ["30s", "1min", "5min", "15min", "30min", "1h", "2h", "6h", "12h", "1D"]
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

