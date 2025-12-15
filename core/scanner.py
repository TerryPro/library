# -*- coding: utf-8 -*-
"""
Library Scanner
===============
扫描算法库，构建算法元数据
"""

import inspect
import pkgutil
import importlib
from typing import List, Dict, Any, Optional, Callable

from .models import AlgorithmMetadata, AlgorithmParameter, AlgorithmPort, get_category_labels
from .parser import DocstringParser
from .extractor import CodeExtractor


class LibraryScanner:
    """
    算法库扫描器
    
    扫描Python包中的算法函数，解析docstring，构建元数据
    """
    
    def __init__(self, package=None):
        """
        初始化扫描器
        
        Args:
            package: 要扫描的Python包（可选，可以后续通过scan方法传入）
        """
        self.package = package
        self.parser = DocstringParser()
        self.extractor = CodeExtractor()
        self._cache: Dict[str, AlgorithmMetadata] = {}
    
    def scan(self, package=None) -> Dict[str, List[AlgorithmMetadata]]:
        """
        扫描包中所有算法，按分类返回
        
        Args:
            package: 要扫描的Python包，如果不提供则使用初始化时的包
            
        Returns:
            字典，key是分类ID，value是该分类下的算法元数据列表
        """
        if package is not None:
            self.package = package
        
        if self.package is None:
            raise ValueError("No package specified for scanning")
        
        result: Dict[str, List[AlgorithmMetadata]] = {}
        self._cache.clear()
        
        # 获取所有模块
        modules = self._get_all_modules(self.package)
        
        for module in modules:
            algos = self.scan_module(module)
            for algo in algos:
                if algo.id in self._cache:
                    continue  # 避免重复
                
                self._cache[algo.id] = algo
                
                if algo.category not in result:
                    result[algo.category] = []
                result[algo.category].append(algo)
        
        return result
    
    def scan_with_labels(self, package=None) -> Dict[str, List[AlgorithmMetadata]]:
        """
        扫描并使用分类标签作为key返回
        
        Args:
            package: 要扫描的Python包
            
        Returns:
            字典，key是分类标签（中文），value是该分类下的算法元数据列表
        """
        by_id = self.scan(package)
        cat_labels = get_category_labels()
        
        result: Dict[str, List[AlgorithmMetadata]] = {}
        for cat_id, algos in by_id.items():
            label = cat_labels.get(cat_id, cat_id)
            result[label] = algos
        
        return result
    
    def scan_module(self, module) -> List[AlgorithmMetadata]:
        """
        扫描单个模块中的算法
        
        Args:
            module: Python模块对象
            
        Returns:
            AlgorithmMetadata列表
        """
        algorithms = []
        
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if name.startswith('_'):
                continue
            
            # 只处理在当前模块定义的函数（避免导入的函数重复）
            if func.__module__ != module.__name__:
                continue
            
            algo = self.create_metadata_from_func(func, module)
            if algo:
                algorithms.append(algo)
        
        return algorithms
    
    def create_metadata_from_func(self, func: Callable, module=None) -> Optional[AlgorithmMetadata]:
        """
        从函数创建算法元数据
        
        Args:
            func: 函数对象
            module: 函数所在模块
            
        Returns:
            AlgorithmMetadata对象，如果函数不是算法则返回None
        """
        docstring = inspect.getdoc(func)
        
        if not docstring or not self.parser.has_algorithm_section(docstring):
            return None
        
        # 解析docstring
        parsed = self.parser.parse(docstring)
        algo_meta = parsed.get("algorithm", {})
        param_meta = parsed.get("parameters", {})
        returns_meta = parsed.get("returns", [])
        
        # 提取参数
        all_params = self.extractor.extract_parameters(func, param_meta)
        
        # 分离inputs和parameters
        inputs = []
        parameters = []
        for param in all_params:
            if param.role == 'input':
                inputs.append(AlgorithmPort(
                    name=param.name,
                    type=param.type,
                    description=param.description
                ))
            else:
                parameters.append(param)
        
        # 提取imports
        imports = algo_meta.get('imports', [])
        if not imports and module:
            imports = self.extractor.extract_imports_from_module(module)
        
        # 推断outputs
        outputs = self._infer_outputs(func, returns_meta)
        
        # 生成template
        try:
            source = inspect.getsource(func)
        except OSError:
            source = "# Source not available"
        
        template = f"# {algo_meta.get('name', func.__name__)}\n{source}"
        
        # 确定nodeType
        node_type = "generic"
        if func.__name__ == "load_csv":
            node_type = "csv_loader"
        
        return AlgorithmMetadata(
            id=func.__name__,
            name=algo_meta.get('name', func.__name__),
            category=algo_meta.get('category', 'uncategorized'),
            description=parsed.get("description", ""),
            prompt=algo_meta.get('prompt', ''),
            template=template,
            imports=imports,
            parameters=parameters,
            inputs=inputs,
            outputs=outputs,
            node_type=node_type
        )
    
    def _infer_outputs(self, func: Callable, returns_meta: List[Dict[str, str]]) -> List[AlgorithmPort]:
        """推断输出端口"""
        outputs = []
        
        # 优先使用docstring中的Returns定义
        if returns_meta:
            for ret in returns_meta:
                outputs.append(AlgorithmPort(
                    name=ret.get("name", "output"),
                    type=ret.get("type", "DataFrame"),
                    description=ret.get("description", "")
                ))
            return outputs
        
        # 从签名推断
        return self.extractor.extract_outputs_from_signature(func)
    
    def _get_all_modules(self, package) -> List:
        """递归获取包中所有模块"""
        modules = []
        if hasattr(package, "__path__"):
            for _, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
                if not is_pkg:
                    try:
                        module = importlib.import_module(name)
                        modules.append(module)
                    except Exception as e:
                        print(f"Failed to import {name}: {e}")
        return modules
    
    def get_all_algorithms(self) -> List[AlgorithmMetadata]:
        """获取所有已扫描的算法（平铺列表）"""
        return list(self._cache.values())
    
    def get_algorithm_by_id(self, algo_id: str) -> Optional[AlgorithmMetadata]:
        """根据ID获取算法"""
        return self._cache.get(algo_id)
    
    def refresh(self) -> Dict[str, List[AlgorithmMetadata]]:
        """刷新扫描结果"""
        return self.scan(self.package)


# 全局扫描器实例（延迟初始化）
_global_scanner: Optional[LibraryScanner] = None


def get_scanner() -> LibraryScanner:
    """获取全局扫描器实例"""
    global _global_scanner
    if _global_scanner is None:
        _global_scanner = LibraryScanner()
    return _global_scanner


def scan_library(package) -> Dict[str, List[AlgorithmMetadata]]:
    """
    扫描算法库（便捷函数）
    
    Args:
        package: Python包对象
        
    Returns:
        按分类ID组织的算法元数据
    """
    scanner = get_scanner()
    return scanner.scan(package)


def scan_library_with_labels(package) -> Dict[str, List[AlgorithmMetadata]]:
    """
    扫描算法库并使用分类标签（便捷函数）
    
    Args:
        package: Python包对象
        
    Returns:
        按分类标签组织的算法元数据
    """
    scanner = get_scanner()
    return scanner.scan_with_labels(package)
