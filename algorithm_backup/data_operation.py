import pandas as pd

def select_columns(df, columns) -> pd.DataFrame:
    """
    Select specified columns from a DataFrame.

    Algorithm:
        name: 选择列
        category: data_operation
        prompt: 请从 {VAR_NAME} 中选择指定的列 {columns}，生成新的 DataFrame。
        imports: import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    columns (list): List of columns to select.
        label: 选择列
        widget: column-selector
        priority: critical
    
    Returns:
    pandas.DataFrame: DataFrame with selected columns.
    """
    result = df.copy()
    
    # Check if columns exist
    missing_cols = [c for c in columns if c not in result.columns]
    if missing_cols:
        print(f"Error: Columns not found: {missing_cols}")
        return result
    else:
        result = result[columns]
        print(f"Selected {len(columns)} columns. Shape: {result.shape}")
        return result


def filter_rows(df, condition) -> pd.DataFrame:
    """
    Filter rows based on a condition string.

    Algorithm:
        name: 筛选行
        category: data_operation
        prompt: 请对 {VAR_NAME} 进行行筛选。根据条件 {condition} 筛选数据（例如 'age > 18'）。
        imports: import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    condition (str): Condition string (e.g., "col_a > 5 and col_b < 10").
        label: 筛选条件
        priority: critical
    
    Returns:
    pandas.DataFrame: Filtered DataFrame.
    """
    result = df.copy()
    
    try:
        result = result.query(condition)
        print(f"Filtered rows using query: '{condition}'")
        print(f"Rows remaining: {result.shape[0]}")
        return result
    except Exception as e:
        print(f"Filtering failed: {e}")
        return result


def concat_dfs(df1, df2, axis=0) -> pd.DataFrame:
    """
    Concatenate two DataFrames.

    Algorithm:
        name: 数据连接 (Concat)
        category: data_operation
        prompt: 请连接两个 DataFrame {df1} 和 {df2}。沿轴 {axis} 进行连接。
        imports: import pandas as pd
    
    Parameters:
    df1 (pandas.DataFrame): First DataFrame.
        role: input
    df2 (pandas.DataFrame): Second DataFrame.
        role: input
    axis (int): Concatenation axis (0=rows, 1=columns).
        label: 轴向
        priority: critical
    
    Returns:
    pandas.DataFrame: Concatenated DataFrame.
    """
    try:
        result = pd.concat([df1, df2], axis=axis)
        print(f"Concatenated DataFrames along axis {axis}.")
        print(f"New shape: {result.shape}")
        return result
    except Exception as e:
        print(f"Concat failed: {e}")
        return df1


def rename_columns(df, columns_map) -> pd.DataFrame:
    """
    Rename columns in a DataFrame.

    Algorithm:
        name: 重命名列
        category: data_operation
        prompt: 请对 {VAR_NAME} 的列进行重命名。使用映射关系 {columns_map}。
        imports: import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    columns_map (dict): Dictionary mapping old column names to new names.
        label: 列名映射
        type: dict
        priority: critical
    
    Returns:
    pandas.DataFrame: DataFrame with renamed columns.
    """
    result = df.copy()
    
    try:
        result = result.rename(columns=columns_map)
        print(f"Renamed columns using map: {columns_map}")
        return result
    except Exception as e:
        print(f"Renaming failed: {e}")
        return result


def fill_na(df, value=None, method=None) -> pd.DataFrame:
    """
    Fill missing values in a DataFrame.

    Algorithm:
        name: 填充缺失值
        category: data_operation
        prompt: 请对 {VAR_NAME} 填充缺失值。使用值 {value} 或方法 {method} 进行填充。
        imports: import pandas as pd, import numpy as np
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    value (any): Value to use for filling missing values.
        label: 填充值
        priority: non-critical
    method (str): Method to use for filling missing values (ffill, bfill).
        label: 填充方法
        options: ["ffill", "bfill"]
        priority: non-critical
    
    Returns:
    pandas.DataFrame: DataFrame with filled missing values.
    """
    result = df.copy()
    
    try:
        if value is not None:
            result = result.fillna(value=value)
            print(f"Filled NA with value: {value}")
        elif method:
            result = result.fillna(method=method)
            print(f"Filled NA with method: {method}")
        else:
            print("Warning: No value or method specified for fillna.")
        
        return result
    except Exception as e:
        print(f"Fill NA failed: {e}")
        return result


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


def merge_dfs(left, right, how="inner", on=None) -> pd.DataFrame:
    """
    Merge two DataFrames.

    Algorithm:
        name: 数据合并 (Merge)
        category: data_operation
        prompt: 请合并两个数据框 {left} 和 {right}。根据指定的合并方式（inner, outer, left, right）和连接键进行 pd.merge 操作。
        imports: import pandas as pd
    
    Parameters:
    left (pandas.DataFrame): Left DataFrame.
        role: input
    right (pandas.DataFrame): Right DataFrame.
        role: input
    how (str): Merge method (inner, outer, left, right).
        label: 合并方式
        options: ["inner", "outer", "left", "right"]
        priority: critical
    on (str): Column to merge on.
        label: 合并列
        widget: column-selector
        priority: non-critical
    
    Returns:
    pandas.DataFrame: Merged DataFrame.
    """
    try:
        if on:
            result = pd.merge(left, right, how=how, on=on)
        else:
            # Merge on index if no column specified
            result = pd.merge(left, right, how=how, left_index=True, right_index=True)
        
        print(f"Merged DataFrames using {how} join.")
        print(f"New shape: {result.shape}")
        return result
    except Exception as e:
        print(f"Merge failed: {e}")
        return left

# Alias for backward compatibility or ID matching
window_calculation = rolling_window
