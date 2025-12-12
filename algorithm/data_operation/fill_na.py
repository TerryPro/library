import pandas as pd

def fill_na(df, value=None, method=None) -> pd.DataFrame:
    """
    Fill missing values in a DataFrame.

    Algorithm:
        name: 填充缺失值
        category: data_operation
        prompt: 请对 {VAR_NAME} 填充缺失值。使用值 {value} 或方法 {method} 进行填充。
        imports: import pandas as pd, import numpy as np
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    value (any): Value to use for filling missing values.
        label: 填充值
        priority: non-critical
    method (str): Method to use for filling missing values (ffill, bfill).
        label: 填充方法
        options: ["ffill", "bfill"]
        priority: non-critical
    
    Returns:
    pandas.DataFrame: DataFrame with filled missing values.
    """
    result = df.copy()
    
    try:
        if value is not None:
            result = result.fillna(value=value)
            print(f"Filled NA with value: {value}")
        elif method:
            result = result.fillna(method=method)
            print(f"Filled NA with method: {method}")
        else:
            print("Warning: No value or method specified for fillna.")
        
        return result
    except Exception as e:
        print(f"Fill NA failed: {e}")
        return result
