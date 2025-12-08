# Algorithm Library

## 简介
这是一个为 JuServer 定制的数据分析与算法库，提供了数据加载、预处理、EDA、异常检测、趋势分析等功能。

## 安装
```bash
pip install -e .
```

## 使用
```python
from algorithm import load_csv, box_plot

# 加载数据
df = load_csv("dataset/data.csv")

# 绘制箱型图
box_plot(df)
```
