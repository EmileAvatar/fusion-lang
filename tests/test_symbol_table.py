"""Tests for symbol table, symbol, and scope classes."""

import pytest
from src.semantic import Symbol, Scope, SymbolTable, SemanticError
from src.parser.ast_nodes import PrimitiveType, FunctionType
from src.lexer.token import SourceLocation


# Test fixtures
@pytest.fixture
def location():
    """Create a test source location."""
    return SourceLocation("test.fusion", 1, 1)


@pytest.fixture
def int_type(location):
    """Create int primitive type."""
    return PrimitiveType(location, "int")


@pytest.fixture
def string_type(location):
    """Create string primitive type."""
    return PrimitiveType(location, "string")


@pytest.fixture
def void_type(location):
    """Create void primitive type."""
    return PrimitiveType(location, "void")


# ============================================================================
# Test Symbol Class (8 tests)
# ============================================================================

class TestSymbol:
    """Test Symbol class."""

    def test_create_variable_symbol(self, int_type, location):
        """Test creating a variable symbol."""
        sym = Symbol("count", "variable", int_type, location)
        assert sym.name == "count"
        assert sym.symbol_type == "variable"
        assert sym.data_type == int_type
        assert sym.location == location
        assert sym.is_constant == False
        assert sym.value is None

    def test_create_function_symbol(self, location, void_type, int_type):
        """Test creating a function symbol."""
        func_type = FunctionType(location, [int_type], void_type)
        sym = Symbol("test", "function", func_type, location)
        assert sym.name == "test"
        assert sym.symbol_type == "function"
        assert isinstance(sym.data_type, FunctionType)

    def test_create_parameter_symbol(self, string_type, location):
        """Test creating a parameter symbol."""
        sym = Symbol("name", "parameter", string_type, location)
        assert sym.name == "name"
        assert sym.symbol_type == "parameter"
        assert sym.data_type == string_type

    def test_create_constant_symbol(self, int_type, location):
        """Test creating a constant symbol."""
        sym = Symbol("PI", "constant", int_type, location, is_constant=True, value=3.14)
        assert sym.name == "PI"
        assert sym.symbol_type == "constant"
        assert sym.is_constant == True
        assert sym.value == 3.14

    def test_symbol_with_source_location(self):
        """Test symbol with source location."""
        loc = SourceLocation("main.fusion", 10, 5)
        int_type = PrimitiveType(loc, "int")
        sym = Symbol("x", "variable", int_type, loc)
        assert sym.location.filename == "main.fusion"
        assert sym.location.line == 10
        assert sym.location.column == 5

    def test_symbol_equality(self, int_type, location):
        """Test symbol equality comparison."""
        sym1 = Symbol("x", "variable", int_type, location)
        sym2 = Symbol("x", "variable", int_type, location)
        # Dataclasses support equality by default
        assert sym1 == sym2

    def test_symbol_str_representation(self, int_type, location):
        """Test symbol string representation."""
        sym = Symbol("count", "variable", int_type, location)
        s = str(sym)
        assert "variable" in s
        assert "count" in s

    def test_symbol_with_value(self, int_type, location):
        """Test symbol with compile-time value."""
        sym = Symbol("MAX", "constant", int_type, location, is_constant=True, value=100)
        assert sym.value == 100
        assert sym.is_constant == True


# ============================================================================
# Test Scope Class (12 tests)
# ============================================================================

