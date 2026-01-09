"""Symbol table for managing scopes and symbol resolution."""

from typing import Optional, List
from .symbol import Symbol, Scope
from .errors import SemanticError


class SymbolTable:
    """Manages scopes and symbol resolution.

    The symbol table maintains a stack of scopes, with the global scope at
    the bottom and nested scopes (function, block, etc.) on top.

    Attributes:
        global_scope: The global scope (bottom of stack)
        current_scope: The currently active scope (top of stack)
        scope_stack: Stack of all active scopes
    """

    def __init__(self):
        """Initialize symbol table with global scope."""
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        self.scope_stack: List[Scope] = [self.global_scope]

    def enter_scope(self, name: str) -> None:
        """Enter a new nested scope.

        Args:
            name: Name for the new scope (e.g., "function:main", "block:1")
        """
        new_scope = Scope(name, parent=self.current_scope)
        self.scope_stack.append(new_scope)
        self.current_scope = new_scope

    def exit_scope(self) -> None:
        """Exit the current scope and return to parent.

        Raises:
            SemanticError: If attempting to exit global scope
        """
        if len(self.scope_stack) <= 1:
            raise SemanticError("Cannot exit global scope")
        self.scope_stack.pop()
        self.current_scope = self.scope_stack[-1]

    def define(self, symbol: Symbol) -> None:
        """Define a symbol in the current scope.

        Args:
            symbol: Symbol to define

        Raises:
            SemanticError: If symbol is already defined in current scope
        """
        self.current_scope.define(symbol)

    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol starting from current scope.

        Searches current scope and all parent scopes recursively.

        Args:
            name: Symbol name to look up

        Returns:
            Symbol if found, None otherwise
        """
        return self.current_scope.lookup_recursive(name)

    def is_defined_in_current_scope(self, name: str) -> bool:
        """Check if symbol exists in current scope (not parent scopes).

        Args:
            name: Symbol name to check

        Returns:
            True if symbol is defined in current scope, False otherwise
        """
        return self.current_scope.lookup(name) is not None

    def get_current_scope_name(self) -> str:
        """Get the name of the current scope.

        Returns:
            Current scope name
        """
        return self.current_scope.name

    def get_scope_depth(self) -> int:
        """Get the current scope nesting depth.

        Returns:
            Scope depth (0 = global, 1 = first nested scope, etc.)
        """
        return len(self.scope_stack) - 1

    def __str__(self) -> str:
        """Return string representation."""
        scopes = " -> ".join(scope.name for scope in self.scope_stack)
        return f"SymbolTable({scopes})"

    def __repr__(self) -> str:
        """Return repr string."""
        return f"SymbolTable(depth={self.get_scope_depth()}, current={self.current_scope.name!r})"
