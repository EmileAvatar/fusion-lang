"""Quick test to verify const keyword tokenization."""
from src.lexer.lexer import Lexer

code = "const int x = 5"
lexer = Lexer(code, "test.fusion")
tokens = list(lexer.tokenize())

print("Tokens:")
for token in tokens:
    if token.type.name != 'EOF':
        print(f"  {token.type.name}: '{token.value}'")

# Verify const is recognized
assert tokens[0].type.name == 'CONST', f"Expected CONST, got {tokens[0].type.name}"
assert tokens[0].value == 'const'
print("\n[OK] const keyword is correctly tokenized as CONST")
