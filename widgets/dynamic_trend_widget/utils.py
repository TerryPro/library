"""
工具函数模块
"""

import pandas as pd
import ipywidgets as widgets
from typing import List, Dict, Optional

from .constants import DEFAULT_COLORS


def is_timeseries_dataframe(df: pd.DataFrame, x_column: Optional[str] = None) -> bool:
    """检测DataFrame是否为时间序列DataFrame"""
    # 检查索引是否为DatetimeIndex
    if isinstance(df.index, pd.DatetimeIndex):
        return True

    # 检查是否有主要的datetime列（第一个datetime列）
    datetime_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
    if len(datetime_cols) > 0:
        # 如果没有指定x_column，且有datetime列，则认为是时间序列
        return x_column is None

    return False


def get_default_color(index: int) -> str:
    """获取默认颜色"""
    return DEFAULT_COLORS[index % len(DEFAULT_COLORS)]


def create_dtype_icon(dtype: str) -> widgets.HTML:
    """创建数据类型图标"""
    dt_lower = dtype.lower()

    if 'float' in dt_lower or 'int' in dt_lower or 'number' in dt_lower:
        icon_svg = ('<svg width="14" height="14" viewBox="0 0 14 14" xmlns="http://www.w3.org/2000/svg">'
                   '<rect x="1" y="8" width="2" height="5" fill="#2b7cff"/>'
                   '<rect x="5" y="5" width="2" height="8" fill="#2b7cff"/>'
                   '<rect x="9" y="3" width="2" height="10" fill="#2b7cff"/>'
                   '</svg>')
    elif 'datetime' in dt_lower or 'time' in dt_lower or 'date' in dt_lower:
        icon_svg = ('<svg width="14" height="14" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
                   '<circle cx="12" cy="12" r="10" stroke="#666" stroke-width="1" fill="none"/>'
                   '<path d="M12 7v6l4 2" stroke="#666" stroke-width="1" fill="none" stroke-linecap="round"/>'
                   '</svg>')
    elif 'bool' in dt_lower:
        icon_svg = ('<svg width="14" height="14" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
                   '<rect x="2" y="6" width="20" height="12" rx="6" fill="#ddd"/>'
                   '<circle cx="7" cy="12" r="3" fill="#4caf50"/>'
                   '</svg>')
    elif 'object' in dt_lower or 'str' in dt_lower or 'string' in dt_lower:
        icon_svg = ('<svg width="14" height="14" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
                   '<text x="4" y="16" font-size="12" fill="#444" font-family="Arial, sans-serif">A</text>'
                   '</svg>')
    else:
        icon_svg = ('<svg width="14" height="14" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
                   '<text x="4" y="16" font-size="12" fill="#999" font-family="Arial, sans-serif">?</text>'
                   '</svg>')

    return widgets.HTML(
        value=f'<span title="{dtype}" style="line-height:20px;">{icon_svg}</span>',
        layout=widgets.Layout(width='36px')
    )


def create_param_row(children, margin='2px 0'):
    """创建参数行HBox"""
    from ipywidgets import HBox, Layout
    return HBox(children, layout=Layout(align_items='center', margin=margin))
