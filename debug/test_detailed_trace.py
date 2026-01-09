"""Detailed trace to see every position change."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.lexer import Lexer

source = "int multiply(int x, int y) : x * y"
print(f"Testing: '{source}'")
print(f"Length: {len(source)}")
print()

lexer = Lexer(source)

# Patch advance to trace it
original_advance = lexer.advance

call_stack = []

def traced_advance(count=1):
    old_pos = lexer.pos
    result = original_advance(count)
    new_pos = lexer.pos

    # Get caller info
    import traceback
    stack = traceback.extract_stack()
    caller = stack[-2]  # -1 is this function, -2 is caller
    caller_info = f"{caller.filename.split(os.sep)[-1]}:{caller.lineno} in {caller.name}"

    print(f"  advance({count}) at {caller_info}")
    print(f"    pos: {old_pos} -> {new_pos}")

    return result

lexer.advance = traced_advance

# Limit iterations
iteration_count = [0]
MAX_ITERATIONS = 20

original_is_eof = lexer.is_eof

def traced_is_eof():
    result = original_is_eof()
    iteration_count[0] += 1

    ch = lexer.current_char()
    print(f"\n[Iteration {iteration_count[0]}]")
    print(f"  pos={lexer.pos}, ch={repr(ch)}, eof={result}")

    if iteration_count[0] > MAX_ITERATIONS:
        print(f"\nSAFETY LIMIT REACHED!")
        raise RuntimeError("Infinite loop detected")

    return result

lexer.is_eof = traced_is_eof

try:
    tokens = lexer.tokenize()
    print(f"\nSUCCESS! Got {len(tokens)} tokens")
except RuntimeError as e:
    print(f"\nERROR: {e}")
except Exception as e:
    print(f"\nUNEXPECTED ERROR: {e}")
    import traceback
    traceback.print_exc()
