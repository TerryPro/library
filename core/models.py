# -*- coding: utf-8 -*-
"""
Algorithm Data Models
=====================
统一的算法数据模型定义，保持与前端接口的兼容性
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class AlgorithmPort:
    """算法输入/输出端口定义"""
    name: str
    type: str = "DataFrame"
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为前端格式（保持兼容性）"""
        return {
            "name": self.name,
            "type": self.type
        }


@dataclass
class AlgorithmParameter:
    """
    算法参数定义
    
    保持与现有 aiserver.algorithms.base.AlgorithmParameter 完全兼容的 to_dict 格式
    """
    name: str
    type: str = "str"
    default: Any = None
    label: str = ""
    description: str = ""
    widget: Optional[str] = None
    options: Optional[List[Any]] = None
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    priority: str = "non-critical"  # critical or non-critical
    role: str = "parameter"  # input, output, or parameter
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为前端格式（保持与现有API完全兼容）
        
        返回格式与 aiserver.algorithms.base.AlgorithmParameter.to_dict() 一致
        """
        d = {
            "name": self.name,
            "type": self.type,
            "default": self.default,
            "label": self.label or self.name.replace("_", " ").title(),
            "description": self.description,
            "priority": self.priority,
            "role": self.role
        }
        if self.min is not None: 
            d["min"] = self.min
        if self.max is not None: 
            d["max"] = self.max
        if self.step is not None: 
            d["step"] = self.step
        if self.options is not None: 
            d["options"] = self.options
        if self.widget is not None: 
            d["widget"] = self.widget
        return d


@dataclass
class AlgorithmMetadata:
    """
    算法元数据
    
    统一的算法信息容器，支持转换为多种格式（前端元数据、AI提示等）
    """
    id: str
    name: str
    category: str
    description: str = ""
    prompt: str = ""
    template: str = ""
    imports: List[str] = field(default_factory=list)
    parameters: List[AlgorithmParameter] = field(default_factory=list)
    inputs: List[AlgorithmPort] = field(default_factory=list)
    outputs: List[AlgorithmPort] = field(default_factory=list)
    node_type: str = "generic"  # csv_loader, generic, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为前端库元数据格式
        
        返回格式与 aiserver.lib.library.get_library_metadata() 中的算法条目一致
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "template": self.template,
            "imports": self.imports,
            "args": [p.to_dict() for p in self.parameters],
            "inputs": [p.to_dict() for p in self.inputs],
            "outputs": [p.to_dict() for p in self.outputs],
            "nodeType": self.node_type
        }
    
    def to_prompt_dict(self) -> Dict[str, Any]:
        """转换为AI提示格式"""
        return {
            "id": self.id,
            "name": self.name,
            "prompt": self.prompt
        }
    
    def to_port_dict(self) -> Dict[str, List[Dict[str, str]]]:
        """转换为端口信息格式"""
        return {
            "inputs": [p.to_dict() for p in self.inputs],
            "outputs": [p.to_dict() for p in self.outputs]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlgorithmMetadata':
        """
        从字典创建 AlgorithmMetadata 实例
        
        用于将前端API传来的字典格式转换为统一的数据模型
        
        Args:
            data: 包含算法元数据的字典（通常来自前端API或code_manager）
                  支持的字段：
                  - id: 算法ID
                  - name: 算法名称
                  - category: 类别
                  - description: 描述
                  - prompt: AI提示模板
                  - template: 代码模板
                  - imports: 导入列表
                  - args: 参数列表（转换为parameters）
                  - inputs: 输入端口列表
                  - outputs: 输出端口列表
                  - nodeType: 节点类型
                
        Returns:
            AlgorithmMetadata 实例
        """
        # 处理 parameters（args）
        parameters = []
        for p in data.get('args', []):
            parameters.append(AlgorithmParameter(
                name=p.get('name'),
                type=p.get('type', 'str'),
                default=p.get('default'),
                label=p.get('label', ''),
                description=p.get('description', ''),
                widget=p.get('widget'),
                options=p.get('options'),
                min=p.get('min'),
                max=p.get('max'),
                step=p.get('step'),
                priority=p.get('priority', 'non-critical'),
                role=p.get('role', 'parameter')
            ))
        
        # 处理 inputs
        inputs = []
        for i in data.get('inputs', []):
            inputs.append(AlgorithmPort(
                name=i.get('name'),
                type=i.get('type', 'DataFrame'),
                description=i.get('description', '')
            ))
        
        # 处理 outputs
        outputs = []
        for o in data.get('outputs', []):
            outputs.append(AlgorithmPort(
                name=o.get('name', 'output'),
                type=o.get('type', 'DataFrame'),
                description=o.get('description', '')
            ))
        
        return cls(
            id=data.get('id', 'new_algorithm'),
            name=data.get('name', 'Algorithm'),
            category=data.get('category', 'uncategorized'),
            description=data.get('description', ''),
            prompt=data.get('prompt', ''),
            template=data.get('template', ''),
            imports=data.get('imports', []),
            parameters=parameters,
            inputs=inputs,
            outputs=outputs,
            node_type=data.get('nodeType', 'generic')
        )


# 类别标签映射（从algorithm包导入或使用默认值）
DEFAULT_CATEGORY_LABELS = {
    'load_data': '输入输出',
    'data_operation': '数据操作',
    'data_preprocessing': '数据预处理',
    'eda': '探索式分析',
    'anomaly_detection': '异常检测',
    'trend_plot': '趋势绘制',
    'plotting': '数据绘图'
}


def get_category_labels() -> Dict[str, str]:
    """获取类别标签映射"""
    try:
        from algorithm import CATEGORY_LABELS
        return CATEGORY_LABELS
    except ImportError:
        return DEFAULT_CATEGORY_LABELS
