# -*- coding: utf-8 -*-
"""
Code Extractor
==============
从Python代码中提取Import语句和函数参数信息
"""

import ast
import inspect
from typing import List, Dict, Any, Optional, Callable

from .models import AlgorithmParameter, AlgorithmPort
from .parser import DocstringParser


class CodeExtractor:
    """
    代码信息提取器
    
    提供从Python源码和函数对象中提取信息的能力
    """
    
    def __init__(self):
        self.parser = DocstringParser()
    
    def extract_imports(self, source: str) -> List[str]:
        """
        从源码字符串中提取import语句
        
        Args:
            source: Python源码字符串
            
        Returns:
            import语句列表
        """
        try:
            imports = []
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if name.asname:
                            imports.append(f"import {name.name} as {name.asname}")
                        else:
                            imports.append(f"import {name.name}")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        if name.asname:
                            imports.append(f"from {module} import {name.name} as {name.asname}")
                        else:
                            imports.append(f"from {module} import {name.name}")
            return imports
        except Exception:
            return []
    
    def extract_imports_from_module(self, module) -> List[str]:
        """
        从模块对象中提取import语句
        
        Args:
            module: Python模块对象
            
        Returns:
            import语句列表
        """
        if module is None:
            return []
        
        try:
            module_file = inspect.getsourcefile(module)
            if module_file:
                with open(module_file, 'r', encoding='utf-8') as f:
                    module_source = f.read()
                return self.extract_imports(module_source)
        except Exception:
            pass
        
        return []
    
    def extract_imports_from_func(self, func: Callable) -> List[str]:
        """
        从函数所在模块中提取import语句
        
        Args:
            func: 函数对象
            
        Returns:
            import语句列表
        """
        try:
            module = inspect.getmodule(func)
            if module:
                return self.extract_imports_from_module(module)
            
            # 回退：从函数源码提取
            source = inspect.getsource(func)
            return self.extract_imports(source)
        except Exception:
            return []
    
    def extract_parameters(
        self, 
        func: Callable, 
        docstring_params: Dict[str, Dict[str, Any]] = None,
        overrides: Dict[str, Dict[str, Any]] = None
    ) -> List[AlgorithmParameter]:
        """
        从函数签名和docstring中提取参数定义
        
        Args:
            func: 函数对象
            docstring_params: 从docstring解析出的参数元数据
            overrides: 参数覆盖配置
            
        Returns:
            AlgorithmParameter列表
        """
        if docstring_params is None:
            docstring_params = {}
        if overrides is None:
            overrides = {}
        
        sig = inspect.signature(func)
        parameters = []
        
        for name, param in sig.parameters.items():
            param_info = docstring_params.get(name, {})
            override = overrides.get(name, {})
            
            # 检查是否忽略
            if param_info.get("ignore"):
                continue
            
            # 确定类型
            param_type = self._infer_type(param, param_info)
            
            # 确定默认值
            default_val = self._get_default_value(param, param_type)
            
            # 确定角色
            role = self._infer_role(name, param_type, param_info)
            
            # 确定优先级
            priority = param_info.get("priority")
            if not priority:
                priority = "critical" if default_val is None else "non-critical"
            
            # 确定widget类型
            options = override.get("options", param_info.get("options"))
            widget = override.get("widget", 
                     param_info.get("widget", 
                     self.infer_widget_type(name, param_type, options)))
            
            # 构建参数
            algo_param = AlgorithmParameter(
                name=name,
                type=override.get("type", param_type),
                default=override.get("default", param_info.get("default", default_val)),
                label=override.get("label", param_info.get("label", name.replace("_", " ").title())),
                description=override.get("description", param_info.get("description", f"Parameter {name}")),
                widget=widget,
                options=options,
                min=override.get("min", param_info.get("min")),
                max=override.get("max", param_info.get("max")),
                step=override.get("step", param_info.get("step")),
                priority=override.get("priority", priority),
                role=override.get("role", role)
            )
            
            parameters.append(algo_param)
        
        return parameters
    
    def _infer_type(self, param, param_info: Dict[str, Any]) -> str:
        """从签名和docstring推断参数类型"""
        # 优先使用docstring中的类型
        doc_type = param_info.get("type", "")
        if doc_type:
            doc_type_lower = doc_type.lower()
            if "list" in doc_type_lower:
                return "list"
            elif "int" in doc_type_lower:
                return "int"
            elif "float" in doc_type_lower:
                return "float"
            elif "bool" in doc_type_lower:
                return "bool"
            elif "dataframe" in doc_type_lower:
                return "DataFrame"
        
        # 从签名注解推断
        if param.annotation != inspect.Parameter.empty:
            if param.annotation == int:
                return "int"
            elif param.annotation == float:
                return "float"
            elif param.annotation == bool:
                return "bool"
            elif param.annotation == list:
                return "list"
            elif param.annotation == tuple:
                return "tuple"
            elif hasattr(param.annotation, '__name__'):
                return param.annotation.__name__
        
        # 从默认值推断
        if param.default != inspect.Parameter.empty and param.default is not None:
            if isinstance(param.default, int) and not isinstance(param.default, bool):
                return "int"
            elif isinstance(param.default, float):
                return "float"
            elif isinstance(param.default, bool):
                return "bool"
            elif isinstance(param.default, list):
                return "list"
        
        return "str"
    
    def _get_default_value(self, param, param_type: str) -> Any:
        """获取参数默认值"""
        if param.default != inspect.Parameter.empty:
            return param.default
        
        # 对于没有默认值的参数，返回类型对应的空值
        type_defaults = {
            "int": 0,
            "float": 0.0,
            "bool": False,
            "list": [],
            "str": ""
        }
        return type_defaults.get(param_type, None)
    
    def _infer_role(self, name: str, param_type: str, param_info: Dict[str, Any]) -> str:
        """推断参数角色"""
        # 优先使用docstring中的角色
        doc_role = param_info.get("role")
        if doc_role:
            return doc_role
        
        # 根据名称和类型推断
        if name == 'df' or 'dataframe' in param_type.lower():
            return 'input'
        elif name == 'output_var':
            return 'output'
        else:
            return 'parameter'
    
    def infer_widget_type(self, name: str, param_type: str, options: List[Any] = None) -> str:
        """
        根据参数名称和类型推断widget类型
        
        Args:
            name: 参数名称
            param_type: 参数类型
            options: 可选值列表
            
        Returns:
            widget类型字符串
        """
        if options:
            return "select"
        
        name_lower = name.lower()
        
        if "filepath" in name_lower or "file_path" in name_lower:
            return "file-selector"
        if "columns" in name_lower or "column" in name_lower:
            return "column-selector"
        if "color" in name_lower:
            return "color-picker"
        
        if param_type == "bool":
            return "checkbox"
        if param_type in ("int", "float"):
            return "input-number"
        
        return "input-text"
    
    def extract_outputs_from_signature(self, func: Callable) -> List[AlgorithmPort]:
        """
        从函数签名的返回类型注解推断输出端口
        
        Args:
            func: 函数对象
            
        Returns:
            AlgorithmPort列表
        """
        import typing
        
        outputs = []
        sig = inspect.signature(func)
        
        if sig.return_annotation is inspect.Signature.empty:
            return outputs
        
        ret_type = sig.return_annotation
        
        def is_dataframe_type(t) -> bool:
            if isinstance(t, str):
                return "DataFrame" in t
            elif hasattr(t, "__name__") and "DataFrame" in t.__name__:
                return True
            elif "DataFrame" in str(t):
                return True
            return False
        
        origin = typing.get_origin(ret_type)
        if origin is tuple or origin is typing.Tuple:
            args = typing.get_args(ret_type)
            for i, arg in enumerate(args):
                if is_dataframe_type(arg):
                    outputs.append(AlgorithmPort(
                        name=f"df_out_{i+1}",
                        type="DataFrame"
                    ))
        else:
            if is_dataframe_type(ret_type):
                outputs.append(AlgorithmPort(
                    name="df_out",
                    type="DataFrame"
                ))
        
        return outputs
    
    def extract_function_body(self, source: str) -> Optional[str]:
        """
        从源码中提取函数体（不含docstring）
        
        Args:
            source: 包含函数定义的源码
            
        Returns:
            函数体代码字符串
        """
        try:
            tree = ast.parse(source)
            func_node = None
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    func_node = node
                    break
            
            if not func_node:
                return None
            
            # 检查是否有docstring
            has_docstring = (
                func_node.body and 
                isinstance(func_node.body[0], ast.Expr) and
                isinstance(func_node.body[0].value, (ast.Str, ast.Constant))
            )
            
            if has_docstring:
                # 获取docstring结束行
                last_doc_line = func_node.body[0].end_lineno
                lines = source.splitlines()
                body_lines = lines[last_doc_line:]
                return "\n".join(body_lines)
            else:
                # 无docstring，从第一个语句开始
                first_stmt = func_node.body[0]
                start_line = first_stmt.lineno - 1
                lines = source.splitlines()
                body_lines = lines[start_line:]
                return "\n".join(body_lines)
        except Exception:
            return None


# 便捷函数（保持兼容性）
_extractor = CodeExtractor()

def extract_imports_from_source(source: str) -> List[str]:
    """提取import语句（兼容函数）"""
    return _extractor.extract_imports(source)

def extract_imports_from_func(func: Callable) -> List[str]:
    """从函数模块提取import（兼容函数）"""
    return _extractor.extract_imports_from_func(func)

def extract_parameters_from_func(
    func: Callable, 
    overrides: Dict[str, Dict[str, Any]] = None
) -> List[AlgorithmParameter]:
    """提取函数参数（兼容函数）"""
    parser = DocstringParser()
    doc_params = parser.parse_parameters_section(inspect.getdoc(func) or "")
    return _extractor.extract_parameters(func, doc_params, overrides)

def infer_widget_type(name: str, param_type: str, options: List[Any] = None) -> str:
    """推断widget类型（兼容函数）"""
    return _extractor.infer_widget_type(name, param_type, options)
