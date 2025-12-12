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
