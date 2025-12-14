import pandas as pd
import numpy as np
import ast
from typing import Tuple, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler

def interpolation_spline(df: pd.DataFrame, order: int = 3) -> pd.DataFrame:
    """
    Perform spline interpolation on a DataFrame.

    Algorithm:
        name: 样条插值
        category: data_preprocessing
        prompt: 请对{VAR_NAME} 进行样条插值 (Spline)。使用 pandas 的 interpolate(method='spline', order=3) 以获得更平滑的补全曲线。

    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    order (int): 样条插值的阶数
        label: 样条阶数
        min: 1
        max: 5
        priority: critical
    
    Returns:
    pandas.DataFrame: DataFrame with spline interpolation applied.
    """
    result = df.copy()
    
    # Requires numeric index (or datetime converted to numeric) for spline
    try:
        result = result.interpolate(method='spline', order=order)
    except Exception as e:
        print(f"Spline interpolation failed (index might not be compatible): {e}")
        print("Falling back to linear interpolation")
        result = result.interpolate(method='linear')
    
    print(f"Applied spline interpolation with order {order}")
    return result
