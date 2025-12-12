import pandas as pd
import numpy as np
import ast
from typing import Tuple, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler


def interpolation_spline(df: pd.DataFrame, order: int = 3) -> pd.DataFrame:
    """
    Perform spline interpolation on a DataFrame.

    Algorithm:
        name: 样条插值
        category: data_preprocessing
        prompt: 请对{VAR_NAME} 进行样条插值 (Spline)。使用 pandas 的 interpolate(method='spline', order=3) 以获得更平滑的补全曲线。
        imports: import pandas as pd, import numpy as np
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    order (int): 样条插值的阶数
        label: 样条阶数
        min: 1
        max: 5
        priority: critical
    
    Returns:
    pandas.DataFrame: DataFrame with spline interpolation applied.
    """
    result = df.copy()
    
    # Requires numeric index (or datetime converted to numeric) for spline
    try:
        result = result.interpolate(method='spline', order=order)
    except Exception as e:
        print(f"Spline interpolation failed (index might not be compatible): {e}")
        print("Falling back to linear interpolation")
        result = result.interpolate(method='linear')
    
    print(f"Applied spline interpolation with order {order}")
    return result


def resampling_down(df: pd.DataFrame, rule: str = "1小时", agg_method: str = "均值") -> pd.DataFrame:
    """
    Downsample a DataFrame to a lower frequency.

    Algorithm:
        name: 降采样
        category: data_preprocessing
        prompt: 请对{VAR_NAME} 进行降采样聚合。使用 pandas 的 resample() 将数据聚合到更低的时间分辨率（例如 '1min' 或 '1H'）；数值列使用 mean()，状态列使用 last() 或 max()。
        imports: import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame with DatetimeIndex.
        role: input
    rule (str): 目标重采样频率
        label: 频率规则
        options: ["15秒", "30秒", "1分钟", "5分钟", "15分钟", "30分钟", "1小时"]
        priority: critical
    agg_method (str): 降采样时使用的聚合函数
        label: 聚合方法
        options: ["均值", "求和", "最小值", "最大值", "第一个值", "最后一个值", "中位数", "标准差", "方差", "计数"]
        priority: critical
    
    Returns:
    pandas.DataFrame: Downsampled DataFrame.
    """
    result = df.copy()
    
    if not isinstance(result.index, pd.DatetimeIndex):
        print("Error: Input DataFrame index is not a DatetimeIndex. Cannot resample.")
        return result
    
    # Map Chinese rule to pandas offset alias
    rule_map = {
        "15秒": "15S",
        "30秒": "30S",
        "1分钟": "1T",
        "5分钟": "5T",
        "15分钟": "15T",
        "30分钟": "30T",
        "1小时": "1H"
    }
    pandas_rule = rule_map.get(rule, rule) # Fallback to using the string directly if not in map

    # Map Chinese aggregation method to pandas function name
    agg_method_map = {
        "均值": "mean",
        "求和": "sum",
        "最小值": "min",
        "最大值": "max",
        "第一个值": "first",
        "最后一个值": "last",
        "中位数": "median",
        "标准差": "std",
        "方差": "var",
        "计数": "count"
    }
    
    agg_func = agg_method_map.get(agg_method, agg_method)
    
    # Define aggregation dictionary: use selected method for all columns
    agg_dict = {col: agg_func for col in result.columns}
            
    result = result.resample(pandas_rule).agg(agg_dict)
    print(f"Resampled to {pandas_rule} frequency. New shape: {result.shape}")
    print(f"Aggregation method: {agg_method} ({agg_func})")
    return result


