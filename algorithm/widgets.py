# -*- coding: utf-8 -*-
"""
Backward Compatibility Layer
=============================
This module provides backward compatibility for the old import path.

The widgets module has been moved from 'algorithm/widgets.py' to 'widgets/'.
This file redirects imports to maintain backward compatibility.

Old usage (still supported):
    from algorithm.widgets import AlgorithmWidget

New usage (recommended):
    from widgets import AlgorithmWidget
"""

import sys
import os

# Add parent directory to path to enable importing widgets
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import and re-export from new location
from widgets import AlgorithmWidget

__all__ = ['AlgorithmWidget']
