# -*- coding: utf-8 -*-
"""
Algorithm Widget
================
Notebook端的算法选择和执行Widget主类
"""

import ipywidgets as widgets
from IPython.display import display, clear_output
from IPython import get_ipython
import algorithm
from core import LibraryScanner

from .widget_builder import WidgetBuilder
from .code_generator import CodeGenerator


class AlgorithmWidget(widgets.VBox):
    """算法选择和执行Widget
    
    提供交互式界面用于：
    1. 浏览和选择算法
    2. 配置算法参数
    3. 生成和执行代码
    
    Args:
        metadata_path: 算法元数据路径（已废弃，保留用于兼容）
        init_algo: 初始化显示的算法ID，如果指定则隐藏类别和算法选择器
    """
    
    def __init__(self, metadata_path=None, init_algo=None):
        super().__init__()
        
        # Load metadata
        self.metadata = self.load_metadata(metadata_path)
        self.categories = list(self.metadata.keys())
        self.init_algo_id = init_algo
        
        # Initialize helpers
        self._init_style()
        self._init_widgets()
        self._init_builders()
        
        # Setup layout
        self._setup_layout()
        
        # Trigger initial loading
        self._trigger_initial_load()
    
    def _init_style(self):
        """初始化样式配置"""
        self.layout.border = '1px solid #ddd'
        self.layout.padding = '10px'
        self.layout.margin = '5px 0'
        self.common_style = {'description_width': '100px'}
        self.common_layout = widgets.Layout(width='98%')
    
    def _init_widgets(self):
        """初始化所有Widget组件"""
        # Dropdowns
        self.category_dropdown = widgets.Dropdown(
            options=self.categories,
            description='类别:',
            style=self.common_style,
            layout=self.common_layout
        )
        
        self.algorithm_dropdown = widgets.Dropdown(
            description='算法:',
            style=self.common_style,
            layout=self.common_layout
        )
        
        # Output areas
        self.description_output = widgets.Output()
        self.params_container = widgets.VBox()
        self.code_output = widgets.Output()
        
        # Buttons
        self.generate_btn = widgets.Button(
            description='查看代码',
            button_style='primary',
            icon='code'
        )
        self.run_btn = widgets.Button(
            description='执行',
            button_style='warning',
            icon='play'
        )
        
        # Event Listeners
        self.category_dropdown.observe(self.on_category_change, names='value')
        self.algorithm_dropdown.observe(self.on_algorithm_change, names='value')
        self.generate_btn.on_click(self.on_generate_click)
        self.run_btn.on_click(self.on_run_click)
    
    def _init_builders(self):
        """初始化构建器和生成器"""
        self.widget_builder = WidgetBuilder(
            common_style=self.common_style,
            common_layout=self.common_layout
        )
        self.code_generator = CodeGenerator()
    
    def _setup_layout(self):
        """设置Widget布局"""
        header_widgets = []
        if not self.init_algo_id:
            header_widgets.append(widgets.HBox([
                self.category_dropdown,
                self.algorithm_dropdown
            ]))
            header_widgets.append(widgets.HTML('<hr>'))

        self.children = header_widgets + [
            self.description_output,
            self.params_container,
            widgets.HTML('<hr>'),
            widgets.HBox([self.generate_btn, self.run_btn]),
            self.code_output
        ]
    
    def _trigger_initial_load(self):
        """触发初始加载"""
        if not self.categories:
            return
        
        # If init_algo is specified, try to find it
        found = False
        if self.init_algo_id:
            for cat, algos in self.metadata.items():
                # Check if target algo is in this category
                target_algo = next((a for a in algos if a['id'] == self.init_algo_id), None)
                
                if target_algo:
                    self.category_dropdown.value = cat
                    self.on_category_change({'new': cat})
                    self.algorithm_dropdown.value = target_algo
                    found = True
                    break
        
        if not found:
            self.on_category_change({'new': self.categories[0]})
    
    def load_metadata(self, metadata_path):
        """使用核心扫描器加载算法元数据
        
        Args:
            metadata_path: 元数据路径（已废弃，保留用于兼容）
            
        Returns:
            dict: 算法元数据字典，格式为 {category_label: [algo_dict, ...]}
        """
        scanner = LibraryScanner(algorithm)
        metadata_by_label = scanner.scan_with_labels()
        
        # 转换为Widget需要的格式（dict形式）
        result = {}
        for label, algos in metadata_by_label.items():
            result[label] = [algo.to_dict() for algo in algos]
        return result

    def on_category_change(self, change):
        """类别变更事件处理"""
        cat = change['new']
        if cat in self.metadata:
            algos = self.metadata[cat]
            options = [(a['name'], a) for a in algos]
            self.algorithm_dropdown.options = options
            if options:
                self.algorithm_dropdown.value = options[0][1]

    def on_algorithm_change(self, change):
        """算法变更事件处理"""
        algo = change['new']
        if not algo:
            return
            
        self._update_description(algo)
        self.build_params_widgets(algo)
        self.code_output.clear_output()
    
    def _update_description(self, algo):
        """更新算法描述显示"""
        with self.description_output:
            clear_output()
            if not self.init_algo_id:
                print(algo.get('description', ''))
            else:
                # In compact mode, show description as HTML
                display(widgets.HTML(
                    f"<b>{algo.get('name')}</b>: {algo.get('description', '')}"
                ))

    def build_params_widgets(self, algo):
        """构建参数输入Widget
        
        Args:
            algo: 算法元数据字典
        """
        widgets_list = []
        self.param_widgets_map = {}
        
        # 1. Input DataFrames (from inputs array or implicit args)
        inputs = algo.get('inputs', [])
        args = algo.get('args', [])
        
        # Combine inputs from 'inputs' field and 'args' with role='input'
        processed_inputs = set()
        
        for inp in inputs:
            name = inp.get('name')
            if name and name not in processed_inputs:
                w = self.widget_builder.create_dataframe_selector(
                    name, inp.get('label', name)
                )
                widgets_list.append(w)
                self.param_widgets_map[name] = w
                processed_inputs.add(name)
                
        for arg in args:
            name = arg.get('name')
            role = arg.get('role', '')
            
            if role == 'input' and name not in processed_inputs:
                w = self.widget_builder.create_dataframe_selector(
                    name, arg.get('label', name)
                )
                widgets_list.append(w)
                self.param_widgets_map[name] = w
                processed_inputs.add(name)
                continue
            
            if role == 'output':
                # 输出参数在后面统一处理
                continue
                
            if role == 'parameter':
                w = self.widget_builder.create_parameter_widget(arg)
                if w:
                    widgets_list.append(w)
                    self.param_widgets_map[name] = w
        
        # 2. 使用新的输出配置方法
        output_widgets, output_map = self.widget_builder.create_output_widgets(algo)
        if output_widgets:
            widgets_list.extend(output_widgets)
            self.param_widgets_map.update(output_map)
        
        self.params_container.children = widgets_list
    


    def generate_code(self):
        """生成算法调用代码
        
        Returns:
            str: 生成的Python代码
        """
        algo = self.algorithm_dropdown.value
        args_config = algo.get('args', [])
        return self.code_generator.generate_code(
            algo, self.param_widgets_map, args_config
        )

    def on_generate_click(self, b):
        """查看代码按钮点击事件"""
        code = self.generate_code()
        with self.code_output:
            clear_output()
            print(code)

    def on_run_click(self, b):
        """执行按钮点击事件"""
        code = self.generate_code()
        ip = get_ipython()
        if ip:
            with self.code_output:
                clear_output()
                print("Running...")
                result = ip.run_cell(code)
                if result.error_in_exec:
                    print("Error during execution.")
                else:
                    print("Execution complete.")
