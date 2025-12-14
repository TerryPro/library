import pandas as pd
from typing import Optional
from typing import Tuple

def first(df1: pd.DataFrame, df2: pd.DataFrame, df3: pd.DataFrame, new_param1: str, new_param2: str, new_param3: str) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    这个是用户通过前端界面创建的第一个算法。
    
    Algorithm:
        name: 第一个算法
        category: data_operation
        prompt: Perform {ALGO_NAME} on {VAR_NAME}

    
    Parameters:
    df1 (pd.DataFrame): Input DataFrame
        role: input
    df2 (pd.DataFrame): Input DataFrame
        role: input
    df3 (pd.DataFrame): Input DataFrame
        role: input
    new_param1 (str): Description
        label: 新参数
        widget: input
        priority: critical
        role: parameter
    new_param2 (str): Description
        label: 新参数
        widget: input
        priority: critical
        role: parameter
    new_param3 (str): Description
        label: 新参数
        widget: input
        priority: critical
        role: parameter
    
    Returns:
    df_out_1 (pd.DataFrame): Result
    df_out_2 (pd.DataFrame): Result
    """
    # Implementation
    return df
