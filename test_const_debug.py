"""Debug const variable resolution."""

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.semantic.name_resolver import NameResolver
from src.semantic.type_checker import TypeChecker
from src.semantic.symbol_table import SymbolTable


def debug_const():
    code = """
void function test()
    const int x = 5
    x = 10
End function
"""

    print("=== Parsing ===")
    lexer = Lexer(code, "test.fusion")
    parser = Parser(list(lexer.tokenize()))
    program = parser.parse_program()

    print(f"Program has {len(program.declarations)} declarations")
    func = program.declarations[0]
    print(f"Function '{func.name}' has {len(func.body.statements)} statements")

    for i, stmt in enumerate(func.body.statements):
        print(f"  Statement {i}: {stmt.__class__.__name__}")
        if hasattr(stmt, 'is_const'):
            print(f"    is_const = {stmt.is_const}")
        if hasattr(stmt, 'name'):
            print(f"    name = {stmt.name}")

    print("\n=== Name Resolution ===")
    symbol_table = SymbolTable()
    name_resolver = NameResolver(symbol_table)
    name_errors = name_resolver.resolve_program(program)

    print(f"Name resolution errors: {len(name_errors)}")
    for error in name_errors:
        print(f"  {error}")

    print(f"\nSymbol table (global scope):")
    for name, symbol in symbol_table.global_scope.symbols.items():
        print(f"  {name}: {symbol}")

    print("\n=== Type Checking ===")
    type_checker = TypeChecker(symbol_table)
    type_errors = type_checker.check_program(program)

    print(f"Type checking errors: {len(type_errors)}")
    for error in type_errors:
        print(f"  {error}")


if __name__ == "__main__":
    debug_const()
