import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

def moving_window_iqr_anomaly(df: pd.DataFrame, columns: list, window: int = 60, multiplier: float = 1.5, center: bool = True) -> pd.DataFrame:
    """
    Detect anomalies using moving window IQR method.

    Algorithm:
        name: 移动窗口 IQR 检测
        category: anomaly_detection
        prompt: 请对 {VAR_NAME} 执行移动窗口 IQR 异常检测。窗口大小 {window}，倍数 {multiplier}。
        imports: import pandas as pd
    
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
    multiplier (float): IQR multiplier for threshold.
        label: IQR倍数
        min: 0.5
        max: 5.0
        step: 0.1
        priority: critical
    center (bool): Whether to center the window.
        label: 居中窗口
        priority: non-critical
    
    Returns:
    pandas.DataFrame: DataFrame with anomaly flags.
    """
    result = df.copy()
    
    if not columns:
        columns = result.select_dtypes(include=['number']).columns.tolist()
    
    for col in columns:
        # 计算移动窗口的四分位数
        rolling_q1 = result[col].rolling(window=window, center=center).quantile(0.25)
        rolling_q3 = result[col].rolling(window=window, center=center).quantile(0.75)
        
        # 计算移动窗口IQR和上下界
        rolling_iqr = rolling_q3 - rolling_q1
        rolling_lower = rolling_q1 - multiplier * rolling_iqr
        rolling_upper = rolling_q3 + multiplier * rolling_iqr
        
        # 标记异常值
        result[f'{col}_rolling_lower'] = rolling_lower
        result[f'{col}_rolling_upper'] = rolling_upper
        result[f'{col}_anomaly'] = (result[col] < rolling_lower) | (result[col] > rolling_upper)
        
        # 统计异常值数量
        anomalies_count = result[f'{col}_anomaly'].sum()
        print(f"列 '{col}' 发现 {anomalies_count} 个异常值。")
    
    return result
