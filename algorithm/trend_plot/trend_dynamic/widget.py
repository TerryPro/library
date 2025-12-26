
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from ipywidgets import HBox, VBox, Layout
from typing import List, Dict, Optional

class DynamicTrendWidget(VBox):
    def __init__(self, df: pd.DataFrame, x_column: str, y_columns: List[str], title: str = "动态趋势图"):
        super().__init__()
        
        self.df = df.copy()
        # 确保时间列是 datetime 类型并排序
        if x_column in self.df.columns:
            self.df[x_column] = pd.to_datetime(self.df[x_column])
            self.df = self.df.sort_values(x_column)
            
        self.x_column = x_column
        self.title = title
        
        # 初始化配置状态
        self.state = {
            'layout_mode': 'overlay',  # overlay | split
            'series': [
                {'col': col, 'color': self._get_default_color(i), 'visible': True}
                for i, col in enumerate(y_columns)
            ]
        }
        
        # 初始化 UI 组件
        self._init_ui()
        
        # 首次绘制
        self._update_figure()

    def _get_default_color(self, index: int) -> str:
        colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        return colors[index % len(colors)]

    def _init_ui(self):
        # 1. 顶部工具栏
        self.mode_selector = widgets.ToggleButtons(
            options=[('叠加模式', 'overlay'), ('分栏模式', 'split')],
            value='overlay',
            description='布局模式:',
            style={'button_width': '100px'}
        )
        self.mode_selector.observe(self._on_mode_change, names='value')
        
        self.toolbar = HBox([self.mode_selector], layout=Layout(margin='0 0 10px 0'))
        
        # 2. 侧边栏 (参数列表)
        self.sidebar_items = VBox(layout=Layout(width='250px', margin='0 10px 0 0'))
        self._refresh_sidebar()
        
        # 3. 绘图区域 - 初始化时就创建最大行数的子图
        max_rows = len(self.state['series'])
        titles = [s['col'] for s in self.state['series']]
        
        # 直接创建FigureWidget并设置子图
        self.fig = go.FigureWidget()
        self.fig.set_subplots(
            rows=max_rows, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=titles
        )
        self.fig.update_layout(
            title=self.title,
            margin=dict(l=50, r=20, t=50, b=50),
            height=600,
            template='plotly_white',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            autosize=True  # 启用自动适应容器大小
        )
        
        # 4. 组合布局
        # 简化布局结构，避免多层嵌套
        # 使用flex布局确保图表区域填充剩余空间
        # 为图表创建一个容器并设置flex属性
        fig_container = widgets.Box([self.fig], layout=Layout(flex='1', min_width='0'))
        
        self.main_area = HBox([self.sidebar_items, fig_container], 
                             layout=Layout(width='100%', display='flex', flex_flow='row', align_items='stretch'))
        
        self.children = [self.toolbar, self.main_area]

    def _refresh_sidebar(self):
        """根据 state['series'] 重新生成侧边栏控件"""
        items = []
        total = len(self.state['series'])
        
        for i, s in enumerate(self.state['series']):
            # 颜色选择器
            color_picker = widgets.ColorPicker(
                concise=True, 
                value=s['color'], 
                layout=Layout(width='30px')
            )
            color_picker.observe(lambda c, idx=i: self._on_color_change(c, idx), names='value')
            
            # 可见性复选框
            checkbox = widgets.Checkbox(
                value=s['visible'], 
                indent=False, 
                layout=Layout(width='20px')
            )
            checkbox.observe(lambda c, idx=i: self._on_visible_change(c, idx), names='value')
            
            # 标签
            label = widgets.Label(value=s['col'], layout=Layout(width='120px', overflow='hidden'))
            
            # 排序按钮
            up_btn = widgets.Button(icon='arrow-up', layout=Layout(width='30px', height='25px'))
            up_btn.disabled = (i == 0)
            up_btn.on_click(lambda b, idx=i: self._move_item(idx, -1))
            
            down_btn = widgets.Button(icon='arrow-down', layout=Layout(width='30px', height='25px'))
            down_btn.disabled = (i == total - 1)
            down_btn.on_click(lambda b, idx=i: self._move_item(idx, 1))
            
            # 单行容器
            row = HBox([checkbox, color_picker, label, up_btn, down_btn], layout=Layout(align_items='center', margin='2px 0'))
            items.append(row)
            
        self.sidebar_items.children = items

    def _update_figure(self):
        """核心绘图逻辑"""
        mode = self.state['layout_mode']
        series = [s for s in self.state['series'] if s['visible']]
        
        with self.fig.batch_update():
            self.fig.data = []  # 清空现有 Trace
            
            if not series:
                return

            if mode == 'overlay':
                # 叠加模式：所有 Trace 在第一个子图中
                self.fig.update_layout(
                    height=600,
                    showlegend=True,
                    yaxis_title="Value",
                    margin=dict(l=50, r=20, t=50, b=50),  # 减少右侧margin
                    autosize=True  # 自动适应容器大小
                )
                # 显示第一个子图的所有元素
                self.fig.update_yaxes(visible=True, row=1, col=1)
                self.fig.update_xaxes(visible=True, row=1, col=1)
                self.fig.update_layout({
                    f'annotations[0].visible': True
                })
                # 隐藏其他子图的所有元素
                for i in range(1, len(self.state['series'])):
                    self.fig.update_yaxes(visible=False, row=i+1, col=1)
                    self.fig.update_xaxes(visible=False, row=i+1, col=1)
                    self.fig.update_layout({
                        f'annotations[{i}].visible': False
                    })
                
                # 在第一个子图添加所有可见的 trace
                for s in series:
                    self.fig.add_trace(
                        go.Scatter(
                            x=self.df[self.x_column],
                            y=self.df[s['col']],
                            name=s['col'],
                            line=dict(color=s['color']),
                            mode='lines',
                            connectgaps=True
                        ),
                        row=1, col=1
                    )
                
            elif mode == 'split':
                # 分栏模式：每个 trace 在对应的子图中
                rows = len(series)
                self.fig.update_layout(
                    height=max(600, rows * 200),
                    showlegend=False,
                    margin=dict(l=50, r=20, t=50, b=50),  # 减少右侧margin
                    autosize=True  # 自动适应容器大小
                )
                
                # 显示需要的子图，隐藏不需要的
                for i in range(len(self.state['series'])):
                    if i < len(series):
                        # 显示第 i+1 个子图的所有元素
                        self.fig.update_yaxes(visible=True, row=i+1, col=1)
                        self.fig.update_xaxes(visible=True, row=i+1, col=1)
                        self.fig.update_layout({
                            f'annotations[{i}].visible': True
                        })
                    else:
                        # 隐藏第 i+1 个子图的所有元素
                        self.fig.update_yaxes(visible=False, row=i+1, col=1)
                        self.fig.update_xaxes(visible=False, row=i+1, col=1)
                        self.fig.update_layout({
                            f'annotations[{i}].visible': False
                        })
                
                # 每个可见的 trace 放在对应的子图中
                for i, s in enumerate(series):
                    self.fig.add_trace(
                        go.Scatter(
                            x=self.df[self.x_column],
                            y=self.df[s['col']],
                            name=s['col'],
                            line=dict(color=s['color']),
                            mode='lines',
                            connectgaps=True
                        ),
                        row=i+1, col=1
                    )

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

    def _move_item(self, index, direction):
        """调整顺序: direction -1 (up), 1 (down)"""
        new_index = index + direction
        if 0 <= new_index < len(self.state['series']):
            # 交换
            self.state['series'][index], self.state['series'][new_index] = \
                self.state['series'][new_index], self.state['series'][index]
            
            # 刷新 UI
            self._refresh_sidebar()
            self._update_figure()
