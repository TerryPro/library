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


def decomposition(df: pd.DataFrame, figsize: tuple = None) -> pd.DataFrame:
    """
    Perform STL decomposition on a DataFrame.

    Algorithm:
        name: STL 分解
        category: eda
        prompt: 请对{VAR_NAME} 执行 STL 分解 (Seasonal-Trend decomposition using LOESS)。将数据分解为趋势、季节与残差，并绘制分解结果图。
        imports: import matplotlib.pyplot as plt, from statsmodels.tsa.seasonal import STL, import pandas as pd
    
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


def sampling_period(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze sampling periods in a DataFrame.

    Algorithm:
        name: 采样周期统计
        category: eda
        prompt: 请对{VAR_NAME} 进行采样周期统计。计算每一列数据的实际采样周次。
        imports: import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame with DatetimeIndex.
        role: input
    
    Returns:
    pandas.DataFrame: Original DataFrame (unchanged).
    """
    result = df.copy()
    
    if isinstance(result.index, pd.DatetimeIndex):
        # Initialize results list
        results = []
        
        # Iterate through each column
        for col in result.columns:
            # Calculate time differences for non-null values in this column
            col_data = result[col].dropna()
            
            if len(col_data) < 2:
                continue
                
            # Get the indices of non-null values
            non_null_indices = col_data.index
            
            # Calculate time differences between consecutive non-null points
            col_time_diffs = non_null_indices.to_series().diff().dropna()
            
            if not col_time_diffs.empty:
                # Calculate average sampling period in seconds
                avg_seconds = col_time_diffs.mean().total_seconds()
                if avg_seconds > 0:
                    # Add to results list
                    results.append({
                        "列名": col,
                        "平均采样周期": "平均采样周期",
                        "采样周期值": f"{avg_seconds:.0f}s"
                    })
        
        # Create DataFrame from results
        if results:
            sampling_df = pd.DataFrame(results)
            display(sampling_df)
        else:
            print("没有足够的数据点来计算采样周期。")
    else:
        print("错误: 数据索引不是时间索引，无法进行采样周期统计。")
    
    return result


def data_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate data features for a DataFrame.

    Algorithm:
        name: 数据特征
        category: eda
        prompt: 请对{VAR_NAME} 进行数据特征计算。使用pandas的describe()函数，计算各列的基本统计特征。
        imports: import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    
    Returns:
    pandas.DataFrame: Original DataFrame (unchanged).
    """
    result = df.copy()
    
    print("=== 数据基本统计特征 ===")
    print()
    
    # Calculate and display describe()
    describe_result = result.describe()
    display(describe_result)
    
    print()
    print("=== 数据结构信息 ===")
    print(f"数据形状: {result.shape}")
    print(f"列名: {list(result.columns)}")
    print(f"数据类型:")
    display(result.dtypes)
    
    print()
    print("=== 缺失值统计 ===")
    missing_values = result.isnull().sum()
    missing_percentage = (result.isnull().sum() / len(result)) * 100
    missing_stats = pd.DataFrame({"缺失值数量": missing_values, "缺失值百分比(%)": missing_percentage.round(2)})
    display(missing_stats[missing_stats["缺失值数量"] > 0])
    
    if missing_stats[missing_stats["缺失值数量"] > 0].empty:
        print("无缺失值")
    
    return result
