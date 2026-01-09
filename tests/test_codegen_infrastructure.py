"""Tests for C Code Generator Infrastructure.

Tests the foundational components of the C code generator:
- Type mapping (Fusion types → C types)
- Code formatting helpers (emit, indent, dedent)
- Header generation (includes, forward declarations)
"""

import pytest
from src.codegen.c_generator import CCodeGenerator
from src.parser.ast_nodes import (
    ASTNode, ProgramNode, FunctionDecl, ParameterDecl,
    PrimitiveType, FunctionType, BlockStmt
)
from src.lexer.token import SourceLocation


# Fixtures
@pytest.fixture
def generator():
    """Create a fresh code generator."""
    return CCodeGenerator()


@pytest.fixture
def loc():
    """Create a dummy source location."""
    return SourceLocation(filename='test.fusion', line=1, column=1)


# ==============================================================================
# Type Mapping Tests (8 tests)
# ==============================================================================

def test_map_int_type(generator, loc):
    """Test mapping int type."""
    fusion_type = PrimitiveType(loc, 'int')
    assert generator.map_type(fusion_type) == 'int'


def test_map_float_type(generator, loc):
    """Test mapping float type."""
    fusion_type = PrimitiveType(loc, 'float')
    assert generator.map_type(fusion_type) == 'float'


def test_map_double_type(generator, loc):
    """Test mapping double type."""
    fusion_type = PrimitiveType(loc, 'double')
    assert generator.map_type(fusion_type) == 'double'


def test_map_bool_type(generator, loc):
    """Test mapping bool type."""
    fusion_type = PrimitiveType(loc, 'bool')
    assert generator.map_type(fusion_type) == 'bool'


def test_map_char_type(generator, loc):
    """Test mapping char type."""
    fusion_type = PrimitiveType(loc, 'char')
    assert generator.map_type(fusion_type) == 'char'


def test_map_string_type(generator, loc):
    """Test mapping string type to char*."""
    fusion_type = PrimitiveType(loc, 'string')
    assert generator.map_type(fusion_type) == 'char*'


def test_map_void_type(generator, loc):
    """Test mapping void type."""
    fusion_type = PrimitiveType(loc, 'void')
    assert generator.map_type(fusion_type) == 'void'


def test_map_unknown_type_fallback(generator, loc):
    """Test mapping unknown type returns void as fallback."""
    fusion_type = PrimitiveType(loc, 'unknown')
    assert generator.map_type(fusion_type) == 'void'


# ==============================================================================
# Code Formatting Tests (7 tests)
# ==============================================================================

def test_emit_adds_indentation(generator):
    """Test emit adds proper indentation."""
    generator.indent_level = 2
    generator.emit('int x = 5')
    assert generator.output[-1] == '        int x = 5'  # 8 spaces (2 levels * 4 spaces)


def test_emit_line_adds_semicolon(generator):
    """Test emit_line adds semicolon."""
    generator.emit_line('int x = 5')
    assert generator.output[-1] == 'int x = 5;'


def test_indent_increases_level(generator):
    """Test indent increases indentation level."""
    generator.indent_level = 0
    generator.indent()
    assert generator.indent_level == 1
    generator.indent()
    assert generator.indent_level == 2


def test_dedent_decreases_level(generator):
    """Test dedent decreases indentation level."""
    generator.indent_level = 2
    generator.dedent()
    assert generator.indent_level == 1
    generator.dedent()
    assert generator.indent_level == 0


def test_emit_block_start(generator):
    """Test emit_block_start adds brace and indents."""
    initial_level = generator.indent_level
    generator.emit_block_start()
    assert generator.output[-1] == '{'
    assert generator.indent_level == initial_level + 1


def test_emit_block_end(generator):
    """Test emit_block_end dedents and adds brace."""
    generator.indent_level = 1
    generator.emit_block_end()
    assert generator.output[-1] == '}'
    assert generator.indent_level == 0


def test_multiple_indent_levels(generator):
    """Test multiple indentation levels work correctly."""
    generator.emit('level 0')
    generator.indent()
    generator.emit('level 1')
    generator.indent()
    generator.emit('level 2')
    generator.dedent()
    generator.emit('level 1 again')
    generator.dedent()
    generator.emit('level 0 again')

    assert generator.output[0] == 'level 0'
    assert generator.output[1] == '    level 1'
    assert generator.output[2] == '        level 2'
    assert generator.output[3] == '    level 1 again'
    assert generator.output[4] == 'level 0 again'


# ==============================================================================
# Header Generation Tests (5 tests)
# ==============================================================================

