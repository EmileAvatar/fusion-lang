"""
Tests for Type Parsing

This module tests the parser's ability to parse type annotations:
- Primitive types (int, float, double, string, bool, char, void)
- Type detection helpers (is_type_start, check_any)
- Type parsing in various contexts (var decl, function decl, parameters)
"""

import pytest
from src.parser.parser import Parser, ParserError
from src.parser.ast_nodes import *
from src.lexer.lexer import Lexer
from src.lexer.token import TokenType


def parse_type_from_source(source: str) -> TypeNode:
    """Helper: tokenize and parse type."""
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse_type()


# ============================================================================
# Primitive Type Parsing
# ============================================================================

def test_int_type():
    """Test int type parsing."""
    type_node = parse_type_from_source("int")
    assert isinstance(type_node, PrimitiveType)
    assert type_node.name == "int"
    assert type_node.location is not None


def test_float_type():
    """Test float type parsing."""
    type_node = parse_type_from_source("float")
    assert isinstance(type_node, PrimitiveType)
    assert type_node.name == "float"


def test_double_type():
    """Test double type parsing."""
    type_node = parse_type_from_source("double")
    assert isinstance(type_node, PrimitiveType)
    assert type_node.name == "double"


def test_string_type():
    """Test string type parsing."""
    type_node = parse_type_from_source("string")
    assert isinstance(type_node, PrimitiveType)
    assert type_node.name == "string"


def test_bool_type():
    """Test bool type parsing."""
    type_node = parse_type_from_source("bool")
    assert isinstance(type_node, PrimitiveType)
    assert type_node.name == "bool"


def test_char_type():
    """Test char type parsing."""
    type_node = parse_type_from_source("char")
    assert isinstance(type_node, PrimitiveType)
    assert type_node.name == "char"


def test_void_type():
    """Test void type parsing."""
    type_node = parse_type_from_source("void")
    assert isinstance(type_node, PrimitiveType)
    assert type_node.name == "void"


# ============================================================================
# Type in Variable Declarations
# ============================================================================

def test_type_in_var_declaration_int():
    """Test type parsing in variable declaration context (int)."""
    source = "int x = 5"
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    stmt = parser.parse_statement()

    assert isinstance(stmt, VarDeclStmt)
    assert isinstance(stmt.var_type, PrimitiveType)
    assert stmt.var_type.name == "int"


def test_type_in_var_declaration_string():
    """Test type parsing in variable declaration context (string)."""
    source = 'string name = "Alice"'
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    stmt = parser.parse_statement()

    assert isinstance(stmt, VarDeclStmt)
    assert stmt.var_type.name == "string"


def test_type_in_var_declaration_bool():
    """Test type parsing in variable declaration context (bool)."""
    source = "bool flag = true"
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    stmt = parser.parse_statement()

    assert isinstance(stmt, VarDeclStmt)
    assert stmt.var_type.name == "bool"


def test_type_in_var_declaration_float():
    """Test type parsing in variable declaration context (float)."""
    source = "float pi = 3.14"
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    stmt = parser.parse_statement()

    assert isinstance(stmt, VarDeclStmt)
    assert stmt.var_type.name == "float"


def test_type_in_var_declaration_double():
    """Test type parsing in variable declaration context (double)."""
    source = "double bigNumber = 123.456"
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    stmt = parser.parse_statement()

    assert isinstance(stmt, VarDeclStmt)
    assert stmt.var_type.name == "double"


def test_type_in_var_declaration_char():
    """Test type parsing in variable declaration context (char)."""
    source = "char letter = 'A'"
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    stmt = parser.parse_statement()

    assert isinstance(stmt, VarDeclStmt)
    assert stmt.var_type.name == "char"


# ============================================================================
# Type in Function Declarations
# ============================================================================

def test_type_in_function_return_type():
    """Test type parsing as function return type."""
    source = """
int function add(int a, int b) {
    return a + b
}
"""
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse_program()

    func = program.declarations[0]
    assert isinstance(func.return_type, PrimitiveType)
    assert func.return_type.name == "int"


def test_type_in_function_parameters():
    """Test type parsing in function parameters."""
    source = """
int function calculate(int a, float b, string c) {
    return 0
}
"""
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse_program()

    func = program.declarations[0]
    assert len(func.parameters) == 3
    assert func.parameters[0].param_type.name == "int"
    assert func.parameters[1].param_type.name == "float"
    assert func.parameters[2].param_type.name == "string"