class TestScope:
    """Test Scope class."""

    def test_create_scope_with_name(self):
        """Test creating a scope with name."""
        scope = Scope("global")
        assert scope.name == "global"
        assert scope.parent is None
        assert len(scope.symbols) == 0

    def test_define_symbol_in_scope(self, int_type, location):
        """Test defining a symbol in scope."""
        scope = Scope("global")
        sym = Symbol("x", "variable", int_type, location)
        scope.define(sym)
        assert "x" in scope.symbols
        assert scope.symbols["x"] == sym

    def test_lookup_symbol_in_scope(self, int_type, location):
        """Test looking up symbol in scope."""
        scope = Scope("global")
        sym = Symbol("x", "variable", int_type, location)
        scope.define(sym)
        found = scope.lookup("x")
        assert found == sym

    def test_lookup_nonexistent_symbol_returns_none(self):
        """Test lookup of nonexistent symbol returns None."""
        scope = Scope("global")
        found = scope.lookup("nonexistent")
        assert found is None

    def test_duplicate_declaration_raises_error(self, int_type, location):
        """Test duplicate declaration raises error."""
        scope = Scope("global")
        sym1 = Symbol("x", "variable", int_type, location)
        sym2 = Symbol("x", "variable", int_type, location)
        scope.define(sym1)
        with pytest.raises(SemanticError) as exc_info:
            scope.define(sym2)
        assert "Duplicate declaration" in str(exc_info.value)
        assert "'x'" in str(exc_info.value)

    def test_recursive_lookup_finds_parent_symbol(self, int_type, location):
        """Test recursive lookup finds symbol in parent scope."""
        parent = Scope("global")
        child = Scope("function:main", parent=parent)

        sym = Symbol("x", "variable", int_type, location)
        parent.define(sym)

        found = child.lookup_recursive("x")
        assert found == sym

    def test_recursive_lookup_returns_none_if_not_found(self):
        """Test recursive lookup returns None if not found."""
        parent = Scope("global")
        child = Scope("function:main", parent=parent)

        found = child.lookup_recursive("nonexistent")
        assert found is None

    def test_child_scope_shadows_parent_symbol(self, int_type, location):
        """Test child scope shadows parent symbol."""
        parent = Scope("global")
        child = Scope("function:main", parent=parent)

        parent_sym = Symbol("x", "variable", int_type, location)
        child_sym = Symbol("x", "variable", int_type, location)

        parent.define(parent_sym)
        child.define(child_sym)

        # Child scope lookup should find child's symbol (not parent's)
        found = child.lookup_recursive("x")
        assert found == child_sym
        # Note: found == parent_sym due to dataclass equality, but it's from child scope
        assert found is child_sym  # Use identity check instead

    def test_scope_hierarchy_grandparent_lookup(self, int_type, location):
        """Test scope hierarchy with grandparent lookup."""
        grandparent = Scope("global")
        parent = Scope("function:main", parent=grandparent)
        child = Scope("block:1", parent=parent)

        sym = Symbol("x", "variable", int_type, location)
        grandparent.define(sym)

        found = child.lookup_recursive("x")
        assert found == sym

    def test_scope_name_tracking(self):
        """Test scope name tracking."""
        scope = Scope("function:add")
        assert scope.name == "function:add"

    def test_empty_scope(self):
        """Test empty scope."""
        scope = Scope("global")
        assert len(scope.symbols) == 0
        assert scope.lookup("anything") is None

    def test_multiple_symbols_in_scope(self, int_type, string_type, location):
        """Test multiple symbols in scope."""
        scope = Scope("global")
        sym1 = Symbol("x", "variable", int_type, location)
        sym2 = Symbol("y", "variable", string_type, location)
        sym3 = Symbol("z", "variable", int_type, location)

        scope.define(sym1)
        scope.define(sym2)
        scope.define(sym3)

        assert len(scope.symbols) == 3
        assert scope.lookup("x") == sym1
        assert scope.lookup("y") == sym2
        assert scope.lookup("z") == sym3


# ============================================================================
# Test SymbolTable (20+ tests)
# ============================================================================

