# Widgets 模块

Notebook端的算法选择和执行Widget组件

## 目录结构

```
widgets/
├── __init__.py              # 模块入口
├── algorithm_widget.py      # 主Widget类
├── widget_builder.py        # 参数Widget构建器
├── code_generator.py        # 代码生成器
└── data_provider.py         # 数据提供者
```

## 模块职责

### 1. AlgorithmWidget (algorithm_widget.py)
- **职责**: 主要的算法选择和执行Widget UI
- **功能**:
  - 提供算法分类和选择界面
  - 协调各个子组件工作
  - 处理用户交互事件
  - 管理Widget生命周期

### 2. WidgetBuilder (widget_builder.py)
- **职责**: 根据算法元数据构建参数输入Widget
- **功能**:
  - 创建DataFrame选择器
  - 根据参数类型创建对应Widget（文本框、下拉框、复选框等）
  - 处理file-selector等特殊Widget类型
  - 统一Widget样式和布局

### 3. CodeGenerator (code_generator.py)
- **职责**: 生成算法调用代码
- **功能**:
  - 根据算法元数据和参数值生成Python代码
  - 处理参数值格式化（字符串引号、路径转义等）
  - 生成imports和函数定义
  - 生成输出变量赋值

### 4. DataProvider (data_provider.py)
- **职责**: 提供Notebook环境中的数据源
- **功能**:
  - 获取当前Notebook中所有DataFrame变量
  - 扫描dataset目录中的CSV文件
  - 返回文件的绝对路径

## 使用方法

### 基本使用

```python
from widgets import AlgorithmWidget

# 显示所有算法的选择器
widget = AlgorithmWidget()
widget
```

### 指定算法

```python
from widgets import AlgorithmWidget

# 直接显示特定算法的参数配置界面
widget = AlgorithmWidget(init_algo='trend_plot')
widget
```

## 向后兼容

为了保持向后兼容，在 `algorithm/__init__.py` 中添加了导入别名：

```python
from algorithm.widgets import AlgorithmWidget  # 仍然有效
```

## 重构说明

### 重构前
- 单个文件 `algorithm/widgets.py` (493行)
- 所有功能混在一个类中
- 职责不清晰，难以维护

### 重构后
- 拆分为4个模块文件
- 单一职责原则
- 易于测试和扩展
- 更清晰的代码结构

## 依赖关系

```
algorithm_widget.py
├── core.LibraryScanner        # 算法扫描器
├── widget_builder.WidgetBuilder
├── code_generator.CodeGenerator
└── ipywidgets

widget_builder.py
├── data_provider.DataProvider
└── ipywidgets

code_generator.py
└── ipywidgets

data_provider.py
├── pandas
└── IPython
```
