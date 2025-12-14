import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Optional, Dict, Any

def box_plot(df: pd.DataFrame, y_columns: List[str] = None, group_by: str = "", layout: str = "子图", 
             title: str = "箱型图", xlabel: str = "", ylabel: str = "", 
             show_outliers: bool = True, figsize: tuple = None) -> None:
    """
    Create box plot for the given DataFrame.

    Algorithm:
        name: 箱型图绘制
        category: plotting
        prompt: 请对 {VAR_NAME} 绘制箱型图，展示数据分布特征。支持单变量、多变量和分组箱型图。

    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    y_columns (list): 要绘制箱型图的列 (留空则绘制所有数值列)
        label: Y轴列名
        widget: column-selector
        priority: critical
    group_by (str): 用于分组的列名 (可选)
        label: 分组列
        widget: column-selector
        priority: non-critical
    layout (str): 选择图表的排布方式：子图（每行4个）或所有数据显示在一张图
        label: 排布方式
        widget: select
        options: ["子图", "一张图"]
        priority: non-critical
    title (str): 图表的标题
        label: 图表标题
        priority: non-critical
    xlabel (str): X轴的显示标签
        label: X轴标签
        priority: non-critical
    ylabel (str): Y轴的显示标签
        label: Y轴标签
        priority: non-critical
    show_outliers (bool): 是否在箱型图中显示异常值
        label: 显示异常值
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
    
    # Add group column if specified
    if group_by and group_by in df.columns:
        plot_data[group_by] = df[group_by]
    
    # Create box plot
    if len(y_columns) == 1:
        # Single column
        plt.figure(figsize=figsize)
        if group_by:
            sns.boxplot(x=group_by, y=y_columns[0], data=plot_data, showfliers=show_outliers)
            plt.title(f"Box Plot of {y_columns[0]} by {group_by}")
        else:
            plt.boxplot(plot_data[y_columns[0]].dropna(), showfliers=show_outliers)
            plt.title(f"Box Plot of {y_columns[0]}")
            plt.xticks([1], y_columns)
    else:
        if layout == "一张图":
            # Multiple columns on one plot
            plt.figure(figsize=figsize)
            if group_by:
                for i, col in enumerate(y_columns):
                    sns.boxplot(x=group_by, y=col, data=plot_data, showfliers=show_outliers, alpha=0.7, label=col)
                plt.title(f"Box Plots of Multiple Columns by {group_by}")
            else:
                for col in y_columns:
                    sns.boxplot(data=plot_data[col].dropna(), showfliers=show_outliers, alpha=0.5, label=col)
                plt.title("Box Plot of Multiple Columns")
            plt.legend()
        else:
            # Grid subplots
            n_cols = 4
            n_rows = (len(y_columns) + n_cols - 1) // n_cols
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(figsize[0]*n_cols/2, figsize[1]*n_rows))
            axes = axes.flatten()
            
            for i, col in enumerate(y_columns):
                if group_by:
                    sns.boxplot(x=group_by, y=col, data=plot_data, ax=axes[i], showfliers=show_outliers)
                    axes[i].set_title(f"Box Plot of {col} by {group_by}")
                else:
                    axes[i].boxplot(plot_data[col].dropna(), showfliers=show_outliers)
                    axes[i].set_title(f"Box Plot of {col}")
                    axes[i].set_xticklabels([col])
                axes[i].tick_params(axis='x', rotation=45)
            
            # Hide unused axes
            for i in range(len(y_columns), len(axes)):
                axes[i].axis('off')
    
    # Set labels
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
