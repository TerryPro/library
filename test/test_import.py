#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试导入路径兼容性"""

import sys
import os

# 确保 library 目录在路径中
library_dir = os.path.dirname(os.path.abspath(__file__))
if library_dir not in sys.path:
    sys.path.insert(0, library_dir)

print("=" * 60)
print("测试导入路径兼容性")
print("=" * 60)

# 测试1: 新的导入方式
try:
    from widgets import AlgorithmWidget
    print("✓ 新导入方式成功: from widgets import AlgorithmWidget")
except ImportError as e:
    print(f"✗ 新导入方式失败: {e}")

# 测试2: 旧的导入方式（向后兼容）
try:
    from algorithm.widgets import AlgorithmWidget
    print("✓ 旧导入方式成功: from algorithm.widgets import AlgorithmWidget")
except ImportError as e:
    print(f"✗ 旧导入方式失败: {e}")

# 测试3: 验证两种方式导入的是同一个类
try:
    from widgets import AlgorithmWidget as Widget1
    from algorithm.widgets import AlgorithmWidget as Widget2
    
    if Widget1 is Widget2:
        print("✓ 两种导入方式得到的是同一个类")
    else:
        print("✗ 两种导入方式得到的不是同一个类")
except Exception as e:
    print(f"✗ 验证失败: {e}")

print("=" * 60)
print("测试完成")
print("=" * 60)
