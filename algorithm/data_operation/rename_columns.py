import pandas as pd

def rename_columns(df: pd.DataFrame, columns_map: dict) -> pd.DataFrame:
    """
    Rename columns in a DataFrame.

    Algorithm:
        name: 重命名列
        category: data_operation
        prompt: 请对 {VAR_NAME} 的列进行重命名。使用映射关系 {columns_map}。

    
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
