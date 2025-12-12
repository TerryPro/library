import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

def isolation_forest(df, contamination=0.05) -> pd.DataFrame:
    """
    Detect anomalies using Isolation Forest algorithm.

    Algorithm:
        name: 孤立森林异常检测
        category: anomaly_detection
        prompt: 请对 {VAR_NAME} 执行孤立森林异常检测。设置异常比例为 {contamination}。
        imports: import pandas as pd, from sklearn.ensemble import IsolationForest
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    contamination (float): Expected proportion of anomalies in the data.
        label: 异常比例
        min: 0.0
        max: 0.5
        step: 0.01
        priority: critical
    
    Returns:
    pandas.DataFrame: DataFrame with anomaly flags.
    """
    result = df.copy()
    
    # Select numeric columns only
    numeric_data = result.select_dtypes(include=['number'])
    
    if numeric_data.empty:
        print("No numeric columns found for anomaly detection.")
        return result
    
    # Fit isolation forest model
    model = IsolationForest(contamination=contamination, random_state=42)
    result['anomaly'] = model.fit_predict(numeric_data)
    
    # -1 indicates anomaly, 1 indicates normal
    anomalies = result[result['anomaly'] == -1]
    print(f"Found {len(anomalies)} anomalies using Isolation Forest with contamination={contamination}.")
    
    return result
