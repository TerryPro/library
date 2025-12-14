import pandas as pd
import os
import sys
from typing import Any
from IPython.display import display
from typing import Optional

def load_csv(filepath: str, timeIndex: str = 'timestamp') -> Optional[pd.DataFrame]:
    """
    从数据集目录中读取一个CSV文件，读取并形成一个pandas的dataframe数据。
    
    Algorithm:
        name: 加载 CSV
        category: load_data
        prompt: 使用 pandas 读取位于 "{filepath}" 的 CSV 文件。如果加载后的数据中包含时间类型列，则将其转换为时间类型并设为索引。读取完成后，显示数据的前 5 行以供预览。
    
    Parameters:
    filepath (str): CSV文件路径 (相对于项目根目录)
        label: 文件路径
        widget: file-selector
        priority: critical
        role: parameter
    timeIndex (str): 选择作为时间索引的列名，为空则生成普通DataFrame
        label: 时间索引列
        widget: input-text
        priority: critical
        role: parameter
    
    Returns:
    df_out (pd.DataFrame): Result
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
