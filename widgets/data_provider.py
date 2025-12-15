# -*- coding: utf-8 -*-
"""
Data Provider
=============
提供Notebook环境中的数据源（DataFrame变量、CSV文件等）
"""

import os
import pandas as pd
from IPython import get_ipython


class DataProvider:
    """数据提供者，负责获取Notebook环境中的数据源"""
    
    @staticmethod
    def get_dataframe_variables():
        """Get all DataFrame variable names in the user's namespace
        
        Returns:
            list: Sorted list of DataFrame variable names
        """
        ip = get_ipython()
        if not ip:
            return []
        
        dfs = []
        user_ns = ip.user_ns
        for name, var in user_ns.items():
            if not name.startswith('_') and isinstance(var, pd.DataFrame):
                dfs.append(name)
        return sorted(dfs)
    
    @staticmethod
    def get_dataset_csv_files():
        """Get all CSV files from the dataset directory
        
        Returns:
            list of tuples: [(filename, absolute_path), ...]
                filename: just the filename for display (e.g., 'data.csv')
                absolute_path: full absolute path (e.g., 'D:\\project\\dataset\\data.csv')
        """
        # Try multiple possible locations for dataset directory
        possible_paths = [
            os.path.join(os.getcwd(), 'dataset'),
            os.path.join(os.path.dirname(os.getcwd()), 'dataset'),
            'dataset'
        ]
        
        for dataset_path in possible_paths:
            try:
                if os.path.exists(dataset_path) and os.path.isdir(dataset_path):
                    csv_files = []
                    abs_dataset_path = os.path.abspath(dataset_path)
                    for filename in os.listdir(dataset_path):
                        if filename.endswith('.csv'):
                            # Create absolute path
                            absolute_path = os.path.join(abs_dataset_path, filename)
                            # Return tuple: (display_name, value)
                            csv_files.append((filename, absolute_path))
                    if csv_files:
                        # Sort by filename
                        return sorted(csv_files, key=lambda x: x[0])
            except Exception:
                continue
        
        return []
