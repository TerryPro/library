import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Optional, Dict, Any

def violin_plot(df: pd.DataFrame, y_columns: List[str] = None, layout: str = "子图", 
                title: str = "小提琴图", xlabel: str = "", ylabel: str = "", 
                figsize: tuple = None) -> None:
    """
    Create violin plot for the given DataFrame.

    Algorithm:
        name: 小提琴图显示
        category: plotting
        prompt: 请对 {VAR_NAME} 绘制小提琴图，展示数据分布特征。支持自定义颜色、带宽等设置。
        imports: import pandas as pd, import matplotlib.pyplot as plt, import seaborn as sns
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    y_columns (list): 要绘制小提琴图的列 (留空则绘制所有数值列)
        label: Y轴列名
        widget: column-selector
        priority: critical
    layout (str): 选择图表的排布方式：子图（每行4个）或所有数据显示在一张图
        label: 排布方式
        options: ["子图", "一张图"]
        priority: non-critical
    title (str): 小提琴图的标题
        label: 图表标题
        priority: non-critical
    xlabel (str): X轴的显示标签
        label: X轴标签
        priority: non-critical
    ylabel (str): Y轴的显示标签
        label: Y轴标签
        priority: non-critical
    figsize (tuple): 图像大小元组，例如 (15, 8)
        label: 图像尺寸
        priority: non-critical
    
    Returns:
    None
    """
    # Determine Y columns
    if not y_columns:
        y_columns = df.select_dtypes(include=['number']).columns.tolist()
    
    # Set default figsize
    if figsize is None:
        figsize = (15, 8)
    
    # Filter to selected columns
    plot_data = df[y_columns].copy()
    
    # Create violin plot
    if len(y_columns) == 1:
        # Single column
        plt.figure(figsize=figsize)
        sns.violinplot(data=plot_data[y_columns[0]].dropna())
        plt.title(f"Violin Plot of {y_columns[0]}")
        plt.xticks([0], y_columns)
    else:
        if layout == "一张图":
            # Multiple columns on one plot
            plt.figure(figsize=figsize)
            for col in y_columns:
                sns.violinplot(data=plot_data[col].dropna(), alpha=0.5, label=col)
            plt.title("Violin Plot of Multiple Columns")
            plt.legend()
        else:
            # Grid subplots
            n_cols = 4
            n_rows = (len(y_columns) + n_cols - 1) // n_cols
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(figsize[0]*n_cols/2, figsize[1]*n_rows))
            axes = axes.flatten()
            
            for i, col in enumerate(y_columns):
                sns.violinplot(data=plot_data[col].dropna(), ax=axes[i])
                axes[i].set_title(f"Violin Plot of {col}")
                axes[i].tick_params(axis='x', rotation=45)
            
            # Hide unused axes
            for i in range(len(y_columns), len(axes)):
                axes[i].axis('off')
    
    # Set labels
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    
    plt.tight_layout()
    plt.show()
