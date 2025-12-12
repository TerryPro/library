import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

def zscore_anomaly(df: pd.DataFrame, columns: list, threshold: float = 3.0) -> pd.DataFrame:
    """
    Detect anomalies using Z-score method.

    Algorithm:
        name: Z-Score 异常检测
        category: anomaly_detection
        prompt: 请对 {VAR_NAME} 执行 Z-Score 异常检测。使用阈值 {threshold}。
        imports: import pandas as pd, import numpy as np
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    columns (list): Columns to detect anomalies in.
        label: 检测列
        widget: column-selector
        priority: critical
    threshold (float): Z-score threshold for anomalies.
        label: Z-score阈值
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
    
    for col in columns:
        # 计算全局Z-score
        mean = result[col].mean()
        std = result[col].std()
        result[f'{col}_zscore'] = (result[col] - mean) / std
        
        # 标记异常值
        result[f'{col}_anomaly'] = np.abs(result[f'{col}_zscore']) > threshold
        
        # 统计异常值数量
        anomalies_count = result[f'{col}_anomaly'].sum()
        print(f"列 '{col}' 发现 {anomalies_count} 个异常值。")
    
    return result
