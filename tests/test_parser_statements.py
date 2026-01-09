"""
Tests for Statement Parsing

This module tests the parser's ability to parse statements:
- Simple statements (var decl, assignment, return, expression)
- Control flow statements (if, while, for)
- Block statements (braces, indentation, End keywords)
"""

import pytest
from src.parser.parser import Parser, ParserError
from src.parser.ast_nodes import *
from src.lexer.lexer import Lexer
from src.lexer.token import TokenType


def parse_stmt(source: str) -> ASTNode:
    """Helper: tokenize and parse statement."""
    lexer = Lexer(source, "<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse_statement()


# ============================================================================
# Simple Statements
# ============================================================================

def test_var_declaration_with_initializer():
    """Test variable declaration: int x = 5"""
    stmt = parse_stmt("int x = 5")
    assert isinstance(stmt, VarDeclStmt)
    assert stmt.name == "x"
    assert isinstance(stmt.var_type, PrimitiveType)
    assert stmt.var_type.name == "int"
    assert isinstance(stmt.initializer, LiteralExpr)
    assert stmt.initializer.value == 5


def test_var_declaration_without_initializer():
    """Test variable declaration without initializer: int x"""
    stmt = parse_stmt("int x")
    assert isinstance(stmt, VarDeclStmt)
    assert stmt.name == "x"
    assert stmt.var_type.name == "int"
    assert stmt.initializer is None


def test_var_declaration_string():
    """Test string variable declaration: string name = "Alice" """
    stmt = parse_stmt('string name = "Alice"')
    assert isinstance(stmt, VarDeclStmt)
    assert stmt.name == "name"
    assert stmt.var_type.name == "string"
    assert stmt.initializer.value == "Alice"


def test_var_declaration_float():
    """Test float variable declaration: float pi = 3.14"""
    stmt = parse_stmt("float pi = 3.14")
    assert isinstance(stmt, VarDeclStmt)
    assert stmt.name == "pi"
    assert stmt.var_type.name == "float"
    assert isinstance(stmt.initializer, LiteralExpr)
    assert stmt.initializer.value == 3.14


def test_var_declaration_bool():
    """Test bool variable declaration: bool flag = true"""
    stmt = parse_stmt("bool flag = true")
    assert isinstance(stmt, VarDeclStmt)
    assert stmt.name == "flag"
    assert stmt.var_type.name == "bool"
    assert stmt.initializer.value is True


def test_assignment():
    """Test assignment: x = 10"""
    stmt = parse_stmt("x = 10")
    assert isinstance(stmt, AssignmentStmt)
    assert isinstance(stmt.target, IdentifierExpr)
    assert stmt.target.name == "x"
    assert isinstance(stmt.value, LiteralExpr)
    assert stmt.value.value == 10


def test_assignment_expression():
    """Test assignment with expression: x = y + 5"""
    stmt = parse_stmt("x = y + 5")
    assert isinstance(stmt, AssignmentStmt)
    assert stmt.target.name == "x"
    assert isinstance(stmt.value, BinaryExpr)
    assert stmt.value.operator == "+"


def test_expression_statement():
    """Test expression statement: print(x)"""
    stmt = parse_stmt("print(x)")
    assert isinstance(stmt, ExpressionStmt)
    assert isinstance(stmt.expression, CallExpr)


def test_return_with_value():
    """Test return statement: return 42"""
    stmt = parse_stmt("return 42")
    assert isinstance(stmt, ReturnStmt)
    assert isinstance(stmt.value, LiteralExpr)
    assert stmt.value.value == 42


def test_return_without_value():
    """Test return without value: return"""
    stmt = parse_stmt("return")
    assert isinstance(stmt, ReturnStmt)
    assert stmt.value is None


def test_return_expression():
    """Test return with expression: return x + y"""
    stmt = parse_stmt("return x + y")
    assert isinstance(stmt, ReturnStmt)
    assert isinstance(stmt.value, BinaryExpr)
    assert stmt.value.operator == "+"


def test_expression_statement_no_semicolon():
    """Test expression statement without semicolon: print(x)"""
    stmt = parse_stmt("print(x)")
    assert isinstance(stmt, ExpressionStmt)
    assert isinstance(stmt.expression, CallExpr)


# ============================================================================
# Control Flow Statements - If
# ============================================================================

def test_if_statement_brace_block():
    """Test if statement with braces: if x > 0 { return x }"""
    source = """if x > 0 {
    return x
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    assert isinstance(stmt.condition, BinaryExpr)
    assert stmt.condition.operator == ">"
    assert isinstance(stmt.then_branch, BlockStmt)
    assert len(stmt.then_branch.statements) == 1
    assert isinstance(stmt.then_branch.statements[0], ReturnStmt)
    assert stmt.else_branch is None


def test_if_else_statement():
    """Test if-else: if x > 0 { return x } else { return 0 }"""
    source = """if x > 0 {
    return x
} else {
    return 0
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    assert stmt.else_branch is not None
    assert isinstance(stmt.else_branch, BlockStmt)
    assert len(stmt.else_branch.statements) == 1


def test_if_elif_else():
    """Test if-elif-else chain"""
    source = """if x > 0 {
    return 1
} else if x < 0 {
    return -1
} else {
    return 0
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    assert isinstance(stmt.else_branch, IfStmt)  # elif is nested if
    assert isinstance(stmt.else_branch.else_branch, BlockStmt)


def test_if_with_complex_condition():
    """Test if with complex condition: if x > 0 and y < 10"""
    source = """if x > 0 and y < 10 {
    return x
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    assert isinstance(stmt.condition, BinaryExpr)
    assert stmt.condition.operator == "and"


def test_nested_if_statements():
    """Test nested if statements"""
    source = """if x > 0 {
    if y > 0 {
        return x + y
    }
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    inner_stmt = stmt.then_branch.statements[0]
    assert isinstance(inner_stmt, IfStmt)


# ============================================================================
# Control Flow Statements - While
# ============================================================================

def test_while_loop_brace_block():
    """Test while loop: while x > 0 { x = x - 1 }"""
    source = """while x > 0 {
    x = x - 1
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, WhileStmt)
    assert isinstance(stmt.condition, BinaryExpr)
    assert stmt.condition.operator == ">"
    assert isinstance(stmt.body, BlockStmt)
    assert len(stmt.body.statements) == 1
    assert isinstance(stmt.body.statements[0], AssignmentStmt)


def test_while_with_complex_condition():
    """Test while with complex condition"""
    source = """while x > 0 and y < 10 {
    x = x - 1
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, WhileStmt)
    assert isinstance(stmt.condition, BinaryExpr)
    assert stmt.condition.operator == "and"


def test_nested_while_loops():
    """Test nested while loops"""
    source = """while x > 0 {
    while y > 0 {
        y = y - 1
    }
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, WhileStmt)
    inner_stmt = stmt.body.statements[0]
    assert isinstance(inner_stmt, WhileStmt)


# ============================================================================
# Control Flow Statements - For
# ============================================================================

def test_for_loop_brace_block():
    """Test for loop: for i in range { print(i) }"""
    source = """for i in range {
    print(i)
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, ForStmt)
    assert stmt.variable == "i"
    assert isinstance(stmt.iterable, IdentifierExpr)
    assert stmt.iterable.name == "range"
    assert isinstance(stmt.body, BlockStmt)


def test_for_loop_with_function_call():
    """Test for loop with function call: for i in getItems()"""
    source = """for i in getItems() {
    print(i)
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, ForStmt)
    assert stmt.variable == "i"
    assert isinstance(stmt.iterable, CallExpr)


def test_nested_for_loops():
    """Test nested for loops"""
    source = """for i in range1 {
    for j in range2 {
        print(i)
    }
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, ForStmt)
    inner_stmt = stmt.body.statements[0]
    assert isinstance(inner_stmt, ForStmt)


# ============================================================================
# Block Statements - Indentation
# ============================================================================

def test_if_indentation_block():
    """Test if with indentation block"""
    source = """if x > 0
    return x"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    assert isinstance(stmt.then_branch, BlockStmt)


def test_while_indentation_block():
    """Test while with indentation block"""
    source = """while x > 0
    x = x - 1"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, WhileStmt)
    assert isinstance(stmt.body, BlockStmt)


def test_for_indentation_block():
    """Test for with indentation block"""
    source = """for i in range
    print(i)"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, ForStmt)
    assert isinstance(stmt.body, BlockStmt)


def test_if_else_indentation_block():
    """Test if-else with indentation"""
    source = """if x > 0
    return x
else
    return 0"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    assert isinstance(stmt.then_branch, BlockStmt)
    assert isinstance(stmt.else_branch, BlockStmt)


def test_nested_indentation_blocks():
    """Test nested indentation blocks"""
    source = """if x > 0
    if y > 0
        return x + y"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    assert isinstance(stmt.then_branch, BlockStmt)
    inner = stmt.then_branch.statements[0]
    assert isinstance(inner, IfStmt)


# ============================================================================
# Block Statements - End Keywords
# ============================================================================

def test_if_end_keyword():
    """Test if with End keyword: if x > 0 ... End if"""
    source = """if x > 0
    return x
End if"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    assert isinstance(stmt.then_branch, BlockStmt)


def test_while_end_keyword():
    """Test while with End keyword"""
    source = """while x > 0
    x = x - 1
End while"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, WhileStmt)
    assert isinstance(stmt.body, BlockStmt)


def test_for_end_keyword():
    """Test for with End keyword"""
    source = """for i in range
    print(i)
End for"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, ForStmt)
    assert isinstance(stmt.body, BlockStmt)


# ============================================================================
# Block Statements - Empty Blocks
# ============================================================================

def test_empty_brace_block():
    """Test empty brace block: if x > 0 {}"""
    source = """if x > 0 {
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    assert isinstance(stmt.then_branch, BlockStmt)
    assert len(stmt.then_branch.statements) == 0


# ============================================================================
# Complex Statements
# ============================================================================

def test_multiple_statements_in_block():
    """Test multiple statements in block"""
    source = """{
    int x = 5
    int y = 10
    return x + y
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, BlockStmt)
    assert len(stmt.statements) == 3
    assert isinstance(stmt.statements[0], VarDeclStmt)
    assert isinstance(stmt.statements[1], VarDeclStmt)
    assert isinstance(stmt.statements[2], ReturnStmt)


def test_mixed_statements_in_if():
    """Test mixed statements in if block"""
    source = """if x > 0 {
    int temp = x
    temp = temp + 1
    return temp
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    assert len(stmt.then_branch.statements) == 3


def test_complex_nested_structure():
    """Test complex nested control flow"""
    source = """if x > 0 {
    while y > 0 {
        for i in range {
            int temp = i
            print(temp)
        }
        y = y - 1
    }
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    while_stmt = stmt.then_branch.statements[0]
    assert isinstance(while_stmt, WhileStmt)
    for_stmt = while_stmt.body.statements[0]
    assert isinstance(for_stmt, ForStmt)


# ============================================================================
# Error Handling
# ============================================================================

def test_error_missing_variable_name():
    """Test error: variable declaration without name"""
    with pytest.raises(ParserError) as exc_info:
        parse_stmt("int = 5")
    assert "Expected variable name" in str(exc_info.value)


def test_error_missing_semicolon_allowed():
    """Test that semicolons are optional (no error)"""
    # Should NOT raise error
    stmt = parse_stmt("int x = 5")
    assert isinstance(stmt, VarDeclStmt)


def test_error_missing_condition():
    """Test error: if without condition"""
    with pytest.raises(ParserError) as exc_info:
        parse_stmt("if { return 1 }")
    assert "expected expression" in str(exc_info.value).lower()


def test_error_missing_loop_variable():
    """Test error: for without loop variable"""
    with pytest.raises(ParserError) as exc_info:
        parse_stmt("for in range { print(i) }")
    assert "Expected loop variable name" in str(exc_info.value)


def test_error_missing_in_keyword():
    """Test error: for without 'in' keyword"""
    with pytest.raises(ParserError) as exc_info:
        parse_stmt("for i range { print(i) }")
    assert "Expected 'in' after loop variable" in str(exc_info.value)


def test_error_unclosed_brace_block():
    """Test error: unclosed brace block"""
    with pytest.raises(ParserError) as exc_info:
        parse_stmt("if x > 0 { return x")
    assert "Expected '}' after block" in str(exc_info.value)


def test_error_wrong_end_keyword():
    """Test error: End with wrong keyword"""
    # Note: This test is tricky because the lexer tokenizes multi-line input
    # For now, we'll just verify that parse_if_statement validates End keywords
    with pytest.raises(ParserError) as exc_info:
        source = """if x > 0
    return x
End while"""
        parse_stmt(source)
    # The error might happen earlier in parsing due to indentation
    assert "Expected" in str(exc_info.value) or "Unexpected" in str(exc_info.value)


# ============================================================================
# Edge Cases
# ============================================================================

def test_single_statement_no_block():
    """Test single statement without block (for End keyword style)"""
    source = """if x > 0
    return x"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    # Parser wraps single statements in BlockStmt
    assert isinstance(stmt.then_branch, BlockStmt)


def test_assignment_to_complex_expression():
    """Test assignment with complex left side: a + b (should work for now)"""
    # Note: Semantic analyzer will catch invalid assignments later
    stmt = parse_stmt("x = a + b")
    assert isinstance(stmt, AssignmentStmt)
    assert isinstance(stmt.value, BinaryExpr)


def test_return_complex_expression():
    """Test return with complex expression"""
    stmt = parse_stmt("return (x + y) * z")
    assert isinstance(stmt, ReturnStmt)
    assert isinstance(stmt.value, BinaryExpr)


def test_chained_comparisons():
    """Test if with chained comparison: if x > 0 and x < 10"""
    source = """if x > 0 and x < 10 {
    return x
}"""
    stmt = parse_stmt(source)
    assert isinstance(stmt, IfStmt)
    assert isinstance(stmt.condition, BinaryExpr)
    assert stmt.condition.operator == "and"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
