"""
Introspection utilities for automatically generating pydantic models and schemas
from algorithm modules in the library.
"""

import inspect
import importlib.util
import sys
from typing import Dict, List, Any, Optional, Type, Union, get_type_hints, get_origin, get_args
from pathlib import Path
import re
import logging

from pydantic import BaseModel, Field, create_model

logger = logging.getLogger(__name__)


class TypeMapper:
    """Map Python types to JSON Schema types and pydantic fields."""

    @staticmethod
    def get_json_schema_type(py_type: Type) -> Dict[str, Any]:
        """Convert Python type to JSON Schema type."""
        origin = get_origin(py_type)
        args = get_args(py_type)

        # Handle Optional types
        if origin is Union:
            # Check if it's Optional (Union[T, None])
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                schema = TypeMapper.get_json_schema_type(non_none_args[0])
                return schema

        # Handle basic types
        if py_type == int:
            return {"type": "integer"}
        elif py_type == float:
            return {"type": "number"}
        elif py_type == str:
            return {"type": "string"}
        elif py_type == bool:
            return {"type": "boolean"}
        elif py_type == list or origin == list:
            item_type = args[0] if args else Any
            return {
                "type": "array",
                "items": TypeMapper.get_json_schema_type(item_type)
            }
        elif py_type == dict or origin == dict:
            return {"type": "object"}
        elif py_type == tuple or origin == tuple:
            # For tuple, we'll represent as array
            return {"type": "array"}
        elif hasattr(py_type, '__name__') and py_type.__name__ in ['DataFrame', 'Series']:
            # Handle pandas types as arrays/objects
            if py_type.__name__ == 'DataFrame':
                return {"type": "object", "description": "pandas.DataFrame"}
            else:
                return {"type": "array", "description": "pandas.Series"}
        else:
            # Default to string for unknown types
            return {"type": "string"}

    @staticmethod
    def get_pydantic_field(py_type: Type, default_value: Any = None, description: str = "") -> Any:
        """Create a pydantic Field with appropriate type and validation."""
        field_kwargs = {}

        if default_value is not None:
            field_kwargs["default"] = default_value
        else:
            field_kwargs["default"] = ...

        if description:
            field_kwargs["description"] = description

        # Add validation based on type hints from docstring
        # This is a simplified version - in practice you'd parse more constraints

        return Field(**field_kwargs)


class DocstringParser:
    """Parse algorithm docstrings to extract metadata."""

    @staticmethod
    def parse_docstring(docstring: str) -> Dict[str, Any]:
        """Parse the algorithm docstring to extract parameters and metadata."""
        if not docstring:
            return {}

        result = {
            "description": "",
            "algorithm_name": "",
            "category": "",
            "parameters": {},
            "returns": {}
        }

        lines = docstring.strip().split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for section headers
            if line.startswith("Algorithm:"):
                current_section = "algorithm"
                continue
            elif line.startswith("Parameters:"):
                current_section = "parameters"
                continue
            elif line.startswith("Returns:"):
                current_section = "returns"
                continue

            # Parse content based on current section
            if current_section == "algorithm":
                if line.startswith("name:"):
                    result["algorithm_name"] = line.split(":", 1)[1].strip()
                elif line.startswith("category:"):
                    result["category"] = line.split(":", 1)[1].strip()
                elif line.startswith("prompt:"):
                    # Skip prompt for now
                    continue
            elif current_section == "parameters":
                # Parse parameter lines like: "param_name (type): description"
                param_match = re.match(r'^(\w+)\s*\(([^)]+)\):\s*(.+)$', line)
                if param_match:
                    param_name, param_type, param_desc = param_match.groups()
                    result["parameters"][param_name] = {
                        "type": param_type,
                        "description": param_desc.strip()
                    }
            elif current_section == "returns":
                # Parse return description
                if line.startswith("pandas.DataFrame:") or line.startswith("DataFrame:"):
                    result["returns"]["type"] = "DataFrame"
                    result["returns"]["description"] = line.split(":", 1)[1].strip()

        # Extract main description (first paragraph before Algorithm section)
        desc_lines = []
        for line in lines:
            if line.startswith("Algorithm:"):
                break
            if line.strip():
                desc_lines.append(line.strip())
        result["description"] = " ".join(desc_lines).strip()

        return result


