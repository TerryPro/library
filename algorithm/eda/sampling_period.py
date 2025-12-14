import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.seasonal import STL

def sampling_period(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze sampling periods in a DataFrame.

    Algorithm:
        name: 采样周期统计
        category: eda
        prompt: 请对{VAR_NAME} 进行采样周期统计。计算每一列数据的实际采样周次。

    
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
