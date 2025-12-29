"""
统计图表渲染模块
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import math

from .constants import DEFAULT_FIGSIZE, STATISTICS_LABELS, DEFAULT_COLORS
from .utils import format_statistic_value, get_default_color


def hex_to_rgba(hex_color: str, alpha: float = 0.1) -> str:
    """将hex颜色转换为rgba格式"""
    if not hex_color.startswith('#'):
        return hex_color

    # 移除#号
    hex_color = hex_color[1:]

    # 转换为RGB值
    if len(hex_color) == 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    elif len(hex_color) == 3:
        r = int(hex_color[0] * 2, 16)
        g = int(hex_color[1] * 2, 16)
        b = int(hex_color[2] * 2, 16)
    else:
        return hex_color

    return f'rgba({r}, {g}, {b}, {alpha})'


class StatisticsChartRenderer:
    """统计图表渲染器"""

    def __init__(self, figsize: Tuple[int, int] = DEFAULT_FIGSIZE):
        self.figsize = figsize
        self.fig = None
        # 子图尺寸缩放因子（相对于 figsize 高度），可调以控制子图大小
        self._subplot_scale = 0.40
        self._subplot_min_px = 160

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
            'displayModeBar': True,  # 显示plotly工具栏
            'displaylogo': False,
            'modeBarButtonsToRemove': []
        }
        try:
            fig._config = config
        except:
            pass

        # 设置基础布局
        fig.update_layout(
            autosize=False,
            width=int(self.figsize[0] * 72) - 10,
            height=int(self.figsize[1] * 72) - 10,
            margin=dict(l=50, r=50, t=50, b=50),
        )

        # 添加响应式CSS类
        try:
            fig.add_class('plotly-responsive')
        except:
            pass

    def _create_empty_figure(self, fig_container: widgets.Box, message: str = "没有数据可显示") -> go.FigureWidget:
        """创建一个带居中提示文本的空图并放入容器，返回 FigureWidget"""
        fig = self.create_figure_widget()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig_container.children = [fig]
        return fig

    def _build_summary_table_trace(self, stats_df: pd.DataFrame) -> Tuple[go.Table, List[str]]:
        """根据 stats_df 构建并返回 Plotly Table trace 与行标签（指标顺序）"""
        row_labels = list(STATISTICS_LABELS.keys())

        # 每列按 row_labels 的顺序抓取并格式化
        col_values = []
        col_values.append(row_labels)
        for col in stats_df.columns:
            col_list = []
            for r in row_labels:
                try:
                    val = stats_df.at[r, col]
                except Exception:
                    val = stats_df.loc[r, col] if (r in stats_df.index and col in stats_df.columns) else None
                col_list.append(format_statistic_value(val))
            col_values.append(col_list)

        # 行背景与对齐
        n_rows = len(row_labels)
        row_colors = ['#ffffff' if i % 2 == 0 else '#f7f9fc' for i in range(n_rows)]
        cells_fill_colors = [row_colors] + [row_colors for _ in stats_df.columns]
        align_cols = ['left'] + ['right'] * len(stats_df.columns)

        table = go.Table(
            header=dict(
                values=["指标"] + list(stats_df.columns),
                fill_color='#2c3e50',
                align='center',
                font=dict(size=14, color='white', family='Arial'),
                height=42,
                line=dict(color='#cfd8e3', width=1)
            ),
            cells=dict(
                values=col_values,
                fill_color=cells_fill_colors,
                align=align_cols,
                font=dict(size=13, color='#17202a', family='Arial'),
                height=34,
                line=dict(color='#e6eef6', width=1)
            )
        )
        return table, row_labels

    def _compute_subplot_sizes(self, n_items: int, rows: int = 2) -> Tuple[int, int, int, float, float, int]:
        """
        计算子图尺寸和间距比例。
        返回 (per_col_size, total_width, total_height, horizontal_spacing_ratio, vertical_spacing_ratio, cols_per_row)
        """
        cols_per_row = math.ceil(n_items / rows) if rows > 0 else n_items
        per_col_size = max(self._subplot_min_px, int(self.figsize[1] * 72 * self._subplot_scale) - 10)
        total_width = per_col_size * max(1, cols_per_row)
        total_height = per_col_size * rows
        horizontal_spacing_ratio = 40.0 / total_width if cols_per_row > 1 else 0.0
        vertical_spacing_ratio = 40.0 / total_height if total_height > 0 else 0.0
        return per_col_size, total_width, total_height, horizontal_spacing_ratio, vertical_spacing_ratio, cols_per_row

    def _apply_subplot_borders(self, fig: go.Figure, rows: int, cols: int,
                               stroke_color: str = "#d9d9d9", fillcolor: str = "white", line_width: int = 1) -> None:
        """
        为子图添加边框 shapes 并将背景设为白色。
        rows, cols: grid 的行列数（cols 表示每行的列数）
        """
        try:
            shapes = []
            total = rows * cols
            for r in range(1, rows + 1):
                for c in range(1, cols + 1):
                    idx = (r - 1) * cols + c
                    xaxis_name = 'xaxis' if idx == 1 else f'xaxis{idx}'
                    yaxis_name = 'yaxis' if idx == 1 else f'yaxis{idx}'
                    xaxis = getattr(fig.layout, xaxis_name, None)
                    yaxis = getattr(fig.layout, yaxis_name, None)
                    xdom = getattr(xaxis, 'domain', None) if xaxis is not None else None
                    ydom = getattr(yaxis, 'domain', None) if yaxis is not None else None
                    if xdom and ydom:
                        shapes.append(dict(
                            type="rect",
                            xref="paper", yref="paper",
                            x0=xdom[0], x1=xdom[1],
                            y0=ydom[0], y1=ydom[1],
                            line=dict(color=stroke_color, width=line_width),
                            fillcolor=fillcolor,
                            layer="below"
                        ))
            if shapes:
                fig.update_layout(shapes=shapes, plot_bgcolor=fillcolor, paper_bgcolor=fillcolor)
        except Exception:
            # 保持向后兼容：若发生任何问题，不影响整体渲染
            pass

    def _apply_common_layout(self, fig: go.Figure, width: int, height: int,
                             margin: Dict[str, int] = None, showlegend: bool = False) -> None:
        """统一更新布局的 helper"""
        if margin is None:
            margin = dict(l=20, r=10, t=10, b=20)
        fig.update_layout(
            width=width,
            height=height,
            showlegend=showlegend,
            margin=margin
        )

    def render_summary_table(self, stats_df: pd.DataFrame, fig_container: widgets.Box) -> go.FigureWidget:
        """渲染统计汇总表"""
        if stats_df.empty:
            return self._create_empty_figure(fig_container)

        fig = self.create_figure_widget()

        table_trace, row_labels = self._build_summary_table_trace(stats_df)
        fig.add_trace(table_trace)

        # 更新布局：尽量填充右侧高度，宽度增加以支持左右滚动（容器已设置 overflow_x='auto'）
        # 首先尝试读取外部容器的高度（例如 '600px'）
        container_height = None
        try:
            container_height = getattr(fig_container, 'layout', None).height
        except Exception:
            container_height = None

        # 宽度按 figsize 放大 1.4 倍，且至少保证每列有约120px 可用宽度
        min_per_col_px = 120
        computed_min_width = int(len(stats_df.columns) * min_per_col_px + 200)
        computed_fig_width = max(int(self.figsize[0] * 72 * 1.4), computed_min_width)

        # 高度优先使用容器高度（减去边距），否则使用基于行数的高度（加大行高与上下边距）
        if container_height:
            try:
                if isinstance(container_height, str) and container_height.endswith('px'):
                    h_px = int(container_height[:-2])
                else:
                    h_px = int(container_height)
                # 为表头和底部保留更多空间，略微减少容器高度
                fig_height = max(360, h_px - 40)
            except Exception:
                fig_height = max(480, len(row_labels) * 34 + 140)
        else:
            fig_height = max(480, len(row_labels) * 34 + 140)

        fig.update_layout(
            width=computed_fig_width,
            height=fig_height,
            margin=dict(l=20, r=20, t=20, b=20),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        # 将 FigureWidget 放入外层容器，容器布局负责显示滚动条（fig_container 在 UI 中已设置 overflow_x='auto'）
        fig_container.children = [fig]
        return fig

    def render_boxplot(self, boxplot_data: List[Dict[str, Any]], fig_container: widgets.Box) -> go.FigureWidget:
        """渲染箱线图"""
        if not boxplot_data:
            fig = self.create_figure_widget()
            fig.add_annotation(
                text="没有数据可显示",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="gray")
            )
            fig_container.children = [fig]
            return fig
        # 采用两排布局：将参数平均分配到两行，子图间留出20px空隙
        n = len(boxplot_data)
        cols_per_row = math.ceil(n / 2)

        # 计算20px间距对应的比例
        per_col_size, total_width, total_height, horizontal_spacing_ratio, vertical_spacing_ratio, _cols = \
            self._compute_subplot_sizes(n, rows=2)

        fig = make_subplots(rows=2, cols=cols_per_row, shared_xaxes=False, shared_yaxes=False,
                            horizontal_spacing=horizontal_spacing_ratio, vertical_spacing=vertical_spacing_ratio)

        for i, data in enumerate(boxplot_data):
            color = get_default_color(i)
            row = 1 + (i // cols_per_row)
            col = (i % cols_per_row) + 1

            # 添加箱线图到对应子图
            fig.add_trace(go.Box(
                y=data['data'],
                name=data['column'],
                marker_color=color,
                boxmean=True,
                showlegend=False
            ), row=row, col=col)

            # 添加异常值散点（如果有）
            if data['outliers']:
                fig.add_trace(go.Scatter(
                    x=[0] * len(data['outliers']),
                    y=data['outliers'],
                    mode='markers',
                    marker=dict(color='red', size=6, symbol='x'),
                    name=f"{data['column']} 异常值",
                    showlegend=False
                ), row=row, col=col)
            # y轴刻度字体统一
            fig.update_yaxes(tickfont=dict(size=11), row=row, col=col)

        # 每个子图宽度与高度相同（方形），以 figsize 的高度为基准（单行高度）
        rows = 2
        # 使用计算好的 total_width/total_height 并应用统一布局
        self._apply_common_layout(fig, width=total_width, height=total_height, margin=dict(l=20, r=10, t=10, b=20))
        # 添加子图边框并设置白色背景
        self._apply_subplot_borders(fig, rows=rows, cols=cols_per_row)

        fig_container.children = [go.FigureWidget(fig)]
        return go.FigureWidget(fig)

    def render_histogram(self, columns: List[str], data_processor, fig_container: widgets.Box) -> go.FigureWidget:
        """渲染直方图"""
        if not columns:
            fig = self.create_figure_widget()
            fig.add_annotation(
                text="没有数据可显示",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="gray")
            )
            fig_container.children = [fig]
            return fig

        # 两排布局：单行多列改为两行，子图间留出20px空隙
        cols = len(columns)
        cols_per_row = math.ceil(cols / 2)

        # 计算20px间距对应的比例
        per_col_size, total_width, total_height, horizontal_spacing_ratio, vertical_spacing_ratio, _cols = \
            self._compute_subplot_sizes(cols, rows=2)

        fig = make_subplots(rows=2, cols=cols_per_row, shared_xaxes=False, shared_yaxes=False,
                            horizontal_spacing=horizontal_spacing_ratio, vertical_spacing=vertical_spacing_ratio)

        for i, col in enumerate(columns):
            row = 1 + (i // cols_per_row)
            col_idx = (i % cols_per_row) + 1
            hist_data, bin_edges = data_processor.get_histogram_data(col)
            if len(hist_data) > 0:
                bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                fig.add_trace(
                    go.Bar(
                        x=bin_centers,
                        y=hist_data,
                        name=col,
                        marker_color=get_default_color(i),
                        showlegend=False
                    ),
                    row=row, col=col_idx
                )
            # 轴标签：底部行显示x轴参数名称，左侧列显示y轴标签

            # 底部行显示参数名称作为X轴标题，其余行隐藏x轴刻度以避免重复
            fig.update_xaxes(title_text=col, row=row, col=col_idx,
                title_font=dict(size=12), tickfont=dict(size=11), title_standoff=2)

            # 左侧列显示Y轴标题（频数），并统一字体；其他列只显示刻度
            if col_idx == 1:
                fig.update_yaxes(title_text="频数", row=row, col=col_idx,
                                 title_font=dict(size=12), tickfont=dict(size=11))
            else:
                fig.update_yaxes(showticklabels=True, row=row, col=col_idx, tickfont=dict(size=11))

        # 每个子图为方形，宽度使用高度像素值
        rows = 2
        self._apply_common_layout(fig, width=total_width, height=total_height, margin=dict(l=20, r=10, t=10, b=20))
        self._apply_subplot_borders(fig, rows=rows, cols=cols_per_row)

        fig_container.children = [go.FigureWidget(fig)]
        return go.FigureWidget(fig)

    def render_density_plot(self, columns: List[str], data_processor, fig_container: widgets.Box) -> go.FigureWidget:
        """渲染密度图"""
        if not columns:
            fig = self.create_figure_widget()
            fig.add_annotation(
                text="没有数据可显示",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="gray")
            )
            fig_container.children = [fig]
            return fig

        # 两排布局：每列一个变量的密度曲线，子图间留出20px空隙
        cols = len(columns)
        cols_per_row = math.ceil(cols / 2)

        # 计算20px间距对应的比例
        per_col_size = max(self._subplot_min_px, int(self.figsize[1] * 72 * self._subplot_scale) - 10)
        total_width = per_col_size * max(1, cols_per_row)
        total_height = per_col_size * 2
        horizontal_spacing_ratio = 40.0 / total_width if cols_per_row > 1 else 0.0
        vertical_spacing_ratio = 40.0 / total_height

        fig = make_subplots(rows=2, cols=cols_per_row, shared_xaxes=False, shared_yaxes=False,
                            horizontal_spacing=horizontal_spacing_ratio, vertical_spacing=vertical_spacing_ratio)

        for i, col in enumerate(columns):
            row = 1 + (i // cols_per_row)
            col_idx = (i % cols_per_row) + 1
            x_data, density = data_processor.get_density_data(col)
            if len(x_data) > 0 and len(density) > 0:
                fig.add_trace(go.Scatter(
                    x=x_data,
                    y=density,
                    mode='lines',
                    name=col,
                    line=dict(color=get_default_color(i), width=2),
                    fill='tozeroy',
                    fillcolor=hex_to_rgba(get_default_color(i), 0.1),
                    showlegend=False
                ), row=row, col=col_idx)
            # 轴标签：底部行显示x轴参数名称，左侧列显示y轴标签

            # 底部行显示参数名称作为X轴标题，其余行隐藏x轴刻度以避免重复
            fig.update_xaxes(title_text=col, row=row, col=col_idx,
                title_font=dict(size=12), tickfont=dict(size=11), title_standoff=2)

            # 左侧列显示Y轴标题（密度），并统一字体；其他列只显示刻度
            if col_idx == 1:
                fig.update_yaxes(title_text="密度", row=row, col=col_idx,
                                 title_font=dict(size=12), tickfont=dict(size=11))
            else:
                fig.update_yaxes(showticklabels=True, row=row, col=col_idx, tickfont=dict(size=11))

        # 每个子图为方形，宽度使用高度像素值
        per_col_size = max(self._subplot_min_px, int(self.figsize[1] * 72 * self._subplot_scale) - 10)
        total_width = per_col_size * max(1, cols_per_row)
        rows = 2
        total_height = per_col_size * rows

        fig.update_layout(
            width=total_width,
            height=total_height,
            showlegend=False,
            margin=dict(l=20, r=10, t=10, b=20)
        )
        # 添加子图边框并设置白色背景
        try:
            shapes = []
            rows = 2
            cols = cols_per_row
            for r in range(1, rows + 1):
                for c in range(1, cols + 1):
                    idx = (r - 1) * cols + c
                    xaxis_name = 'xaxis' if idx == 1 else f'xaxis{idx}'
                    yaxis_name = 'yaxis' if idx == 1 else f'yaxis{idx}'
                    xaxis = getattr(fig.layout, xaxis_name, None)
                    yaxis = getattr(fig.layout, yaxis_name, None)
                    xdom = getattr(xaxis, 'domain', None) if xaxis is not None else None
                    ydom = getattr(yaxis, 'domain', None) if yaxis is not None else None
                    if xdom and ydom:
                        shapes.append(dict(
                            type="rect",
                            xref="paper", yref="paper",
                            x0=xdom[0], x1=xdom[1],
                            y0=ydom[0], y1=ydom[1],
                            line=dict(color="#d9d9d9", width=1),
                            fillcolor="white",
                            layer="below"
                        ))
            if shapes:
                fig.update_layout(shapes=shapes, plot_bgcolor='white', paper_bgcolor='white')
        except Exception:
            pass

        fig_container.children = [go.FigureWidget(fig)]
        return go.FigureWidget(fig)

    def render_chart(self, chart_type: str, data_processor, columns: List[str],
                    scatter_columns: Optional[Tuple[str, str]], fig_container: widgets.Box) -> go.FigureWidget:
        """根据类型渲染对应的图表"""
        if chart_type == 'summary':
            # 计算统计数据
            stats_df = data_processor.calculate_basic_statistics(columns)
            return self.render_summary_table(stats_df, fig_container)

        elif chart_type == 'boxplot':
            # 准备箱线图数据
            boxplot_data = data_processor.prepare_boxplot_data(columns)
            return self.render_boxplot(boxplot_data, fig_container)

        elif chart_type == 'histogram':
            return self.render_histogram(columns, data_processor, fig_container)

        elif chart_type == 'density':
            return self.render_density_plot(columns, data_processor, fig_container)

        else:
            # 默认显示汇总表
            stats_df = data_processor.calculate_basic_statistics(columns)
            return self.render_summary_table(stats_df, fig_container)
