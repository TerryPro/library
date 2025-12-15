import pandas as pd
from typing import Tuple

def split_train_test(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    将DataFrame分割为训练集和测试集。

    Algorithm:
        name: 数据集分割
        category: data_operation
        prompt: 将{VAR_NAME}按比例分割为训练集和测试集，支持随机种子设置以确保结果可重现。

    Parameters:
    df (pd.DataFrame): Input DataFrame.
        role: input
    test_size (float): 测试集比例
        label: 测试集比例
        min: 0.1
        max: 0.5
        step: 0.05
        priority: critical
    random_state (int): 随机种子
        label: 随机种子
        priority: non-critical

    Returns:
    train (pd.DataFrame): 训练集
    test (pd.DataFrame): 测试集
    """
    # Shuffle the dataframe
    df_shuffled = df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    
    # Calculate split index
    split_idx = int(len(df_shuffled) * (1 - test_size))
    
    # Split the data
    train = df_shuffled.iloc[:split_idx].copy()
    test = df_shuffled.iloc[split_idx:].copy()
    
    print(f"训练集大小: {len(train)} 行")
    print(f"测试集大小: {len(test)} 行")
    
    return train, test