def test_void_return_type():
    """Test void return type in function."""
    source = """
void function printHello() {
    print("Hello")
}
"""
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse_program()

    func = program.declarations[0]
    assert func.return_type.name == "void"


def test_multiple_types_in_function():
    """Test multiple different types in single function."""
    source = """
string function process(int count, bool flag, double value) {
    return "result"
}
"""
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse_program()

    func = program.declarations[0]
    assert func.return_type.name == "string"
    assert func.parameters[0].param_type.name == "int"
    assert func.parameters[1].param_type.name == "bool"
    assert func.parameters[2].param_type.name == "double"


# ============================================================================
# Type Detection Helpers
# ============================================================================

def test_is_type_start_with_int():
    """Test is_type_start() with int keyword."""
    lexer = Lexer("int x", "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)

    assert parser.is_type_start()  # 'int' is a type


def test_is_type_start_with_identifier():
    """Test is_type_start() with identifier."""
    lexer = Lexer("x = 5", "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)

    assert not parser.is_type_start()  # 'x' is not a type


def test_is_type_start_all_types():
    """Test is_type_start() with all primitive types."""
    types = ["int", "float", "double", "string", "bool", "char", "void"]

    for type_name in types:
        lexer = Lexer(f"{type_name} x", "<test>")
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        assert parser.is_type_start(), f"Failed for type: {type_name}"


def test_check_any_helper():
    """Test check_any() helper method."""
    lexer = Lexer("int x", "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)

    # Check if current token matches any of the given types
    assert parser.check_any(TokenType.INT, TokenType.FLOAT)
    assert parser.check_any(TokenType.INT)
    assert not parser.check_any(TokenType.STRING, TokenType.BOOL)


# ============================================================================
# Error Handling
# ============================================================================

def test_error_invalid_type():
    """Test error when parsing invalid type."""
    with pytest.raises(ParserError) as exc_info:
        parse_type_from_source("invalid_type")
    assert "Expected type name" in str(exc_info.value)


def test_error_identifier_instead_of_type():
    """Test error when identifier used instead of type."""
    with pytest.raises(ParserError) as exc_info:
        parse_type_from_source("myType")
    assert "Expected type name" in str(exc_info.value)


def test_error_number_instead_of_type():
    """Test error when number used instead of type."""
    with pytest.raises(ParserError) as exc_info:
        parse_type_from_source("42")
    assert "Expected type name" in str(exc_info.value)


def test_error_keyword_instead_of_type():
    """Test error when non-type keyword used instead of type."""
    with pytest.raises(ParserError) as exc_info:
        parse_type_from_source("if")
    assert "Expected type name" in str(exc_info.value)


def test_error_empty_type():
    """Test error when trying to parse empty type."""
    with pytest.raises(ParserError) as exc_info:
        parse_type_from_source("")
    # Empty source results in EOF token
    assert "Expected type name" in str(exc_info.value) or "EOF" in str(exc_info.value)


# ============================================================================
# Edge Cases
# ============================================================================

def test_type_with_whitespace():
    """Test type parsing with surrounding whitespace."""
    source = "  int  "
    type_node = parse_type_from_source(source)
    assert type_node.name == "int"


def test_type_case_sensitivity():
    """Test that type keywords are case-sensitive."""
    # 'INT' is not the same as 'int' - lexer should treat 'INT' as identifier
    with pytest.raises(ParserError):
        parse_type_from_source("INT")


def test_multiple_var_declarations_different_types():
    """Test parsing multiple variable declarations with different types."""
    source = """int x = 1
float y = 2.5
string z = "hello"
"""
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)

    # Skip initial newlines
    while parser.peek().type == TokenType.NEWLINE:
        parser.advance()

    # Parse first statement
    stmt1 = parser.parse_statement()
    assert isinstance(stmt1, VarDeclStmt)
    assert stmt1.var_type.name == "int"

    # Skip newlines
    while parser.peek().type == TokenType.NEWLINE:
        parser.advance()

    # Parse second statement
    stmt2 = parser.parse_statement()
    assert isinstance(stmt2, VarDeclStmt)
    assert stmt2.var_type.name == "float"

    # Skip newlines
    while parser.peek().type == TokenType.NEWLINE:
        parser.advance()

    # Parse third statement
    stmt3 = parser.parse_statement()
    assert isinstance(stmt3, VarDeclStmt)
    assert stmt3.var_type.name == "string"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
