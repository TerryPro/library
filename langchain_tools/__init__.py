"""
LangChain Tools Integration for AI Server

This module provides functionality to wrap library algorithms as LangChain-compatible tools
that can be called by LLM agents.
"""

from typing import Dict, List, Any, Optional
from .registry import ToolRegistry, ToolSpec

__all__ = [
    'get_tool_specs',
    'call_tool',
    'register_tool',
    'ToolSpec',
    'ToolRegistry'
]


def get_tool_specs() -> List[Dict[str, Any]]:
    """
    Get specifications for all registered tools.

    Returns:
        List of tool specifications in JSON Schema format suitable for LLM consumption.
    """
    return ToolRegistry.get_instance().get_tool_specs()


def call_tool(name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call a registered tool with the given parameters.

    Args:
        name: Name of the tool to call
        params: Parameters to pass to the tool

    Returns:
        Standardized result dict with success/error information
    """
    return ToolRegistry.get_instance().call_tool(name, params)


def register_tool(spec: ToolSpec) -> None:
    """
    Register a new tool specification.

    Args:
        spec: Tool specification to register
    """
    ToolRegistry.get_instance().register_tool(spec)