def alignment(baseline_df: pd.DataFrame, other_df: pd.DataFrame) -> pd.DataFrame:
    """
    Align other_df to baseline_df using merge_asof.

    Algorithm:
        name: 多源数据对齐
        category: data_preprocessing
        prompt: 请以 {VAR_NAME} 为基准执行多源时间对齐。使用 pandas 的 merge_asof 方法，将其他数据对齐到该时间轴。
        imports: import pandas as pd
    
    Parameters:
    baseline_df (pandas.DataFrame): Baseline DataFrame with DatetimeIndex.
        role: input
    other_df (pandas.DataFrame): Other DataFrame with DatetimeIndex to align.
        role: input
    
    Returns:
    pandas.DataFrame: Aligned DataFrame.
    """
    result = baseline_df.copy()
    
    # Using merge_asof (requires sorted DatetimeIndex)
    try:
        result = pd.merge_asof(baseline_df.sort_index(), other_df.sort_index(), 
                              left_index=True, right_index=True, direction='nearest')
        print(f"Aligned DataFrame shape: {result.shape}")
    except Exception as e:
        print(f"Alignment failed: {e}")
        print("Returning baseline DataFrame.")
    
    return result


def feature_scaling(df: pd.DataFrame, method: str = "standard", with_mean: bool = True, with_std: bool = True, feature_range: str = "(0, 1)") -> pd.DataFrame:
    """
    Perform feature scaling on a DataFrame.

    Algorithm:
        name: 数据标准化/归一化
        category: data_preprocessing
        prompt: 请对 {VAR_NAME} 进行特征缩放。支持多种缩放方法，直接修改原始列。
        imports: import pandas as pd, from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    method (str): 选择缩放方法：standard（Z-score）、minmax（0-1归一化）、robust（鲁棒缩放）、maxabs（最大绝对值缩放）
        label: 缩放方法
        options: ["standard", "minmax", "robust", "maxabs"]
        priority: critical
    with_mean (bool): 对于standard和robust方法，是否减去均值
        label: 包含均值
        priority: non-critical
    with_std (bool): 对于standard方法，是否除以标准差
        label: 包含标准差
        priority: non-critical
    feature_range (str): 对于minmax方法，指定目标范围，格式为'(min, max)'
        label: 特征范围
        priority: non-critical
    
    Returns:
    pandas.DataFrame: Scaled DataFrame.
    """
    result = df.copy()
    
    # Parse feature_range string to tuple
    try:
        if isinstance(feature_range, str):
            feature_range_tuple = ast.literal_eval(feature_range)
        else:
            feature_range_tuple = feature_range
            
        if not isinstance(feature_range_tuple, tuple) or len(feature_range_tuple) != 2:
             feature_range_tuple = (0, 1)
    except:
        feature_range_tuple = (0, 1)

    # Select numeric columns only
    numeric_cols = result.select_dtypes(include=['number']).columns
    if not numeric_cols.empty:
        try:
            if method == 'standard':
                scaler = StandardScaler(with_mean=with_mean, with_std=with_std)
            elif method == 'minmax':
                scaler = MinMaxScaler(feature_range=feature_range_tuple)
            elif method == 'robust':
                scaler = RobustScaler(with_centering=with_mean, with_scaling=with_std)
            elif method == 'maxabs':
                scaler = MaxAbsScaler()
            else:
                scaler = StandardScaler()  # Fallback
            
            # Scale in-place on original columns
            result[numeric_cols] = scaler.fit_transform(result[numeric_cols])
            
            print(f"Applied {method} scaling to {len(numeric_cols)} columns")
            if method == 'standard':
                print(f"  with_mean: {with_mean}, with_std: {with_std}")
            elif method == 'minmax':
                print(f"  feature_range: {feature_range_tuple}")
            elif method == 'robust':
                print(f"  with_centering: {with_mean}, with_scaling: {with_std}")
        except Exception as e:
            print(f"Scaling failed: {e}")
    else:
        print("No numeric columns found for scaling")
    
    return result


