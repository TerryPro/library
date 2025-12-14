import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.seasonal import STL

def decomposition(df: pd.DataFrame, figsize: tuple = None) -> pd.DataFrame:
    """
    Perform STL decomposition on a DataFrame.

    Algorithm:
        name: STL 分解
        category: eda
        prompt: 请对{VAR_NAME} 执行 STL 分解 (Seasonal-Trend decomposition using LOESS)。将数据分解为趋势、季节与残差，并绘制分解结果图。

    
    Parameters:
    df (pandas.DataFrame): Input DataFrame with DatetimeIndex.
        role: input
    figsize (tuple): 图像大小元组，例如 (15, 8)
        label: 图像尺寸
        priority: non-critical
    
    Returns:
    pandas.DataFrame: Original DataFrame (unchanged).
    """
    result = df.copy()
    df_stl = df.select_dtypes(include=['number']).copy()
    
    # Set default figsize
    if figsize is None:
        figsize = (15, 8)
    
    # Try to set frequency if missing
    if isinstance(df_stl.index, pd.DatetimeIndex) and df_stl.index.freq is None:
        inferred_freq = pd.infer_freq(df_stl.index)
        if inferred_freq:
            df_stl = df_stl.asfreq(inferred_freq)
            df_stl = df_stl.interpolate() # Fill gaps created by asfreq
    
    target_col = df_stl.columns[0] # Decompose the first column
    print(f"Decomposing column: {target_col}")
    
    try:
        # Period is optional if freq is set, otherwise might need to specify
        res = STL(df_stl[target_col], robust=True).fit()
        
        fig = res.plot()
        fig.set_size_inches(figsize[0], figsize[1])
        plt.show()
    except Exception as e:
        print(f"STL Decomposition failed: {e}")
        print("Ensure data has a regular time frequency.")
    
    return result
