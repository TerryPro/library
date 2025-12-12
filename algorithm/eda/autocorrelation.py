import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.seasonal import STL

def autocorrelation(df: pd.DataFrame, lags: int = 50, figsize: tuple = None) -> pd.DataFrame:
    """
    Perform autocorrelation analysis on a DataFrame.

    Algorithm:
        name: 自相关分析 (ACF)
        category: eda
        prompt: 请对{VAR_NAME} 进行自相关分析。计算并绘制 ACF 图，使用 statsmodels.graphics.tsaplots.plot_acf，以发现周期性模式。
        imports: import matplotlib.pyplot as plt, from statsmodels.graphics.tsaplots import plot_acf
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    lags (int): 绘制的滞后数量
        label: 滞后数
        min: 10
        max: 200
    figsize (tuple): 图像大小元组，例如 (15, 8)
        label: 图像尺寸
        priority: non-critical
    
    Returns:
    pandas.DataFrame: Original DataFrame (unchanged).
    """
    result = df.copy()
    df_acf = df.select_dtypes(include=['number'])
    
    # Set default figsize
    if figsize is None:
        figsize = (15, 8)
    
    # Plot ACF for first few numeric columns
    max_cols = 3
    cols_to_plot = df_acf.columns[:max_cols]
    
    fig, axes = plt.subplots(len(cols_to_plot), 1, figsize=figsize, sharex=False)
    if len(cols_to_plot) == 1: axes = [axes]
    
    for i, col in enumerate(cols_to_plot):
        # Drop NA
        data = df_acf[col].dropna()
        plot_acf(data, ax=axes[i], title=f'Autocorrelation: {col}', lags=lags)
    
    plt.tight_layout()
    plt.show()
    
    return result
