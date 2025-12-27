import pandas as pd
from IPython.display import display
from widgets.dynamic_trend_widget.main import DynamicTrendWidget

def trend_dynamic(df: pd.DataFrame, x_column: str = None, y_columns: list = None, title: str = '动态趋势分析', figsize: tuple = (16, 8)) -> None:
    """
    Plot dynamic trend chart for a DataFrame with interactive parameter selection.

    Algorithm:
        name: 动态趋势图 (Dynamic)
        category: trend_plot
        prompt: 请根据配置绘制 {VAR_NAME} 的动态趋势图。支持时间轴缩放、多参数对比和布局切换。

    Parameters:
    df (pd.DataFrame): Input DataFrame
        role: input
    x_column (str, optional): Column to use as X-axis. If None, user will select interactively.
        label: X轴列名
        widget: column-selector
        priority: high
        role: parameter
    y_columns (list, optional): Columns to plot on Y-axis. If None, user will select interactively.
        label: Y轴列名
        widget: column-selector
        priority: high
        role: parameter
    title (str): Chart title.
        label: 图表标题
        widget: input-text
        priority: non-critical
        role: parameter
    figsize (tuple): Figure size as (width, height) in inches, similar to matplotlib.
        label: 图像尺寸
        widget: input-text
        priority: non-critical
        role: parameter

    Returns:
    None

    Usage:
    # Interactive mode - user selects parameters
    trend_dynamic(df)

    # Direct mode - specify parameters directly
    trend_dynamic(df, x_column='timestamp', y_columns=['col1', 'col2'])

    # With custom figure size
    trend_dynamic(df, figsize=(16, 8))
    """
    widget = DynamicTrendWidget(df, x_column, y_columns, title, figsize)
    display(widget)
