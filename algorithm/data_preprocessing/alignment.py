import pandas as pd
import numpy as np
import ast
from typing import Tuple, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler

def alignment(baseline_df: pd.DataFrame, other_df: pd.DataFrame) -> pd.DataFrame:
    """
    Align other_df to baseline_df using merge_asof.

    Algorithm:
        name: 多源数据对齐
        category: data_preprocessing
        prompt: 请以 {VAR_NAME} 为基准执行多源时间对齐。使用 pandas 的 merge_asof 方法，将其他数据对齐到该时间轴。
        imports: import pandas as pd
    
    Parameters:
    baseline_df (pandas.DataFrame): Baseline DataFrame with DatetimeIndex.
        role: input
    other_df (pandas.DataFrame): Other DataFrame with DatetimeIndex to align.
        role: input
    
    Returns:
    pandas.DataFrame: Aligned DataFrame.
    """
    result = baseline_df.copy()
    
    # Using merge_asof (requires sorted DatetimeIndex)
    try:
        result = pd.merge_asof(baseline_df.sort_index(), other_df.sort_index(), 
                              left_index=True, right_index=True, direction='nearest')
        print(f"Aligned DataFrame shape: {result.shape}")
    except Exception as e:
        print(f"Alignment failed: {e}")
        print("Returning baseline DataFrame.")
    
    return result
