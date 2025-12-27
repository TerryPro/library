"""
常量定义
"""

# 默认颜色列表
DEFAULT_COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]

# 重采样选项
RESAMPLE_OPTIONS = [
    ('无重采样', None),
    ('按分钟聚合', '1min'),
    ('按5分钟聚合', '5min'),
    ('按15分钟聚合', '15min'),
    ('按小时聚合', '1H'),
    ('按6小时聚合', '6H'),
    ('按日聚合', '1D'),
    ('按周聚合', '1W'),
    ('按月聚合', '1M')
]

# 显示模式选项
LAYOUT_MODE_OPTIONS = [
    ('叠加模式', 'overlay'),
    ('分栏模式', 'split')
]

# 默认参数
DEFAULT_TITLE = "动态趋势图"
DEFAULT_FIGSIZE = (16, 8)
DEFAULT_SMOOTH_WINDOW = 5
