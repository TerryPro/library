"""
动态统计分析组件主类
"""

import pandas as pd
import ipywidgets as widgets
from ipywidgets import VBox, Layout
from typing import List, Dict, Optional, Tuple, Any

from .constants import DEFAULT_TITLE, DEFAULT_FIGSIZE, DEFAULT_CHART_TYPE
from .data_processor import StatisticsDataProcessor
from .ui_components import StatisticsUIComponents
from .chart_renderer import StatisticsChartRenderer


class DynamicStaticWidget(VBox):
    """动态统计分析组件"""

    def __init__(self, df: pd.DataFrame, columns: Optional[List[str]] = None,
                 chart_type: str = DEFAULT_CHART_TYPE, title: str = DEFAULT_TITLE,
                 figsize: Tuple[int, int] = DEFAULT_FIGSIZE):
        super().__init__(layout=Layout(width='100%'))

        self.df = df.copy()
        self.title = title
        self.figsize = figsize

        # 初始化组件（需要先初始化data_processor）
        self.data_processor = StatisticsDataProcessor(self.df)
        self.ui_components = StatisticsUIComponents(self.df)
        self.chart_renderer = StatisticsChartRenderer(self.figsize)

        # 初始化状态
        self.state = {
            'selected_columns': columns or self._get_default_columns(),
            'chart_type': chart_type,
            'figsize': figsize
        }

        # Wire UI callbacks
        self.ui_components.on_column_selection_change = self._on_column_selection_change
        self.ui_components.on_chart_type_change = self._on_chart_type_change
        # 监听图表尺寸变化
        if hasattr(self.ui_components, 'on_figsize_change'):
            self.ui_components.on_figsize_change = self._on_figsize_change

        # 初始化UI
        self._init_ui()

        # 绑定工具栏事件
        self._bind_toolbar_events()

        # 初始化图表
        self._update_chart()

    def _get_default_columns(self) -> List[str]:
        """获取默认选择的列"""
        numeric_columns = self.data_processor.get_numeric_columns()
        # 默认选择前5个数值列
        return numeric_columns[:5] if len(numeric_columns) >= 5 else numeric_columns

    def _init_ui(self):
        """初始化UI"""
        # 设置UI组件的初始状态
        self.ui_components.set_chart_type(self.state['chart_type'])
        self.ui_components.set_selected_columns(self.state['selected_columns'])
        # 同步图表尺寸选择器
        try:
            self.ui_components.figsize_selector.value = self.figsize
        except Exception:
            pass

        # 创建主UI
        main_ui = self.ui_components.create_main_ui()
        self.children = [main_ui]

    def _bind_toolbar_events(self):
        """绑定工具栏事件"""
        self.ui_components.toolbar_reset.on_click(self._on_reset)
        self.ui_components.toolbar_export.on_click(self._on_export)

    def _update_chart(self):
        """更新图表显示"""
        selected_columns = self.ui_components.get_selected_columns()
        chart_type = self.ui_components.chart_type_selector.value
        # 更新状态
        self.state['selected_columns'] = selected_columns
        self.state['chart_type'] = chart_type

        # 渲染图表（scatter 已移除，传入 None）
        self.chart_renderer.render_chart(
            chart_type=chart_type,
            data_processor=self.data_processor,
            columns=selected_columns,
            scatter_columns=None,
            fig_container=self.ui_components.fig_container
        )

    def _on_column_selection_change(self, change, column):
        """列选择变化处理"""
        # 延迟更新，避免频繁刷新
        import threading
        if hasattr(self, '_update_timer'):
            self._update_timer.cancel()

        self._update_timer = threading.Timer(0.3, self._update_chart)
        self._update_timer.start()

    def _on_chart_type_change(self, change):
        """图表类型变化处理"""
        self._update_chart()

    def _on_figsize_change(self, change):
        """图表尺寸变化处理"""
        new_size = change.get('new')
        if new_size and isinstance(new_size, tuple):
            try:
                # 更新渲染器和状态
                self.figsize = new_size
                self.chart_renderer.figsize = new_size
                self.state['figsize'] = new_size
                # 触发重绘
                self._update_chart()
            except Exception:
                pass

    def _on_reset(self, button):
        """重置按钮处理"""
        # 重置为默认状态
        self.state['selected_columns'] = self._get_default_columns()
        self.state['chart_type'] = DEFAULT_CHART_TYPE

        # 更新UI
        self.ui_components.set_chart_type(DEFAULT_CHART_TYPE)
        self.ui_components.set_selected_columns(self.state['selected_columns'])

        # 更新图表
        self._update_chart()

    def _on_export(self, button):
        """导出按钮处理"""
        try:
            # 获取当前图表
            if self.ui_components.fig_container.children:
                fig = self.ui_components.fig_container.children[0]
                if hasattr(fig, 'write_image'):
                    # 使用plotly的导出功能
                    fig.write_image("statistics_chart.png", format='png', scale=2)
                    print("图表已导出为 statistics_chart.png")
                else:
                    print("当前图表不支持导出功能")
            else:
                print("没有图表可导出")
        except Exception as e:
            print(f"导出失败: {e}")
            print("请确保安装了kaleido: pip install kaleido")

    def get_selected_columns(self) -> List[str]:
        """获取当前选中的列"""
        return self.state['selected_columns'].copy()

    def get_chart_type(self) -> str:
        """获取当前图表类型"""
        return self.state['chart_type']

    def set_columns(self, columns: List[str]):
        """设置要分析的列"""
        valid_columns = [col for col in columns if col in self.df.columns]
        self.state['selected_columns'] = valid_columns
        self.ui_components.set_selected_columns(valid_columns)
        self._update_chart()

    def set_chart_type(self, chart_type: str):
        """设置图表类型"""
        from .constants import CHART_TYPE_OPTIONS
        valid_types = [option[1] for option in CHART_TYPE_OPTIONS]
        if chart_type in valid_types:
            self.state['chart_type'] = chart_type
            self.ui_components.set_chart_type(chart_type)
            self._update_chart()

    def get_statistics_summary(self) -> pd.DataFrame:
        """获取统计汇总数据"""
        return self.data_processor.calculate_basic_statistics(self.state['selected_columns'])

    def get_data_summary(self) -> Dict[str, Any]:
        """获取数据汇总信息"""
        return self.data_processor.get_data_summary(self.state['selected_columns'])
