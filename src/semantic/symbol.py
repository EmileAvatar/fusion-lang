"""Symbol and Scope classes for symbol table management."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from src.lexer.token import SourceLocation
from src.parser.ast_nodes import TypeNode
from .errors import SemanticError


@dataclass
class Symbol:
    """Represents a variable, function, or parameter in the symbol table.

    Attributes:
        name: Identifier name (e.g., "count", "add")
        symbol_type: Kind of symbol ('variable', 'function', 'parameter', 'constant')
        data_type: Fusion type from AST (PrimitiveType, FunctionType, etc.)
        location: Source location where symbol was declared
        is_constant: True for const declarations
        value: Compile-time constant value (if known)
    """
    name: str
    symbol_type: str  # 'variable', 'function', 'parameter', 'constant'
    data_type: TypeNode
    location: SourceLocation
    is_constant: bool = False
    value: Optional[Any] = None

    def __str__(self) -> str:
        """Return string representation."""
        const_str = " const" if self.is_constant else ""
        return f"{self.symbol_type}{const_str} {self.name}: {self.data_type}"

    def __repr__(self) -> str:
        """Return repr string."""
        return (f"Symbol({self.name!r}, {self.symbol_type!r}, "
                f"{self.data_type!r}, {self.location!r})")


class Scope:
    """Represents a single scope (global, function, block).

    A scope contains a collection of symbols and can have a parent scope
    for nested scope resolution.

    Attributes:
        name: Scope name (e.g., "global", "function:add", "block:1")
        parent: Parent scope (None for global scope)
        symbols: Dictionary mapping symbol names to Symbol objects
    """

    def __init__(self, name: str, parent: Optional['Scope'] = None):
        """Initialize a scope.

        Args:
            name: Scope name
            parent: Parent scope (None for global scope)
        """
        self.name = name
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}

    def define(self, symbol: Symbol) -> None:
        """Add a symbol to this scope.

        Args:
            symbol: Symbol to add

        Raises:
            SemanticError: If symbol is already defined in this scope
        """
        if symbol.name in self.symbols:
            existing = self.symbols[symbol.name]
            raise SemanticError(
                f"Duplicate declaration of '{symbol.name}' "
                f"(previously declared at {existing.location})",
                symbol.location
            )
        self.symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope only.

        Args:
            name: Symbol name to look up

        Returns:
            Symbol if found, None otherwise
        """
        return self.symbols.get(name)

    def lookup_recursive(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope and parent scopes.

        Args:
            name: Symbol name to look up

        Returns:
            Symbol if found in this scope or any parent scope, None otherwise
        """
        symbol = self.lookup(name)
        if symbol:
            return symbol
        if self.parent:
            return self.parent.lookup_recursive(name)
        return None

    def __str__(self) -> str:
        """Return string representation."""
        symbols_str = ", ".join(self.symbols.keys()) if self.symbols else "(empty)"
        return f"Scope({self.name}: {symbols_str})"

    def __repr__(self) -> str:
        """Return repr string."""
        return f"Scope({self.name!r}, parent={self.parent.name if self.parent else None!r})"
