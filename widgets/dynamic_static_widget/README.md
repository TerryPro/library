# DynamicStaticWidget - 动态统计分析组件

## 📊 概述

`DynamicStaticWidget` 是基于 `DynamicTrendWidget` 架构开发的统计分析组件，专门用于对时序数据的各个类进行全面的统计分析，并通过直观的图形化方式展示统计结果。

## 🎯 主要功能

### 支持的统计图表类型

1. **统计汇总表** - 显示各列的主要统计指标表格
2. **箱线图** - 显示数据的四分位数分布，清晰标记异常值
3. **直方图** - 数据分布频率可视化，支持自定义分组
4. **密度图** - 数据的概率密度函数估计
5. **散点图** - 用于两个变量的相关性分析，支持回归线

### 核心特性

- **交互式参数选择**: 动态选择要分析的数值列
- **多种图表类型**: 一键切换不同的统计图表视图
- **实时更新**: 参数变化时图表即时刷新
- **数据质量检查**: 自动检测和显示缺失数据信息
- **异常值检测**: 基于IQR方法识别异常值
- **导出功能**: 支持将图表导出为PNG格式

## 🚀 快速开始

### 基本使用

```python
from library.widgets import DynamicStaticWidget
import pandas as pd

# 创建数据
df = pd.DataFrame({
    'temperature': [25.1, 26.3, 24.8, ...],
    'pressure': [1.013, 1.015, 1.012, ...],
    'humidity': [65.2, 67.1, 63.8, ...]
})

# 创建统计分析组件
widget = DynamicStaticWidget(df, title="传感器数据分析")

# 显示组件（在Jupyter Notebook中）
widget
```

### 指定列和图表类型

```python
# 选择特定列进行分析
widget = DynamicStaticWidget(
    df,
    columns=['temperature', 'pressure'],  # 指定要分析的列
    chart_type='boxplot',                 # 指定图表类型
    title="温度和压力分析",
    figsize=(16, 10)                      # 指定图表尺寸
)
```

## 📋 API 参考

### 构造函数参数

- `df` (pd.DataFrame): 输入数据表
- `columns` (List[str], optional): 要分析的列，默认分析所有数值列的前5列
- `chart_type` (str): 图表类型，默认为 'summary'
  - `'summary'`: 统计汇总表
  - `'boxplot'`: 箱线图
  - `'histogram'`: 直方图
  - `'density'`: 密度图
  - `'scatter'`: 散点图
- `title` (str): 图表标题，默认为 "动态统计分析"
- `figsize` (Tuple[int, int]): 图表尺寸，默认为 (16, 10)

### 主要方法

#### 配置方法

- `set_columns(columns: List[str])`: 设置要分析的列
- `set_chart_type(chart_type: str)`: 设置图表类型

#### 获取方法

- `get_selected_columns() -> List[str]`: 获取当前选中的列
- `get_chart_type() -> str`: 获取当前图表类型
- `get_statistics_summary() -> pd.DataFrame`: 获取统计汇总数据
- `get_data_summary() -> Dict`: 获取数据质量汇总信息

## 🎨 用户界面

### 界面布局

组件采用左右分栏布局：

- **左侧控制面板**: 参数选择和配置
  - 列选择器：复选框选择要分析的数值列
  - 图表类型选择器：下拉菜单选择统计图表类型
  - 图表尺寸设置：选择预定义的图表尺寸
  - 散点图设置：X轴和Y轴变量选择（仅散点图模式）
- **右侧图表区域**: 统计图表显示区域

### 工具栏功能

- **重置**: 重置所有参数到默认状态
- **导出**: 将当前图表导出为PNG文件

## 📊 统计指标

组件计算以下统计指标：

### 基础统计量
- **样本数量**: 非缺失值的数量
- **均值**: 算术平均值
- **标准差**: 数据的离散程度
- **最小值/最大值**: 数据范围
- **中位数**: 第50百分位数
- **Q1/Q3**: 第25/75百分位数

### 分布特征
- **偏度**: 分布的对称性度量
- **峰度**: 分布的尖峰程度

### 数据质量
- **缺失值数量**: 每列缺失值的数量

## 🔧 技术实现

### 架构设计

组件采用模块化设计，包含以下核心模块：

- `main.py`: 主控制器 `DynamicStaticWidget`
- `ui_components.py`: UI组件管理器 `StatisticsUIComponents`
- `chart_renderer.py`: 图表渲染器 `StatisticsChartRenderer`
- `data_processor.py`: 数据处理器 `StatisticsDataProcessor`
- `utils.py`: 工具函数
- `constants.py`: 常量定义

### 依赖库

- `pandas`: 数据处理
- `numpy`: 数值计算
- `plotly`: 图表渲染
- `ipywidgets`: 交互式组件
- `scipy` (可选): 高级统计计算

## 📝 使用示例

### 完整示例

```python
import pandas as pd
import numpy as np
from library.widgets import DynamicStaticWidget

# 创建示例数据
np.random.seed(42)
data = {
    '温度': np.random.normal(25, 3, 1000),
    '压力': np.random.normal(1.0, 0.1, 1000),
    '湿度': np.random.normal(60, 10, 1000),
    '电压': np.random.normal(12, 0.5, 1000)
}
df = pd.DataFrame(data)

# 创建并显示统计分析组件
widget = DynamicStaticWidget(
    df,
    columns=['温度', '压力', '湿度'],
    chart_type='boxplot',
    title="环境监测数据统计分析"
)

# 在Jupyter中显示
widget
```

### 集成到算法系统

```python
def statistics_analysis(df: pd.DataFrame, columns: list = None,
                       chart_type: str = 'summary', **kwargs) -> None:
    """
    时序数据统计分析算法

    Parameters:
    df (pd.DataFrame): 输入数据表
    columns (list, optional): 要分析的列，默认分析所有数值列
    chart_type (str): 图表类型 ('summary', 'boxplot', 'histogram', 'density', 'scatter')
    """
    widget = DynamicStaticWidget(df, columns, chart_type, **kwargs)
    display(widget)
```

## 🐛 故障排除

### 常见问题

1. **没有数值列**: 确保DataFrame包含数值类型的列
2. **图表不显示**: 检查数据是否包含有效的数值
3. **导出失败**: 确保安装了plotly的导出后端 (kaleido)

### 错误处理

组件包含完善的错误处理机制：
- 自动过滤非数值列
- 处理缺失数据
- 提供友好的错误提示

## 📈 性能优化

- **数据缓存**: 统计计算结果缓存，避免重复计算
- **延迟更新**: 参数变化时延迟更新，避免频繁刷新
- **采样处理**: 对大数据集自动采样，保证响应性能

## 🔄 更新日志

### v1.0.0
- 初始版本发布
- 支持5种统计图表类型
- 完整的交互式参数配置
- 导出和重置功能