class TestSymbolTable:
    """Test SymbolTable class."""

    def test_initialize_with_global_scope(self):
        """Test symbol table initializes with global scope."""
        st = SymbolTable()
        assert st.global_scope is not None
        assert st.global_scope.name == "global"
        assert st.current_scope == st.global_scope
        assert len(st.scope_stack) == 1

    def test_enter_nested_scope(self):
        """Test entering a nested scope."""
        st = SymbolTable()
        st.enter_scope("function:main")
        assert st.current_scope.name == "function:main"
        assert len(st.scope_stack) == 2
        assert st.current_scope.parent == st.global_scope

    def test_exit_nested_scope(self):
        """Test exiting a nested scope."""
        st = SymbolTable()
        st.enter_scope("function:main")
        st.exit_scope()
        assert st.current_scope == st.global_scope
        assert len(st.scope_stack) == 1

    def test_cannot_exit_global_scope(self):
        """Test cannot exit global scope."""
        st = SymbolTable()
        with pytest.raises(SemanticError) as exc_info:
            st.exit_scope()
        assert "Cannot exit global scope" in str(exc_info.value)

    def test_define_symbol_in_global_scope(self, int_type, location):
        """Test defining symbol in global scope."""
        st = SymbolTable()
        sym = Symbol("x", "variable", int_type, location)
        st.define(sym)
        assert st.global_scope.lookup("x") == sym

    def test_define_symbol_in_nested_scope(self, int_type, location):
        """Test defining symbol in nested scope."""
        st = SymbolTable()
        st.enter_scope("function:main")
        sym = Symbol("x", "variable", int_type, location)
        st.define(sym)
        assert st.current_scope.lookup("x") == sym
        assert st.global_scope.lookup("x") is None

    def test_lookup_in_current_scope(self, int_type, location):
        """Test lookup in current scope."""
        st = SymbolTable()
        sym = Symbol("x", "variable", int_type, location)
        st.define(sym)
        found = st.lookup("x")
        assert found == sym

    def test_lookup_in_parent_scope(self, int_type, location):
        """Test lookup in parent scope."""
        st = SymbolTable()
        sym = Symbol("x", "variable", int_type, location)
        st.define(sym)

        st.enter_scope("function:main")
        found = st.lookup("x")
        assert found == sym

    def test_lookup_in_global_scope_from_nested(self, int_type, location):
        """Test lookup in global scope from nested scope."""
        st = SymbolTable()
        sym = Symbol("x", "variable", int_type, location)
        st.define(sym)

        st.enter_scope("function:main")
        st.enter_scope("block:1")
        found = st.lookup("x")
        assert found == sym

    def test_symbol_shadowing(self, int_type, location):
        """Test symbol shadowing (child hides parent)."""
        st = SymbolTable()
        global_sym = Symbol("x", "variable", int_type, location)
        st.define(global_sym)

        st.enter_scope("function:main")
        local_sym = Symbol("x", "variable", int_type, location)
        st.define(local_sym)

        found = st.lookup("x")
        assert found == local_sym
        # Use identity check (dataclasses with same values are equal)
        assert found is local_sym

    def test_multiple_nested_scopes(self, int_type, location):
        """Test multiple nested scopes."""
        st = SymbolTable()
        st.enter_scope("function:main")
        st.enter_scope("block:1")
        st.enter_scope("block:2")

        assert len(st.scope_stack) == 4
        assert st.current_scope.name == "block:2"

        sym = Symbol("x", "variable", int_type, location)
        st.define(sym)

        found = st.lookup("x")
        assert found == sym

    def test_scope_stack_tracking(self):
        """Test scope stack tracking."""
        st = SymbolTable()
        assert len(st.scope_stack) == 1

        st.enter_scope("function:main")
        assert len(st.scope_stack) == 2

        st.enter_scope("block:1")
        assert len(st.scope_stack) == 3

        st.exit_scope()
        assert len(st.scope_stack) == 2

        st.exit_scope()
        assert len(st.scope_stack) == 1

    def test_is_defined_in_current_scope_true(self, int_type, location):
        """Test is_defined_in_current_scope returns True."""
        st = SymbolTable()
        sym = Symbol("x", "variable", int_type, location)
        st.define(sym)
        assert st.is_defined_in_current_scope("x") == True

    def test_is_defined_in_current_scope_false_parent_has_it(self, int_type, location):
        """Test is_defined_in_current_scope returns False when parent has it."""
        st = SymbolTable()
        sym = Symbol("x", "variable", int_type, location)
        st.define(sym)

        st.enter_scope("function:main")
        assert st.is_defined_in_current_scope("x") == False

    def test_define_multiple_symbols(self, int_type, string_type, location):
        """Test defining multiple symbols."""
        st = SymbolTable()
        sym1 = Symbol("x", "variable", int_type, location)
        sym2 = Symbol("y", "variable", string_type, location)
        sym3 = Symbol("z", "variable", int_type, location)

        st.define(sym1)
        st.define(sym2)
        st.define(sym3)

        assert st.lookup("x") == sym1
        assert st.lookup("y") == sym2
        assert st.lookup("z") == sym3

    def test_lookup_nonexistent_symbol(self):
        """Test lookup of nonexistent symbol."""
        st = SymbolTable()
        found = st.lookup("nonexistent")
        assert found is None

    def test_complex_nesting_3plus_levels(self, location):
        """Test complex nesting (3+ levels)."""
        st = SymbolTable()
        int_type = PrimitiveType(location, "int")

        # Level 0: global
        global_sym = Symbol("a", "variable", int_type, location)
        st.define(global_sym)

        # Level 1: function
        st.enter_scope("function:main")
        func_sym = Symbol("b", "variable", int_type, location)
        st.define(func_sym)

        # Level 2: block
        st.enter_scope("block:1")
        block1_sym = Symbol("c", "variable", int_type, location)
        st.define(block1_sym)

        # Level 3: nested block
        st.enter_scope("block:2")
        block2_sym = Symbol("d", "variable", int_type, location)
        st.define(block2_sym)

        # Can look up all symbols from deepest scope
        assert st.lookup("a") == global_sym
        assert st.lookup("b") == func_sym
        assert st.lookup("c") == block1_sym
        assert st.lookup("d") == block2_sym

    def test_scope_names(self):
        """Test scope names (function:add, block:1)."""
        st = SymbolTable()
        st.enter_scope("function:add")
        assert st.current_scope.name == "function:add"

        st.enter_scope("block:for")
        assert st.current_scope.name == "block:for"

    def test_enter_exit_multiple_times(self):
        """Test entering and exiting scopes multiple times."""
        st = SymbolTable()

        st.enter_scope("function:test1")
        st.exit_scope()

        st.enter_scope("function:test2")
        st.exit_scope()

        st.enter_scope("function:test3")
        assert st.current_scope.name == "function:test3"
        st.exit_scope()

        assert st.current_scope == st.global_scope

    def test_current_scope_tracking(self):
        """Test current scope tracking."""
        st = SymbolTable()
        assert st.current_scope.name == "global"

        st.enter_scope("function:main")
        assert st.current_scope.name == "function:main"

        st.enter_scope("block:1")
        assert st.current_scope.name == "block:1"

        st.exit_scope()
        assert st.current_scope.name == "function:main"

    def test_get_current_scope_name(self):
        """Test get_current_scope_name method."""
        st = SymbolTable()
        assert st.get_current_scope_name() == "global"

        st.enter_scope("function:test")
        assert st.get_current_scope_name() == "function:test"

    def test_get_scope_depth(self):
        """Test get_scope_depth method."""
        st = SymbolTable()
        assert st.get_scope_depth() == 0

        st.enter_scope("function:main")
        assert st.get_scope_depth() == 1

        st.enter_scope("block:1")
        assert st.get_scope_depth() == 2

        st.exit_scope()
        assert st.get_scope_depth() == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
