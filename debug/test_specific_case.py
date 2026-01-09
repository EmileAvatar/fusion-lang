"""Test the specific case that was hanging."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.lexer import Lexer

source = "int multiply(int x, int y) : x * y"
print(f"Testing: '{source}'")
print()

lexer = Lexer(source)

# Add safety limit
iteration_count = [0]
MAX_ITERATIONS = 100

original_is_eof = lexer.is_eof

def traced_is_eof():
    result = original_is_eof()
    iteration_count[0] += 1

    if iteration_count[0] % 10 == 0 or iteration_count[0] <= 5:
        ch = lexer.current_char()
        print(f"[Iter {iteration_count[0]:3d}] pos={lexer.pos:2d}, ch={repr(ch):6s}, eof={result}")

    if iteration_count[0] > MAX_ITERATIONS:
        print(f"\nSAFETY LIMIT REACHED at iteration {iteration_count[0]}")
        print(f"Position stuck at: {lexer.pos}")
        print(f"Current char: {repr(lexer.current_char())}")
        print(f"Remaining source: {repr(lexer.source[lexer.pos:lexer.pos+20])}")
        raise RuntimeError("Infinite loop detected")

    return result

lexer.is_eof = traced_is_eof

try:
    tokens = lexer.tokenize()
    print(f"\nSUCCESS! Got {len(tokens)} tokens in {iteration_count[0]} iterations")
    for i, token in enumerate(tokens):
        print(f"  {i:2d}: {token.type.name:15s} = {repr(token.value)}")
except RuntimeError as e:
    print(f"\nERROR: {e}")
except Exception as e:
    print(f"\nUNEXPECTED ERROR: {e}")
    import traceback
    traceback.print_exc()
