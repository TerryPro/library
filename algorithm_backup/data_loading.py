import pandas as pd
import os
import sys
from typing import Any, Optional
from IPython.display import display

def load_csv(filepath: str = "dataset/data.csv", timeIndex: str = "") -> Optional[pd.DataFrame]:
    """
    Load CSV data from the specified filepath.

    Algorithm:
        name: 加载 CSV
        category: load_data
        prompt: 使用 pandas 读取位于 "{filepath}" 的 CSV 文件。如果加载后的数据中包含时间类型列，则将其转换为时间类型并设为索引。读取完成后，显示数据的前 5 行以供预览。
        imports: import pandas as pd, import os
    
    Parameters:
    filepath (str): CSV文件路径 (相对于项目根目录)
        label: 文件路径
        widget: file-selector
        priority: critical
    timeIndex (str): 选择作为时间索引的列名，为空则生成普通DataFrame
        label: 时间索引列
        widget: select
        priority: critical
    
    Returns:
    pandas.DataFrame: Loaded DataFrame.
    """
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return None
    else:
        result = pd.read_csv(filepath)
        
        # Set time index if specified
        if timeIndex:
            try:
                result[timeIndex] = pd.to_datetime(result[timeIndex])
                result = result.set_index(timeIndex)
                print(f"Set '{timeIndex}' as time index")
            except Exception as e:
                print(f"Failed to set time index: {e}")
        
        print(f"Loaded data with shape: {result.shape}")
        return result

def import_variable(variable_name: str = "") -> pd.DataFrame:
    """
    Import an existing variable from the global namespace.

    Algorithm:
        name: 引入变量
        category: load_data
        prompt: 从全局命名空间中引入变量 "{variable_name}"。如果该变量是 DataFrame，则创建其副本以避免修改原始数据；否则直接引用。引入后打印变量形状并显示前 5 行。
        imports: import pandas as pd
    
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
