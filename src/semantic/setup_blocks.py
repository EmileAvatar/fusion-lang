"""Form B on any variable (Task 32.2d, user decisions 2026-10-30 - files/Classes.md section 4).

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
                        _collection_options(s, program)                       # 32.14
                        s.has_setup = True
                        statements.append(s.setup)
                        s.setup = None
                node.statements = statements
            return node
        visit(function.body)
        _walk([function.body], visit)
    return errors


# List / Map options (Task 32.14, user decisions 2026-10-30 / 31): set in the variable's form B
# block - `List<string> names = [] { names.noDuplicates() }`
COLLECTION_OPTIONS = ('noDuplicates', 'noNull', 'readOnly')


def _collection_options(decl, program) -> None:
    """Mark each option call in a List / Map's set-up block; readOnly() takes effect after the
    block, so it moves to the block's end."""
    from src.parser.ast_nodes import ListType, MapType
    if not isinstance(decl.var_type, (ListType, MapType)):
        return
    options, last = set(), []
    for statement in decl.setup.statements:
        call = statement.expression if isinstance(statement, ExpressionStmt) else None
        if isinstance(call, CallExpr) and isinstance(call.callee, MemberExpr) \
                and getattr(call.callee.object, 'name', None) == decl.name \
                and call.callee.member in COLLECTION_OPTIONS:
            call.in_setup = True
            options.add(call.callee.member)
            if call.callee.member == 'readOnly':
                last.append(statement)
    if options:
        decl.collection_options = options
        program.collection_options = True
        decl.setup.statements = [s for s in decl.setup.statements if s not in last] + last


def check_collection_options(program) -> List[SemanticError]:
    """After type checking (32.14): a readOnly List / Map isn't changed after its set-up; a
    noNull one isn't given a null - a compile error where it can be seen (D.086); anything else
    is a ReadOnlyError / NullError while running."""
    from dataclasses import fields as dataclass_fields, is_dataclass
    from src.parser.ast_nodes import IdentifierExpr, IndexExpr, LiteralExpr
    from .collection_rules import MUTATING_LIST_METHODS, MUTATING_MAP_METHODS
    errors = []
    changing = MUTATING_LIST_METHODS | MUTATING_MAP_METHODS

    def walk(node, options):
        if isinstance(node, list):
            for item in node:
                walk(item, options)
            return
        if not is_dataclass(node) or isinstance(node, type):
            return
        if isinstance(node, VarDeclStmt) and getattr(node, 'collection_options', None):
            options[node.name] = node.collection_options
        if isinstance(node, BlockStmt) and getattr(node, 'sets_up', None) in options:
            return                                  # its own set-up may change it
        if isinstance(node, CallExpr) and isinstance(node.callee, MemberExpr) \
                and isinstance(node.callee.object, IdentifierExpr) and not getattr(node, 'in_setup', False):
            name, member = node.callee.object.name, node.callee.member
            given = options.get(name, ())
            if 'readOnly' in given and member in changing:
                errors.append(SemanticError(f"'{name}' is read only after its set-up - it can't change "
                                            f"({member})", node.location))
            if 'noNull' in given and member in ('add', 'insert') and any(
                    isinstance(a, LiteralExpr) and a.type_hint == 'null' for a in node.arguments):
                errors.append(SemanticError(f"'{name}' takes no null (noNull)", node.location))
        if isinstance(node, AssignmentStmt) and isinstance(node.target, IndexExpr) \
                and isinstance(node.target.array, IdentifierExpr) \
                and 'noNull' in options.get(node.target.array.name, ()) \
                and isinstance(node.value, LiteralExpr) and node.value.type_hint == 'null':
            errors.append(SemanticError(f"'{node.target.array.name}' takes no null (noNull)", node.location))
        if isinstance(node, AssignmentStmt) and isinstance(node.target, IndexExpr) \
                and isinstance(node.target.array, IdentifierExpr) \
                and 'readOnly' in options.get(node.target.array.name, ()):
            errors.append(SemanticError(f"'{node.target.array.name}' is read only after its set-up - "
                                        f"it can't change", node.location))
        # D.139 (Task 52.10): a List or Map never holds null - with noNull() or not
        def is_null(e):
            return isinstance(e, LiteralExpr) and e.type_hint == 'null'
        if isinstance(node, CallExpr) and isinstance(node.callee, MemberExpr) \
                and getattr(node, 'list_method', None) in ('add', 'insert') \
                and any(is_null(a) for a in node.arguments) \
                and 'noNull' not in options.get(getattr(node.callee.object, 'name', None), ()):
            errors.append(SemanticError("A List never holds null - add an object (D.139)", node.location))
        if isinstance(node, AssignmentStmt) and isinstance(node.target, IndexExpr) and is_null(node.value) \
                and type(getattr(node.target.array, 'inferred_type', None)).__name__ in ('ListType', 'MapType') \
                and 'noNull' not in options.get(getattr(node.target.array, 'name', None), ()):
            kind = 'List' if type(node.target.array.inferred_type).__name__ == 'ListType' else 'Map'
            errors.append(SemanticError(f"A {kind} never holds null - set an object (D.139)", node.location))
        for f in dataclass_fields(node):
            if f.name not in ('location', 'inferred_type', 'declaration', 'scope', 'callee_declaration',
                              'resolved_arguments'):
                walk(getattr(node, f.name), options)

    for d in program.declarations:
        if isinstance(d, FunctionDecl) and d.body is not None:
            walk(d.body, {})
    return errors

