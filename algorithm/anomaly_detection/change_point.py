import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

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
