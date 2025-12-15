# -*- coding: utf-8 -*-
"""
Widget Builder
==============
负责根据算法元数据构建参数输入Widget
"""

import ipywidgets as widgets
from .data_provider import DataProvider


class WidgetBuilder:
    """Widget构建器，负责根据参数配置创建对应的ipywidgets控件"""
    
    def __init__(self, common_style=None, common_layout=None):
        """初始化Widget构建器
        
        Args:
            common_style: 通用样式配置
            common_layout: 通用布局配置
        """
        self.common_style = common_style or {'description_width': '100px'}
        self.common_layout = common_layout or widgets.Layout(width='98%')
        self.data_provider = DataProvider()
    
    def create_output_widgets(self, algo):
        """创建输出参数配置Widget
        
        Args:
            algo: 算法元数据字典
            
        Returns:
            tuple: (widgets_list, output_widgets_map)
                - widgets_list: 输出相关的Widget列表
                - output_widgets_map: 输出名称到Widget的映射
        """
        widgets_list = []
        output_widgets_map = {}
        
        # 检查算法是否有输出
        outputs = algo.get('outputs', [])
        ret_config = algo.get('returns', {})
        ret_type = ret_config.get('return', '').strip() if ret_config else ''
        
        # 优先使用 outputs 字段（多输出支持）
        if outputs:
            widgets_list.append(widgets.HTML("<b>输出配置:</b>"))
            for output in outputs:
                output_name = output.get('name', 'output')
                output_type = output.get('type', 'DataFrame')
                output_desc = output.get('description', '')
                
                # 默认输出变量名
                default_var = f"{output_name}"
                
                # 创建输出变量名输入框
                w = widgets.Text(
                    value=default_var,
                    description=f'{output_name}:',
                    placeholder=f'输出变量名 ({output_type})',
                    style=self.common_style,
                    layout=self.common_layout
                )
                widgets_list.append(w)
                output_widgets_map[output_name] = w
                
                # 如果有描述，添加提示信息
                if output_desc:
                    widgets_list.append(widgets.HTML(
                        f"<div style='margin-left: 20px; color: #666; font-size: 0.9em;'>{output_desc}</div>"
                    ))
        
        # 如果没有 outputs 但有 return 类型，使用传统单输出模式
        elif ret_type and ret_type.lower() != 'none':
            widgets_list.append(widgets.HTML("<b>输出配置:</b>"))
            default_out = f"res_{algo['id']}"
            
            w = widgets.Text(
                value=default_out,
                description='输出变量名:',
                placeholder='输入变量名以接收结果',
                style=self.common_style,
                layout=self.common_layout
            )
            widgets_list.append(w)
            output_widgets_map['__single_output__'] = w
        
        return widgets_list, output_widgets_map
    
    def create_dataframe_selector(self, name, label):
        """创建DataFrame选择器
        
        Args:
            name: 参数名称
            label: 显示标签
            
        Returns:
            widgets.Dropdown: DataFrame下拉选择框
        """
        dfs = self.data_provider.get_dataframe_variables()
        if not dfs:
            dfs = ['df']  # Default fallback
            
        return widgets.Dropdown(
            options=dfs,
            description=f'{label} ({name}):',
            style=self.common_style,
            layout=self.common_layout
        )
    
    def create_parameter_widget(self, arg):
        """根据参数配置创建对应的Widget
        
        Args:
            arg: 参数配置字典，包含name, label, widget, type, default, options等字段
            
        Returns:
            ipywidgets.Widget: 对应的Widget实例
        """
        name = arg.get('name')
        label = arg.get('label', name)
        w_type = arg.get('widget', '')
        p_type = arg.get('type', 'str')
        default = arg.get('default')
        options = arg.get('options')
        
        widget = None
        
        # Special handling for file-selector: load CSV files from dataset directory
        if w_type == 'file-selector':
            widget = self._create_file_selector_widget(label, default)
        elif options:
            widget = self._create_dropdown_widget(label, default, options)
        elif p_type == 'bool' or w_type == 'checkbox':
            widget = self._create_checkbox_widget(label, default)
        elif p_type == 'int':
            widget = self._create_int_widget(label, default)
        elif p_type == 'float':
            widget = self._create_float_widget(label, default)
        else:  # str or default
            widget = self._create_text_widget(label, default)
            
        return widget
    
    def _create_file_selector_widget(self, label, default):
        """创建文件选择器Widget"""
        csv_files = self.data_provider.get_dataset_csv_files()
        if csv_files:
            # csv_files is list of tuples: [(filename, absolute_path), ...]
            # Dropdown will display filename but use absolute_path as value
            
            # Find default value - check if default matches any absolute path
            default_value = csv_files[0][1] if csv_files else None
            if default:
                # Check if default matches any absolute path or filename
                for filename, abs_path in csv_files:
                    if default == abs_path or default == filename or default.endswith(filename):
                        default_value = abs_path
                        break
            
            return widgets.Dropdown(
                options=csv_files,
                value=default_value,
                description=label,
                style=self.common_style,
                layout=self.common_layout
            )
        else:
            # Fallback to text input if no files found
            return widgets.Text(
                value=str(default) if default is not None else '',
                description=label,
                style=self.common_style,
                layout=self.common_layout
            )
    
    def _create_dropdown_widget(self, label, default, options):
        """创建下拉选择Widget"""
        return widgets.Dropdown(
            options=options,
            value=default if default in options else options[0],
            description=label,
            style=self.common_style,
            layout=self.common_layout
        )
    
    def _create_checkbox_widget(self, label, default):
        """创建复选框Widget"""
        return widgets.Checkbox(
            value=bool(default),
            description=label,
            style=self.common_style,
            layout=self.common_layout
        )
    
    def _create_int_widget(self, label, default):
        """创建整数输入Widget"""
        return widgets.IntText(
            value=int(default) if default is not None else 0,
            description=label,
            style=self.common_style,
            layout=self.common_layout
        )
    
    def _create_float_widget(self, label, default):
        """创建浮点数输入Widget"""
        return widgets.FloatText(
            value=float(default) if default is not None else 0.0,
            description=label,
            style=self.common_style,
            layout=self.common_layout
        )
    
    def _create_text_widget(self, label, default):
        """创建文本输入Widget"""
        return widgets.Text(
            value=str(default) if default is not None else '',
            description=label,
            style=self.common_style,
            layout=self.common_layout
        )
