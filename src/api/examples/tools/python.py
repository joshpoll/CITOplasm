import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import io
import sys
from typing import Any
from fvalues import F


def eval_python(expression: str) -> str:
    try:
        import math

        result = eval(expression)
    except Exception as e:
        result = F(f"Error: {e}")
    return str(result)


def exec_python(code: str) -> str:
    output_capture = io.StringIO()

    # Redirect sys.stdout to the in-memory text stream
    original_stdout = sys.stdout
    sys.stdout = output_capture

    try:
        # Execute the code
        exec(f"global _i; _i = {code}")
    except Exception as e:
        print(f"An error occurred during execution: {e}")
    finally:
        # Restore sys.stdout to its original value
        sys.stdout = original_stdout

    # Get the captured output
    captured_output = output_capture.getvalue()

    global _i
    return F(
        f"""{captured_output}
{_i if "_i" in globals() and _i is not None else ""}"""
    ).strip()


async def async_eval_python(expression: str) -> str:
    loop = asyncio.get_event_loop()
    # Use a ThreadPoolExecutor to run the non_async_function in a separate thread
    result = await loop.run_in_executor(ThreadPoolExecutor(), eval_python, expression)
    return result


async def async_exec_python(code: str) -> str:
    loop = asyncio.get_event_loop()
    # Use a ThreadPoolExecutor to run the non_async_function in a separate thread
    result = await loop.run_in_executor(ThreadPoolExecutor(), exec_python, code)
    return result


@dataclass(frozen=True)
class Python:
    code: str
    desc: str = "A Python `exec`. print() statements will be captured and returned. Output one line of code with semicolons separating statements, no newlines. Always use this tool for any math calculation rather than computing math answers yourself."

    async def run(self) -> Any:
        return await async_exec_python(self.code)


@dataclass(frozen=True)
class Calculate:
    expr: str
    desc: str = "A Python `exec` with math imported as `math`."

    async def run(self) -> Any:
        return await async_exec_python(self.expr)
