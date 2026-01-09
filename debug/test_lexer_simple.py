"""Simple test to debug lexer."""

from src.lexer import Lexer

# Test 1: Simple code
print("Test 1: Using tokenize() method")
try:
    source = "int multiply(int x, int y) : x * y"
    print(f"Source: '{source}'")

    lexer = Lexer(source)
    print(f"Lexer created")
    print(f"Calling tokenize()...")

    # Add timeout detection
    import signal

    def timeout_handler(signum, frame):
        print("TIMEOUT! Infinite loop detected")
        raise TimeoutError("Tokenize took too long")

    # Set timeout (only works on Unix)
    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(2)  # 2 second timeout
    except:
        print("(Timeout not supported on Windows)")

    tokens = lexer.tokenize()

    try:
        signal.alarm(0)  # Cancel alarm
    except:
        pass

    print(f"Success! Got {len(tokens)} tokens")
    for i, token in enumerate(tokens):
        print(f"  {i}: {token.type.name} = '{token.value}'")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
