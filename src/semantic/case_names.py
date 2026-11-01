"""[source] caseSensitive (Task 32.11, Decisions.md SYN.040).

    [source]
    caseSensitive = false

True (the default, as in most languages): `count` and `Count` are two names. False: the
project treats them as one, so two names that differ only in case are an error - each pair
is listed, where the second one is declared. Checked before anything else rewrites the
program, so only the names the developer wrote are compared.

Where two names meet: the program's own (functions, types, module variables); a type's
fields, functions and enum values; a function's parameters and variables, together with the
program's names (and, in a class function, its class's members).
"""

from typing import Dict, List

from src.parser.ast_nodes import (
    CatchClause, EnumDecl, ErrorDecl, ForStmt, FunctionDecl, ParameterDecl, StructDecl, VarDeclStmt,
)
from .errors import SemanticError
from .statics import _walk


def _clashes(names: List[tuple], errors: List[SemanticError]) -> None:
    """names: (name, location) in the order written; a later name that matches an earlier
    one in all but case is an error."""
    first: Dict[str, str] = {}
    reported = set()
    for name, location in names:
        key = name.lower()
        seen = first.setdefault(key, name)
        if seen != name and (seen, name) not in reported:
            reported.add((seen, name))
            errors.append(SemanticError(
                f"'{seen}' and '{name}' differ only in case - one name in a project that isn't "
                f"case sensitive ([source] caseSensitive = false); rename one", location))


def _locals(function: FunctionDecl) -> List[tuple]:
    """A function's parameters and every variable declared in its body."""
    found = [(p.name, p.location) for p in function.parameters]

    def visit(n):
        if isinstance(n, VarDeclStmt):
            found.append((n.name, n.location))
        elif isinstance(n, ParameterDecl):
            found.append((n.name, n.location))
        elif isinstance(n, ForStmt) and isinstance(n.variable, str):
            found.append((n.variable, n.location))
        elif isinstance(n, CatchClause) and n.name:
            found.append((n.name, n.location))
        return n
    if function.body is not None:
        _walk([function.body], visit)
    return found


def check_case_names(program) -> List[SemanticError]:
    errors: List[SemanticError] = []
    top = []
    for d in program.declarations:
        if isinstance(d, (FunctionDecl, StructDecl, EnumDecl, ErrorDecl, VarDeclStmt)):
            top.append((d.name, d.location))
    _clashes(top, errors)

    for d in program.declarations:
        if isinstance(d, FunctionDecl):
            _clashes(top + _locals(d), errors)
        elif isinstance(d, EnumDecl):
            _clashes([(v.name, v.location) for v in d.variants], errors)
        elif isinstance(d, StructDecl):
            methods = d.methods + getattr(d, 'static_methods', [])
            members = [(f.name, f.location) for f in d.fields] + [(m.name, m.location) for m in methods]
            _clashes(members, errors)
            for m in methods:
                _clashes(top + members + _locals(m), errors)
    # one error per pair, however many scopes it shows up in
    unique, seen = [], set()
    for e in errors:
        if e.message not in seen:
            seen.add(e.message)
            unique.append(e)
    return unique