def diff_transform(df: pd.DataFrame, order: int = 1, periods: int = 1, axis: int = 0, fill_method: str = "") -> pd.DataFrame:
    """
    Perform difference transformation on a DataFrame.

    Algorithm:
        name: 差分变换
        category: data_preprocessing
        prompt: 请对 {VAR_NAME} 进行差分变换，以消除趋势并使数据平稳。可配置差分阶数和滞后步数。
        imports: import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    order (int): 差分的阶数，1为一阶差分，2为二阶差分等
        label: 差分阶数
        min: 1
        max: 5
        step: 1
        priority: critical
    periods (int): 差分的滞后步数，默认1
        label: 滞后步数
        min: 1
        max: 10
        step: 1
        priority: critical
    axis (int): 沿哪个轴进行差分，0=行（时间轴），1=列
        label: 差分轴
        options: [0, 1]
        min: 0
        max: 1
        step: 1
        priority: non-critical
    fill_method (str): 差分后缺失值的填充方法，留空则不填充
        label: 填充方法
        options: ["", "ffill", "bfill"]
        priority: non-critical
    
    Returns:
    pandas.DataFrame: Differenced DataFrame.
    """
    result = df.select_dtypes(include=['number']).copy()
    
    # Perform difference transformation
    try:
        # Apply difference multiple times for higher orders
        for i in range(order):
            result = result.diff(periods=periods, axis=axis)
        
        # Fill missing values if specified
        if fill_method:
            result = result.fillna(method=fill_method)
            print(f"Filled missing values using {fill_method}")
        
        print(f"Applied {order}nd order difference with periods={periods} along axis={axis}")
        print(f"New shape: {result.shape}")
    except Exception as e:
        print(f"Difference transform failed: {e}")
    
    return result


def data_fill(df: pd.DataFrame, method: str = "均值", value: float = 0.0, axis: int = 0, limit: int = 0) -> pd.DataFrame:
    """
    Fill missing values in a DataFrame.

    Algorithm:
        name: 数据填充
        category: data_preprocessing
        prompt: 请对 {VAR_NAME} 进行缺失值填充。支持多种填充方法，包括均值、中位数、众数、前向填充、后向填充、常数填充等。
        imports: import pandas as pd
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame.
        role: input
    method (str): 选择缺失值填充方法
        label: 填充方法
        options: ["均值", "中位数", "众数", "前向填充", "后向填充", "常数", "线性插值", "最近邻插值"]
        priority: critical
    value (float): 当使用常数填充时，指定填充的值
        label: 填充值
        priority: non-critical
    axis (int): 沿哪个轴进行填充，0=按列填充，1=按行填充
        label: 填充轴
        options: [0, 1]
        priority: non-critical
    limit (int): 限制连续缺失值的填充数量，0表示无限制
        label: 填充限制
        min: 0
        max: 1000
        priority: non-critical
    
    Returns:
    pandas.DataFrame: DataFrame with filled missing values.
    """
    result = df.copy()
    
    # Map Chinese method name to pandas method
    method_map = {
        "均值": "mean",
        "中位数": "median",
        "众数": "mode",
        "前向填充": "ffill",
        "后向填充": "bfill",
        "常数": "constant",
        "线性插值": "linear",
        "最近邻插值": "nearest"
    }
    
    pandas_method = method_map.get(method, "mean")
    
    # Perform filling
    limit_arg = limit if limit > 0 else None

    try:
        if pandas_method == "constant":
            result = result.fillna(value=value, limit=limit_arg, axis=axis)
        elif pandas_method in ["ffill", "bfill"]:
            result = result.fillna(method=pandas_method, limit=limit_arg, axis=axis)
        elif pandas_method in ["mean", "median"]:
            # Fill numeric columns with mean/median
            for col in result.columns:
                if pd.api.types.is_numeric_dtype(result[col]):
                    fill_val = result[col].agg(pandas_method)
                    result[col] = result[col].fillna(fill_val, limit=limit_arg)
        elif pandas_method == "mode":
            # Fill with mode
            for col in result.columns:
                fill_val = result[col].mode().iloc[0] if not result[col].mode().empty else np.nan
                result[col] = result[col].fillna(fill_val, limit=limit_arg)
        else:  # Interpolation methods
            result = result.interpolate(method=pandas_method, limit=limit_arg, axis=axis)
        
        print(f"Filled missing values using '{method}' method")
        print(f"New shape: {result.shape}")
    except Exception as e:
        print(f"Data filling failed: {e}")
    
    return result
