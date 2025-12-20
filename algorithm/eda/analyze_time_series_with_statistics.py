
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional

def analyze_time_series_with_statistics(df: pd.DataFrame) -> None:
    """
    分析时间序列数据并显示曲线图和统计表格
    
    Algorithm:
        name: 时序数据分析与统计
        category: eda
        prompt: 对 {VAR_NAME} 进行时间序列分析，绘制各参数曲线并显示统计表格
        imports: import pandas as pd, import matplotlib.pyplot as plt
    
    Parameters:
    df (pd.DataFrame): 输入数据表.
        role: input
        priority: critical
    
    Returns:
    None
    """
    if df is None:
        return
    
    # 设置中文显示
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    def create_statistics_table(data: pd.Series) -> pd.DataFrame:
        """创建统计信息表格"""
        stats_dict = {
            '统计量': ['样本数量', '缺失值数量', '平均值', '标准差', '最小值', 
                      '25%分位数', '中位数', '75%分位数', '最大值', '偏度', '峰度'],
            '值': [
                f"{len(data):,}",
                f"{data.isnull().sum()}",
                f"{data.mean():.4f}",
                f"{data.std():.4f}",
                f"{data.min():.4f}",
                f"{data.quantile(0.25):.4f}",
                f"{data.median():.4f}",
                f"{data.quantile(0.75):.4f}",
                f"{data.max():.4f}",
                f"{data.skew():.4f}",
                f"{data.kurtosis():.4f}"
            ]
        }
        
        data_range = data.max() - data.min()
        stats_dict['统计量'].extend(['数据范围', '变异系数', '异常值数量'])
        
        cv_value = data.std() / abs(data.mean()) if abs(data.mean()) > 1e-10 else 'N/A'
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        
        stats_dict['值'].extend([
            f"{data_range:.4f}",
            f"{cv_value:.4f}" if isinstance(cv_value, float) else cv_value,
            f"{len(outliers)}"
        ])
        
        return pd.DataFrame(stats_dict)
    
    def plot_table_on_axis(ax, table_df: pd.DataFrame) -> None:
        """在坐标轴上绘制表格"""
        ax.axis('off')
        table = ax.table(
            cellText=table_df.values,
            colLabels=table_df.columns,
            cellLoc='center',
            loc='center',
            colWidths=[0.4, 0.6]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        
        for i in range(len(table_df.columns)):
            cell = table[(0, i)]
            cell.set_facecolor('#4F81BD')
            cell.set_text_props(weight='bold', color='white')
        
        for i in range(1, len(table_df) + 1):
            for j in range(len(table_df.columns)):
                cell = table[(i, j)]
                cell.set_facecolor('#F2F2F2' if i % 2 == 0 else '#FFFFFF')
        
        for key, cell in table.get_celld().items():
            cell.set_linewidth(0.5)
            cell.set_edgecolor('#D0D0D0')
    
    parameters = df.columns.tolist()
    n_params = len(parameters)
    
    fig_width = 20
    fig_height = 6 * n_params
    
    fig = plt.figure(figsize=(fig_width, fig_height))
    gs = fig.add_gridspec(n_params, 2, width_ratios=[1.8, 1.2], wspace=0.1, hspace=0.3)
    
    axes = []
    for i in range(n_params):
        ax_left = fig.add_subplot(gs[i, 0])
        ax_right = fig.add_subplot(gs[i, 1])
        axes.append([ax_left, ax_right])
        
        for ax in [ax_left, ax_right]:
            for spine in ax.spines.values():
                spine.set_linewidth(1.5)
                spine.set_color('#333333')
    
    for i, param in enumerate(parameters):
        data = df[param].dropna()
        
        ax_left, ax_right = axes[i]
        ax_left.plot(data.index, data.values, linewidth=1.5, color='steelblue')
        ax_left.set_title(f'{param}', fontsize=12, fontweight='bold')
        ax_left.set_ylabel(param)
        ax_left.grid(True, alpha=0.3)
        
        stats_table = create_statistics_table(df[param])
        plot_table_on_axis(ax_right, stats_table)
    
    plt.show()