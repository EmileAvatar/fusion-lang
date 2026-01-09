"""Trace ALL position changes via property wrapper."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.lexer import Lexer

source = "int multiply(int x, int y) : x * y"
print(f"Testing: '{source}'")
print(f"Length: {len(source)}")
print()

lexer = Lexer(source)

# Wrap pos with a property to trace all modifications
_actual_pos = 0

def get_pos():
    return _actual_pos

def set_pos(value):
    global _actual_pos
    old_pos = _actual_pos

    # Get caller info
    import traceback
    stack = traceback.extract_stack()
    caller = stack[-2]  # -1 is this function, -2 is caller
    caller_info = f"{caller.filename.split(os.sep)[-1]}:{caller.lineno} in {caller.name}"

    print(f"  pos = {value} (was {old_pos}) at {caller_info}")

    _actual_pos = value

# Replace pos with property
del lexer.pos
lexer.__class__.pos = property(get_pos, set_pos)

# Limit iterations
iteration_count = [0]
MAX_ITERATIONS = 10

original_is_eof = lexer.is_eof

def traced_is_eof():
    result = original_is_eof()
    iteration_count[0] += 1

    ch = lexer.current_char()
    print(f"\n[Iteration {iteration_count[0]}] pos={lexer.pos}, ch={repr(ch)}, eof={result}")

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
