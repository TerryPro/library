import os
import sys
import pandas as pd
from typing import Optional
from typing import Any
from IPython.display import display

def load_csv(filepath: str, timeIndex: str = 'timestamp') -> Optional[pd.DataFrame]:
    """
    从数据集目录中读取一个CSV文件，读取并返回pandas的dataframe数据。
    
    Algorithm:
        name: 加载 CSV
        category: load_data
        prompt: 使用 pandas 读取位于 "{filepath}" 的 CSV 文件。如果加载后的数据中包含时间类型列，则将其转换为时间类型并设为索引。读取完成后，显示数据的前 5 行以供预览。
    
    Parameters:
    filepath (str): Parameter filepath
        label: Filepath
        widget: file-selector
        options: ["satellite_eps_telemetry.csv", "satellite_eps_telemetry_24h.csv", "satellite_gnc_telemetry.csv", "satellite_gnc_telemetry_24h.csv", "satellite_obdh_telemetry.csv", "satellite_obdh_telemetry_24h.csv", "satellite_power_data.csv", "satellite_power_telemetry.csv", "satellite_power_telemetry_24h.csv", "satellite_thermal_telemetry_24h.csv", "satellite_ttc_telemetry.csv", "satellite_ttc_telemetry_24h.csv", "test_sampling_periods.csv"]
        priority: non-critical
        role: parameter
    timeIndex (str): Parameter timeIndex
        label: Timeindex
        widget: input-text
        priority: non-critical
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
