# -*- coding: utf-8 -*-
"""
Algorithm Core Library
======================
统一的算法解析与生成核心模块

模块说明:
- models: 算法数据模型定义
- parser: Docstring解析器
- extractor: Import和参数提取器
- scanner: 算法库扫描器
- generator: 代码生成器
- path_utils: 路径管理工具
"""

# 首先导入路径工具，确保路径正确初始化
from .path_utils import ensure_library_in_path, get_library_path

from .models import AlgorithmPort, AlgorithmParameter, AlgorithmMetadata, get_category_labels
from .parser import DocstringParser, CodeParser, parse_function_code
from .extractor import CodeExtractor
from .scanner import LibraryScanner
from .generator import CodeGenerator

__all__ = [
    'AlgorithmPort',
    'AlgorithmParameter', 
    'AlgorithmMetadata',
    'DocstringParser',
    'CodeParser',
    'CodeExtractor',
    'LibraryScanner',
    'CodeGenerator',
    'get_category_labels',
    'parse_function_code',
    'ensure_library_in_path',
    'get_library_path',
]
