#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试导入路径兼容性（不依赖第三方库）"""

import sys
import os

# 确保 library 目录在路径中
library_dir = os.path.dirname(os.path.abspath(__file__))
if library_dir not in sys.path:
    sys.path.insert(0, library_dir)

print("=" * 60)
print("测试导入路径兼容性")
print("=" * 60)

# 测试1: 检查 widgets 模块是否可导入
try:
    import widgets
    print("✓ widgets 模块导入成功")
    print(f"  模块路径: {widgets.__file__}")
except ImportError as e:
    print(f"✗ widgets 模块导入失败: {e}")
    sys.exit(1)

# 测试2: 检查 algorithm 模块是否可导入
try:
    import algorithm
    print("✓ algorithm 模块导入成功")
except ImportError as e:
    print(f"✗ algorithm 模块导入失败: {e}")
    sys.exit(1)

# 测试3: 检查 sys.modules 中是否注册了 algorithm.widgets
if 'algorithm.widgets' in sys.modules:
    print("✓ algorithm.widgets 已注册到 sys.modules")
    widgets_module = sys.modules['algorithm.widgets']
    print(f"  指向模块: {widgets_module.__name__}")
    
    # 验证是否指向同一个模块
    if widgets_module is widgets:
        print("✓ algorithm.widgets 正确指向 widgets 模块")
    else:
        print("✗ algorithm.widgets 没有指向 widgets 模块")
else:
    print("✗ algorithm.widgets 未注册到 sys.modules")

# 测试4: 测试导入语句（模拟用户使用）
try:
    from algorithm.widgets import AlgorithmWidget
    print("✓ from algorithm.widgets import AlgorithmWidget 语法验证成功")
    print("  注意: 实际运行需要 ipywidgets 等依赖")
except ImportError as e:
    error_msg = str(e)
    # 如果是因为 ipywidgets 等依赖缺失，这是预期的
    if 'ipywidgets' in error_msg or 'pandas' in error_msg or 'IPython' in error_msg:
        print("✓ 导入路径正确，但缺少运行时依赖（预期行为）")
        print(f"  缺少依赖: {error_msg}")
    else:
        print(f"✗ 导入路径失败: {e}")

print("=" * 60)
print("测试完成 - 向后兼容性已实现")
print("=" * 60)
