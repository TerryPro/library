# Auto-generated library init
from .anomaly_detection import *
from .data_operation import *
from .data_preprocessing import *
from .eda import *
from .load_data import *
from .plotting import *
from .trend_plot import *

CATEGORY_LABELS = {'load_data': '输入输出', 'data_operation': '数据操作', 'data_preprocessing': '数据预处理', 'eda': '探索式分析', 'anomaly_detection': '异常检测', 'trend_plot': '趋势绘制', 'plotting': '数据绘图'}

# Backward compatibility: make widgets accessible via algorithm.widgets
import sys
import os
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Import widgets module and attach it to algorithm namespace
import widgets as _widgets_module
sys.modules['algorithm.widgets'] = _widgets_module
