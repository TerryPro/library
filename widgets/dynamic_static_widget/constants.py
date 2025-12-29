"""
动态统计分析组件常量定义
"""

# 默认颜色列表
DEFAULT_COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]

# 图表类型选项
CHART_TYPE_OPTIONS = [
    ('统计汇总表', 'summary'),
    ('箱线图', 'boxplot'),
    ('直方图', 'histogram'),
    ('密度图', 'density'),
]

# 统计指标名称映射
STATISTICS_LABELS = {
    'count': '样本数量',
    'mean': '均值',
    'std': '标准差',
    'min': '最小值',
    'max': '最大值',
    'median': '中位数',
    'q25': 'Q1 (25%)',
    'q75': 'Q3 (75%)',
    'skewness': '偏度',
    'kurtosis': '峰度',
    'missing': '缺失值'
}

# 图表尺寸选项
FIGSIZE_OPTIONS = [
    ('标准 (12x8)', (12, 8)),
    ('宽屏 (16x10)', (16, 10)),
    ('大屏 (20x12)', (20, 12))
]

# 默认参数
DEFAULT_TITLE = "动态统计分析"
DEFAULT_FIGSIZE = (16, 10)
DEFAULT_CHART_TYPE = 'summary'

# 直方图参数
DEFAULT_HIST_BINS = 30

# 散点图相关参数
DEFAULT_SCATTER_SIZE = 8
