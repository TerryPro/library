
from .widget import DynamicTrendWidget
import pandas as pd

def trend_dynamic(df: pd.DataFrame, x_column: str = '', y_columns: list = [], title: str = '动态趋势分析') -> DynamicTrendWidget:
    """
    Plot dynamic trend chart for a DataFrame.

    Algorithm:
        name: 动态趋势图 (Dynamic)
        category: trend_plot
        prompt: 请根据配置绘制 {VAR_NAME} 的动态趋势图。支持时间轴缩放、多参数对比和布局切换。
    
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
    title (str): Chart title.
        label: 图表标题
        widget: input-text
        priority: non-critical
        role: parameter
    
    Returns:
    DynamicTrendWidget: The interactive widget
    """
    return DynamicTrendWidget(df, x_column, y_columns, title)
