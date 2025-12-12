import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.seasonal import STL
import mplfinance.original_flavor as mpf

def trend_polyfit(df: pd.DataFrame, y_columns: list = None, degree: int = 2, title: str = "多项式趋势拟合图", figsize: tuple = None) -> None:
    """
    Plot polynomial trend fit for a DataFrame.

    Algorithm:
        name: 多项式趋势拟合
        category: trend_plot
        prompt: 请对{VAR_NAME} 进行多项式趋势拟合并绘制趋势。使用 numpy.polyfit 对指定阶数进行拟合，绘制拟合曲线与原始数据，并计算与输出拟合优度（R²）。
        imports: import numpy as np, import matplotlib.pyplot as plt, import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    y_columns (list): Columns to perform polynomial fitting on.
        label: Y轴列名
        widget: column-selector
        priority: critical
    degree (int): Polynomial degree.
        label: 多项式阶数
        min: 1
        max: 5
        priority: critical
    title (str): Chart title.
        label: 图表标题
        priority: non-critical
    figsize (tuple): Figure size tuple.
        label: 图像尺寸
        priority: non-critical
    
    Returns:
    None
    """
    result = df.copy()
    
    if y_columns is None:
        y_columns = []
    
    # Parse figsize
    if figsize is None:
        figsize = (15, 8)
    elif isinstance(figsize, str):
        try:
            figsize = eval(figsize)
        except:
            figsize = (15, 8)
    
    # Determine Y columns
    if not y_columns:
        # Use all numeric columns if none specified
        y_columns = result.select_dtypes(include=['number']).columns.tolist()
    
    # Set Chinese font support
    plt.rcParams['font.sans-serif'] = ['SimHei']  # Use SimHei for Chinese
    plt.rcParams['axes.unicode_minus'] = False   # Fix minus sign display
    
    # Filter to selected columns
    poly_data = result[y_columns].dropna().copy()
    
    # Plot polynomial fit for each column
    for col in y_columns:
        # Prepare data
        y = poly_data[col].values
        x = np.arange(len(y))

        # Fit polynomial
        coefs = np.polyfit(x, y, deg=degree)
        trend_poly = np.polyval(coefs, x)
        
        # Calculate R-squared
        ss_res = np.sum((y - trend_poly) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        # Create plot
        plt.figure(figsize=figsize)
        plt.plot(poly_data.index, y, label='原始数据', alpha=0.4)
        plt.plot(poly_data.index, trend_poly, label=f'{degree}阶多项式拟合 (R²={r_squared:.4f})', linewidth=2, color='purple')
        
        plt.title(f"多项式趋势拟合: {col}" if title == "多项式趋势拟合图" else title)
        plt.xlabel('时间' if isinstance(poly_data.index, pd.DatetimeIndex) else '索引')
        plt.ylabel(col)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()
        
        # Print R-squared
        print(f"{col} 的 {degree}阶多项式拟合优度 R² = {r_squared:.4f}")
