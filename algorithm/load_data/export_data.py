import pandas as pd
import os
import sys
from typing import Any, Optional
from IPython.display import display

def export_data(df: pd.DataFrame, global_name: str = "exported_data") -> None:
    """
    Export data to the global namespace.

    Algorithm:
        name: 引出变量
        category: load_data
        prompt: 将变量 {VAR_NAME} 导出到全局变量 "{global_name}" 中，以便在其他 Notebook 单元格或分析步骤中使用。导出成功后显示确认信息。
    
    Parameters:
    df (pandas.DataFrame): DataFrame to export.
        role: input
    global_name (str): 引出的全局变量名称
        label: 全局变量名
        priority: critical
    
    Returns:
    None
    """
    
    try:
        # Export to __main__ (notebook namespace)
        setattr(sys.modules['__main__'], global_name, df)
        print(f"Successfully exported to global variable: '{global_name}'")
        if hasattr(df, 'shape'):
            print(f"Variable shape: {df.shape}")
        if hasattr(df, 'head'):
            print(f"Variable preview:")
            display(df.head())
    except Exception as e:
        print(f"Export failed: {e}")
        return None
    return None
