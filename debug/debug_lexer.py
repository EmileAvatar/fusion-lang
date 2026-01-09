"""Minimal diagnostic script to debug lexer infinite loop.

This script tests the lexer with detailed trace output to find exactly
where the tokenization gets stuck.
"""

import sys
import os

# Ensure imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.lexer import Lexer
from src.lexer.token import TokenType

def test_minimal():
    """Test with absolutely minimal tokenizer."""
    print("=" * 60)
    print("TEST 1: Minimal tokenizer (just EOF)")
    print("=" * 60)

    source = "int"
    print(f"Source: '{source}'")

    lexer = Lexer(source)

    # Temporarily replace tokenize with minimal version
    original_tokenize = lexer.tokenize

    def minimal_tokenize():
        print("[DEBUG] Minimal tokenizer - returning just EOF")
        from src.lexer.token import Token
        return [Token(TokenType.EOF, "", lexer.location())]

    lexer.tokenize = minimal_tokenize
    tokens = lexer.tokenize()

    print(f"SUCCESS! Got {len(tokens)} tokens")
    print()


def test_with_trace():
    """Test with detailed trace output."""
    print("=" * 60)
    print("TEST 2: Full tokenizer with trace output")
    print("=" * 60)

    source = "int"
    print(f"Source: '{source}'")
    print(f"Length: {len(source)}")
    print()

    lexer = Lexer(source)

    print(f"Initial state:")
    print(f"  pos={lexer.pos}, line={lexer.line}, column={lexer.column}")
    print(f"  is_eof={lexer.is_eof()}")
    print(f"  current_char={repr(lexer.current_char())}")
    print()

    # Manually trace through what SHOULD happen
    print("Manual step-through:")
    print(f"1. Loop iteration 1:")
    print(f"   pos={lexer.pos}, ch={repr(lexer.current_char())}")

    # Check what path it would take
    ch = lexer.current_char()
    print(f"   - Is None? {ch is None}")
    print(f"   - Is newline? {ch == chr(10)}")
    print(f"   - Is whitespace? {ch in [' ', chr(9)]}")
    print(f"   - Is digit? {ch.isdigit() if ch else 'N/A'}")
    print(f"   - Is alpha? {ch.isalpha() if ch else 'N/A'}")

    if ch and (ch.isalpha() or ch == '_'):
        print(f"   OK - Should tokenize as identifier/keyword")
        print(f"   Calling tokenize_identifier_or_keyword()...")

        old_pos = lexer.pos
        token = lexer.tokenize_identifier_or_keyword()
        new_pos = lexer.pos

        print(f"   Result: {token}")
        print(f"   Position advanced: {old_pos} -> {new_pos} (delta={new_pos - old_pos})")

        if new_pos == old_pos:
            print(f"   ERROR: Position did not advance!")
        else:
            print(f"   OK - Position advanced correctly")

    print()


def test_actual_tokenize_with_limit():
    """Test actual tokenize() with iteration limit."""
    print("=" * 60)
    print("TEST 3: Actual tokenize() with safety limit")
    print("=" * 60)

    source = "int"
    print(f"Source: '{source}'")
    print()

    lexer = Lexer(source)

    # Patch tokenize to add debugging
    original_is_eof = lexer.is_eof

    iteration_count = [0]  # Use list for mutable closure
    MAX_ITERATIONS = 20

    def traced_is_eof():
        result = original_is_eof()
        iteration_count[0] += 1

        if iteration_count[0] % 5 == 0 or iteration_count[0] <= 3:
            print(f"  [Iter {iteration_count[0]}] pos={lexer.pos}, ch={repr(lexer.current_char())}, eof={result}")

        if iteration_count[0] > MAX_ITERATIONS:
            print(f"\n❌ SAFETY LIMIT REACHED! Stopping at iteration {iteration_count[0]}")
            print(f"   Last position: {lexer.pos}")
            print(f"   Last char: {repr(lexer.current_char())}")
            raise RuntimeError("Infinite loop detected - safety limit reached")

        return result

    lexer.is_eof = traced_is_eof

    try:
        tokens = lexer.tokenize()
        print(f"\nSUCCESS! Got {len(tokens)} tokens in {iteration_count[0]} iterations")
        for i, token in enumerate(tokens):
            print(f"  {i}: {token.type.name} = {repr(token.value)}")
    except RuntimeError as e:
        print(f"\nERROR - Caught safety limit: {e}")
        print(f"   This confirms infinite loop exists")
    except Exception as e:
        print(f"\nERROR - Unexpected error: {e}")
        import traceback
        traceback.print_exc()

    print()


def test_check_imports():
    """Verify all imports are working."""
    print("=" * 60)
    print("TEST 4: Import verification")
    print("=" * 60)

    try:
        from src.lexer.comments import is_comment_start
        print("OK - is_comment_start imported")

        result = is_comment_start("// test", 0)
        print(f"   is_comment_start('// test', 0) = {result}")

    except Exception as e:
        print(f"ERROR - Failed to import is_comment_start: {e}")

    try:
        from src.lexer.operators import is_operator_char
        print("OK - is_operator_char imported")

        result = is_operator_char(':')
        print(f"   is_operator_char(':') = {result}")

        result2 = is_operator_char('(')
        print(f"   is_operator_char('(') = {result2}")

    except Exception as e:
        print(f"ERROR - Failed to import is_operator_char: {e}")

    print()


if __name__ == "__main__":
    print("\nLEXER DIAGNOSTIC SCRIPT\n")

    # Run all tests
    test_check_imports()
    test_minimal()
    test_with_trace()
    test_actual_tokenize_with_limit()

    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
