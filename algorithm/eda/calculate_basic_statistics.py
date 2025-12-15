import pandas as pd
import numpy as np
from typing import Optional

# 增加更多统计指标
def calculate_basic_statistics(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    计算卫星电源遥测参数的基本统计量。
    
    Algorithm:
        name: 遥测参数基本统计
        category: eda
        prompt: 对卫星电源遥测数据表 {df} 计算每个参数的最大值、最小值、最频值、均值、方差和中位数。
    
    Parameters:
    df (pd.DataFrame): 输入数据集
        role: input
    
    Returns:
    stats_df (pd.DataFrame): 统计结果数据表，包含每个参数的max、min、mode、mean、variance、median.
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
        # 计算中位数
        median_val = data_series.median()
        
        # 新增统计指标
        # 计算标准差
        std_val = data_series.std()
        # 计算变异系数（标准差/均值），避免除零错误
        cv_val = std_val / mean_val if mean_val != 0 else np.nan
        # 计算四分位数
        q1_val = data_series.quantile(0.25)
        q3_val = data_series.quantile(0.75)
        # 计算四分位距
        iqr_val = q3_val - q1_val
        # 计算偏度
        skew_val = data_series.skew()
        # 计算峰度
        kurt_val = data_series.kurtosis()
        # 计算极差
        range_val = max_val - min_val
        # 计算非缺失值数量
        count_val = data_series.count()
        # 计算缺失值数量
        missing_val = data_series.isnull().sum()
        # 计算缺失值比例
        missing_pct = missing_val / len(data_series) * 100
        
        # 将结果存入字典
        statistics_summary[col] = {
            'max': max_val,
            'min': min_val,
            'mode': mode_val,
            'mean': mean_val,
            'variance': variance_val,
            'median': median_val,
            'std': std_val,
            'cv': cv_val,
            'q1': q1_val,
            'q3': q3_val,
            'iqr': iqr_val,
            'skewness': skew_val,
            'kurtosis': kurt_val,
            'range': range_val,
            'count': count_val,
            'missing': missing_val,
            'missing_pct': missing_pct
        }

    # 将统计结果转换为DataFrame以便于查看
    stats_df = pd.DataFrame(statistics_summary).T
    # 调整列顺序，将核心指标放在前面
    core_columns = ['max', 'min', 'mode', 'mean', 'variance', 'median', 'std', 'cv']
    other_columns = ['q1', 'q3', 'iqr', 'skewness', 'kurtosis', 'range', 'count', 'missing', 'missing_pct']
    stats_df = stats_df[core_columns + other_columns]
    
    return stats_df
