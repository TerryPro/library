import pandas as pd
import os
import sys
from typing import Any, Optional
from IPython.display import display

def import_variable(variable_name: str = "") -> pd.DataFrame:
    """
    Import an existing variable from the global namespace.

    Algorithm:
        name: 引入变量
        category: load_data
        prompt: 从全局命名空间中引入变量 "{variable_name}"。如果该变量是 DataFrame，则创建其副本以避免修改原始数据；否则直接引用。引入后打印变量形状并显示前 5 行。

    
    Parameters:
    variable_name (str): 当前会话中的DataFrame变量名
        label: 变量名称
        widget: variable-selector
        priority: critical
    
    Returns:
    pandas.DataFrame: Imported variable.
    """
  
    try:
        source_var = None
        # Try to find variable in __main__ (notebook namespace) first
        if variable_name in sys.modules['__main__'].__dict__:
            source_var = sys.modules['__main__'].__dict__[variable_name]
        elif variable_name in globals():
            source_var = globals()[variable_name]
            
        if source_var is None:
            print(f"Error: Variable '{variable_name}' not found in global scope.")
            return None
        
        if hasattr(source_var, 'copy'):
            result = source_var.copy()
        else:
            result = source_var
            
        print(f"Imported '{variable_name}'")
        if hasattr(result, 'shape'):
             print(f"Shape: {result.shape}")
        if hasattr(result, 'head'):
             print(f"First few rows:")
             display(result.head())
        return result
    except Exception as e:
        print(f"Import failed: {e}")
        return None