class ModuleIntrospector:
    """Introspect Python modules to extract function signatures and generate models."""

    @staticmethod
    def load_module_from_path(module_path: str) -> Any:
        """Load a Python module from file path."""
        try:
            spec = importlib.util.spec_from_file_location("temp_module", module_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load module from {module_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules["temp_module"] = module
            spec.loader.exec_module(module)
            return module
        except ImportError as e:
            logger.warning(f"Import error loading {module_path}: {e}")
            # Try to load with minimal dependencies by mocking imports
            return ModuleIntrospector._load_module_with_mocks(module_path)

    @staticmethod
    def _load_module_with_mocks(module_path: str) -> Any:
        """Load module with mocked dependencies for introspection."""
        import types

        # Create a mock module with basic function signatures
        mock_module = types.ModuleType("mock_module")

        # Try to parse the file to extract function signatures without executing
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple regex to find function definitions
            import re
            func_pattern = r'def\s+(\w+)\s*\(([^)]*)\)\s*->\s*([^:]+):'
            matches = re.findall(func_pattern, content, re.MULTILINE | re.DOTALL)

            for match in matches:
                func_name, params_str, return_type = match
                # Create a mock function with signature
                mock_func = lambda *args, **kwargs: None
                mock_func.__name__ = func_name
                mock_func.__doc__ = f"Mock function {func_name} with return type {return_type.strip()}"
                setattr(mock_module, func_name, mock_func)

                # If this looks like the main function, return it
                if func_name in ['run', 'main', 'execute']:
                    return mock_func

            # Return the first function found
            if hasattr(mock_module, 'run'):
                return getattr(mock_module, 'run')

        except Exception as e:
            logger.error(f"Failed to create mock for {module_path}: {e}")

        raise ImportError(f"Cannot load or mock module from {module_path}")

    @staticmethod
    def find_entry_function(module: Any) -> Optional[callable]:
        """Find the main entry function in a module."""
        # Look for a function named 'run' first
        if hasattr(module, 'run'):
            return getattr(module, 'run')

        # Otherwise, find the first public function
        for name in dir(module):
            obj = getattr(module, name)
            if (callable(obj) and
                not name.startswith('_') and
                hasattr(obj, '__code__') and
                len(inspect.signature(obj).parameters) > 0):
                return obj

        return None

    @staticmethod
    def introspect_function(func: callable) -> Dict[str, Any]:
        """Introspect a function to extract signature and metadata."""
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)

        # Parse docstring
        docstring_info = DocstringParser.parse_docstring(func.__doc__ or "")

        # Build parameters schema
        parameters = {}
        pydantic_fields = {}

        for param_name, param in sig.parameters.items():
            param_type = type_hints.get(param_name, Any)
            default_value = param.default if param.default != inspect.Parameter.empty else None

            # Get description from docstring if available
            param_desc = ""
            if param_name in docstring_info.get("parameters", {}):
                param_desc = docstring_info["parameters"][param_name].get("description", "")

            # Create JSON schema
            json_schema = TypeMapper.get_json_schema_type(param_type)
            if param_desc:
                json_schema["description"] = param_desc

            # Add default value info
            if default_value is not None:
                json_schema["default"] = default_value

            parameters[param_name] = json_schema

            # Create pydantic field
            pydantic_fields[param_name] = TypeMapper.get_pydantic_field(
                param_type, default_value, param_desc
            )

        # Create pydantic model
        model_name = f"{func.__name__.title()}Args"
        ArgsModel = create_model(model_name, **pydantic_fields)

        # Build returns schema
        return_type = type_hints.get('return', Any)
        returns_schema = TypeMapper.get_json_schema_type(return_type)
        if "returns" in docstring_info:
            returns_schema.update(docstring_info["returns"])

        return {
            "name": func.__name__,
            "description": docstring_info.get("description", f"Execute {func.__name__}"),
            "parameters": parameters,
            "returns": returns_schema,
            "args_model": ArgsModel,
            "callable": func
        }

    @staticmethod
    def introspect_module(module_path: str) -> Optional[Dict[str, Any]]:
        """Introspect a module and return tool specification."""
        try:
            module = ModuleIntrospector.load_module_from_path(module_path)
            func = ModuleIntrospector.find_entry_function(module)

            if func is None:
                logger.warning(f"No suitable entry function found in {module_path}")
                return None

            return ModuleIntrospector.introspect_function(func)

        except Exception as e:
            logger.exception(f"Error introspecting module {module_path}: {e}")
            return None


def generate_tool_spec_from_module(module_path: str) -> Optional[Dict[str, Any]]:
    """
    Generate a tool specification from a module path.

    Args:
        module_path: Path to the Python module file

    Returns:
        Tool specification dict or None if introspection fails
    """
    return ModuleIntrospector.introspect_module(module_path)
