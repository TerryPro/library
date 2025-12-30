"""
Parameter adapter for converting between API inputs and algorithm function calls.
"""

import logging
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
import json
from io import StringIO

logger = logging.getLogger(__name__)


class ParameterAdapter:
    """Adapter for converting parameters between different formats."""

    @staticmethod
    def adapt_input_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt input parameters from API format to algorithm function format.

        This handles common conversions like:
        - JSON strings to pandas DataFrames
        - Lists to numpy arrays
        - String representations to actual types
        """
        adapted = {}

        for key, value in params.items():
            adapted[key] = ParameterAdapter._adapt_single_parameter(key, value)

        return adapted

    @staticmethod
    def _adapt_single_parameter(key: str, value: Any) -> Any:
        """Adapt a single parameter based on its name and type."""

        # Handle DataFrame parameters (common in ML algorithms)
        if key.lower() in ['df', 'dataframe', 'data'] and isinstance(value, str):
            try:
                # Try to parse as JSON first
                if value.startswith('{') or value.startswith('['):
                    data = json.loads(value)
                    if isinstance(data, list):
                        # Convert list of dicts to DataFrame
                        return pd.DataFrame(data)
                    elif isinstance(data, dict):
                        # Convert dict to DataFrame (single row)
                        return pd.DataFrame([data])
                else:
                    # Try to parse as CSV
                    return pd.read_csv(StringIO(value))
            except Exception as e:
                logger.warning(f"Failed to parse DataFrame parameter '{key}': {e}")
                # Return original value if parsing fails
                return value

        # Handle Series/array parameters
        elif key.lower() in ['series', 'array', 'signal'] and isinstance(value, list):
            return np.array(value)

        # Handle tuple parameters (like figsize)
        elif key.lower() in ['figsize', 'size'] and isinstance(value, list) and len(value) == 2:
            return tuple(value)

        # Handle column lists
        elif key.lower() in ['columns', 'cols'] and isinstance(value, str):
            try:
                # Try to parse as JSON array
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except:
                # If not JSON, treat as comma-separated string
                return [col.strip() for col in value.split(',')]

        # Handle numeric parameters that might come as strings
        elif isinstance(value, str):
            # Try to convert numeric strings
            try:
                if '.' in value:
                    return float(value)
                else:
                    return int(value)
            except ValueError:
                pass

        # Return original value if no adaptation needed
        return value

    @staticmethod
    def adapt_output_result(result: Any) -> Any:
        """
        Adapt output result from algorithm to API-friendly format.

        This handles conversions like:
        - pandas DataFrames to JSON-serializable format
        - numpy arrays to lists
        - matplotlib figures to base64 strings (if needed)
        """
        if isinstance(result, pd.DataFrame):
            # Convert DataFrame to dict with records orientation
            return {
                "type": "DataFrame",
                "data": result.to_dict('records'),
                "columns": result.columns.tolist(),
                "shape": result.shape
            }

        elif isinstance(result, pd.Series):
            return {
                "type": "Series",
                "data": result.tolist(),
                "index": result.index.tolist(),
                "name": result.name
            }

        elif isinstance(result, np.ndarray):
            return {
                "type": "ndarray",
                "data": result.tolist(),
                "shape": result.shape,
                "dtype": str(result.dtype)
            }

        elif isinstance(result, dict):
            # Recursively adapt nested structures
            adapted = {}
            for k, v in result.items():
                adapted[k] = ParameterAdapter.adapt_output_result(v)
            return adapted

        elif isinstance(result, list):
            # Recursively adapt list elements
            return [ParameterAdapter.adapt_output_result(item) for item in result]

        else:
            # Return as-is for primitive types
            return result

    @staticmethod
    def validate_parameters(params: Dict[str, Any], expected_schema: Dict[str, Any]) -> List[str]:
        """
        Basic parameter validation against expected schema.

        Returns list of validation errors (empty if valid).
        """
        errors = []

        for param_name, param_schema in expected_schema.items():
            if param_name not in params and param_schema.get("default") is None:
                # Required parameter missing
                if "default" not in param_schema:
                    errors.append(f"Missing required parameter: {param_name}")
                continue

            value = params.get(param_name)
            if value is None:
                continue

            # Basic type checking
            expected_type = param_schema.get("type")
            if expected_type:
                actual_type = type(value).__name__
                type_matches = (
                    (expected_type == "integer" and isinstance(value, int)) or
                    (expected_type == "number" and isinstance(value, (int, float))) or
                    (expected_type == "string" and isinstance(value, str)) or
                    (expected_type == "boolean" and isinstance(value, bool)) or
                    (expected_type == "array" and isinstance(value, list)) or
                    (expected_type == "object" and isinstance(value, dict))
                )

                if not type_matches:
                    errors.append(f"Parameter '{param_name}' type mismatch: expected {expected_type}, got {actual_type}")

        return errors
