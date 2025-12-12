import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

def threshold_sigma(df, columns, window=20, sigma=3.0) -> pd.DataFrame:
    """
    Detect anomalies using 3-sigma threshold method.

    Algorithm:
        name: 3-Sigma 异常检测
        category: anomaly_detection
        prompt: 请对 {VAR_NAME} 执行 3-Sigma 异常检测。使用窗口大小 {window} 和阈值 {sigma}。
        imports: import pandas as pd, import numpy as np
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    columns (list): Columns to detect anomalies in.
        label: 检测列
        widget: column-selector
        priority: critical
    window (int): Rolling window size.
        label: 窗口大小
        min: 5
        priority: critical
    sigma (float): Number of standard deviations for threshold.
        label: Sigma阈值
        min: 1.0
        max: 10.0
        step: 0.1
        priority: critical
    
    Returns:
    pandas.DataFrame: DataFrame with anomaly flags.
    """
    result = df.copy()
    
    if not columns:
        columns = result.select_dtypes(include=['number']).columns.tolist()
    
    # 存储所有异常值数量
    total_anomalies = 0
    
    # 为每个列执行3-Sigma异常检测
    for col in columns:
        data = result[col]
        
        # 计算移动窗口均值和标准差
        rolling_mean = data.rolling(window=window).mean()
        rolling_std = data.rolling(window=window).std()
        
        # 计算上下界
        upper_bound = rolling_mean + sigma * rolling_std
        lower_bound = rolling_mean - sigma * rolling_std
        
        # 标记异常值
        result[f'{col}_rolling_mean'] = rolling_mean
        result[f'{col}_rolling_std'] = rolling_std
        result[f'{col}_upper_bound'] = upper_bound
        result[f'{col}_lower_bound'] = lower_bound
        result[f'{col}_is_anomaly'] = (data > upper_bound) | (data < lower_bound)
        
        # 统计异常值数量
        anomalies_count = result[f'{col}_is_anomaly'].sum()
        total_anomalies += anomalies_count
        
        print(f"列 '{col}' 发现 {anomalies_count} 个异常值。")
    
    print(f"\n总计发现 {total_anomalies} 个异常值。")
    
    return result
