"""
Tool invoker for executing algorithm functions with proper error handling and timeouts.
"""

import logging
import time
import signal
from typing import Dict, List, Any, Optional, Callable
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import threading

logger = logging.getLogger(__name__)


class ToolInvoker:
    """Invoker for calling tools with timeout and error handling."""

    def __init__(self, timeout_seconds: float = 30.0):
        """
        Initialize the invoker.

        Args:
            timeout_seconds: Default timeout for tool execution
        """
        self.timeout_seconds = timeout_seconds

    def invoke_sync(self, func: Callable, args: Dict[str, Any],
                   timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Invoke a tool function synchronously with timeout protection.

        Args:
            func: The function to call
            args: Arguments to pass to the function
            timeout: Timeout in seconds (overrides default)

        Returns:
            Standardized result dict
        """
        timeout = timeout or self.timeout_seconds
        start_time = time.time()

        try:
            # Use ThreadPoolExecutor for timeout control
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, **args)
                result = future.result(timeout=timeout)

                return {
                    "success": True,
                    "output": result,
                    "error": None,
                    "meta": {
                        "duration_ms": (time.time() - start_time) * 1000,
                        "timeout_used": timeout
                    }
                }

        except FutureTimeoutError:
            logger.warning(f"Tool execution timed out after {timeout} seconds")
            return {
                "success": False,
                "output": None,
                "error": {
                    "code": "TIMEOUT",
                    "message": f"Tool execution timed out after {timeout} seconds",
                    "retryable": True
                },
                "meta": {
                    "duration_ms": (time.time() - start_time) * 1000,
                    "timeout_used": timeout
                }
            }

        except Exception as e:
            logger.exception(f"Tool execution failed: {e}")
            return {
                "success": False,
                "output": None,
                "error": {
                    "code": "EXECUTION_ERROR",
                    "message": str(e),
                    "retryable": True
                },
                "meta": {
                    "duration_ms": (time.time() - start_time) * 1000,
                    "timeout_used": timeout
                }
            }

    def invoke_with_subprocess(self, func: Callable, args: Dict[str, Any],
                              timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Invoke a tool function in a subprocess for better isolation.

        This method uses multiprocessing to run the function in a separate process,
        providing better isolation and the ability to forcibly terminate on timeout.

        Args:
            func: The function to call (must be importable)
            args: Arguments to pass to the function
            timeout: Timeout in seconds

        Returns:
            Standardized result dict
        """
        timeout = timeout or self.timeout_seconds
        start_time = time.time()

        # Create a queue for inter-process communication
        result_queue = mp.Queue()

        def worker():
            """Worker function that runs in subprocess."""
            try:
                result = func(**args)
                result_queue.put({
                    "success": True,
                    "output": result,
                    "error": None
                })
            except Exception as e:
                result_queue.put({
                    "success": False,
                    "output": None,
                    "error": {
                        "code": "EXECUTION_ERROR",
                        "message": str(e),
                        "retryable": True
                    }
                })

        # Start the subprocess
        process = mp.Process(target=worker)
        process.start()

        try:
            # Wait for result with timeout
            result = result_queue.get(timeout=timeout)
            result["meta"] = {
                "duration_ms": (time.time() - start_time) * 1000,
                "timeout_used": timeout,
                "execution_mode": "subprocess"
            }
            return result

        except Exception as e:
            # Timeout or other error
            if process.is_alive():
                process.terminate()
                process.join(timeout=1.0)
                if process.is_alive():
                    process.kill()

            if isinstance(e, mp.TimeoutError):
                return {
                    "success": False,
                    "output": None,
                    "error": {
                        "code": "TIMEOUT",
                        "message": f"Tool execution timed out after {timeout} seconds",
                        "retryable": True
                    },
                    "meta": {
                        "duration_ms": (time.time() - start_time) * 1000,
                        "timeout_used": timeout,
                        "execution_mode": "subprocess"
                    }
                }
            else:
                return {
                    "success": False,
                    "output": None,
                    "error": {
                        "code": "SUBPROCESS_ERROR",
                        "message": str(e),
                        "retryable": False
                    },
                    "meta": {
                        "duration_ms": (time.time() - start_time) * 1000,
                        "timeout_used": timeout,
                        "execution_mode": "subprocess"
                    }
                }

    def invoke(self, func: Callable, args: Dict[str, Any],
              timeout: Optional[float] = None, use_subprocess: bool = False) -> Dict[str, Any]:
        """
        Invoke a tool function with automatic method selection.

        Args:
            func: The function to call
            args: Arguments to pass to the function
            timeout: Timeout in seconds
            use_subprocess: Whether to use subprocess for isolation

        Returns:
            Standardized result dict
        """
        if use_subprocess:
            return self.invoke_with_subprocess(func, args, timeout)
        else:
            return self.invoke_sync(func, args, timeout)


# Global invoker instance
_default_invoker = ToolInvoker(timeout_seconds=30.0)


def invoke_tool(func: Callable, args: Dict[str, Any],
               timeout: Optional[float] = None, use_subprocess: bool = False) -> Dict[str, Any]:
    """
    Convenience function to invoke a tool with the default invoker.

    Args:
        func: The function to call
        args: Arguments to pass to the function
        timeout: Timeout in seconds
        use_subprocess: Whether to use subprocess for isolation

    Returns:
        Standardized result dict
    """
    return _default_invoker.invoke(func, args, timeout, use_subprocess)
