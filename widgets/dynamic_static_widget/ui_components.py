"""
UI组件模块
"""

import pandas as pd
import ipywidgets as widgets
from ipywidgets import HBox, VBox, Layout, GridBox
from typing import List, Dict, Optional, Any, Tuple

from .constants import CHART_TYPE_OPTIONS, FIGSIZE_OPTIONS, STATISTICS_LABELS
from .utils import get_default_color, create_dtype_icon, create_param_row


class StatisticsUIComponents:
    """统计分析UI组件管理器"""

    def __init__(self, df: pd.DataFrame):
        self.df = df

        # 初始化组件
        self._init_components()

    def _init_components(self):
        """初始化UI组件"""
        # Callbacks that the parent widget can set
        self.on_column_selection_change = None
        self.on_chart_type_change = None
        self.on_figsize_change = None

        # 列选择器
        self.column_selector_container = VBox(layout=Layout(width='280px'))

        # 图表类型选择器
        self.chart_type_selector = widgets.Dropdown(
            options=CHART_TYPE_OPTIONS,
            value='summary',
            description='图表类型:',
            layout=Layout(width='280px', margin='0 0 10px 0')
        )

        # 图表尺寸选择器
        self.figsize_selector = widgets.Dropdown(
            options=FIGSIZE_OPTIONS,
            value=(16, 10),
            description='图表尺寸:',
            layout=Layout(width='280px', margin='0 0 10px 0')
        )

        # 散点图已移除，相关选择器不再创建

        # 图表容器（允许横向滚动，隐藏纵向滚动）
        self.fig_container = widgets.Box(
            [],
            layout=Layout(width='100%', height='600px', min_width='0', overflow_x='auto', overflow_y='hidden', border='1px solid #ddd')
        )

        # 工具栏按钮
        self.toolbar_reset = widgets.Button(description='重置', icon='arrows-rotate', layout=Layout(width='80px'))
        self.toolbar_export = widgets.Button(description='导出', icon='download', layout=Layout(width='80px'))

        # 工具栏
        self.toolbar = HBox(
            [self.toolbar_reset, self.toolbar_export],
            layout=Layout(width='100%', padding='6px 0', align_items='center', justify_content='flex-start')
        )

        # 主布局容器
        self.main_layout = None
        self.left_panel = None

    def create_main_ui(self) -> VBox:
        """创建主UI界面"""
        # 刷新列选择器
        self._refresh_column_selector()

        # 左侧控制面板
        left_panel_children = [
            widgets.HTML("<h4 style='margin:0 0 10px 0;'>统计分析配置</h4>"),
            self.chart_type_selector,
            self.figsize_selector,
            widgets.HTML("<h5 style='margin:10px 0 5px 0;'>选择分析列</h5>"),
            self.column_selector_container,
            # 散点图功能已移除
        ]

        self.left_panel = VBox(
            left_panel_children,
            layout=Layout(width='300px', padding='10px', border='1px solid #ddd')
        )

        # 主布局（左侧控制面板 + 右侧图表）
        self.main_layout = GridBox(
            children=[self.left_panel, self.fig_container],
            layout=Layout(
                display='grid',
                grid_template_columns='300px 1fr',
                grid_template_rows='auto',
                grid_gap='10px',
                width='100%',
                height='600px'
            )
        )

        # 绑定事件
        self._bind_events()

        # 顶部放置工具栏，然后是主布局
        return VBox([self.toolbar, self.main_layout], layout=Layout(width='100%'))

    def _bind_events(self):
        """绑定事件处理器"""
        self.chart_type_selector.observe(self._on_chart_type_change, names='value')
        # 监听图表尺寸变化
        self.figsize_selector.observe(self._on_figsize_change, names='value')

    def _on_figsize_change(self, change):
        """图表尺寸变化处理"""
        if callable(self.on_figsize_change):
            self.on_figsize_change(change)

    def _refresh_column_selector(self):
        """刷新列选择器"""
        # 获取数值列
        numeric_columns = self.df.select_dtypes(include=['number']).columns.tolist()

        if not numeric_columns:
            self.column_selector_container.children = [
                widgets.HTML("<p style='color:gray;'>没有数值列可供分析</p>")
            ]
            return

        # 创建列选择复选框
        column_checkboxes = []
        for col in numeric_columns:
            checkbox = widgets.Checkbox(
                value=True,  # 默认全选
                indent=False,
                layout=Layout(width='20px', margin='0 5px 0 0')
            )

            # 绑定事件
            checkbox.observe(lambda change, col=col: self._on_column_checkbox_change(change, col), names='value')

            # 参数名标签
            label = widgets.Label(
                value=col,
                layout=Layout(width='180px', overflow='hidden')
            )

            # 数据类型图标
            type_icon = create_dtype_icon(str(self.df[col].dtype))

            # 创建行
            row = create_param_row([checkbox, label, type_icon])
            column_checkboxes.append(row)

        # 添加全选/取消全选按钮
        select_all_btn = widgets.Button(
            description='全选',
        )
        select_none_btn = widgets.Button(
            description='取消',
        )

        select_all_btn.on_click(lambda btn: self._select_all_columns(True))
        select_none_btn.on_click(lambda btn: self._select_all_columns(False))

        button_row = HBox([select_all_btn, select_none_btn], layout=Layout(margin='5px 0'))

        self.column_selector_container.children = [button_row] + column_checkboxes

    def _refresh_scatter_selectors(self):
        """刷新散点图的轴选择器"""
        # 散点图功能已移除
        return

    def _on_chart_type_change(self, change):
        """图表类型变化处理"""
        chart_type = change['new']
        # 通知父组件
        if callable(self.on_chart_type_change):
            self.on_chart_type_change(change)

    def _on_column_checkbox_change(self, change, column):
        """列选择复选框变化处理"""
        if callable(self.on_column_selection_change):
            self.on_column_selection_change(change, column)

    def _on_scatter_axis_change(self, change):
        """散点图轴变化处理"""
        # 散点图功能已移除
        return

    def _select_all_columns(self, select_all: bool):
        """全选或取消全选所有列"""
        for child in self.column_selector_container.children[1:]:  # 跳过按钮行
            if hasattr(child, 'children') and len(child.children) > 0:
                checkbox = child.children[0]
                if hasattr(checkbox, 'value'):
                    checkbox.value = select_all

    def get_selected_columns(self) -> List[str]:
        """获取选中的列"""
        selected_columns = []
        numeric_columns = self.df.select_dtypes(include=['number']).columns.tolist()

        for i, child in enumerate(self.column_selector_container.children[1:], 0):  # 跳过按钮行
            if hasattr(child, 'children') and len(child.children) > 0:
                checkbox = child.children[0]
                if hasattr(checkbox, 'value') and checkbox.value and i < len(numeric_columns):
                    selected_columns.append(numeric_columns[i])

        return selected_columns

    def get_scatter_columns(self) -> Tuple[Optional[str], Optional[str]]:
        """获取散点图的X轴和Y轴列"""
        # 散点图功能已移除
        return None, None

    def set_chart_type(self, chart_type: str):
        """设置图表类型"""
        if chart_type in [option[1] for option in CHART_TYPE_OPTIONS]:
            self.chart_type_selector.value = chart_type

    def set_selected_columns(self, columns: List[str]):
        """设置选中的列"""
        numeric_columns = self.df.select_dtypes(include=['number']).columns.tolist()

        for i, child in enumerate(self.column_selector_container.children[1:], 0):  # 跳过按钮行
            if hasattr(child, 'children') and len(child.children) > 0:
                checkbox = child.children[0]
                if hasattr(checkbox, 'value') and i < len(numeric_columns):
                    checkbox.value = numeric_columns[i] in columns
