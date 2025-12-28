"""
图表渲染模块
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from typing import List, Dict, Any, Optional, Tuple

from .constants import DEFAULT_FIGSIZE

# 每个分栏子图的固定像素高度（分栏模式下每个参数的高度）
DEFAULT_SUBPLOT_HEIGHT_PX = 200

class ChartRenderer:
    """图表渲染器"""

    def __init__(self, figsize: Tuple[int, int] = DEFAULT_FIGSIZE):
        self.figsize = figsize
        self.fig = None

    def create_figure_widget(self) -> go.FigureWidget:
        """创建配置好的FigureWidget"""
        fig = go.FigureWidget()
        self._configure_figure_widget(fig)
        return fig

    def _configure_figure_widget(self, fig: go.FigureWidget):
        """配置FigureWidget的响应式设置"""
        # 设置图表配置
        config = {
            'responsive': False,  # 使用固定尺寸
            # 禁用 plotly 的内置 modebar（我们使用自定义 ipywidgets 工具栏）
            'displayModeBar': False,
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
            width=int(self.figsize[0] * 72) - 10,  # 转换为像素
            height=int(self.figsize[1] * 72) - 10,  # 转换为像素
            margin=dict(l=50, r=50, t=50, b=50),
        )

        # 添加响应式CSS类
        try:
            fig.add_class('plotly-responsive')
        except:
            pass

    def update_figure_layout(self, fig: go.FigureWidget, title: str, yaxis_range: Optional[List[float]] = None,
                           mode: str = 'overlay', series_count: int = 1, show_legend: bool = True):
        """更新图表布局的通用方法"""
        # 将figsize转换为像素 (matplotlib默认72 DPI)
        dpi = 72
        width_px = int(self.figsize[0] * dpi) - 10
        base_height_px = int(self.figsize[1] * dpi) - 10

        # 根据显示模式计算图形内部高度（像素）
        if mode == 'overlay':
            # 叠加模式：图表高度严格等于 figsize 指定的高度
            height = base_height_px
        elif mode == 'split':
            # 分栏模式：每个参数使用固定像素高度，整体图高度会随参数数量增加而增长
            per_series_px = DEFAULT_SUBPLOT_HEIGHT_PX
            height = series_count * per_series_px
        else:
            height = base_height_px

        # 计算右边距：为图例和 modebar 留出适度空间（分栏模式也将图例放入绘图区内侧）
        right_margin = 30

        layout_kwargs = {
            'width': width_px,
            'height': height,
            'showlegend': show_legend,
            # 为右侧 legend 和 modebar 留出空间
            #'margin': dict(l=60, r=right_margin, t=80, b=50),
            'template': 'plotly_white',
            'hovermode': 'x unified',
            # 使用 plotly 内置 title 布局，居中显示
            'title': {
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 18, 'color': '#092b4a'}
            },
            'title_x': 0.5
        }

        if show_legend:
            # 分栏模式下将图例放在绘图区外侧并在右边显示；叠加模式下放在绘图区内侧
            # 对于 split 模式也使用绘图区内侧的竖直图例（与 overlay 保持一致）
            layout_kwargs['legend'] = dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="right",
                x=0.98,
                bgcolor='rgba(255,255,255,0.0)',
                borderwidth=0,
                itemclick='toggleothers',
                traceorder='normal'
            )

        if yaxis_range is not None:
            layout_kwargs['yaxis'] = dict(range=yaxis_range, title="Value")

        fig.update_layout(**layout_kwargs)

    def create_scatter_trace(self, trace_data: Dict[str, Any]) -> go.Scatter:
        """创建scatter trace的通用方法"""
        return go.Scatter(
            x=trace_data['x'],
            y=trace_data['y'],
            name=trace_data['name'],
            line=dict(color=trace_data['color']),
            mode='lines',
            connectgaps=True
        )

    def update_figure(self, fig: go.FigureWidget, title: str, processed_df: pd.DataFrame,
                     series: List[Dict], x_column: Optional[str], is_timeseries: bool,
                     fig_container: widgets.Box):
        """核心绘图逻辑"""
        # 计算基础像素高度（与 update_figure_layout 保持一致）
        dpi = 72
        base_height_px = int(self.figsize[1] * dpi) - 10
        width_px = int(self.figsize[0] * dpi) - 10
        mode = series[0].get('layout_mode', 'overlay') if series else 'overlay'
        visible_series = [s for s in series if s.get('visible')]

        if not visible_series:
            # 清空图表
            fig.data = []
            fig_container.children = [fig]
            return

        if mode == 'overlay':
            # 叠加模式：创建新的FigureWidget以清除分栏模式残留并更新数据与布局
            fig = self.create_figure_widget()

            # 先收集所有数值型数据以计算统一的y轴范围（忽略非数值）
            all_y_values = []
            traces = []
            x_values = processed_df.index if is_timeseries else (processed_df[x_column] if x_column in processed_df.columns else None)

            for s in visible_series:
                # 强制转换为数值，非数值转换为 NaN 并在绘图前过滤
                y_series = pd.to_numeric(processed_df.get(s['col'], pd.Series()), errors='coerce')
                mask = ~y_series.isna()
                if mask.sum() == 0:
                    # 没有可绘制的数据，跳过该系列
                    continue
                all_y_values.append(y_series[mask])
                trace_x = x_values[mask] if x_values is not None else processed_df.index[mask]
                traces.append(dict(x=trace_x, y=y_series[mask], name=s['col'], color=s['color']))

            # debug removed

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
            self.update_figure_layout(fig, title, yaxis_range, mode='overlay', series_count=len(traces), show_legend=True)

            # 添加所有traces
            for t in traces:
                fig.add_trace(self.create_scatter_trace(t))

            # debug removed

        elif mode == 'split':
            # 分栏模式：重新创建多行子图结构
            rows = len(visible_series)
            titles = [s['col'] for s in visible_series]

            # 创建FigureWidget用于分栏模式（不在每个子图上显示标题，使用右侧图例辨识）
            fig = self.create_figure_widget()
            fig.set_subplots(
                rows=rows, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05
            )
            # 在分栏模式下显示右侧图例（通过 layout 控制）
            self.update_figure_layout(fig, title, mode='split', series_count=rows, show_legend=True)

            # 每个可见的 trace 放在对应的子图中
            for i, s in enumerate(visible_series):
                x_data = processed_df.index if is_timeseries else processed_df[x_column]
                trace = self.create_scatter_trace({
                    'x': x_data,
                    'y': processed_df[s['col']],
                    'name': s['col'],
                    'color': s['color']
                })
                fig.add_trace(trace, row=i+1, col=1)

            # debug removed

        # 更新容器
        fig_container.children = [fig]
        # 容器高度控制策略：
        # - 叠加模式：容器高度与 figsize 保持一致（不出现额外滚动）
        # - 分栏模式：容器高度固定为 figsize 高度，图形内部高度会随参数数量变大，容器显示滚动条用于浏览
        try:
            # 只同步容器高度为 figsize 指定的高度；不要强制设置容器宽度，
            # 容器宽度由外部布局（left panel + grid）控制，避免页面溢出。
            fig_container.layout.height = f"{int(base_height_px)}px"
        except Exception:
            pass
