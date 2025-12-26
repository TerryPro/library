
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from ipywidgets import HBox, VBox, Layout
from typing import List, Dict, Optional

class DynamicTrendWidget(VBox):
    def __init__(self, df: pd.DataFrame, x_column: Optional[str] = None, y_columns: Optional[List[str]] = None, title: str = "动态趋势图", figsize: tuple = (16, 8)):
        super().__init__(layout=Layout(width='100%'))

        self.df = df.copy()
        self.title = title
        self.x_column = x_column
        self.y_columns = y_columns or []
        self.figsize = figsize  # (width, height) in inches

        # 数据处理：如果提供了x_column，转换为datetime并排序
        if self.x_column and self.x_column in self.df.columns:
            self.df[self.x_column] = pd.to_datetime(self.df[self.x_column])
            self.df = self.df.sort_values(self.x_column)

        # 初始化配置状态
        self.state = {
            'layout_mode': 'overlay',  # overlay | split
            'series': []
        }
        # 用于在添加系列前临时保存每列的颜色选择
        self._pending_colors: Dict[str, str] = {}

        # 初始化 UI 组件
        self._init_ui()

        # 如果有完整的参数，初始化图表并绘制
        if self.x_column and self.y_columns:
            self._init_series_state()
            self._init_figure()
            self._update_figure()
        else:
            # 显示参数选择界面
            self._show_param_selection()

    def _get_default_color(self, index: int) -> str:
        colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        return colors[index % len(colors)]

    def _create_dtype_icon(self, dtype: str) -> widgets.HTML:
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
            layout=Layout(width='36px')
        )

    def _create_param_row(self, children, margin='2px 0'):
        """创建参数行HBox"""
        return HBox(children, layout=Layout(align_items='center', margin=margin))

    def _update_figure_layout(self, title, yaxis_range=None, mode='overlay', series_count=1, show_legend=True):
        """更新图表布局的通用方法"""
        # 将figsize转换为像素 (matplotlib默认72 DPI)
        dpi = 72
        width_px = int(self.figsize[0] * dpi)
        base_height_px = int(self.figsize[1] * dpi)

        # 根据显示模式计算高度
        if mode == 'overlay':
            height = base_height_px  # 使用figsize指定的高度
        elif mode == 'split':
            # 分栏模式下，每条曲线使用基础高度的一部分
            height_per_series = max(200, base_height_px // max(1, series_count))
            height = series_count * height_per_series
        else:
            height = base_height_px

        layout_kwargs = {
            'title': title,
            'width': width_px,
            'height': height,
            'showlegend': show_legend,
            'margin': dict(l=50, r=10, t=50, b=50),
            'template': 'plotly_white',
            'hovermode': 'x unified'
            # 移除autosize，使用固定尺寸
        }

        if show_legend:
            layout_kwargs['legend'] = dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
            )

        if yaxis_range is not None:
            layout_kwargs['yaxis'] = dict(range=yaxis_range, title="Value")

        self.fig.update_layout(**layout_kwargs)

    def _create_scatter_trace(self, trace_data):
        """创建scatter trace的通用方法"""
        return go.Scatter(
            x=trace_data['x'],
            y=trace_data['y'],
            name=trace_data['name'],
            line=dict(color=trace_data['color']),
            mode='lines',
            connectgaps=True
        )

    def _init_series_state(self):
        """根据y_columns初始化系列状态"""
        self.state['series'] = [
            {'col': col, 'color': self._get_default_color(i), 'visible': True}
            for i, col in enumerate(self.y_columns)
        ]

    def _create_figure_widget(self):
        """创建配置好的FigureWidget"""
        fig = go.FigureWidget()
        self._configure_figure_widget(fig)
        return fig

    def _configure_figure_widget(self, fig):
        """配置FigureWidget的响应式设置"""
        # 设置图表配置
        config = {
            'responsive': False,  # 使用固定尺寸
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'autoScale2d']
        }
        try:
            fig._config = config
        except:
            pass

        # 设置基础布局 - 使用固定宽度以获得更好的显示效果
        fig.update_layout(
            autosize=False,  # 禁用自动调整大小
            width=1100,      # 设置固定宽度为1100px
            height=600,      # 设置固定高度为600px
            margin=dict(l=50, r=50, t=50, b=50),
        )

        # 添加响应式CSS类
        try:
            fig.add_class('plotly-responsive')
        except:
            pass

    def _init_figure(self):
        """初始化图表对象"""
        self.fig = self._create_figure_widget()

    def _set_fig_container(self):
        """设置fig_container的children并触发resize"""
        self.fig_container.children = [self.fig]
        # 触发plotly的resize事件以确保图表正确调整大小
        try:
            # 尝试不同的resize方法
            if hasattr(self.fig, '_js2py_resize'):
                self.fig._js2py_resize()
            elif hasattr(self.fig, '_relayout'):
                self.fig._relayout()
        except:
            pass

    def _show_param_selection(self):
        """显示参数选择界面"""
        # 构建主布局：左侧参数面板 + 右侧图表占位
        all_columns = self.df.columns.tolist()

        # X轴选择器（列出所有列供选择）
        self.x_selector = widgets.Dropdown(
            options=all_columns,
            value=self.x_column if (self.x_column in all_columns) else (all_columns[0] if all_columns else None),
            description='X轴参数:',
            layout=Layout(width='280px', margin='0 0 10px 0')
        )
        self.x_selector.observe(self._on_param_change, names='value')
        # 保持内部状态与选择器初始值一致（避免用户不切换但期望使用默认值的情况）
        self.x_column = self.x_selector.value

        # Y轴参数选择表格（列出所有数值型列，始终可见）
        self.y_param_table = VBox(layout=Layout(width='280px'))
        self._refresh_param_selection_table()

        # 左侧参数面板（简洁风格：不显示重复标题）
        self.left_panel = VBox([
            # 如果已有mode_selector则使用，否则创建一个简洁选择器（description 已在控件内部显示）
            getattr(self, 'mode_selector', widgets.Dropdown(
                options=[('叠加模式', 'overlay'), ('分栏模式', 'split')],
                value='overlay',
                description='显示方式:',
                layout=Layout(width='280px', margin='0 0 10px 0')
            )),
            self.x_selector,
            widgets.HTML("<h5 style='margin:10px 0 5px 0;'>Y轴参数</h5>"),
            self.y_param_table
        ], layout=Layout(width='300px', padding='6px', border='none'))

        # 右侧图表占位（初始为空或提示）
        placeholder = widgets.HTML("<div style='color:gray;padding:20px;'>请在左侧选择X轴和至少一个Y轴参数以显示图表</div>")
        # 使用 flex 布局让 FigureWidget 可以伸缩到容器全宽
        self.fig_container = widgets.Box([placeholder], layout=Layout(display='flex', align_items='stretch', width='100%', height='600px', min_width='0', flex='1 1 auto'))

        # 主布局：左侧固定，右侧自适应；始终保持在children中
        self.main_layout = widgets.GridBox(
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

        self.children = [self.main_layout]

    def _refresh_param_selection_table(self):
        """刷新参数选择表格"""
        # 仅列出数值型列，并排除当前选定的X轴列
        numeric_columns = self.df.select_dtypes(include=['number']).columns.tolist()
        all_columns = [col for col in numeric_columns if col != self.x_selector.value]

        table_rows = []
        for idx, col in enumerate(all_columns):
            # 复选框
            checkbox = widgets.Checkbox(
                value=False,
                indent=False,
                layout=Layout(width='20px', margin='0 5px 0 0')
            )
            checkbox.observe(lambda c, col_name=col: self._on_y_param_toggle(c, col_name), names='value')

            # 颜色选择器：优先使用已存在系列颜色，其次是pending颜色，否则使用默认色
            existing_series = next((s for s in self.state['series'] if s['col'] == col), None)
            if existing_series:
                color_value = existing_series.get('color', self._get_default_color(idx))
            else:
                color_value = self._pending_colors.get(col, self._get_default_color(idx))
            color_picker = widgets.ColorPicker(
                concise=True,
                value=color_value,
                layout=Layout(width='40px', margin='0 8px 0 0')
            )
            color_picker.observe(lambda c, col_name=col: self._on_param_color_change(c, col_name), names='value')

            # 参数名标签
            label = widgets.Label(
                value=col,
                layout=Layout(width='180px', overflow='hidden')
            )

            # 数据类型图标
            type_icon = self._create_dtype_icon(str(self.df[col].dtype))

            table_rows.append(self._create_param_row([checkbox, color_picker, label, type_icon]))

        self.y_param_table.children = table_rows

    def _on_y_param_toggle(self, change, col_name):
        """Y轴参数勾选变化处理"""
        if change['new']:
            # 添加参数
            if not any(s['col'] == col_name for s in self.state['series']):
                color = self._pending_colors.get(col_name, self._get_default_color(len(self.state['series'])))
                self.state['series'].append({
                    'col': col_name,
                    'color': color,
                    'visible': True
                })
        else:
            # 移除参数
            self.state['series'] = [s for s in self.state['series'] if s['col'] != col_name]

        # 检查是否可以开始绘图
        self._check_and_start_plotting()

    def _on_param_change(self, change):
        """X轴参数变化时的处理"""
        self.x_column = change['new']

        # 当X轴改变时，需要刷新Y轴参数表格（排除X轴列）
        if hasattr(self, 'y_param_table'):
            self._refresh_param_selection_table()

        # 检查是否可以开始绘图
        self._check_and_start_plotting()

    def _check_and_start_plotting(self):
        """检查参数是否完整，决定是否开始绘图"""
        if self.x_column and self.state['series']:
            self.y_columns = [s['col'] for s in self.state['series']]

            # 数据处理
            if self.x_column in self.df.columns:
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

    def _on_reselect_params(self, button):
        """重新选择参数"""
        self.x_column = None
        self.y_columns = []
        self.state['series'] = []
        self._show_param_selection()

    def _init_ui(self):
        # 1. 左侧参数配置面板
        self._init_left_panel()

        # 2. 右侧图表显示区域
        self.fig_container = widgets.Box([], layout=Layout(width='100%', height='600px', min_width='0', overflow='hidden'))

        # 3. 左右布局
        self.main_layout = widgets.GridBox(
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

        self.children = [self.main_layout]

    def _init_left_panel(self):
        """初始化左侧参数配置面板"""
        # 1. 显示方式选择器
        self.mode_selector = widgets.Dropdown(
            options=[('叠加模式', 'overlay'), ('分栏模式', 'split')],
            value='overlay',
            description='显示方式:',
            layout=Layout(width='280px', margin='0 0 10px 0')
        )
        self.mode_selector.observe(self._on_mode_change, names='value')

        # 2. X轴选择器
        all_columns = self.df.columns.tolist()
        self.x_selector = widgets.Dropdown(
            options=all_columns,
            value=self.x_column if self.x_column else (all_columns[0] if all_columns else None),
            description='X轴参数:',
            layout=Layout(width='280px', margin='0 0 10px 0')
        )
        self.x_selector.observe(self._on_x_axis_change, names='value')

        # 3. Y轴参数表格
        self.y_axis_table = VBox(layout=Layout(width='280px'))
        self._refresh_y_axis_table()

        # 4. 组合左侧面板
        self.left_panel = VBox([
            widgets.HTML("<h4 style='margin:0 0 10px 0;'>参数配置</h4>"),
            self.mode_selector,
            self.x_selector,
            widgets.HTML("<h5 style='margin:10px 0 5px 0;'>Y轴参数</h5>"),
            self.y_axis_table
        ], layout=Layout(width='300px', padding='10px', border='1px solid #ddd'))

    def _refresh_y_axis_table(self):
        """刷新Y轴参数表格"""
        if not self.state['series']:
            self.y_axis_table.children = [widgets.HTML("<p style='color:gray;'>暂无参数</p>")]
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

            # 参数名标签
            label = widgets.Label(
                value=s['col'],
                layout=Layout(width='200px', overflow='hidden')
            )

            table_rows.append(self._create_param_row([checkbox, color_picker, label]))

        self.y_axis_table.children = table_rows

    def _on_x_axis_change(self, change):
        """X轴参数变化处理"""
        self.x_column = change['new']
        # 数据处理
        if self.x_column in self.df.columns:
            self.df[self.x_column] = pd.to_datetime(self.df[self.x_column])
            self.df = self.df.sort_values(self.x_column)

        self._update_figure()


    def _update_figure(self):
        """核心绘图逻辑"""
        mode = self.state['layout_mode']
        series = [s for s in self.state['series'] if s['visible']]

        if not series:
            # 清空图表
            self.fig.data = []
            self._set_fig_container()
            return

        if mode == 'overlay':
            # 叠加模式：更新现有图表的数据和布局
            # 先收集所有数值型数据以计算统一的y轴范围（忽略非数值）
            all_y_values = []
            traces = []
            x_values = None
            if self.x_column in self.df.columns:
                x_values = self.df[self.x_column]

            for s in series:
                # 强制转换为数值，非数值转换为 NaN 并在绘图前过滤
                y_series = pd.to_numeric(self.df.get(s['col'], pd.Series()), errors='coerce')
                mask = ~y_series.isna()
                if mask.sum() == 0:
                    # 没有可绘制的数据，跳过该系列
                    continue
                all_y_values.append(y_series[mask])
                trace_x = x_values[mask] if x_values is not None else self.df.index[mask]
                traces.append(dict(x=trace_x, y=y_series[mask], name=s['col'], color=s['color']))

            # 计算y轴范围
            yaxis_range = None
            if all_y_values:
                concat_y = pd.concat(all_y_values)
                ymin = float(concat_y.min())
                ymax = float(concat_y.max())
                if ymin == ymax:
                    # 常数序列，给出小幅度上下边距
                    delta = abs(ymin) * 0.01 if ymin != 0 else 1.0
                    yaxis_range = [ymin - delta, ymax + delta]
                else:
                    span = ymax - ymin
                    margin = span * 0.05
                    yaxis_range = [ymin - margin, ymax + margin]

            # 更新布局
            self._update_figure_layout(self.title, yaxis_range, mode='overlay', series_count=len(traces), show_legend=True)

            # 添加所有traces
            for t in traces:
                self.fig.add_trace(self._create_scatter_trace(t))

        elif mode == 'split':
            # 分栏模式：重新创建多行子图结构
            rows = len(series)
            titles = [s['col'] for s in series]

            # 创建FigureWidget用于分栏模式
            self.fig = self._create_figure_widget()
            self.fig.set_subplots(
                rows=rows, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=titles
            )
            self._update_figure_layout(self.title, mode='split', series_count=rows, show_legend=False)

            # 每个可见的 trace 放在对应的子图中
            for i, s in enumerate(series):
                trace = self._create_scatter_trace({
                    'x': self.df[self.x_column],
                    'y': self.df[s['col']],
                    'name': s['col'],
                    'color': s['color']
                })
                self.fig.add_trace(trace, row=i+1, col=1)

        # 更新容器
        self.fig_container.children = [self.fig]

    # --- 事件处理 ---

    def _on_mode_change(self, change):
        self.state['layout_mode'] = change['new']
        self._update_figure()

    def _on_color_change(self, change, index):
        self.state['series'][index]['color'] = change['new']
        # 颜色改变不需要重构 Subplots，只需更新 Trace
        # 但为了简单，MVP 版本直接全量更新，后续可优化
        self._update_figure()

    def _on_visible_change(self, change, index):
        self.state['series'][index]['visible'] = change['new']
        self._update_figure()

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

