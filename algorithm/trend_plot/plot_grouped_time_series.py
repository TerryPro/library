import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional

def plot_grouped_time_series(df: pd.DataFrame, timestamp_col: str = 'timestamp', variable_groups: Optional[dict] = None, show_stats: bool = False) -> None:
    """
    将时间序列数据按逻辑分组绘制分栏曲线图
    
    Algorithm:
        name: 分组时间序列图
        category: trend_plot
        prompt: 对 {VAR_NAME} 绘制分组时间序列图，按变量组显示曲线
        imports: import pandas as pd, import matplotlib.pyplot as plt
    
    Parameters:
    df (pd.DataFrame): 包含时间序列数据的输入数据表.
        role: input
    timestamp_col (str): 时间戳列名.
        label: 时间戳列
        widget: column-selector
        priority: non-critical
        role: parameter
    variable_groups (dict): 变量分组字典，格式为{'组名': ['列名1', '列名2']}.
        label: 变量分组
        widget: input
        priority: non-critical
        role: parameter
    show_stats (bool): 是否显示基本统计信息.
        label: 显示统计信息
        widget: checkbox
        priority: non-critical
        role: parameter
    
    Returns:
    None
    """
    if df is None or df.empty:
        print("输入数据为空")
        return
    
    # 复制数据以避免修改原始数据
    df_copy = df.copy()
    
    # 确保时间戳列被正确解析为datetime类型
    if timestamp_col in df_copy.columns:
        df_copy[timestamp_col] = pd.to_datetime(df_copy[timestamp_col])
    
    # 设置默认变量分组：如果variable_groups为空，则使用所有列（排除时间戳列）
    if variable_groups is None:
        # 获取所有数值列（排除时间戳列）
        numeric_columns = df_copy.select_dtypes(include=['float64', 'int64']).columns.tolist()
        # 移除时间戳列（如果它是数值类型）
        if timestamp_col in numeric_columns:
            numeric_columns.remove(timestamp_col)
        
        # 如果没有数值列，则使用所有非时间戳列
        if not numeric_columns:
            all_columns = df_copy.columns.tolist()
            if timestamp_col in all_columns:
                all_columns.remove(timestamp_col)
            numeric_columns = all_columns
        
        # 将所有数值列放入一个分组
        variable_groups = {'All Variables': numeric_columns}
    
    # 过滤掉数据中不存在的列
    filtered_groups = {}
    for group_name, variables in variable_groups.items():
        existing_vars = [var for var in variables if var in df_copy.columns]
        if existing_vars:
            filtered_groups[group_name] = existing_vars
    
    if not filtered_groups:
        print("没有找到有效的变量进行绘图")
        return
    
    # 设置绘图风格
    plt.rcParams['figure.figsize'] = [15, 10]
    
    # 创建分栏子图
    fig, axes = plt.subplots(len(filtered_groups), 1, figsize=(15, 4 * len(filtered_groups)))
    fig.suptitle('Satellite Power Telemetry Time Series Analysis', fontsize=16, y=1.02)
    
    # 如果只有一个子图，确保axes是列表
    if len(filtered_groups) == 1:
        axes = [axes]
    
    # 为每个变量组绘制曲线
    for ax, (group_name, variables) in zip(axes, filtered_groups.items()):
        for var in variables:
            if var in df_copy.columns:
                ax.plot(df_copy[timestamp_col], df_copy[var], label=var, linewidth=1.5)
        
        ax.set_title(f'{group_name} Metrics', fontsize=12)
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Value')
        ax.legend(loc='upper right', fontsize='small')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # 可选：计算并打印每组变量的基本统计信息
    if show_stats:
        print("Basic Statistics for Each Variable Group:")
        print("=" * 50)
        for group_name, variables in filtered_groups.items():
            print(f"\n{group_name}:")
            for var in variables:
                if var in df_copy.columns:
                    data_series = df_copy[var]
                    print(f"  {var}:")
                    print(f"    Mean: {data_series.mean():.4f}")
                    print(f"    Std:  {data_series.std():.4f}")
                    print(f"    Min:  {data_series.min():.4f}")
                    print(f"    Max:  {data_series.max():.4f}")