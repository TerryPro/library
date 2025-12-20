# -*- coding: utf-8 -*-
"""
Code Generator
==============
算法代码生成器
"""

import json
from typing import List, Dict, Any, Optional

from .models import AlgorithmMetadata, AlgorithmParameter, AlgorithmPort
from .extractor import CodeExtractor


class CodeGenerator:
    """
    算法代码生成器
    
    支持生成算法函数定义代码和函数调用代码
    """
    
    def __init__(self):
        self.extractor = CodeExtractor()
    
    def generate_function_code(
        self, 
        metadata: AlgorithmMetadata,
        existing_body: str = None,
        existing_code: str = None
    ) -> str:
        """
        根据元数据生成完整的算法函数代码
        
        Args:
            metadata: 算法元数据
            existing_body: 保留的现有函数体
            existing_code: 完整的原始代码(用于提取imports)
            
        Returns:
            完整的Python函数代码
        """
        # 处理imports - 如果有原始代码,先提取原有imports以保留它们
        if existing_code:
            existing_imports = self.extractor.extract_imports(existing_code)
            # 合并原有imports和metadata中的imports,去重
            all_imports = list(dict.fromkeys(existing_imports + list(metadata.imports)))
            # 更新metadata中的imports
            metadata.imports = all_imports
        
        imports = self._process_imports(metadata)
        imports_str = "\n".join(imports)
        
        # 构建函数签名
        sig_str = self._build_signature(metadata)
        
        # 返回类型注解
        ret_annotation = self._build_return_annotation(metadata.outputs)
        
        # 构建docstring
        docstring_str = self._build_docstring(metadata)
        
        # 函数体
        if existing_body:
            body_str = existing_body
        else:
            body_str = self._generate_default_body(metadata)
        
        # 组装代码
        code = f"""{imports_str}

def {metadata.id}({sig_str}) {ret_annotation}:
    \"\"\"
    {docstring_str}
    \"\"\"
{body_str}
"""
        return code
    
    def generate_call_code(
        self, 
        metadata: AlgorithmMetadata, 
        params: Dict[str, Any],
        output_var: str = None
    ) -> str:
        """
        生成函数调用代码（用于Notebook执行）
        
        Args:
            metadata: 算法元数据
            params: 参数值字典
            output_var: 输出变量名
            
        Returns:
            函数调用代码
        """
        # Imports
        imports = metadata.imports
        import_str = '\n'.join(imports) + '\n' if imports else ''
        
        # 函数模板
        code = f"{import_str}# {metadata.name}\n"
        code += f"{metadata.template}\n"
        
        # 构建调用参数
        call_args = self._build_call_args(metadata, params)
        
        # 函数调用
        call_expr = f"{metadata.id}({', '.join(call_args)})"
        
        if output_var:
            code += f"{output_var} = {call_expr}\n"
            code += f"{output_var}"
        else:
            code += call_expr
        
        return code
    
    def generate_template(self, algo_name: str, source: str) -> str:
        """
        生成简化的代码模板
        
        Args:
            algo_name: 算法名称
            source: 函数源码
            
        Returns:
            带注释的模板代码
        """
        return f"# {algo_name}\n{source}"
    
    def _process_imports(self, metadata: AlgorithmMetadata) -> List[str]:
        """处理并补全imports"""
        imports = list(metadata.imports)
        
        # 确保pandas导入
        has_pandas = any("pandas" in imp for imp in imports)
        if not has_pandas:
            imports = ["import pandas as pd"] + imports
        
        # 检查typing导入需求
        typing_types = set()
        if len(metadata.outputs) > 0:
            typing_types.add("Optional")
        if len(metadata.outputs) > 1:
            typing_types.add("Tuple")
        
        # 检查参数类型
        for param in metadata.parameters:
            if 'List' in param.type: typing_types.add('List')
            if 'Dict' in param.type: typing_types.add('Dict')
            if 'Tuple' in param.type: typing_types.add('Tuple')
            if 'Optional' in param.type: typing_types.add('Optional')
            if 'Any' in param.type: typing_types.add('Any')
        
        for t in sorted(list(typing_types)):
            already_imported = any(f"import {t}" in imp or f", {t}" in imp for imp in imports)
            if not already_imported:
                imports.append(f"from typing import {t}")
        
        return imports
    
    def _build_signature(self, metadata: AlgorithmMetadata) -> str:
        """构建函数签名参数字符串"""
        sig_args = []
        
        # 先添加inputs
        for inp in metadata.inputs:
            t = self._normalize_type(inp.type)
            sig_args.append(f"{inp.name}: {t}")
        
        # 分离必需和可选参数
        required_params = []
        optional_params = []
        
        for param in metadata.parameters:
            if param.default is not None and param.default != "":
                optional_params.append(param)
            else:
                required_params.append(param)
        
        # 必需参数先，可选参数后
        for param in required_params + optional_params:
            a_type = self._normalize_type(param.type)
            if param.default is not None and param.default != "":
                if isinstance(param.default, str):
                    sig_args.append(f"{param.name}: {a_type} = '{param.default}'")
                else:
                    sig_args.append(f"{param.name}: {a_type} = {param.default}")
            else:
                sig_args.append(f"{param.name}: {a_type}")
        
        return ", ".join(sig_args)
    
    def _build_return_annotation(self, outputs: List[AlgorithmPort]) -> str:
        """构建返回类型注解"""
        if not outputs:
            return "-> None"
        elif len(outputs) == 1:
            t = self._normalize_type(outputs[0].type)
            return f"-> Optional[{t}]"
        else:
            types = [f"Optional[{self._normalize_type(o.type)}]" for o in outputs]
            return f"-> Tuple[{', '.join(types)}]"
    
    def _build_docstring(self, metadata: AlgorithmMetadata) -> str:
        """构建docstring"""
        lines = []
        lines.append(metadata.description)
        lines.append('')
        lines.append('Algorithm:')
        lines.append(f'    name: {metadata.name}')
        lines.append(f'    category: {metadata.category}')
        if metadata.prompt:
            lines.append(f'    prompt: {metadata.prompt}')
        
        lines.append('')
        lines.append('Parameters:')
        
        # Inputs
        for inp in metadata.inputs:
            p_type = self._normalize_type(inp.type)
            lines.append(f'{inp.name} ({p_type}): {inp.description or "Input DataFrame"}')
            lines.append('    role: input')
        
        # Parameters
        for param in metadata.parameters:
            p_type = self._normalize_type(param.type)
            lines.append(f'{param.name} ({p_type}): {param.description}')
            
            if param.label: lines.append(f'    label: {param.label}')
            if param.widget: lines.append(f'    widget: {param.widget}')
            if param.options: lines.append(f'    options: {json.dumps(param.options)}')
            if param.min is not None: lines.append(f'    min: {param.min}')
            if param.max is not None: lines.append(f'    max: {param.max}')
            if param.step is not None: lines.append(f'    step: {param.step}')
            if param.priority: lines.append(f'    priority: {param.priority}')
            lines.append(f'    role: {param.role}')
        
        lines.append('')
        lines.append('Returns:')
        
        if not metadata.outputs:
            lines.append('None')
        else:
            for out in metadata.outputs:
                o_type = self._normalize_type(out.type)
                lines.append(f'{out.name} ({o_type}): {out.description or "Result"}')
        
        return "\n    ".join(lines)
    
    def _generate_default_body(self, metadata: AlgorithmMetadata) -> str:
        """生成默认函数体"""
        if not metadata.outputs:
            return "    # Implementation\n    pass"
        elif len(metadata.outputs) == 1:
            if metadata.inputs:
                return f"    # Implementation\n    return {metadata.inputs[0].name}"
            else:
                return "    # Implementation\n    return pd.DataFrame()"
        else:
            return "    # Implementation\n    return " + ", ".join(["pd.DataFrame()" for _ in metadata.outputs])
    
    def _build_call_args(self, metadata: AlgorithmMetadata, params: Dict[str, Any]) -> List[str]:
        """构建函数调用参数列表"""
        call_args = []
        
        # 获取所有参数定义
        all_params = {p.name: p for p in metadata.parameters}
        for inp in metadata.inputs:
            all_params[inp.name] = AlgorithmParameter(
                name=inp.name, 
                type=inp.type, 
                role='input'
            )
        
        for name, val in params.items():
            param_def = all_params.get(name)
            is_df = param_def and param_def.role == 'input'
            
            if is_df:
                # DataFrame变量名直接使用
                call_args.append(f"{name}={val}")
            else:
                # 格式化值
                v_str = self._format_value(val, param_def)
                call_args.append(f"{name}={v_str}")
        
        return call_args
    
    def _format_value(self, val: Any, param_def: AlgorithmParameter = None) -> str:
        """格式化参数值为代码字符串"""
        if isinstance(val, bool):
            return "True" if val else "False"
        elif isinstance(val, (int, float)):
            return str(val)
        else:
            val_str = str(val).strip()
            
            # 检查是否是列表/字典/元组字面量
            if (val_str.startswith('[') and val_str.endswith(']')) or \
               (val_str.startswith('{') and val_str.endswith('}')) or \
               (val_str.startswith('(') and val_str.endswith(')')):
                return val_str
            
            # 检查None
            if val_str == "None":
                return "None"
            
            # 处理文件路径
            if param_def and param_def.widget == 'file-selector':
                val_str = val_str.replace('\\', '\\\\')
            
            return f"'{val_str}'"
    
    def _normalize_type(self, t: str) -> str:
        """标准化类型名称"""
        if t == 'DataFrame':
            return 'pd.DataFrame'
        return t


# 全局生成器实例
_generator = CodeGenerator()


def generate_function_code(metadata: AlgorithmMetadata, existing_body: str = None, existing_code: str = None) -> str:
    """生成函数代码（便捷函数）"""
    return _generator.generate_function_code(metadata, existing_body, existing_code)


def generate_call_code(
    metadata: AlgorithmMetadata, 
    params: Dict[str, Any],
    output_var: str = None
) -> str:
    """生成调用代码（便捷函数）"""
    return _generator.generate_call_code(metadata, params, output_var)


def generate_template(algo_name: str, source: str) -> str:
    """生成模板（便捷函数）"""
    return _generator.generate_template(algo_name, source)
