import pandas as pd
import numpy as np
import ast
from typing import Tuple, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler

def resampling_down(df: pd.DataFrame, rule: str = "1小时", agg_method: str = "均值") -> pd.DataFrame:
    """
    Downsample a DataFrame to a lower frequency.

    Algorithm:
        name: 降采样
        category: data_preprocessing
        prompt: 请对{VAR_NAME} 进行降采样聚合。使用 pandas 的 resample() 将数据聚合到更低的时间分辨率（例如 '1min' 或 '1H'）；数值列使用 mean()，状态列使用 last() 或 max()。
        imports: import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame with DatetimeIndex.
        role: input
    rule (str): 目标重采样频率
        label: 频率规则
        options: ["15秒", "30秒", "1分钟", "5分钟", "15分钟", "30分钟", "1小时"]
        priority: critical
    agg_method (str): 降采样时使用的聚合函数
        label: 聚合方法
        options: ["均值", "求和", "最小值", "最大值", "第一个值", "最后一个值", "中位数", "标准差", "方差", "计数"]
        priority: critical
    
    Returns:
    pandas.DataFrame: Downsampled DataFrame.
    """
    result = df.copy()
    
    if not isinstance(result.index, pd.DatetimeIndex):
        print("Error: Input DataFrame index is not a DatetimeIndex. Cannot resample.")
        return result
    
    # Map Chinese rule to pandas offset alias
    rule_map = {
        "15秒": "15S",
        "30秒": "30S",
        "1分钟": "1T",
        "5分钟": "5T",
        "15分钟": "15T",
        "30分钟": "30T",
        "1小时": "1H"
    }
    pandas_rule = rule_map.get(rule, rule) # Fallback to using the string directly if not in map

    # Map Chinese aggregation method to pandas function name
    agg_method_map = {
        "均值": "mean",
        "求和": "sum",
        "最小值": "min",
        "最大值": "max",
        "第一个值": "first",
        "最后一个值": "last",
        "中位数": "median",
        "标准差": "std",
        "方差": "var",
        "计数": "count"
    }
    
    agg_func = agg_method_map.get(agg_method, agg_method)
    
    # Define aggregation dictionary: use selected method for all columns
    agg_dict = {col: agg_func for col in result.columns}
            
    result = result.resample(pandas_rule).agg(agg_dict)
    print(f"Resampled to {pandas_rule} frequency. New shape: {result.shape}")
    print(f"Aggregation method: {agg_method} ({agg_func})")
    return result
