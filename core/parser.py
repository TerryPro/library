# -*- coding: utf-8 -*-
"""
Docstring Parser
================
统一的Docstring解析器，支持算法元数据格式
"""

import re
import json
from typing import Dict, Any, List, Optional


class DocstringParser:
    """
    Docstring解析器
    
    支持解析以下格式：
    - Algorithm: 块 - 算法元数据
    - Parameters: 块 - 参数定义
    - Returns: 块 - 返回值定义
    """
    
    def parse(self, docstring: str) -> Dict[str, Any]:
        """
        解析完整的docstring，返回所有元数据
        
        Args:
            docstring: 完整的docstring字符串
            
        Returns:
            包含 algorithm, parameters, returns, description 的字典
        """
        if not docstring:
            return {}
        
        return {
            "description": self.parse_description(docstring),
            "algorithm": self.parse_algorithm_section(docstring),
            "parameters": self.parse_parameters_section(docstring),
            "returns": self.parse_returns_section(docstring)
        }
    
    def parse_description(self, docstring: str) -> str:
        """
        解析描述部分（Algorithm:之前的内容）
        
        Args:
            docstring: docstring字符串
            
        Returns:
            描述文本
        """
        if not docstring:
            return ""
        
        desc_lines = []
        for line in docstring.split('\n'):
            stripped = line.strip()
            if stripped.startswith('Algorithm:') or \
               stripped.startswith('Parameters:') or \
               stripped.startswith('Returns:') or \
               stripped.startswith('Example:'):
                break
            if stripped:
                desc_lines.append(stripped)
        
        return "\n".join(desc_lines).strip()
    
    def parse_algorithm_section(self, docstring: str) -> Dict[str, Any]:
        """
        解析 Algorithm: 块
        
        支持格式:
            Algorithm:
                name: 算法名称
                category: 分类ID
                prompt: 提示词模板
                imports: import pandas as pd, import numpy as np
        
        Args:
            docstring: docstring字符串
            
        Returns:
            算法元数据字典，包含 name, category, prompt, imports 等
        """
        if not docstring:
            return {}
        
        metadata = {}
        lines = docstring.split('\n')
        in_algo_section = False
        
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            
            if stripped_line.startswith('Algorithm:'):
                in_algo_section = True
                continue
            
            if in_algo_section:
                # 遇到其他段落时停止
                if stripped_line.startswith('Parameters:') or \
                   stripped_line.startswith('Returns:') or \
                   stripped_line.startswith('Example:'):
                    break
                
                # 解析 key: value 格式
                match = re.match(r'^(\w+)\s*:\s*(.+)$', stripped_line)
                if match:
                    key = match.group(1)
                    value = match.group(2)
                    
                    if key == 'imports':
                        # imports 是逗号分隔的列表
                        metadata[key] = [imp.strip() for imp in value.split(',') if imp.strip()]
                    else:
                        metadata[key] = value
        
        return metadata
    
    def parse_parameters_section(self, docstring: str) -> Dict[str, Dict[str, Any]]:
        """
        解析 Parameters: 块
        
        支持格式:
            Parameters:
            param_name (type): Description
                label: Label Name
                widget: widget-type
                priority: critical
                options: [a, b, c]
                min: 0
                max: 100
                step: 1
                ignore: true
                role: parameter
                default: value
        
        Args:
            docstring: docstring字符串
            
        Returns:
            参数字典，key是参数名，value是参数元数据
        """
        if not docstring:
            return {}
        
        params = {}
        lines = docstring.split('\n')
        in_params_section = False
        current_param = None
        param_indent = None
        
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            
            # 计算缩进
            indent = len(line) - len(line.lstrip())
            
            if stripped_line.startswith('Parameters:'):
                in_params_section = True
                continue
            if stripped_line.startswith('Returns:') or \
               stripped_line.startswith('Example:') or \
               stripped_line.startswith('Algorithm:'):
                in_params_section = False
                break
            
            if in_params_section:
                # 检查是否是参数定义行: name (type): description
                match = re.match(r'^(\w+)\s*(?:\((.+?)\))?\s*:\s*(.+)$', stripped_line)
                
                is_param_def = False
                if match:
                    if param_indent is None:
                        is_param_def = True
                    elif indent > param_indent:
                        is_param_def = False
                    else:
                        is_param_def = True
                
                if is_param_def:
                    if param_indent is None:
                        param_indent = indent
                    
                    current_param = match.group(1)
                    param_type_str = match.group(2)
                    desc = match.group(3)
                    params[current_param] = {"description": desc}
                    if param_type_str:
                        params[current_param]["type"] = param_type_str
                
                elif current_param:
                    # 解析参数的元数据
                    meta_match = re.match(
                        r'^(label|widget|priority|options|min|max|step|ignore|role|default)\s*:\s*(.+)$',
                        stripped_line
                    )
                    if meta_match:
                        key = meta_match.group(1)
                        value = meta_match.group(2)
                        
                        # 类型转换
                        value = self._convert_param_meta_value(key, value)
                        params[current_param][key] = value
                    else:
                        # 描述的续行
                        params[current_param]["description"] += " " + stripped_line
        
        return params
    
    def _convert_param_meta_value(self, key: str, value: str) -> Any:
        """转换参数元数据值的类型"""
        if key in ['min', 'max', 'step']:
            try:
                if '.' in value:
                    return float(value)
                else:
                    return int(value)
            except ValueError:
                return value
        
        elif key == 'ignore':
            return value.strip().lower() == 'true'
        
        elif key == 'options':
            val_str = value.strip('[]')
            if not val_str:
                return []
            
            # 尝试 JSON 解析
            if value.strip().startswith('[') and value.strip().endswith(']'):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    pass
            
            # 简单逗号分隔
            value_list = [v.strip() for v in val_str.split(',')]
            
            # 尝试转换为数字
            try:
                return [int(v) for v in value_list]
            except ValueError:
                try:
                    return [float(v) for v in value_list]
                except ValueError:
                    return [v.strip("'").strip('"') for v in value_list]
        
        elif key == 'default':
            # 尝试类型推断
            value = value.strip()
            if value.lower() == 'none':
                return None
            if value.lower() == 'true':
                return True
            if value.lower() == 'false':
                return False
            try:
                if '.' in value:
                    return float(value)
                return int(value)
            except ValueError:
                return value.strip("'").strip('"')
        
        return value
    
    def parse_returns_section(self, docstring: str) -> List[Dict[str, str]]:
        """
        解析 Returns: 块
        
        支持格式:
            Returns:
            name (type): description
            或
            type: description
        
        Args:
            docstring: docstring字符串
            
        Returns:
            返回值列表，每项包含 name, type, description
        """
        if not docstring:
            return []
        
        returns = []
        lines = docstring.split('\n')
        in_returns_section = False
        
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            
            if stripped_line.startswith('Returns:'):
                in_returns_section = True
                continue
            
            if in_returns_section:
                if stripped_line.startswith('Example:') or \
                   stripped_line.startswith('Algorithm:') or \
                   stripped_line.startswith('Parameters:'):
                    break
                
                if stripped_line == 'None':
                    continue
                
                # 匹配 "name (type): description" 格式
                match_name = re.match(r'^(\w+)\s*\((.+)\)\s*:\s*(.+)$', stripped_line)
                if match_name:
                    returns.append({
                        "name": match_name.group(1).strip(),
                        "type": match_name.group(2).strip(),
                        "description": match_name.group(3).strip()
                    })
                    continue
                
                # 匹配 "Type: Description" 格式
                match = re.match(r'^([^:]+):\s*(.+)$', stripped_line)
                if match:
                    r_type = match.group(1).strip()
                    r_desc = match.group(2).strip()
                    returns.append({"type": r_type, "description": r_desc})
        
        return returns
    
    def has_algorithm_section(self, docstring: str) -> bool:
        """检查docstring是否包含Algorithm:块"""
        if not docstring:
            return False
        return 'Algorithm:' in docstring


