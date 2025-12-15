import pandas as pd
from typing import Optional

def calculate_basic_statistics(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    计算卫星电源遥测参数的基本统计量。
    
    Algorithm:
        name: 遥测参数基本统计
        category: eda
        prompt: 对卫星电源遥测数据表 {df} 计算每个参数的最大值、最小值、最频值、均值和方差。
    
    Parameters:
    df (pd.DataFrame): 输入数据集
        role: input
    
    Returns:
    stats_df (pd.DataFrame): 统计结果数据表，包含每个参数的max、min、mode、mean、variance.
    """
    # 定义要分析的数值列，排除'timestamp'和'system_status'
    numeric_columns = [
        'solar_panel_1_voltage', 'solar_panel_1_current',
        'solar_panel_2_voltage', 'solar_panel_2_current',
        'battery_voltage', 'battery_current',
        'battery_temperature', 'power_consumption',
        'power_generation'
    ]

    # 初始化一个字典来存储每个参数的统计结果
    statistics_summary = {}

    # 对每个数值列进行计算
    for col in numeric_columns:
        # 获取列数据
        data_series = df[col]
        
        # 计算最大值
        max_val = data_series.max()
        # 计算最小值
        min_val = data_series.min()
        # 计算最频值（众数），返回第一个众数
        mode_val = data_series.mode().iloc[0] if not data_series.mode().empty else np.nan
        # 计算均值
        mean_val = data_series.mean()
        # 计算方差
        variance_val = data_series.var()
        
        # 将结果存入字典
        statistics_summary[col] = {
            'max': max_val,
            'min': min_val,
            'mode': mode_val,
            'mean': mean_val,
            'variance': variance_val
        }

    # 将统计结果转换为DataFrame以便于查看
    stats_df = pd.DataFrame(statistics_summary).T
    stats_df = stats_df[['max', 'min', 'mode', 'mean', 'variance']]  # 调整列顺序
    
    return stats_df
