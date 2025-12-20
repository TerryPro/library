import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.seasonal import STL
import mplfinance.original_flavor as mpf

def trend_plot(df: pd.DataFrame, x_column: str = '', y_columns: list = [], xlabel: str = '', ylabel: str = '', figsize: tuple = None, plot_type: str = '叠加显示', title: str = '趋势图', grid: bool = True) -> None:
    """
    Plot trend chart for a DataFrame.
No
    Algorithm:
        name: 通用趋势图 (Trend)
        category: trend_plot
        prompt: 请根据配置绘制 {VAR_NAME} 的趋势图。支持自定义 X 轴、Y 轴列、标题、网格等设置。
    
    Parameters:
    df (pd.DataFrame): Input DataFrame
        role: input
    x_column (str): Column to use as X-axis.
        label: X轴列名
        widget: column-selector
        priority: critical
        role: parameter
    y_columns (list): Columns to plot on Y-axis.
        label: Y轴列名
        widget: column-selector
        priority: critical
        role: parameter
    plot_type (str): Plot type (叠加显示, 堆叠显示, 分栏显示, 网格显示).
        label: 绘图方式
        widget: select
        options: ["叠加显示", "堆叠显示", "分栏显示", "网格显示"]
        priority: critical
        role: parameter
    title (str): Chart title.
        label: 图表标题
        widget: input-text
        priority: non-critical
        role: parameter
    xlabel (str): X-axis label.
        label: X轴标签
        widget: input-text
        priority: non-critical
        role: parameter
    ylabel (str): Y-axis label.
        label: Y轴标签
        widget: input-text
        priority: non-critical
        role: parameter
    grid (bool): Whether to show grid.
        label: 显示网格
        widget: select
        priority: non-critical
        role: parameter
    figsize (tuple): Figure size tuple.
        label: 图像尺寸
        widget: input-text
        priority: non-critical
        role: parameter
    
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