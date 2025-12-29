"""
统计数据处理器
负责统计计算和数据预处理
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any, Tuple
from functools import lru_cache

from .utils import calculate_basic_statistics, detect_outliers


class StatisticsDataProcessor:
    """统计数据处理器"""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._stats_cache: Dict[str, Dict] = {}
        self._clear_cache()

    def _clear_cache(self):
        """清空统计缓存"""
        self._stats_cache.clear()

    def get_numeric_columns(self) -> List[str]:
        """获取数值列"""
        return self.df.select_dtypes(include=['number']).columns.tolist()

    def calculate_basic_statistics(self, columns: List[str]) -> pd.DataFrame:
        """计算基础统计量"""
        if not columns:
            return pd.DataFrame()

        stats_data = {}
        for col in columns:
            if col in self.df.columns:
                stats_data[col] = calculate_basic_statistics(self.df[col])

        return pd.DataFrame(stats_data)

    @lru_cache(maxsize=32)
    def get_column_statistics(self, column: str) -> Dict[str, Any]:
        """获取单列统计信息（带缓存）"""
        if column not in self.df.columns:
            return {}

        return calculate_basic_statistics(self.df[column])

    def calculate_correlation_matrix(self, columns: List[str]) -> pd.DataFrame:
        """计算相关系数矩阵"""
        if len(columns) < 2:
            return pd.DataFrame()

        numeric_cols = [col for col in columns if col in self.df.columns and self.df[col].dtype in ['int64', 'float64']]
        if len(numeric_cols) < 2:
            return pd.DataFrame()

        return self.df[numeric_cols].corr()

    def detect_outliers_iqr(self, column: str, multiplier: float = 1.5) -> Tuple[pd.Series, pd.Series]:
        """IQR方法检测异常值"""
        if column not in self.df.columns:
            return pd.Series(), pd.Series()

        return detect_outliers(self.df[column], method='iqr', multiplier=multiplier)

    def get_histogram_data(self, column: str, bins: int = 30) -> Tuple[np.ndarray, np.ndarray]:
        """获取直方图数据"""
        if column not in self.df.columns:
            return np.array([]), np.array([])

        clean_data = self.df[column].dropna()
        if len(clean_data) == 0:
            return np.array([]), np.array([])

        hist, bin_edges = np.histogram(clean_data, bins=bins)
        return hist, bin_edges

    def get_density_data(self, column: str, points: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """获取密度估计数据"""
        if column not in self.df.columns:
            return np.array([]), np.array([])

        clean_data = self.df[column].dropna()
        if len(clean_data) == 0:
            return np.array([]), np.array([])

        try:
            from scipy.stats import gaussian_kde
            kde = gaussian_kde(clean_data)
            x_range = np.linspace(clean_data.min(), clean_data.max(), points)
            density = kde(x_range)
            return x_range, density
        except ImportError:
            # 如果没有scipy，使用简单的直方图近似
            hist, bin_edges = self.get_histogram_data(column, bins=50)
            if len(hist) == 0:
                return np.array([]), np.array([])

            # 计算直方图密度
            bin_width = bin_edges[1] - bin_edges[0]
            density = hist / (len(clean_data) * bin_width)
            x_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            return x_centers, density

    def prepare_boxplot_data(self, columns: List[str]) -> List[Dict[str, Any]]:
        """准备箱线图数据"""
        boxplot_data = []

        for col in columns:
            if col not in self.df.columns:
                continue

            clean_data = self.df[col].dropna()
            if len(clean_data) == 0:
                continue

            # 计算箱线图统计量
            q1 = clean_data.quantile(0.25)
            median = clean_data.median()
            q3 = clean_data.quantile(0.75)
            iqr = q3 - q1
            lower_whisker = clean_data[clean_data >= q1 - 1.5 * iqr].min()
            upper_whisker = clean_data[clean_data <= q3 + 1.5 * iqr].max()

            # 检测异常值
            outliers = clean_data[(clean_data < lower_whisker) | (clean_data > upper_whisker)]

            boxplot_data.append({
                'column': col,
                'q1': q1,
                'median': median,
                'q3': q3,
                'whisker_low': lower_whisker,
                'whisker_high': upper_whisker,
                'outliers': outliers.tolist(),
                'data': clean_data.tolist()
            })

        return boxplot_data

    def prepare_scatter_data(self, x_column: str, y_column: str, sample_size: Optional[int] = None) -> Dict[str, Any]:
        """准备散点图数据"""
        if x_column not in self.df.columns or y_column not in self.df.columns:
            return {}

        # 获取数据
        x_data = self.df[x_column]
        y_data = self.df[y_column]

        # 移除缺失值
        valid_mask = x_data.notna() & y_data.notna()
        x_clean = x_data[valid_mask]
        y_clean = y_data[valid_mask]

        if len(x_clean) == 0:
            return {}

        # 采样（如果指定了样本大小）
        if sample_size and len(x_clean) > sample_size:
            sample_indices = np.random.choice(len(x_clean), size=sample_size, replace=False)
            x_clean = x_clean.iloc[sample_indices]
            y_clean = y_clean.iloc[sample_indices]

        # 计算相关系数
        try:
            correlation = x_clean.corr(y_clean)
        except:
            correlation = None

        # 计算线性回归线（如果可能）
        try:
            from scipy.stats import linregress
            slope, intercept, r_value, p_value, std_err = linregress(x_clean, y_clean)
            x_range = np.linspace(x_clean.min(), x_clean.max(), 100)
            y_regression = slope * x_range + intercept
        except ImportError:
            x_range = np.array([])
            y_regression = np.array([])
            slope = intercept = r_value = p_value = std_err = None

        return {
            'x': x_clean.tolist(),
            'y': y_clean.tolist(),
            'correlation': correlation,
            'regression_x': x_range.tolist() if len(x_range) > 0 else [],
            'regression_y': y_regression.tolist() if len(y_regression) > 0 else [],
            'slope': slope,
            'intercept': intercept,
            'r_value': r_value,
            'p_value': p_value
        }

    def get_data_summary(self, columns: List[str]) -> Dict[str, Any]:
        """获取数据汇总信息"""
        summary = {
            'total_rows': len(self.df),
            'selected_columns': len(columns),
            'numeric_columns': len(self.get_numeric_columns()),
            'datetime_columns': len(self.df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns),
            'object_columns': len(self.df.select_dtypes(include=['object']).columns),
            'missing_data': {}
        }

        # 计算每列的缺失数据比例
        for col in columns:
            if col in self.df.columns:
                missing_ratio = self.df[col].isna().sum() / len(self.df)
                summary['missing_data'][col] = {
                    'count': self.df[col].isna().sum(),
                    'ratio': missing_ratio
                }

        return summary
