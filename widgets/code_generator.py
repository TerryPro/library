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
        
        # Collect args
        call_args = []
        
        for name, widget in param_widgets_map.items():
            if name == '__output_var__':
                continue
            
            val = widget.value
            
            # Find arg config to check type
            arg_def = next((a for a in args_config if a['name'] == name), None)
            
            is_df = False
            # Check if it was created as dataframe selector
            if isinstance(widget, widgets.Dropdown) and 'df' in name.lower() and arg_def is None:
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
        
        # Generate imports: use unified algorithm import
        code = "from algorithm import *\n"
        code += f"# {algo.get('name')}\n\n"
        
        # Output assignment
        output_var = None
        if '__output_var__' in param_widgets_map:
            val = param_widgets_map['__output_var__'].value.strip()
            if val:
                output_var = val
        
        call_expr = f"{func_name}({', '.join(call_args)})"
        
        if output_var:
            code += f"{output_var} = {call_expr}\n"
            # Auto-display the output if it's assigned
            code += f"{output_var}"
        else:
            code += call_expr
            
        return code
    
    def _format_value(self, val, arg_def):
        """格式化参数值为代码字符串
        
        Args:
            val: 参数值
            arg_def: 参数定义
            
        Returns:
            str: 格式化后的参数值字符串
        """
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
