"""
动态趋势组件主类
"""

import pandas as pd
import ipywidgets as widgets
from ipywidgets import VBox, Layout
from typing import List, Dict, Optional, Tuple

from .constants import DEFAULT_TITLE, DEFAULT_FIGSIZE, DEFAULT_SMOOTH_WINDOW
from .utils import is_timeseries_dataframe, get_default_color
from .data_processor import DataProcessor
from .ui_components import UIComponents
from .chart_renderer import ChartRenderer


class DynamicTrendWidget(VBox):
    """动态趋势图组件"""

    def __init__(self, df: pd.DataFrame, x_column: Optional[str] = None, y_columns: Optional[List[str]] = None,
                 title: str = DEFAULT_TITLE, figsize: Tuple[int, int] = DEFAULT_FIGSIZE):
        super().__init__(layout=Layout(width='100%'))

        self.df = df.copy()
        self.title = title
        self.x_column = x_column
        self.y_columns = y_columns or []
        self.figsize = figsize

        # 检测是否为时间序列DataFrame
        self.is_timeseries = is_timeseries_dataframe(self.df, self.x_column)
        if self.is_timeseries and self.x_column is None:
            # 时间序列DataFrame自动使用索引作为X轴
            self.x_column = '__index__'

        # 初始化组件
        self.data_processor = DataProcessor(self.df, self.x_column, self.is_timeseries)
        self.ui_components = UIComponents(self.df, self.x_column, self.is_timeseries)
        # Wire UI callbacks to this widget's handlers
        self.ui_components.on_y_param_toggle = self._on_y_param_toggle
        self.ui_components.on_param_color_change = self._on_param_color_change
        self.ui_components.on_param_smooth_change = self._on_param_smooth_change
        self.chart_renderer = ChartRenderer(self.figsize)

        # 初始化配置状态
        self.state = {
            'layout_mode': 'overlay',  # overlay | split
            'series': [],
            'resample_rule': None,  # 重采样规则，如 '1H', '1D' 等
            'smooth_window': None,  # 平滑窗口大小（全局备用）
        }
        # 用于在添加系列前临时保存每列的颜色选择
        self._pending_colors: Dict[str, str] = {}
        # 用于在添加系列前临时保存每列的平滑配置 {'col': {'enabled': bool, 'window': int}}
        self._pending_smooth: Dict[str, Dict] = {}

        # 初始化UI组件的事件监听
        # toolbar 绑定标识（避免重复绑定）
        self._toolbar_bound = False
        self._setup_event_handlers()

        # 初始化UI
        self._init_ui()

        # 如果有完整的参数，初始化图表并绘制
        if self.x_column and self.y_columns:
            self._init_series_state()
            self._init_figure()
            self._update_figure()
        else:
            # 显示参数选择界面
            self._show_param_selection()

    def _setup_event_handlers(self):
        """设置事件处理器"""
        # 模式选择器
        self.ui_components.mode_selector.observe(self._on_mode_change, names='value')

        # 重采样选择器
        self.ui_components.resample_selector.observe(self._on_resample_change, names='value')

        # X轴选择器（如果存在）
        if self.ui_components.x_selector:
            self.ui_components.x_selector.observe(self._on_x_axis_change, names='value')
        # 绑定 toolbar 的点击事件（一次性绑定）
        try:
            self._bind_toolbar_actions()
        except Exception:
            pass

    def _init_series_state(self):
        """根据y_columns初始化系列状态"""
        self.state['series'] = [
            {
                'col': col,
                'color': get_default_color(i),
                'visible': True,
                'smooth_enabled': False,
                'smooth_window': DEFAULT_SMOOTH_WINDOW
            }
            for i, col in enumerate(self.y_columns)
        ]

    def _init_figure(self):
        """初始化图表对象"""
        fig = self.chart_renderer.create_figure_widget()
        self.ui_components.fig_container.children = [fig]
        # 不在此处绑定 toolbar，绑定已在事件初始化时完成（绑定的是按需获取当前 fig 的 handler）
        # 保留 _wire_toolbar 作历史兼容，但不主动调用它以避免重复绑定

    def _wire_toolbar(self, fig):
        """将自定义工具栏按钮绑定到 FigureWidget 的操作（重置、缩放、平移、导出）"""
        ui = self.ui_components

        # 重置视图
        def on_reset(btn):
            try:
                fig.update_xaxes(autorange=True)
                fig.update_yaxes(autorange=True)
            except Exception:
                pass

        ui.toolbar_reset.on_click(on_reset)

        # 缩放/平移按钮（普通按钮，每次点击启用对应模式）
        def on_zoom_click(btn):
            try:
                fig.update_layout(dragmode='zoom')
            except Exception:
                pass

        def on_pan_click(btn):
            try:
                fig.update_layout(dragmode='pan')
            except Exception:
                pass

        ui.toolbar_zoom.on_click(on_zoom_click)
        ui.toolbar_pan.on_click(on_pan_click)

        # 导出为 PNG（显示在 notebook 中）
        def on_save(btn):
            try:
                # 使用 FigureWidget 的 to_image 方法（需要支持的后端，如 kaleido）
                img_bytes = fig.to_image(format='png')
                from IPython.display import display, Image
                display(Image(img_bytes))
            except Exception as e:
                try:
                    from IPython.display import display, HTML
                    display(HTML(f"<pre style='color:red;'>导出失败: {e}</pre>"))
                except Exception:
                    pass

        ui.toolbar_save.on_click(on_save)

    def _bind_toolbar_actions(self):
        """绑定 toolbar 按钮（一次性绑定），处理函数在点击时动态获取当前 FigureWidget"""
        if getattr(self, '_toolbar_bound', False):
            return
        ui = self.ui_components

        def get_current_fig():
            try:
                if ui.fig_container.children and len(ui.fig_container.children) > 0:
                    return ui.fig_container.children[0]
            except Exception:
                pass
            return None

        def on_reset(btn):
            fig = get_current_fig()
            if fig is None:
                return
            try:
                fig.update_xaxes(autorange=True)
                fig.update_yaxes(autorange=True)
            except Exception:
                pass

        def on_zoom_click(btn):
            fig = get_current_fig()
            if fig is None:
                return
            try:
                fig.update_layout(dragmode='zoom')
            except Exception:
                pass

        def on_pan_click(btn):
            fig = get_current_fig()
            if fig is None:
                return
            try:
                fig.update_layout(dragmode='pan')
            except Exception:
                pass

        def on_save(btn):
            fig = get_current_fig()
            if fig is None:
                return
            try:
                img_bytes = fig.to_image(format='png')
                from IPython.display import display, Image
                display(Image(img_bytes))
            except Exception as e:
                try:
                    from IPython.display import display, HTML
                    display(HTML(f"<pre style='color:red;'>导出失败: {e}</pre>"))
                except Exception:
                    pass

        # 新增：切换 Y 轴尺度（linear <-> log）
        def on_toggle_yscale(btn):
            fig = get_current_fig()
            if fig is None:
                return
            try:
                # 尝试读取当前 yaxis.type，默认 linear
                current_type = getattr(getattr(fig.layout, 'yaxis', None), 'type', None) or 'linear'
                new_type = 'log' if current_type != 'log' else 'linear'
                fig.update_yaxes(type=new_type)
            except Exception:
                pass

        # 新增：切换图例显示/隐藏
        def on_toggle_legend(btn):
            fig = get_current_fig()
            if fig is None:
                return
            try:
                current_show = bool(getattr(fig.layout, 'showlegend', True))
                fig.update_layout(showlegend=not current_show)
            except Exception:
                pass

        # 新增：显示/隐藏范围滑条（Range Slider）
        def on_toggle_rangeslider(btn):
            fig = get_current_fig()
            if fig is None:
                return
            try:
                # 尝试读取 xaxis.rangeslider.visible
                xaxis = getattr(fig.layout, 'xaxis', None)
                rangeslider = getattr(xaxis, 'rangeslider', None) if xaxis is not None else None
                current_visible = bool(getattr(rangeslider, 'visible', False))
                fig.update_layout(xaxis_rangeslider_visible=not current_visible)
            except Exception:
                pass

        # 新增：切换标题显示/隐藏
        def on_toggle_title(btn):
            fig = get_current_fig()
            if fig is None:
                return
            try:
                # 读取当前 title 文本（若为空或 None 视为隐藏）
                current_text = getattr(getattr(fig.layout, 'title', None), 'text', None) or ''
                new_text = self.title if not current_text else ''
                # 使用 title_text 以兼容性更新
                fig.update_layout(title_text=new_text)
            except Exception:
                pass

        try:
            ui.toolbar_reset.on_click(on_reset)
            ui.toolbar_zoom.on_click(on_zoom_click)
            ui.toolbar_pan.on_click(on_pan_click)
            # 绑定新增按钮
            if hasattr(ui, 'toolbar_toggle_yscale'):
                ui.toolbar_toggle_yscale.on_click(on_toggle_yscale)
            if hasattr(ui, 'toolbar_toggle_legend'):
                ui.toolbar_toggle_legend.on_click(on_toggle_legend)
            if hasattr(ui, 'toolbar_toggle_rangeslider'):
                ui.toolbar_toggle_rangeslider.on_click(on_toggle_rangeslider)
            if hasattr(ui, 'toolbar_toggle_title'):
                ui.toolbar_toggle_title.on_click(on_toggle_title)
            ui.toolbar_save.on_click(on_save)
            self._toolbar_bound = True
        except Exception:
            # 绑定失败时仍标记为未绑定以便后续重试
            self._toolbar_bound = False

    def _set_fig_container(self):
        """设置fig_container的children并触发resize"""
        if hasattr(self, 'ui_components') and self.ui_components.fig_container.children:
            fig = self.ui_components.fig_container.children[0]
            # 触发plotly的resize事件以确保图表正确调整大小
            try:
                # 尝试不同的resize方法
                if hasattr(fig, '_js2py_resize'):
                    fig._js2py_resize()
                elif hasattr(fig, '_relayout'):
                    fig._relayout()
            except:
                pass

    def _show_param_selection(self):
        """显示参数选择界面"""
        self.children = [self.ui_components.create_param_selection_ui()]

    def _init_ui(self):
        """初始化UI"""
        self.children = [self.ui_components.create_main_ui()]
        # 如果用户指定了 figsize，则把主布局的右侧列宽固定为 figsize 的像素宽度，
        # 这样图形区域宽度与 figsize 对齐，避免因容器宽度不足而出现水平滚动条。
        try:
            width_px = int(self.figsize[0] * 72)
            if hasattr(self.ui_components, 'main_layout') and hasattr(self.ui_components.main_layout, 'layout'):
                # main_layout 使用 grid_template_columns='300px 1fr'，替换为固定宽度
                self.ui_components.main_layout.layout.grid_template_columns = f'300px {width_px}px'
        except Exception:
            pass

    def _refresh_y_axis_table(self):
        """刷新Y轴参数表格"""
        if not self.state['series']:
            self.ui_components.y_axis_table.children = [widgets.HTML("<p style='color:gray;'>暂无参数</p>")]
            return

        table_rows = []
        total = len(self.state['series'])

        for i, s in enumerate(self.state['series']):
            # 颜色选择器
            color_picker = widgets.ColorPicker(
                concise=True,
                value=s['color'],
                layout=Layout(width='40px', margin='0 5px 0 0')
            )
            color_picker.observe(lambda c, idx=i: self._on_color_change(c, idx), names='value')

            # 可见性复选框
            checkbox = widgets.Checkbox(
                value=s['visible'],
                indent=False,
                layout=Layout(width='20px', margin='0 5px 0 0')
            )
            checkbox.observe(lambda c, idx=i: self._on_visible_change(c, idx), names='value')

            # 平滑开关
            smooth_checkbox = widgets.Checkbox(
                value=s.get('smooth_enabled', False),
                indent=False,
                layout=Layout(width='20px', margin='0 5px 0 0')
            )
            smooth_checkbox.observe(lambda c, idx=i: self._on_smooth_enabled_change(c, idx), names='value')

            # 平滑窗口输入框
            smooth_window_input = widgets.IntText(
                value=s.get('smooth_window', DEFAULT_SMOOTH_WINDOW),
                min=2,
                max=100,
                step=1,
                layout=Layout(width='50px', margin='0 5px 0 0')
            )
            smooth_window_input.observe(lambda c, idx=i: self._on_smooth_window_change(c, idx), names='value')

            # 参数名标签
            label = widgets.Label(
                value=s['col'],
                layout=Layout(width='140px', overflow='hidden')
            )

            from .utils import create_param_row
            table_rows.append(create_param_row([checkbox, color_picker, smooth_checkbox, smooth_window_input, label]))

        self.ui_components.y_axis_table.children = table_rows

    def _update_figure(self):
        """核心绘图逻辑"""
        if not hasattr(self.ui_components, 'fig_container') or not self.ui_components.fig_container.children:
            return

        fig = self.ui_components.fig_container.children[0]
        processed_df = self.data_processor.apply_data_processing(self.df, self.state['series'], self.state['resample_rule'])

        self.chart_renderer.update_figure(
            fig, self.title, processed_df, self.state['series'],
            self.x_column, self.is_timeseries, self.ui_components.fig_container
        )

    # --- 事件处理 ---

    def _on_mode_change(self, change):
        self.state['layout_mode'] = change['new']
        # 更新所有系列的layout_mode
        for s in self.state['series']:
            s['layout_mode'] = change['new']
        self._update_figure()

    def _on_color_change(self, change, index):
        self.state['series'][index]['color'] = change['new']
        # 颜色改变不需要重构 Subplots，只需更新 Trace
        # 但为了简单，MVP 版本直接全量更新，后续可优化
        self._update_figure()

    def _on_visible_change(self, change, index):
        self.state['series'][index]['visible'] = change['new']
        self._update_figure()

    def _on_resample_change(self, change):
        """重采样规则变化处理"""
        self.state['resample_rule'] = change['new']
        self._update_figure()

    def _on_smooth_enabled_change(self, change, index):
        """平滑开关变化处理"""
        self.state['series'][index]['smooth_enabled'] = change['new']
        self._update_figure()

    def _on_smooth_window_change(self, change, index):
        """平滑窗口大小变化处理"""
        self.state['series'][index]['smooth_window'] = change['new']
        self._update_figure()

    def _on_x_axis_change(self, change):
        """X轴参数变化处理"""
        self.x_column = change['new']
        # 数据处理
        if self.x_column in self.df.columns:
            self.df[self.x_column] = pd.to_datetime(self.df[self.x_column])
            self.df = self.df.sort_values(self.x_column)

        self._update_figure()

    # 参数选择界面相关方法（保留兼容性）

    def _on_param_change(self, change):
        """X轴参数变化时的处理（参数选择界面）"""
        self.x_column = change['new']

        # 当X轴改变时，需要刷新Y轴参数表格（排除X轴列）
        if hasattr(self, 'y_param_table'):
            self._refresh_param_selection_table()

        # 检查是否可以开始绘图
        self._check_and_start_plotting()

    def _refresh_param_selection_table(self):
        """刷新参数选择表格（参数选择界面）"""
        self.ui_components._refresh_param_selection_table()

    def _on_y_param_toggle(self, change, col_name):
        """Y轴参数勾选变化处理"""
        if change['new']:
            # 添加参数
            if not any(s['col'] == col_name for s in self.state['series']):
                color = self._pending_colors.get(col_name, get_default_color(len(self.state['series'])))
                pending_s = self._pending_smooth.get(col_name, {})
                smooth_enabled = pending_s.get('enabled', False)
                smooth_window = pending_s.get('window', DEFAULT_SMOOTH_WINDOW)
                self.state['series'].append({
                    'col': col_name,
                    'color': color,
                    'visible': True,
                    'smooth_enabled': smooth_enabled,
                    'smooth_window': smooth_window
                })
        else:
            # 移除参数
            self.state['series'] = [s for s in self.state['series'] if s['col'] != col_name]

        # 检查是否可以开始绘图
        self._check_and_start_plotting()

    def _check_and_start_plotting(self):
        """检查参数是否完整，决定是否开始绘图"""
        if (self.x_column or self.is_timeseries) and self.state['series']:
            self.y_columns = [s['col'] for s in self.state['series']]

            # 数据处理
            if self.is_timeseries:
                # 时间序列DataFrame：确保索引是datetime类型并排序
                if not isinstance(self.df.index, pd.DatetimeIndex):
                    self.df.index = pd.to_datetime(self.df.index)
                self.df = self.df.sort_index()
            elif self.x_column in self.df.columns:
                self.df[self.x_column] = pd.to_datetime(self.df[self.x_column])
                self.df = self.df.sort_values(self.x_column)

            # 初始化图表
            self._init_figure()

            # 仅更新图表区域（保持左侧参数面板不变）
            self._update_figure()
        else:
            # 当没有有效的参数时，清空图表
            if hasattr(self, 'fig') and hasattr(self, 'fig_container'):
                self.fig.data = []
                self._set_fig_container()

    def _on_param_color_change(self, change, col_name):
        """Y轴参数行的颜色选择变化处理"""
        new_color = change['new']
        self._pending_colors[col_name] = new_color
        # 更新现有系列的颜色并刷新图表
        for s in self.state['series']:
            if s['col'] == col_name:
                s['color'] = new_color
                self._update_figure()
                break

    def _on_param_smooth_change(self, change, col_name, kind):
        """参数行中平滑开关或窗口变化处理（用于参数选择界面）"""
        entry = self._pending_smooth.get(col_name, {'enabled': False, 'window': DEFAULT_SMOOTH_WINDOW})
        if kind == 'enabled':
            entry['enabled'] = bool(change['new'])
        elif kind == 'window':
            try:
                entry['window'] = int(change['new'])
            except Exception:
                entry['window'] = entry.get('window', DEFAULT_SMOOTH_WINDOW)
        self._pending_smooth[col_name] = entry
        # 如果该系列已经存在于 state 中，也要同步更新
        for s in self.state['series']:
            if s['col'] == col_name:
                s['smooth_enabled'] = entry['enabled']
                s['smooth_window'] = entry['window']
                self._update_figure()
                break

    def _on_reselect_params(self, button):
        """重新选择参数"""
        self.x_column = None
        self.y_columns = []
        self.state['series'] = []
        self._show_param_selection()
