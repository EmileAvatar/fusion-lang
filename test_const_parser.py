"""Test const declaration parsing."""
import pytest
from src.parser.parser import Parser
from src.parser.ast_nodes import VarDeclStmt
from src.lexer.lexer import Lexer

def parse_code(code: str):
    """Helper to parse code."""
    lexer = Lexer(code, "test.fusion")
    parser = Parser(list(lexer.tokenize()))
    return parser.parse_program()

def test_const_declaration_with_initializer():
    """Test parsing const with initializer inside function."""
    code = """
void function test()
    const int x = 5
End function
"""
    program = parse_code(code)

    assert len(program.declarations) == 1
    func = program.declarations[0]
    assert len(func.body.statements) == 1

    stmt = func.body.statements[0]
    assert isinstance(stmt, VarDeclStmt)
    assert stmt.is_const == True
    assert stmt.name == "x"
    assert stmt.var_type.name == "int"
    assert stmt.initializer is not None
    print("[OK] const int x = 5 parsed correctly with is_const=True")

def test_const_declaration_without_initializer_fails():
    """Test that const without initializer raises error."""
    code = """
void function test()
    const int x
End function
"""
    with pytest.raises(Exception) as exc_info:
        parse_code(code)

    error_msg = str(exc_info.value)
    print(f"Error message: {error_msg}")
    assert "must have an initializer" in error_msg
    print("[OK] const int x (no initializer) correctly raises error")

def test_multiple_const_declarations():
    """Test multiple const declarations."""
    code = """
void function test()
    const int x = 5
    const float PI = 3.14
    const string name = "Alice"
End function
"""
    program = parse_code(code)

    func = program.declarations[0]
    assert len(func.body.statements) == 3

    for stmt in func.body.statements:
        assert isinstance(stmt, VarDeclStmt)
        assert stmt.is_const == True
        assert stmt.initializer is not None

    print("[OK] Multiple const declarations parsed correctly")

def test_regular_var_declaration_still_works():
    """Test that regular var declarations still work (is_const=False)."""
    code = """
void function test()
    int x = 5
End function
"""
    program = parse_code(code)

    func = program.declarations[0]
    stmt = func.body.statements[0]

    assert isinstance(stmt, VarDeclStmt)
    assert stmt.is_const == False
    assert stmt.name == "x"
    print("[OK] Regular var declaration has is_const=False")

if __name__ == "__main__":
    test_const_declaration_with_initializer()
    test_const_declaration_without_initializer_fails()
    test_multiple_const_declarations()
    test_regular_var_declaration_still_works()
    print("\n[ALL TESTS PASSED]")
