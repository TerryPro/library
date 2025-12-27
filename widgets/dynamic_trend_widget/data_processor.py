"""
数据处理模块
"""

import pandas as pd
from typing import List, Dict, Any, Optional


class DataProcessor:
    """数据处理器"""

    def __init__(self, df: pd.DataFrame, x_column: Optional[str] = None, is_timeseries: bool = False):
        self.df = df.copy()
        self.x_column = x_column
        self.is_timeseries = is_timeseries

        # 初始化数据处理
        self._prepare_data()

    def _prepare_data(self):
        """准备数据：转换datetime并排序"""
        if self.is_timeseries:
            # 时间序列DataFrame：确保索引是datetime类型并排序
            if not isinstance(self.df.index, pd.DatetimeIndex):
                self.df.index = pd.to_datetime(self.df.index)
            self.df = self.df.sort_index()
        elif self.x_column and self.x_column in self.df.columns:
            self.df[self.x_column] = pd.to_datetime(self.df[self.x_column])
            self.df = self.df.sort_values(self.x_column)

    def apply_data_processing(self, df: pd.DataFrame, series: List[Dict], resample_rule: Optional[str] = None) -> pd.DataFrame:
        """应用数据聚合和平滑处理"""
        processed_df = df.copy()

        # 应用重采样
        processed_df = self._apply_resampling(processed_df, resample_rule)

        # 对每个系列应用平滑
        for s in series:
            if s.get('smooth_enabled', False) and s['col'] in processed_df.columns:
                window = s.get('smooth_window', 5)
                processed_df = self._apply_smoothing(processed_df, s['col'], window)

        return processed_df

    def _apply_resampling(self, df: pd.DataFrame, resample_rule: Optional[str]) -> pd.DataFrame:
        """应用重采样"""
        if not resample_rule:
            return df

        try:
            if self.is_timeseries:
                # 时间序列DataFrame：索引已经是datetime，直接重采样
                return df.resample(resample_rule).mean()
            elif self.x_column in df.columns:
                df = df.set_index(self.x_column)
                df = df.resample(resample_rule).mean()
                df = df.reset_index()
                return df
        except Exception as e:
            print(f"重采样失败: {e}")
            return df.copy()

        return df

    def _apply_smoothing(self, df: pd.DataFrame, column: str, window: int) -> pd.DataFrame:
        """应用平滑处理"""
        try:
            # 使用滚动平均进行平滑
            df[column] = df[column].rolling(
                window=window, center=True, min_periods=1
            ).mean()
        except Exception as e:
            print(f"平滑处理失败 ({column}): {e}")

        return df
