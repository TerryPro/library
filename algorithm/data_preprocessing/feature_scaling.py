import pandas as pd
import numpy as np
import ast
from typing import Tuple, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler

def feature_scaling(df: pd.DataFrame, method: str = "standard", with_mean: bool = True, with_std: bool = True, feature_range: str = "(0, 1)") -> pd.DataFrame:
    """
    Perform feature scaling on a DataFrame.

    Algorithm:
        name: 数据标准化/归一化
        category: data_preprocessing
        prompt: 请对 {VAR_NAME} 进行特征缩放。支持多种缩放方法，直接修改原始列。

    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    method (str): 选择缩放方法：standard（Z-score）、minmax（0-1归一化）、robust（鲁棒缩放）、maxabs（最大绝对值缩放）
        label: 缩放方法
        widget: select
        options: ["standard", "minmax", "robust", "maxabs"]
        priority: critical
    with_mean (bool): 对于standard和robust方法，是否减去均值
        label: 包含均值
        priority: non-critical
    with_std (bool): 对于standard方法，是否除以标准差
        label: 包含标准差
        priority: non-critical
    feature_range (str): 对于minmax方法，指定目标范围，格式为'(min, max)'
        label: 特征范围
        priority: non-critical
    
    Returns:
    pandas.DataFrame: Scaled DataFrame.
    """
    result = df.copy()
    
    # Parse feature_range string to tuple
    try:
        if isinstance(feature_range, str):
            feature_range_tuple = ast.literal_eval(feature_range)
        else:
            feature_range_tuple = feature_range
            
        if not isinstance(feature_range_tuple, tuple) or len(feature_range_tuple) != 2:
             feature_range_tuple = (0, 1)
    except:
        feature_range_tuple = (0, 1)

    # Select numeric columns only
    numeric_cols = result.select_dtypes(include=['number']).columns
    if not numeric_cols.empty:
        try:
            if method == 'standard':
                scaler = StandardScaler(with_mean=with_mean, with_std=with_std)
            elif method == 'minmax':
                scaler = MinMaxScaler(feature_range=feature_range_tuple)
            elif method == 'robust':
                scaler = RobustScaler(with_centering=with_mean, with_scaling=with_std)
            elif method == 'maxabs':
                scaler = MaxAbsScaler()
            else:
                scaler = StandardScaler()  # Fallback
            
            # Scale in-place on original columns
            result[numeric_cols] = scaler.fit_transform(result[numeric_cols])
            
            print(f"Applied {method} scaling to {len(numeric_cols)} columns")
            if method == 'standard':
                print(f"  with_mean: {with_mean}, with_std: {with_std}")
            elif method == 'minmax':
                print(f"  feature_range: {feature_range_tuple}")
            elif method == 'robust':
                print(f"  with_centering: {with_mean}, with_scaling: {with_std}")
        except Exception as e:
            print(f"Scaling failed: {e}")
    else:
        print("No numeric columns found for scaling")
    
    return result
