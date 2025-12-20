# -*- coding: utf-8 -*-
"""
Code Generator
==============
负责生成算法调用代码
"""

import ipywidgets as widgets


class CodeGenerator:
    """代码生成器，负责根据算法元数据和参数值生成可执行代码"""
    
    def generate_code(self, algo, param_widgets_map, args_config):
        """生成算法调用代码
        
        Args:
            algo: 算法元数据字典
            param_widgets_map: 参数名到Widget的映射
            args_config: 参数配置列表
            
        Returns:
            str: 生成的Python代码
        """
        func_name = algo.get('id')
        
        # 收集输入参数
        call_args = []
        
        for name, widget in param_widgets_map.items():
            # 跳过输出参数
            if name.startswith('__') or name in [o.get('name') for o in algo.get('outputs', [])]:
                continue
            
            # 处理网格布局包装的控件（HBox）
            actual_widget = widget
            if isinstance(widget, widgets.HBox) and len(widget.children) == 2:
                # 网格布局的 HBox，第二个子元素是实际控件
                actual_widget = widget.children[1]
            
            # 处理自定义多选控件（VBox 包含 checkboxes）
            if isinstance(actual_widget, widgets.VBox) and hasattr(actual_widget, '_checkboxes'):
                # 从 checkboxes 中读取选中的列
                selected = [cb.description for cb in actual_widget._checkboxes if cb.value]
                val = tuple(selected) if selected else ()  # 转为元组
            else:
                val = actual_widget.value
            
            # Find arg config to check type
            arg_def = next((a for a in args_config if a['name'] == name), None)

            # 如果值为 None 或空元组，跳过该参数（不传递）
            if val is None or (isinstance(val, (tuple, list)) and len(val) == 0):
                # 对于 column-selector，如果是 None 或空，显式传递 None
                if arg_def and arg_def.get('widget') == 'column-selector':
                    call_args.append(f"{name}=None")
                continue
            
            is_df = False
            # Check if it was created as dataframe selector
            if isinstance(actual_widget, widgets.Dropdown) and 'df' in name.lower() and arg_def is None:
                # Heuristic for inputs from 'inputs' array which don't have arg def
                is_df = True
            elif arg_def and arg_def.get('role') == 'input':
                is_df = True
                
            if is_df:
                call_args.append(f"{name}={val}")
            else:
                # Value formatting directly from widget value
                v_str = self._format_value(val, arg_def)
                call_args.append(f"{name}={v_str}")
        
        # 生成导入语句：使用统一的 algorithm 导入
        code = "from algorithm import *\n"
        code += f"# {algo.get('name')}\n\n"
        
        # 处理输出
        output_vars = self._collect_output_vars(algo, param_widgets_map)
        call_expr = f"{func_name}({', '.join(call_args)})"
        
        if output_vars:
            if len(output_vars) == 1:
                # 单个输出
                code += f"{output_vars[0]} = {call_expr}\n"
                # 自动显示输出
                code += f"{output_vars[0]}"
            else:
                # 多个输出（元组解包）
                code += f"{', '.join(output_vars)} = {call_expr}\n"
                # 显示第一个输出
                code += f"{output_vars[0]}"
        else:
            # 无输出变量，直接调用
            code += call_expr
            
        return code
    
    def _collect_output_vars(self, algo, param_widgets_map):
        """收集输出变量名
        
        Args:
            algo: 算法元数据字典
            param_widgets_map: 参数名到Widget的映射
            
        Returns:
            list: 输出变量名列表，按 outputs 顺序
        """
        output_vars = []
        outputs = algo.get('outputs', [])
        
        if outputs:
            # 多输出模式：从 outputs 字段收集
            for output in outputs:
                output_name = output.get('name')
                if output_name in param_widgets_map:
                    widget = param_widgets_map[output_name]
                    var_name = widget.value.strip()
                    if var_name:
                        output_vars.append(var_name)
        elif '__single_output__' in param_widgets_map:
            # 单输出模式（兼容旧版）
            val = param_widgets_map['__single_output__'].value.strip()
            if val:
                output_vars.append(val)
        
        return output_vars
    
    def _format_value(self, val, arg_def):
        """格式化参数值为代码字符串
        
        Args:
            val: 参数值
            arg_def: 参数定义
            
        Returns:
            str: 格式化后的参数值字符串
        """
        # 处理 SelectMultiple 控件返回的元组/列表
        if isinstance(val, (tuple, list)):
            # 将元组/列表转换为 Python 列表字面量
            formatted_items = [f"'{item}'" if isinstance(item, str) else str(item) for item in val]
            return f"[{', '.join(formatted_items)}]"
        
        if isinstance(val, bool):
            return "True" if val else "False"
        elif isinstance(val, (int, float)):
            return str(val)
        else:
            # String
            val_str = str(val).strip()
            
            # Check if it looks like a list/dict literal
            if (val_str.startswith('[') and val_str.endswith(']')) or \
               (val_str.startswith('{') and val_str.endswith('}')) or \
               (val_str.startswith('(') and val_str.endswith(')')):
                return val_str
            
            # Check for "None"
            if val_str == "None":
                return "None"
            
            # For file paths on Windows, escape backslashes
            if arg_def and arg_def.get('widget') == 'file-selector':
                # Windows paths need double backslashes in Python strings
                val_str = val_str.replace('\\', '\\\\')
            
            return f"'{val_str}'"
