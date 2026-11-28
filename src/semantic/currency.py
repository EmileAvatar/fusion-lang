"""The Currency module (Task 47.2b, D.186): src/stdlib/Fusion/Currency/Currency.fusion - module Fusion.Currency
(57.5, D.210) - written in Fusion, added to a program that uses money, names Currency or imports Fusion.Currency - before names are resolved - so no other program carries it.

The type checker then sends money's rules there: `m / n` is Currency.divide(m, n), and a method on money -
m.convert(...), m.round(2), m.split(3) ... - is the static Currency.<name>(m, ...).
"""
from dataclasses import fields, is_dataclass
from pathlib import Path

CURRENCY_FILE = Path(__file__).resolve().parent.parent / 'stdlib' / 'Fusion' / 'Currency' / 'Currency.fusion'

# money's methods - each the Currency static of the same name, with the money first
CURRENCY_METHODS = ('convert', 'round', 'roundWith', 'settle', 'divide', 'percent', 'split', 'splitBy', 'format')


def _uses_money(program) -> bool:
    seen, todo = set(), [program]
    while todo:
        node = todo.pop()
        if isinstance(node, list):
            todo.extend(node)
            continue
        if not is_dataclass(node) or isinstance(node, type) or id(node) in seen:
            continue
        seen.add(id(node))
        if getattr(node, 'name', None) in ('money', 'Currency'):
            return True
        for f in fields(node):
            if f.name != 'location':
                todo.append(getattr(node, f.name))
    return False


def add_currency_module(program) -> None:
    """Add the Currency class to a program that uses money - unless it has a Currency of its own."""
    from src.parser.ast_nodes import StructDecl
    if any(isinstance(d, StructDecl) and d.name == 'Currency' for d in program.declarations):
        return
    if not (getattr(program, 'wants_currency', False) or _uses_money(program)):
        return
    from src.lexer.lexer import Lexer
    from src.parser.parser import Parser
    source = CURRENCY_FILE.read_text(encoding='utf-8')
    added = Parser(Lexer(source, 'Currency.fusion').tokenize()).parse_program().declarations
    for decl in added:
        decl.from_stdlib = True
    program.declarations.extend(added)
