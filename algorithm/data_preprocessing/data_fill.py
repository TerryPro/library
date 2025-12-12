import pandas as pd
import numpy as np
import ast
from typing import Tuple, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler

def data_fill(df: pd.DataFrame, method: str = "均值", value: float = 0.0, axis: int = 0, limit: int = 0) -> pd.DataFrame:
    """
    Fill missing values in a DataFrame.

    Algorithm:
        name: 数据填充
        category: data_preprocessing
        prompt: 请对 {VAR_NAME} 进行缺失值填充。支持多种填充方法，包括均值、中位数、众数、前向填充、后向填充、常数填充等。
        imports: import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    method (str): 选择缺失值填充方法
        label: 填充方法
        options: ["均值", "中位数", "众数", "前向填充", "后向填充", "常数", "线性插值", "最近邻插值"]
        priority: critical
    value (float): 当使用常数填充时，指定填充的值
        label: 填充值
        priority: non-critical
    axis (int): 沿哪个轴进行填充，0=按列填充，1=按行填充
        label: 填充轴
        options: [0, 1]
        priority: non-critical
    limit (int): 限制连续缺失值的填充数量，0表示无限制
        label: 填充限制
        min: 0
        max: 1000
        priority: non-critical
    
    Returns:
    pandas.DataFrame: DataFrame with filled missing values.
    """
    result = df.copy()
    
    # Map Chinese method name to pandas method
    method_map = {
        "均值": "mean",
        "中位数": "median",
        "众数": "mode",
        "前向填充": "ffill",
        "后向填充": "bfill",
        "常数": "constant",
        "线性插值": "linear",
        "最近邻插值": "nearest"
    }
    
    pandas_method = method_map.get(method, "mean")
    
    # Perform filling
    limit_arg = limit if limit > 0 else None

    try:
        if pandas_method == "constant":
            result = result.fillna(value=value, limit=limit_arg, axis=axis)
        elif pandas_method in ["ffill", "bfill"]:
            result = result.fillna(method=pandas_method, limit=limit_arg, axis=axis)
        elif pandas_method in ["mean", "median"]:
            # Fill numeric columns with mean/median
            for col in result.columns:
                if pd.api.types.is_numeric_dtype(result[col]):
                    fill_val = result[col].agg(pandas_method)
                    result[col] = result[col].fillna(fill_val, limit=limit_arg)
        elif pandas_method == "mode":
            # Fill with mode
            for col in result.columns:
                fill_val = result[col].mode().iloc[0] if not result[col].mode().empty else np.nan
                result[col] = result[col].fillna(fill_val, limit=limit_arg)
        else:  # Interpolation methods
            result = result.interpolate(method=pandas_method, limit=limit_arg, axis=axis)
        
        print(f"Filled missing values using '{method}' method")
        print(f"New shape: {result.shape}")
    except Exception as e:
        print(f"Data filling failed: {e}")
    
    return result
