import pandas as pd
import numpy as np
import ast
from typing import Tuple, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler

def diff_transform(df: pd.DataFrame, order: int = 1, periods: int = 1, axis: int = 0, fill_method: str = "") -> pd.DataFrame:
    """
    Perform difference transformation on a DataFrame.

    Algorithm:
        name: 差分变换
        category: data_preprocessing
        prompt: 请对 {VAR_NAME} 进行差分变换，以消除趋势并使数据平稳。可配置差分阶数和滞后步数。
        imports: import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    order (int): 差分的阶数，1为一阶差分，2为二阶差分等
        label: 差分阶数
        min: 1
        max: 5
        step: 1
        priority: critical
    periods (int): 差分的滞后步数，默认1
        label: 滞后步数
        min: 1
        max: 10
        step: 1
        priority: critical
    axis (int): 沿哪个轴进行差分，0=行（时间轴），1=列
        label: 差分轴
        widget: select
        options: [0, 1]
        min: 0
        max: 1
        step: 1
        priority: non-critical
    fill_method (str): 差分后缺失值的填充方法，留空则不填充
        label: 填充方法
        widget: select
        options: ["", "ffill", "bfill"]
        priority: non-critical
    
    Returns:
    pandas.DataFrame: Differenced DataFrame.
    """
    result = df.select_dtypes(include=['number']).copy()
    
    # Perform difference transformation
    try:
        # Apply difference multiple times for higher orders
        for i in range(order):
            result = result.diff(periods=periods, axis=axis)
        
        # Fill missing values if specified
        if fill_method:
            result = result.fillna(method=fill_method)
            print(f"Filled missing values using {fill_method}")
        
        print(f"Applied {order}nd order difference with periods={periods} along axis={axis}")
        print(f"New shape: {result.shape}")
    except Exception as e:
        print(f"Difference transform failed: {e}")
    
    return result
