"""Which Fusion constructs do the programs in examples/ use? (Task 28.1)

Walks each program's analyzed AST and lists every node kind, operator, type, builtin call and
method call, with how many programs use it (names shown when 3 or fewer do).

    python tools/example_subset.py          # run from the repo root
"""
import sys, dataclasses, collections
from pathlib import Path
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.modules.loader import load_program_file
from src.semantic import SemanticAnalyzer
from src.config import load_project_config
from src.parser import ast_nodes as A

progs = sorted((ROOT / 'examples').glob('*.fusion')) + sorted((ROOT / 'examples').glob('*/main.fusion'))
progs = [p for p in progs if p.name != 'mixed_indent.fusion']

used = collections.defaultdict(set)      # feature -> programs using it

def note(feature, prog):
    used[feature].add(prog)

def walk(node, prog, seen, user_functions):
    if id(node) in seen:
        return
    seen.add(id(node))
    if isinstance(node, list):
        for x in node:
            walk(x, prog, seen, user_functions)
        return
    if not dataclasses.is_dataclass(node):
        return
    name = type(node).__name__
    note('node ' + name, prog)
    if isinstance(node, A.BinaryExpr):
        note('op ' + node.operator, prog)
    elif isinstance(node, A.UnaryExpr):
        note('unary ' + node.operator, prog)
    elif isinstance(node, A.LiteralExpr):
        note('literal ' + str(node.type_hint), prog)
    elif isinstance(node, A.PrimitiveType):
        note('type ' + node.name, prog)
    elif isinstance(node, (A.ListType, A.MapType, A.ArrayType, A.FunctionType, A.StructType,
                           A.EnumType, A.ErrorType)):
        note('type ' + name, prog)
    elif isinstance(node, A.CallExpr):
        c = node.callee
        if isinstance(c, A.IdentifierExpr):
            kind = 'user call' if c.name in user_functions else 'builtin '
            note((kind + c.name) if kind == 'builtin ' else 'call user function', prog)
        elif isinstance(c, A.MemberExpr):
            note('method .' + c.member, prog)
    elif isinstance(node, A.FunctionDecl):
        if node.is_lambda:
            note('feature lambda', prog)
        if node.returns_error:
            note('feature T, Error function', prog)
        if node.is_public:
            note('feature public', prog)
        for p in node.parameters:
            if p.default_value is not None:
                note('feature default parameter', prog)
            if p.is_variadic:
                note('feature variadic parameter', prog)
    elif isinstance(node, A.NamedArgument):
        note('feature named argument', prog)
    elif isinstance(node, A.VarDeclStmt):
        if node.is_const:
            note('feature const', prog)
        if node.error_name:
            note('feature error capture', prog)
    elif isinstance(node, A.ForStmt):
        it = node.iterable
        if isinstance(it, A.CallExpr) and isinstance(it.callee, A.IdentifierExpr) and it.callee.name == 'range':
            note('feature for over range', prog)
        else:
            note('feature for over collection', prog)
    for f in dataclasses.fields(node):
        if f.name in ('location', 'inferred_type', 'scope', 'callee_declaration', 'declaration',
                      'parent_declaration', 'symbol', 'resolved_arguments'):
            continue
        walk(getattr(node, f.name), prog, seen, user_functions)

failed = []
for p in progs:
    label = str(p.relative_to(ROOT / 'examples')).replace('\\', '/')
    try:
        config = load_project_config(str(p))
        program, errors = load_program_file(str(p), config)
        if errors:
            failed.append((label, errors[0])); continue
        an = SemanticAnalyzer(structs_config=config.structs, strings_config=config.strings,
                              stdlib_config=config.stdlib, errors_config=config.errors,
                              numbers_config=config.numbers)
        if not an.analyze(program):
            failed.append((label, 'semantic errors')); continue
    except Exception as e:
        failed.append((label, repr(e))); continue
    users = {d.name for d in program.declarations if isinstance(d, A.FunctionDecl)}
    walk(program, label, set(), users)

print(f'{len(progs)} programs, {len(failed)} failed: {failed}')
groups = collections.defaultdict(list)
for feat, ps in used.items():
    kind, _, rest = feat.partition(' ')
    groups[kind].append((rest, len(ps), sorted(ps)))
for kind in ['node', 'feature', 'type', 'literal', 'op', 'unary', 'builtin', 'method', 'call']:
    print(f'\n== {kind}')
    for rest, n, ps in sorted(groups.get(kind, []), key=lambda x: (-x[1], x[0])):
        shown = ', '.join(ps) if n <= 3 else ''
        print(f'  {rest:32} {n:3}  {shown}')
