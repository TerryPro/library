import pandas as pd

def filter_rows(df: pd.DataFrame, condition: str) -> pd.DataFrame:
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
