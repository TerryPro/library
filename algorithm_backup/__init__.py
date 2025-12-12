# 从各个子模块导入所有算法函数
from .data_loading import *
from .data_operation import *
from .data_preprocessing import *
from .eda import *
from .anomaly_detection import *
from .trend import *
from .plotting import *

# 定义算法分类标签
CATEGORY_LABELS = {
    "load_data": "输入输出",
    "data_operation": "数据操作",
    "data_preprocessing": "数据预处理",
    "eda": "探索式分析",
    "anomaly_detection": "异常检测",
    "trend_plot": "趋势绘制",
    "数据绘图": "数据绘图"
}
