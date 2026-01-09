"""Patch tokenize_operator to see if it's called."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.lexer import Lexer

source = "int multiply(int x, int y) : x * y"
print(f"Testing: '{source}'")
print()

lexer = Lexer(source)

# Patch tokenize_operator
original_tokenize_operator = lexer.tokenize_operator

def traced_tokenize_operator():
    ch = lexer.current_char()
    pos_before = lexer.pos
    print(f"  >> tokenize_operator() called at pos={pos_before}, ch={repr(ch)}")

    result = original_tokenize_operator()

    pos_after = lexer.pos
    print(f"  << tokenize_operator() returned {result.type.name}, pos: {pos_before} -> {pos_after}")

    return result

lexer.tokenize_operator = traced_tokenize_operator

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
    for i, token in enumerate(tokens):
        print(f"  {i}: {token.type.name} = {repr(token.value)}")
except RuntimeError as e:
    print(f"\nERROR: {e}")
except Exception as e:
    print(f"\nUNEXPECTED ERROR: {e}")
    import traceback
    traceback.print_exc()
