import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.seasonal import STL

def data_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate data features for a DataFrame.

    Algorithm:
        name: 数据特征
        category: eda
        prompt: 请对{VAR_NAME} 进行数据特征计算。使用pandas的describe()函数，计算各列的基本统计特征。

    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    
    Returns:
    pandas.DataFrame: Original DataFrame (unchanged).
    """
    result = df.copy()
    
    print("=== 数据基本统计特征 ===")
    print()
    
    # Calculate and display describe()
    describe_result = result.describe()
    display(describe_result)
    
    print()
    print("=== 数据结构信息 ===")
    print(f"数据形状: {result.shape}")
    print(f"列名: {list(result.columns)}")
    print(f"数据类型:")
    display(result.dtypes)
    
    print()
    print("=== 缺失值统计 ===")
    missing_values = result.isnull().sum()
    missing_percentage = (result.isnull().sum() / len(result)) * 100
    missing_stats = pd.DataFrame({"缺失值数量": missing_values, "缺失值百分比(%)": missing_percentage.round(2)})
    display(missing_stats[missing_stats["缺失值数量"] > 0])
    
    if missing_stats[missing_stats["缺失值数量"] > 0].empty:
        print("无缺失值")
    
    return result
