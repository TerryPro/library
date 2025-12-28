"""
UI组件模块
"""

import pandas as pd
import ipywidgets as widgets
from ipywidgets import HBox, VBox, Layout, GridBox
from typing import List, Dict, Optional, Any

from .constants import LAYOUT_MODE_OPTIONS, RESAMPLE_OPTIONS
from .utils import get_default_color, create_dtype_icon, create_param_row


class UIComponents:
    """UI组件管理器"""

    def __init__(self, df: pd.DataFrame, x_column: Optional[str] = None, is_timeseries: bool = False):
        self.df = df
        self.x_column = x_column
        self.is_timeseries = is_timeseries

        # 初始化组件
        self._init_components()

    def _init_components(self):
        """初始化UI组件"""
        # Callbacks that the parent DynamicTrendWidget can set to handle events
        self.on_y_param_toggle = None
        self.on_param_color_change = None
        self.on_param_smooth_change = None

        # 显示方式选择器
        self.mode_selector = widgets.Dropdown(
            options=LAYOUT_MODE_OPTIONS,
            value='overlay',
            description='显示方式:',
            layout=Layout(width='280px', margin='0 0 10px 0')
        )

        # 重采样选择器
        self.resample_selector = widgets.Dropdown(
            options=RESAMPLE_OPTIONS,
            value=None,
            description='数据聚合:',
            layout=Layout(width='280px', margin='0 0 10px 0')
        )

        # X轴选择器（仅当非时间序列时显示）
        if self.is_timeseries:
            self.x_selector = None
        else:
            all_columns = self.df.columns.tolist()
            self.x_selector = widgets.Dropdown(
                options=all_columns,
                value=self.x_column if self.x_column in all_columns else (all_columns[0] if all_columns else None),
                description='X轴参数:',
                layout=Layout(width='280px', margin='0 0 10px 0')
            )

        # Y轴参数表格容器
        self.y_param_table = VBox(layout=Layout(width='280px'))
        self.y_axis_table = VBox(layout=Layout(width='280px'))

        # 图表容器（允许在内容超出时滚动）
        self.fig_container = widgets.Box([], layout=Layout(width='100%', height='600px', min_width='0', overflow='auto', border='1px solid #ddd'))

        # 自定义顶部工具栏（替代 plotly 的 modebar）
        self.toolbar_reset = widgets.Button(description='重置', icon='arrows-rotate', layout=Layout(width='110px'))
        self.toolbar_zoom = widgets.Button(description='缩放', icon='search', layout=Layout(width='80px'))
        self.toolbar_pan = widgets.Button(description='平移', icon='arrows', layout=Layout(width='80px'))
        # 新增按钮：切换 Y 轴尺度（线性 / 对数）
        self.toolbar_toggle_yscale = widgets.Button(description='Y轴尺度', icon='chart-line', layout=Layout(width='100px'))
        # 新增按钮：切换图例显示/隐藏
        self.toolbar_toggle_legend = widgets.Button(description='切换图例', icon='list', layout=Layout(width='100px'))
        # 新增按钮：显示/隐藏范围滑条（Range Slider）
        self.toolbar_toggle_rangeslider = widgets.Button(description='范围滑条', icon='arrows-alt-h', layout=Layout(width='100px'))
        self.toolbar_save = widgets.Button(description='PNG', icon='camera', layout=Layout(width='100px'))
        self.toolbar = HBox(
            [self.toolbar_reset, self.toolbar_zoom, self.toolbar_pan,
             self.toolbar_toggle_yscale, self.toolbar_toggle_legend, self.toolbar_toggle_rangeslider,
             self.toolbar_save],
            layout=Layout(width='100%', padding='6px 0', align_items='center', justify_content='flex-start')
        )

        # 主布局容器
        self.main_layout = None
        self.left_panel = None

    def create_param_selection_ui(self) -> VBox:
        """创建参数选择界面"""
        # 构建主布局：左侧参数面板 + 右侧图表占位
        all_columns = self.df.columns.tolist()

        # 刷新参数选择表格
        self._refresh_param_selection_table()

        # 左侧参数面板
        left_panel_children = [
            self.mode_selector,
            self.resample_selector,
        ]

        # 仅当非时间序列时才添加X轴选择器
        if not self.is_timeseries:
            left_panel_children.append(self.x_selector)

        left_panel_children.extend([
            widgets.HTML("<h5 style='margin:10px 0 5px 0;'>Y轴参数</h5>"),
            self.y_param_table
        ])

        self.left_panel = VBox(left_panel_children, layout=Layout(width='300px', padding='6px', border='1px solid #ddd'))

        # 右侧图表占位
        placeholder = widgets.HTML("<div style='color:gray;padding:20px;'>请在左侧选择X轴和至少一个Y轴参数以显示图表</div>")
        self.fig_container.children = [placeholder]

        # 主布局
        self.main_layout = GridBox(
            children=[self.left_panel, self.fig_container],
            layout=Layout(
                display='grid',
                grid_template_columns='300px 1fr',
                grid_template_rows='auto',
                grid_gap='10px',
                width='100%',
                min_height='400px'
            )
        )
        # 在参数选择界面也显示顶部工具栏，保持与主界面一致
        return VBox([self.toolbar, self.main_layout], layout=Layout(width='100%'))

    def create_main_ui(self) -> VBox:
        """创建主UI界面"""
        # 刷新Y轴参数表格
        self._refresh_y_axis_table()

        # 左侧面板
        left_panel_children = [
            widgets.HTML("<h4 style='margin:0 0 10px 0;'>参数配置</h4>"),
            self.mode_selector,
            self.resample_selector,
        ]

        # 仅当非时间序列时才添加X轴选择器
        if not self.is_timeseries:
            left_panel_children.append(self.x_selector)

        left_panel_children.extend([
            widgets.HTML("<h5 style='margin:10px 0 5px 0;'>Y轴参数</h5>"),
            self.y_axis_table
        ])

        self.left_panel = VBox(left_panel_children, layout=Layout(width='300px', padding='10px', border='1px solid #ddd'))

        # 主布局（左侧参数 + 右侧图表）
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

        # 顶部放置自定义工具栏，然后是主布局
        return VBox([self.toolbar, self.main_layout], layout=Layout(width='100%'))

    def _refresh_param_selection_table(self):
        """刷新参数选择表格"""
        # 仅列出数值型列，并排除当前选定的X轴列
        numeric_columns = self.df.select_dtypes(include=['number']).columns.tolist()
        excluded_x_column = self.x_selector.value if self.x_selector else None
        all_columns = [col for col in numeric_columns if col != excluded_x_column]

        table_rows = []
        for idx, col in enumerate(all_columns):
            # 复选框
            checkbox = widgets.Checkbox(
                value=False,
                indent=False,
                layout=Layout(width='20px', margin='0 5px 0 0')
            )
            # Attach parent callback if provided
            try:
                checkbox.observe(lambda change, col=col: self.on_y_param_toggle(change, col) if callable(self.on_y_param_toggle) else None, names='value')
            except Exception:
                pass

            # 颜色选择器
            color_picker = widgets.ColorPicker(
                concise=True,
                value=get_default_color(idx),
                layout=Layout(width='40px', margin='0 8px 0 0')
            )
            try:
                color_picker.observe(lambda change, col=col: self.on_param_color_change(change, col) if callable(self.on_param_color_change) else None, names='value')
            except Exception:
                pass

            # 平滑开关
            smooth_checkbox = widgets.Checkbox(
                value=False,
                indent=False,
                layout=Layout(width='20px', margin='0 5px 0 0')
            )
            try:
                smooth_checkbox.observe(lambda change, col=col: self.on_param_smooth_change(change, col, 'enabled') if callable(self.on_param_smooth_change) else None, names='value')
            except Exception:
                pass

            # 平滑窗口输入
            smooth_window_input = widgets.IntText(
                value=5,
                min=2,
                max=100,
                step=1,
                layout=Layout(width='50px', margin='0 5px 0 0')
            )
            try:
                smooth_window_input.observe(lambda change, col=col: self.on_param_smooth_change(change, col, 'window') if callable(self.on_param_smooth_change) else None, names='value')
            except Exception:
                pass

            # 参数名标签
            label = widgets.Label(
                value=col,
                layout=Layout(width='120px', overflow='hidden')
            )

            # 数据类型图标
            type_icon = create_dtype_icon(str(self.df[col].dtype))

            table_rows.append(create_param_row([checkbox, color_picker, smooth_checkbox, smooth_window_input, label, type_icon]))

        self.y_param_table.children = table_rows

    def _refresh_y_axis_table(self):
        """刷新Y轴参数表格"""
        # 这将在主类中实现，因为需要访问state
        pass