# 便捷函数（保持兼容性）
_parser = DocstringParser()

def parse_algorithm_metadata(docstring: str) -> Dict[str, Any]:
    """解析算法元数据（兼容函数）"""
    return _parser.parse_algorithm_section(docstring)

def parse_docstring_params(docstring: str) -> Dict[str, Dict[str, Any]]:
    """解析参数（兼容函数）"""
    return _parser.parse_parameters_section(docstring)

def parse_docstring_returns(docstring: str) -> List[Dict[str, str]]:
    """解析返回值（兼容函数）"""
    return _parser.parse_returns_section(docstring)


class CodeParser:
    """
    完整代码解析器
    
    从Python源码中提取算法元数据（包括函数签名、docstring、imports等）
    这是 DocstringParser 的补充，用于解析完整的函数代码
    """
    
    def __init__(self):
        self.docstring_parser = DocstringParser()
    
    def _clean_test_code(self, code: str) -> tuple[str, bool]:
        """
        智能清理测试调用代码，保留算法定义部分
        
        清理策略：
        1. 保留所有 import 语句
        2. 保留函数定义（包含 docstring）
        3. 保留所有注释（单行 # 和多行 '''）
        4. 移除函数定义之后的代码（测试调用、print等）
        
        Args:
            code: 原始代码
            
        Returns:
            (cleaned_code, has_test_code): 清理后的代码和是否包含测试代码的标记
        """
        import ast
        
        try:
            tree = ast.parse(code)
            lines = code.split('\n')
            
            # 找到函数定义节点
            func_def = None
            func_end_line = 0
            
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    func_def = node
                    func_end_line = node.end_lineno
                    break
            
            if not func_def:
                # 没有函数定义，返回原代码
                return code, False
            
            # 检测是否有测试代码（函数定义之后的非空行）
            has_test_code = False
            for i in range(func_end_line, len(lines)):
                line = lines[i].strip()
                if line and not line.startswith('#'):
                    has_test_code = True
                    break
            
            # 保留：从开头到函数定义结束的所有内容（包括注释）
            cleaned_lines = lines[:func_end_line]
            
            # 移除末尾的空行
            while cleaned_lines and not cleaned_lines[-1].strip():
                cleaned_lines.pop()
            
            cleaned_code = '\n'.join(cleaned_lines)
            return cleaned_code, has_test_code
                
        except SyntaxError:
            # 解析失败，返回原代码
            return code, False
    
    def parse_function_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        从完整的函数代码中提取算法元数据
        
        这个方法整合了：
        - AST 解析（函数签名）
        - Docstring 解析（算法元数据、参数、返回值）
        - Import 提取（代码依赖）
        - 智能清理测试调用代码
        
        Args:
            code: 完整的Python函数代码字符串
            
        Returns:
            算法元数据字典，包含以下字段：
            - id: 函数名（算法ID）
            - name: 算法名称
            - category: 类别
            - description: 描述
            - prompt: AI提示模板
            - imports: 导入语句列表
            - args: 参数列表（非input角色）
            - inputs: 输入端口列表（input角色）
            - outputs: 输出端口列表
            - code: 原始代码（已清理测试代码）
            - has_test_code: 是否包含了测试调用代码
            
            如果解析失败返回 None
        """
        import ast
        from .extractor import extract_imports_from_source
        
        try:
            # 0. 智能清理测试代码
            cleaned_code, has_test_code = self._clean_test_code(code)
            
            # 1. 解析AST
            tree = ast.parse(cleaned_code)
            func_node = None
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    func_node = node
                    break
            
            if not func_node:
                return None
            
            # 2. 提取docstring
            docstring = ast.get_docstring(func_node)
            if not docstring:
                return None
            
            # 3. 解析算法元数据
            algo_metadata = self.docstring_parser.parse_algorithm_section(docstring)
            params_meta = self.docstring_parser.parse_parameters_section(docstring)
            
            # 4. 提取imports（从清理后的代码，而非docstring）
            imports = extract_imports_from_source(cleaned_code)
            
            # 5. 提取函数参数
            args = []
            inputs = []
            
            for arg in func_node.args.args:
                name = arg.arg
                p_meta = params_meta.get(name, {})
                role = p_meta.get('role')
                
                # 获取类型（优先从docstring，其次从类型注解）
                arg_type = p_meta.get('type', 'any')
                if arg_type == 'any' and arg.annotation:
                    try:
                        if isinstance(arg.annotation, ast.Name):
                            arg_type = arg.annotation.id
                        elif isinstance(arg.annotation, ast.Attribute):
                            # e.g. pd.DataFrame -> DataFrame
                            arg_type = arg.annotation.attr
                    except:
                        pass
                
                # 推断角色（如果未指定）
                if not role:
                    if name == 'df' or 'df_' in name or 'dataframe' in str(arg_type).lower():
                        role = 'input'
                    else:
                        role = 'parameter'
                
                # 构建参数字典
                item = {
                    "name": name,
                    "type": arg_type,
                    "description": p_meta.get('description', ''),
                    "label": p_meta.get('label'),
                    "widget": p_meta.get('widget'),
                    "options": p_meta.get('options'),
                    "min": p_meta.get('min'),
                    "max": p_meta.get('max'),
                    "step": p_meta.get('step'),
                    "priority": p_meta.get('priority'),
                    "role": role
                }
                
                # 清理None值
                item = {k: v for k, v in item.items() if v is not None}
                
                # 分类到inputs或args
                if role == 'input':
                    inputs.append(item)
                else:
                    args.append(item)
            
            # 6. 解析返回值
            outputs = []
            if "Returns:" in docstring:
                parsed_returns = self.docstring_parser.parse_returns_section(docstring)
                for i, ret in enumerate(parsed_returns):
                    outputs.append({
                        "name": ret.get("name", f"output_{i}"),
                        "type": ret["type"],
                        "description": ret["description"]
                    })
            else:
                # 默认输出
                outputs.append({"name": "result", "type": "pd.DataFrame"})
            
            # 7. 提取描述（Algorithm:之前的内容）
            description = self.docstring_parser.parse_description(docstring)
            
            # 8. 组装结果
            return {
                "id": func_node.name,
                "category": algo_metadata.get('category'),
                "name": algo_metadata.get('name'),
                "description": description,
                "prompt": algo_metadata.get('prompt'),
                "imports": imports,
                "args": args,
                "inputs": inputs,
                "outputs": outputs,
                "code": cleaned_code,
                "has_test_code": has_test_code
            }
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to parse function code: {e}")
            return None


# 全局CodeParser实例
_code_parser = CodeParser()


def parse_function_code(code: str) -> Optional[Dict[str, Any]]:
    """解析函数代码（便捷函数）"""
    return _code_parser.parse_function_code(code)
