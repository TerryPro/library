import pandas as pd
import os
from typing import Any, Optional

def load_csv(filepath: str = "dataset/data.csv", timeIndex: str = "") -> Optional[pd.DataFrame]:
    """
    Load CSV data from the specified filepath.

    Algorithm:
        name: 加载 CSV
        category: load_data
        prompt: 请加载 CSV 文件。使用 pandas.read_csv 读取指定路径的文件，并显示前几行数据。
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
        prompt: 请引入已存在的 DataFrame 变量 {variable_name}。创建其副本或引用，以便后续分析使用。
        imports: import pandas as pd
    
    Parameters:
    variable_name (str): 当前会话中的DataFrame变量名
        label: 变量名称
        widget: variable-selector
        priority: critical
    
    Returns:
    pandas.DataFrame: Imported variable.
    """
    import globals
    
    try:
        if variable_name not in globals():
            print(f"Error: Variable '{variable_name}' not found in global scope.")
            return None
        
        source_var = globals()[variable_name]
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
        prompt: 请将 {VAR_NAME} 引出到全局环境。变量名为 {global_name}。
    
    Parameters:
    df (pandas.DataFrame): DataFrame to export.
        role: input
    global_name (str): 引出的全局变量名称
        label: 全局变量名
        priority: critical
    
    Returns:
    None
    """
    import globals
    
    try:
        globals()[global_name] = df
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
