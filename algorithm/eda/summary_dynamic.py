import pandas as pd
from typing import Optional, Tuple, List
from IPython.display import display

def summary_dynamic(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    figsize: Tuple[int, int] = (16, 10),
    title: str = "统计汇总分析"
) -> None:
    """
    在交互式统计面板中展示 DataFrame 的统计汇总。

    Algorithm:
        name: 交互式统计汇总
        category: eda
        prompt: 在交互式面板中展示 {VAR_NAME} 的统计汇总，支持选择列、切换视图并导出结果

    Parameters:
    df (pandas.DataFrame): 输入数据集。
        role: input
    columns (list[str], optional): 要展示的列名列表。若为 None，将使用组件默认选择。
        label: 处理列
        widget: column-selector
        role: parameter
        priority: non-critical
    figsize (tuple, optional): 图表尺寸 (width, height)。
        label: 图像尺寸
        widget: input
        role: parameter
        priority: non-critical
    title (str): 面板标题。
        label: 面板标题
        widget: input
        role: parameter
        priority: non-critical

    Returns:
    None
    """
    if df is None:
        return None

    # 延迟导入以避免循环依赖
    try:
        from widgets.dynamic_static_widget.main import DynamicStaticWidget
    except Exception:
        from library.widgets.dynamic_static_widget.main import DynamicStaticWidget

    widget = DynamicStaticWidget(df=df, columns=columns, figsize=figsize)
    display(widget)


