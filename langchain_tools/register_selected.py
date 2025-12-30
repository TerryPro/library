#!/usr/bin/env python3
"""
Script to register selected algorithm tools for LangChain integration.

This script introspects the specified algorithm modules from the library
and registers them as LangChain-compatible tools.
"""

import sys
import os
from pathlib import Path
import logging

# Setup paths before any imports
current_dir = Path(__file__).resolve()
aiserver_package_dir = current_dir.parent  # aiserver/langchain_tools -> aiserver (package dir)
project_root = aiserver_package_dir.parent  # aiserver -> JuServer
library_path = project_root / "library"

# Add paths to sys.path
if str(aiserver_package_dir) not in sys.path:
    sys.path.insert(0, str(aiserver_package_dir))
if str(library_path) not in sys.path:
    sys.path.insert(0, str(library_path))

# Now import our modules
from .introspect import generate_tool_spec_from_module
from .registry import ToolRegistry, ToolSpec

logger = logging.getLogger(__name__)


def register_selected_algorithms():
    """Register the five selected anomaly detection algorithms."""

    # Selected algorithm modules (relative to library root)
    selected_modules = [
        "algorithm/anomaly_detection/change_point.py",
        "algorithm/anomaly_detection/iqr_anomaly.py",
        "algorithm/anomaly_detection/isolation_forest.py",
        "algorithm/anomaly_detection/threshold_sigma.py",
        "algorithm/anomaly_detection/zscore_anomaly.py"
    ]

    registry = ToolRegistry.get_instance()

    print(f"Starting registration of {len(selected_modules)} algorithms...")

    success_count = 0
    failed_modules = []

    for module_rel_path in selected_modules:
        module_path = library_path / module_rel_path

        if not module_path.exists():
            print(f"Module not found: {module_path}")
            failed_modules.append(module_rel_path)
            continue

        print(f"Introspecting: {module_rel_path}")

        try:
            # Generate tool specification
            tool_spec = generate_tool_spec_from_module(str(module_path))

            if tool_spec is None:
                print(f"Failed to generate spec for: {module_rel_path}")
                failed_modules.append(module_rel_path)
                continue

            # Create ToolSpec
            tool_name = tool_spec["name"]
            description = tool_spec["description"]
            parameters = tool_spec["parameters"]
            returns = tool_spec["returns"]
            callable_func = tool_spec["callable"]
            args_model = tool_spec["args_model"]

            spec = ToolSpec(
                name=tool_name,
                description=description,
                parameters=parameters,
                returns=returns,
                callable=callable_func,
                args_schema=args_model
            )

            # Register the tool
            registry.register_tool(spec)

            print(f"Registered tool: {tool_name}")
            print(f"   Description: {description[:50]}...")
            print(f"   Parameters: {list(parameters.keys())}")

            success_count += 1

        except Exception as e:
            print(f"Error registering {module_rel_path}: {e}")
            failed_modules.append(module_rel_path)
            continue

    print(f"\nRegistration Summary:")
    print(f"   Successfully registered: {success_count}")
    print(f"   Failed: {len(failed_modules)}")

    if failed_modules:
        print(f"   Failed modules: {failed_modules}")

    return success_count, failed_modules


def main():
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)

    print("LangChain Tools Registration Script")
    print("=" * 50)

    success_count, failed_modules = register_selected_algorithms()

    print("\n" + "=" * 50)
    if success_count > 0:
        print("Registration completed successfully!")

        # Show registered tools
        registry = ToolRegistry.get_instance()
        tools = registry.list_tools()
        print(f"Registered tools ({len(tools)}):")
        for tool_name in tools:
            print(f"   - {tool_name}")

    else:
        print("No tools were registered. Check the errors above.")
        sys.exit(1)

    if failed_modules:
        print(f"\nWarning: Some modules failed to register: {failed_modules}")
        sys.exit(1)


if __name__ == "__main__":
    main()
