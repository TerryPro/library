# -*- coding: utf-8 -*-
"""
Path Utilities
==============
统一的路径管理工具

解决问题：
在多个文件中重复的路径初始化代码，确保 library 目录在 Python 搜索路径中。
这个模块集中管理路径初始化逻辑，避免代码重复。
"""

import sys
import os
from typing import Optional


# 全局变量
_library_path: Optional[str] = None
_initialized: bool = False


def get_library_path() -> str:
    """
    获取 library 目录的绝对路径
    
    这个函数会自动定位 library 目录，无论从哪里调用都能正确找到。
    
    Returns:
        library 目录的绝对路径
    """
    global _library_path
    
    if _library_path is None:
        # 从 core 目录向上找到 library 目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        _library_path = os.path.dirname(current_dir)  # library/
    
    return _library_path


def ensure_library_in_path() -> str:
    """
    确保 library 目录在 Python 搜索路径中
    
    这个函数是幂等的，可以多次调用而不会重复添加路径。
    当 core 模块被导入时，这个函数会自动执行。
    
    Returns:
        library 目录的绝对路径
        
    Example:
        >>> from core import ensure_library_in_path
        >>> lib_path = ensure_library_in_path()
        >>> print(f"Library path: {lib_path}")
    """
    global _initialized
    
    lib_path = get_library_path()
    
    if not _initialized:
        if lib_path not in sys.path:
            sys.path.insert(0, lib_path)
        _initialized = True
    
    return lib_path


# 自动执行：当 core 模块被导入时，自动确保路径正确
# 这样其他模块只需 import core 就能自动初始化路径
ensure_library_in_path()
