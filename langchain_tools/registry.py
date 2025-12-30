"""
Tool Registry for managing LangChain-compatible tools.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from threading import Lock
import time

logger = logging.getLogger(__name__)


@dataclass
class ToolSpec:
    """Specification for a tool."""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema for parameters
    returns: Dict[str, Any]     # JSON Schema for return value
    callable: Callable          # The actual callable function
    args_schema: Optional[Any] = None  # Pydantic model for validation


class ToolRegistry:
    """Singleton registry for managing tools."""

    _instance: Optional['ToolRegistry'] = None
    _lock = Lock()

    def __init__(self):
        self._tools: Dict[str, ToolSpec] = {}
        self._lock = Lock()

    @classmethod
    def get_instance(cls) -> 'ToolRegistry':
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def register_tool(self, spec: ToolSpec) -> None:
        """Register a tool specification."""
        with self._lock:
            if spec.name in self._tools:
                logger.warning(f"Tool '{spec.name}' already registered, overwriting")
            self._tools[spec.name] = spec
            logger.info(f"Registered tool: {spec.name}")

    def get_tool(self, name: str) -> Optional[ToolSpec]:
        """Get a tool specification by name."""
        return self._tools.get(name)

    def get_tool_specs(self) -> List[Dict[str, Any]]:
        """Get all tool specifications in JSON format."""
        specs = []
        for name, spec in self._tools.items():
            specs.append({
                "name": spec.name,
                "description": spec.description,
                "parameters": spec.parameters,
                "returns": spec.returns
            })
        return specs

    def call_tool(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool with standardized error handling.

        Args:
            name: Tool name
            params: Parameters to pass

        Returns:
            Dict with standardized result format:
            {
                "success": bool,
                "output": any,
                "error": null | {"code": str, "message": str, "retryable": bool},
                "meta": {"duration_ms": float, "tool": str}
            }
        """
        start_time = time.time()

        try:
            tool = self.get_tool(name)
            if not tool:
                return {
                    "success": False,
                    "output": None,
                    "error": {
                        "code": "TOOL_NOT_FOUND",
                        "message": f"Tool '{name}' not found",
                        "retryable": False
                    },
                    "meta": {
                        "duration_ms": (time.time() - start_time) * 1000,
                        "tool": name
                    }
                }

            # Call the tool
            result = tool.callable(**params)

            return {
                "success": True,
                "output": result,
                "error": None,
                "meta": {
                    "duration_ms": (time.time() - start_time) * 1000,
                    "tool": name
                }
            }

        except Exception as e:
            logger.exception(f"Error calling tool '{name}': {e}")
            return {
                "success": False,
                "output": None,
                "error": {
                    "code": "TOOL_EXECUTION_ERROR",
                    "message": str(e),
                    "retryable": True  # Assume errors might be retryable
                },
                "meta": {
                    "duration_ms": (time.time() - start_time) * 1000,
                    "tool": name
                }
            }

    def list_tools(self) -> List[str]:
        """Get list of registered tool names."""
        return list(self._tools.keys())

    def clear_tools(self) -> None:
        """Clear all registered tools (for testing/debugging)."""
        with self._lock:
            self._tools.clear()
            logger.info("Cleared all tools")
