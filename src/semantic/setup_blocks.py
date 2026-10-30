"""Form B on any variable (Task 32.2d, user decisions 2026-10-30 - Classes.md section 4).

    Car mine = new Car() {              // a local: the block sets `mine` up further
        mine.setEngine("V6")
    }
    class Garage
        public Car car = new Car() {    // a field: each constructor runs it first
            car.speed = 4
        }

expand_setup_blocks() runs before names are resolved: a local's block becomes a block
statement right after its declaration (the parser already put a field's block at the start
of each constructor, and a static's in the class's set-up - 32.2c). Checked here: the block
changes only its own variable - an assignment, or a method call on another variable, is an
error that says where that change belongs. Names declared inside the block are its own.
"""

from typing import List, Set

from src.parser.ast_nodes import (
    AssignmentStmt, BlockStmt, CallExpr, ExpressionStmt, FunctionDecl, MemberExpr, StructDecl,
    VarDeclStmt,
)
from .errors import SemanticError
from .statics import _root, _walk


def _declared(node) -> Set[str]:
    """Every variable declared somewhere below a node."""
    found = set()

    def visit(n):
        if isinstance(n, VarDeclStmt):
            found.add(n.name)
        return n
    _walk([node], visit)
    return found


def _check_changes(block: BlockStmt, own: str, known: Set[str], elsewhere: str) -> List[SemanticError]:
    """The block changes `own` only: no assignment to, and no method call on, another of the
    `known` variables (a block's own variables are fine)."""
    errors, mine = [], _declared(block) | {own}

    def visit(n):
        target = None
        if isinstance(n, AssignmentStmt):
            target = _root(n.target)
        elif isinstance(n, ExpressionStmt) and isinstance(n.expression, CallExpr) \
                and isinstance(n.expression.callee, MemberExpr):
            target = _root(n.expression.callee.object)
        if target is not None and target in known and target not in mine:
            errors.append(SemanticError(
                f"The set-up block of '{own}' can only change '{own}' - change '{target}' "
                f"{elsewhere}", n.location))
        return n
    _walk([block], visit)
    return errors


def expand_setup_blocks(program) -> List[SemanticError]:
    errors: List[SemanticError] = []
    functions, seen = [], set()
    for d in program.declarations:
        for f in ([d] if isinstance(d, FunctionDecl) else
                  d.methods + d.static_methods if isinstance(d, StructDecl) else []):
            if id(f) not in seen:
                seen.add(id(f))
                functions.append(f)
        if isinstance(d, StructDecl) and d.is_class:
            names = {f.name for f in d.fields} | {'this'}
            for f in d.fields:
                if getattr(f, 'setup', None) is not None:
                    errors += _check_changes(f.setup, f.name, names, "in a constructor")

    for function in functions:
        if function.body is None:
            continue
        known = {p.name for p in function.parameters} | _declared(function.body)

        def visit(node, known=known):
            if isinstance(node, BlockStmt):
                statements = []
                for s in node.statements:
                    statements.append(s)
                    if isinstance(s, VarDeclStmt) and s.setup is not None:
                        errors.extend(_check_changes(s.setup, s.name, known,
                                                     "after the block"))
                        s.setup.sets_up = s.name     # may change a const / let (32.2e)
                        s.has_setup = True
                        statements.append(s.setup)
                        s.setup = None
                node.statements = statements
            return node
        visit(function.body)
        _walk([function.body], visit)
    return errors
