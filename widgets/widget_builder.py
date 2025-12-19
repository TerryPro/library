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
        """创建 DataFrame 选择器
            
        Args:
            name: 参数名称
            label: 显示标签
                
        Returns:
            widgets.Dropdown: DataFrame 下拉选择框
        """
        dfs = self.data_provider.get_dataframe_variables()
            
        # 如果没有可用的 DataFrame，创建一个空的下拉框并禁用
        if not dfs:
            dropdown = widgets.Dropdown(
                options=[('-- 无可用 DataFrame --', None)],
                value=None,
                description=f'{label} ({name}):',
                style=self.common_style,
                layout=self.common_layout,
                disabled=True  # 禁用控件
            )
            return dropdown
            
        # 有可用 DataFrame 时，选择第一个作为默认值
        return widgets.Dropdown(
            options=dfs,
            value=dfs[0] if dfs else None,
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
        
        # 列选择器：根据 type 判断单选或多选
        if w_type == 'column-selector':
            if p_type == 'list':
                # 多选列选择器
                widget = self._create_multi_column_selector(label, default)
            else:
                # 单选列选择器 (type: str)
                widget = self._create_column_selector(label, default)
        # Special handling for file-selector: load CSV files from dataset directory
        elif w_type == 'file-selector':
            widget = self._create_file_selector_widget(label, default)
        elif w_type == 'select' or options:
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
    
    def _create_column_selector(self, label, default):
        """创建列名选择器（单选）
        
        从当前环境中的 DataFrame 获取列名列表，生成下拉选择框。
        如果找不到 DataFrame，则退化为普通文本输入框。
        
        Args:
            label: 显示标签
            default: 默认值
            
        Returns:
            widgets.Dropdown 或 widgets.Text
        """
        # 获取所有可用的 DataFrame 列名
        columns = self.data_provider.get_all_dataframe_columns()
        
        if columns:
            # 如果有列名，创建下拉选择框
            # 添加 "-- 不选择 --" 选项，值为 None
            options = [('-- 不选择 --', None)] + [(col, col) for col in columns]
            
            # 设置默认值
            if default and default in columns:
                default_value = default
            elif default is None:
                default_value = None
            else:
                # 默认选择第一个列
                default_value = columns[0] if columns else None
            
            return widgets.Dropdown(
                options=options,
                value=default_value,
                description=label,
                style=self.common_style,
                layout=self.common_layout
            )
        else:
            # 退化为文本输入框
            return widgets.Text(
                value=str(default) if default is not None else '',
                description=label,
                placeholder='请输入列名',
                style=self.common_style,
                layout=self.common_layout
            )
    
    def _create_multi_column_selector(self, label, default):
        """创建多选列选择器
        
        使用自定义组合控件：
        - Text 显示已选择的列 ['col1', 'col2']
        - Button 按钮点击切换显示/隐藏多选列表
        - VBox 包含多个 Checkbox 用于多选
        
        Args:
            label: 显示标签
            default: 默认值（列表）
            
        Returns:
            widgets.VBox: 包含所有子控件的垂直布局
        """
        # 获取所有可用的 DataFrame 列名
        columns = self.data_provider.get_all_dataframe_columns()
        
        if columns:
            # 处理默认值：确保是列表且在可用列中
            default_value = []
            if default:
                if isinstance(default, list):
                    default_value = [col for col in default if col in columns]
                elif isinstance(default, str) and default in columns:
                    default_value = [default]
            
            # Text 控件显示已选择的列
            text_widget = widgets.Text(
                value=str(default_value),
                description=label,
                placeholder='[]',
                disabled=True,
                style=self.common_style,
                layout=widgets.Layout(
                    width='auto',  # 自适应宽度
                    flex='1'  # 占据剩余空间
                )
            )
            
            # 下拉按钮（固定宽度，与上方 Dropdown 宽度一致）
            dropdown_button = widgets.Button(
                description='▼',  # 下箭头符号
                button_style='',
                tooltip='点击选择列',
                layout=widgets.Layout(
                    width='60px',  # 固定宽度，与 Dropdown 的下拉箭头宽度类似
                    height='28px'
                )
            )
            
            # 创建复选框列表（初始隐藏）
            checkboxes = []
            for col in columns:
                cb = widgets.Checkbox(
                    value=(col in default_value),
                    description=col,
                    indent=False,
                    layout=widgets.Layout(width='80%', height='25px')
                )
                checkboxes.append(cb)
            
            # 复选框容器（可滚动）
            # 宽度与第一行一致，从 Text 左边到 Button 右边
            # 需要添加左边距，与 Text 输入框对齐（跳过 description 标签宽度）
            # description_width(100px) + 间隙(~10px) = 约 110px
            checkbox_container = widgets.VBox(
                checkboxes,
                layout=widgets.Layout(
                    width='calc(100% - 110px)',  # 减去 description 标签宽度 + 间隙
                    max_height='150px',
                    overflow_y='auto',
                    border='1px solid #ccc',
                    padding='5px',
                    margin='0 0 0 110px',  # 左边距，与 Text 输入框左对齐
                    display='none'  # 初始隐藏
                )
            )
            
            # 按钮点击事件：切换显示/隐藏
            def toggle_dropdown(b):
                if checkbox_container.layout.display == 'none':
                    checkbox_container.layout.display = 'block'
                    dropdown_button.description = '▲'  # 上箭头
                else:
                    checkbox_container.layout.display = 'none'
                    dropdown_button.description = '▼'  # 下箭头
            
            dropdown_button.on_click(toggle_dropdown)
            
            # 复选框变化事件：更新 Text 显示
            def on_checkbox_change(change):
                selected = [cb.description for cb in checkboxes if cb.value]
                text_widget.value = str(selected)
            
            for cb in checkboxes:
                cb.observe(on_checkbox_change, names='value')
            
            # 第一行：Text + Button（使用 flex 布局）
            first_row = widgets.HBox(
                [text_widget, dropdown_button],
                layout=widgets.Layout(
                    width='98%',
                    justify_content='space-between'  # 两端对齐
                )
            )
            
            # 整体容器：第一行 + 复选框列表
            container = widgets.VBox(
                [first_row, checkbox_container],
                layout=widgets.Layout(width='98%')
            )
            
            # 存储 checkboxes 列表，便于代码生成时读取
            container._checkboxes = checkboxes
            
            return container
        else:
            # 退化为文本输入框（逗号分隔）
            default_str = ','.join(default) if isinstance(default, list) else str(default) if default else ''
            return widgets.Text(
                value=default_str,
                description=label,
                placeholder='请输入列名，用逗号分隔',
                style=self.common_style,
                layout=self.common_layout
            )
    
    def _create_dropdown_widget(self, label, default, options):
        """创建下拉选择Widget
        
        用于 select 控件，不添加 "-- 不选择 --" 选项，
        用户必须选择一个有效值。
        """
        # 设置默认值
        if default is not None and default in options:
            default_value = default
        else:
            # 选择第一个选项作为默认值
            default_value = options[0] if options else None
        
        return widgets.Dropdown(
            options=options,
            value=default_value,
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