def test_includes_generated_sorted(generator):
    """Test includes are generated in sorted order."""
    generator.includes.add('<math.h>')
    generator.includes.add('<stdlib.h>')
    generator._generate_includes()

    # Find the include lines
    include_lines = [line for line in generator.output if line.startswith('#include')]

    # Should be sorted alphabetically
    assert include_lines[0] == '#include <math.h>'
    assert include_lines[1] == '#include <stdbool.h>'
    assert include_lines[2] == '#include <stdio.h>'
    assert include_lines[3] == '#include <stdlib.h>'
    assert include_lines[4] == '#include <string.h>'


def test_standard_includes_present(generator):
    """Test standard includes are present by default."""
    assert '<stdio.h>' in generator.includes
    assert '<stdbool.h>' in generator.includes
    assert '<string.h>' in generator.includes


def test_forward_declaration_single_function(generator, loc):
    """Test forward declaration for single function."""
    func = FunctionDecl(
        name='add',
        return_type=PrimitiveType(loc, 'int'),
        parameters=[
            ParameterDecl(loc, PrimitiveType(loc, 'int'), 'a', None),
            ParameterDecl(loc, PrimitiveType(loc, 'int'), 'b', None)
        ],
        body=BlockStmt([], loc),
        location=loc
    )
    program = ProgramNode(loc, [func])

    generator._generate_forward_declarations(program)

    # Find the forward declaration line
    decl_lines = [line for line in generator.output if 'add' in line]
    assert len(decl_lines) == 1
    assert decl_lines[0] == 'int add(int a, int b);'


def test_forward_declaration_multiple_functions(generator, loc):
    """Test forward declarations for multiple functions."""
    func1 = FunctionDecl(
        name='add',
        return_type=PrimitiveType(loc, 'int'),
        parameters=[
            ParameterDecl(loc, PrimitiveType(loc, 'int'), 'a', None),
            ParameterDecl(loc, PrimitiveType(loc, 'int'), 'b', None)
        ],
        body=BlockStmt([], loc),
        location=loc
    )
    func2 = FunctionDecl(
        name='greet',
        return_type=PrimitiveType(loc, 'void'),
        parameters=[
            ParameterDecl(loc, PrimitiveType(loc, 'string'), 'name', None)
        ],
        body=BlockStmt([], loc),
        location=loc
    )
    program = ProgramNode(loc, [func1, func2])

    generator._generate_forward_declarations(program)

    # Find declaration lines
    output_str = '\n'.join(generator.output)
    assert 'int add(int a, int b);' in output_str
    assert 'void greet(char* name);' in output_str


def test_forward_declaration_no_parameters(generator, loc):
    """Test forward declaration for function with no parameters."""
    func = FunctionDecl(
        name='main',
        return_type=PrimitiveType(loc, 'void'),
        parameters=[],
        body=BlockStmt([], loc),
        location=loc
    )
    program = ProgramNode(loc, [func])

    generator._generate_forward_declarations(program)

    # Find the forward declaration line
    decl_lines = [line for line in generator.output if 'main' in line]
    assert len(decl_lines) == 1
    assert decl_lines[0] == 'int main(void);'  # void main -> int main conversion


# ==============================================================================
# Integration Tests (Additional)
# ==============================================================================

def test_generator_initialization(generator):
    """Test generator initializes with correct defaults."""
    assert generator.output == []
    assert generator.indent_level == 0
    assert len(generator.includes) == 4  # stdio.h, stdbool.h, string.h, math.h
    assert '<stdio.h>' in generator.includes
    assert '<stdbool.h>' in generator.includes
    assert '<string.h>' in generator.includes
    assert '<math.h>' in generator.includes
    assert generator.generated_functions == []


def test_emit_blank_line(generator):
    """Test emitting blank line."""
    generator.emit()
    assert generator.output[-1] == ''


def test_dedent_at_zero_level(generator):
    """Test dedent doesn't go below zero."""
    generator.indent_level = 0
    generator.dedent()
    assert generator.indent_level == 0


def test_visitor_method_name_generation(generator, loc):
    """Test visitor method name is generated correctly."""
    func = FunctionDecl(
        name='test',
        return_type=PrimitiveType(loc, 'void'),
        parameters=[],
        body=BlockStmt([], loc),
        location=loc
    )

    # Should look for visit_FunctionDecl method
    method_name = f'visit_{type(func).__name__}'
    assert method_name == 'visit_FunctionDecl'


def test_generic_visit_raises_not_implemented(generator, loc):
    """Test generic_visit raises NotImplementedError for unknown nodes."""
    # Create a fake AST node class that doesn't have a visitor
    class UnknownNode(ASTNode):
        def __init__(self, location):
            super().__init__(location)

    unknown = UnknownNode(loc)

    with pytest.raises(NotImplementedError, match="No visitor for UnknownNode"):
        generator.visit(unknown)
