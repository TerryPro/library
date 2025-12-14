import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

def iqr_anomaly(df: pd.DataFrame, columns: list, multiplier: float = 1.5) -> pd.DataFrame:
    """
    Detect anomalies using IQR (Interquartile Range) method.

    Algorithm:
        name: IQR 异常检测
        category: anomaly_detection
        prompt: 请对 {VAR_NAME} 执行 IQR 异常检测。使用 IQR 倍数 {multiplier}。

    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    columns (list): Columns to detect anomalies in.
        label: 检测列
        widget: column-selector
        priority: critical
    multiplier (float): IQR multiplier for threshold.
        label: IQR倍数
        min: 0.5
        max: 5.0
        step: 0.1
        priority: critical
    
    Returns:
    pandas.DataFrame: DataFrame with anomaly flags.
    """
    result = df.copy()
    
    if not columns:
        columns = result.select_dtypes(include=['number']).columns.tolist()
    
    for col in columns:
        # 计算IQR
        q1 = result[col].quantile(0.25)
        q3 = result[col].quantile(0.75)
        iqr = q3 - q1
        
        # 计算上下界
        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr
        
        # 标记异常值
        result[f'{col}_lower_bound'] = lower_bound
        result[f'{col}_upper_bound'] = upper_bound
        result[f'{col}_anomaly'] = (result[col] < lower_bound) | (result[col] > upper_bound)
        
        # 统计异常值数量
        anomalies_count = result[f'{col}_anomaly'].sum()
        print(f"列 '{col}' 发现 {anomalies_count} 个异常值。")
    
    return result
