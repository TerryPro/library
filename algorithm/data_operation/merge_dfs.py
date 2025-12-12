import pandas as pd

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
        widget: select
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
