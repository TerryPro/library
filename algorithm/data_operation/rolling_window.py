import pandas as pd

def rolling_window(df, columns, window=5, func="mean", min_periods=1, center=False) -> pd.DataFrame:
    """
    Apply rolling window calculation to a DataFrame.

    Algorithm:
        name: 窗口计算
        category: data_operation
        prompt: 请对 {VAR_NAME} 进行窗口计算。使用窗口大小 {window} 对列 {columns} 应用 {func} 函数。
        imports: import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    columns (list): Columns to perform window calculation on.
        label: 计算列
        widget: column-selector
        priority: critical
    window (int): Window size.
        label: 窗口大小
        priority: critical
    func (str): Aggregation function to apply.
        label: 统计函数
        options: ["sum", "mean", "min", "max", "std", "var"]
        priority: critical
    min_periods (int): Minimum number of observations required in window.
        label: 最小观测值
        priority: non-critical
    center (bool): Whether to center the window.
        label: 居中窗口
        priority: non-critical
    
    Returns:
    pandas.DataFrame: DataFrame with window calculation results.
    """
    result = df.copy()
    
    # Select columns if specified, otherwise use all numeric columns
    if not columns:
        columns = result.select_dtypes(include=['number']).columns.tolist()
    
    # Apply rolling window function
    try:
        for col in columns:
            result[col] = result[col].rolling(
                window=window,
                min_periods=min_periods,
                center=center
            ).agg(func)
        
        print(f"Applied {func} with window size {window} to columns: {columns}")
        return result
    except Exception as e:
        print(f"Window calculation failed: {e}")
        return result
