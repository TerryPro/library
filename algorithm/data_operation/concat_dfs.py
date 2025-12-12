import pandas as pd

def concat_dfs(df1: pd.DataFrame, df2: pd.DataFrame, axis: int = 0) -> pd.DataFrame:
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
