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


def change_point(df, n_bkps=5, figsize=None) -> pd.DataFrame:
    """
    Detect change points in a time series using binary segmentation.

    Algorithm:
        name: 变点检测
        category: anomaly_detection
        prompt: 请对 {VAR_NAME} 执行变点检测。检测 {n_bkps} 个变点。
        imports: import pandas as pd, import ruptures as rpt, import matplotlib.pyplot as plt
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame with time series data.
        role: input
    n_bkps (int): Number of change points to detect.
        label: 变点数量
        min: 1
        priority: critical
    figsize (tuple): Figure size tuple.
        label: 图像尺寸
        priority: non-critical
    
    Returns:
    pandas.DataFrame: Original DataFrame (unchanged).
    """
    result = df.copy()
    
    if figsize is None:
        figsize = (15, 8)
    elif isinstance(figsize, str):
        try:
            figsize = eval(figsize)
        except:
            figsize = (15, 8)
    
    try:
        import ruptures as rpt
        
        # Select first numeric column for change point detection
        target_col = result.select_dtypes(include=['number']).columns[0]
        signal = result[target_col].values
        
        # Detection
        algo = rpt.Binseg(model="l2").fit(signal)
        change_points = algo.predict(n_bkps=n_bkps)
        
        # Display
        rpt.display(signal, change_points, figsize=figsize)
        plt.title(f'Change Point Detection: {target_col}')
        plt.show()
        
        print(f"Found {len(change_points)} change points in column {target_col}.")
    except ImportError:
        print("ruptures library not installed. Change point detection skipped.")
    except Exception as e:
        print(f"Change point detection failed: {e}")
    
    return result


def zscore_anomaly(df, columns, threshold=3.0) -> pd.DataFrame:
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


def iqr_anomaly(df, columns, multiplier=1.5) -> pd.DataFrame:
    """
    Detect anomalies using IQR (Interquartile Range) method.

    Algorithm:
        name: IQR 异常检测
        category: anomaly_detection
        prompt: 请对 {VAR_NAME} 执行 IQR 异常检测。使用 IQR 倍数 {multiplier}。
        imports: import pandas as pd
    
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


def moving_window_zscore_anomaly(df, columns, window=60, threshold=3.0, center=True) -> pd.DataFrame:
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


def moving_window_iqr_anomaly(df, columns, window=60, multiplier=1.5, center=True) -> pd.DataFrame:
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
