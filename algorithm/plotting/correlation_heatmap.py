import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Optional, Dict, Any

def correlation_heatmap(df: pd.DataFrame, method: str = "pearson", title: str = "相关性热力图", 
                        figsize: tuple = None, annot: bool = True, cmap: str = "coolwarm") -> None:
    """
    Create correlation heatmap for the given DataFrame.

    Algorithm:
        name: 相关性热力图
        category: plotting
        prompt: 请对 {VAR_NAME} 进行相关性分析。使用seaborn的heatmap函数，绘制各列之间的相关性热力图。
        imports: import pandas as pd, import matplotlib.pyplot as plt, import seaborn as sns
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    method (str): 计算相关系数的方法
        label: 相关系数方法
        options: ["pearson", "kendall", "spearman"]
        priority: non-critical
    title (str): 图表的标题
        label: 图表标题
        priority: non-critical
    figsize (tuple): 图像大小元组，例如 (15, 8)
        label: 图像尺寸
        priority: non-critical
    annot (bool): 是否在热力图上显示相关系数数值
        label: 显示数值
        priority: non-critical
    cmap (str): 热力图的颜色映射方案
        label: 颜色映射
        priority: non-critical
    
    Returns:
    None
    """
    # Calculate correlation matrix
    numeric_data = df.select_dtypes(include=['number'])
    corr_matrix = numeric_data.corr(method=method)
    
    # Set default figsize
    if figsize is None:
        figsize = (15, 8)
    
    # Create heatmap
    plt.figure(figsize=figsize)
    sns.heatmap(corr_matrix, annot=annot, cmap=cmap, fmt='.2f', linewidths=0.5)
    plt.title(title)
    plt.tight_layout()
    plt.show()
