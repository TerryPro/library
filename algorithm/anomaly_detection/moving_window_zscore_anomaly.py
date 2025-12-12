import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

def moving_window_zscore_anomaly(df: pd.DataFrame, columns: list, window: int = 60, threshold: float = 3.0, center: bool = True) -> pd.DataFrame:
    """
    Detect anomalies using moving window Z-score method.

    Algorithm:
        name: 移动窗口 Z-Score 检测
        category: anomaly_detection
        prompt: 请对 {VAR_NAME} 执行移动窗口 Z-Score 异常检测。窗口大小 {window}，阈值 {threshold}。
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
    threshold (float): Z-score threshold for anomalies.
        label: Z-score阈值
        min: 1.0
        max: 10.0
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
        # 计算移动窗口均值和标准差
        rolling_mean = result[col].rolling(window=window, center=center).mean()
        rolling_std = result[col].rolling(window=window, center=center).std()
        
        # 计算移动窗口Z-score
        result[f'{col}_rolling_mean'] = rolling_mean
        result[f'{col}_rolling_std'] = rolling_std
        result[f'{col}_zscore'] = (result[col] - rolling_mean) / rolling_std
        
        # 标记异常值
        result[f'{col}_anomaly'] = np.abs(result[f'{col}_zscore']) > threshold
        
        # 统计异常值数量
        anomalies_count = result[f'{col}_anomaly'].sum()
        print(f"列 '{col}' 发现 {anomalies_count} 个异常值。")
    
    return result
