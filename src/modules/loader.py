"""Modules and `import` (Task 18.4.2) - turns a program and the modules it imports into one
program for the semantic analyzer and the C generator.

The model (user decisions 2026-10-10):
- A module is a folder: every .fusion file in `money/` (next to the main file) is module
  `money`; `geometry/shapes/` is module `geometry.shapes`. The program is the main file only
- `import money` -> `money.round(x)`, `money.Price`; `import money.Price` -> `Price`;
  `import money.*` -> every name, no prefix; `import lib.utils as libutils` -> an alias.
  A module is used by the last part of its path (`shapes.area()`)
- Each module is loaded once, from one list of loaded modules - imports that criss-cross
  (money -> tax -> money) can't loop. Two different modules with the same name in one file
  are an error: give one an alias
- Only `public` structs, enums and functions can be used by other modules (Task 18.4.3);
  files of one module see all of each other's names. A public function can't take or
  return a private struct or enum of its module

How: every declaration of module `money` gets the internal name `money.round`; each file's
names are rewritten (scope-aware - a local variable `round` is left alone) to those
internal names; then all files are merged into one ProgramNode. In C, `money.round`
becomes `fu_money__round` (c_names.py).
"""

import os
from dataclasses import fields as dataclass_fields, is_dataclass
from typing import Callable, Dict, List, Optional, Set, Tuple

from src.parser.ast_nodes import (
    ASTNode, ProgramNode, ImportDecl, FunctionDecl, StructDecl, EnumDecl, ErrorDecl, VarDeclStmt,
    TemplateDecl,
    BlockStmt,
    ForStmt, LambdaExpr, IdentifierExpr, MemberExpr, StructType, PrimitiveType, ArrayType,
    FunctionType, LiteralExpr,
)
from src.semantic.errors import SemanticError
from src.semantic.name_resolver import TYPE_CLASSES

ParseFile = Callable[[str, str], ProgramNode]   # (source text, file name) -> ProgramNode

_SKIP_FIELDS = ('location', 'inferred_type', 'scope', 'declaration', 'callee_declaration',
                'resolved_arguments',
                'methods', 'static_methods')   # top-level functions too (32.1, 32.2c)


class Module:
    """One loaded module (or the main program, whose id is '')."""

    def __init__(self, module_id: str, files: List[Tuple[str, ProgramNode]]):
        self.id = module_id
        self.files = files
        self.names: Dict[str, ASTNode] = {}   # top-level name -> its declaration
        for _, program in files:
            for decl in program.declarations:
                if isinstance(decl, (FunctionDecl, StructDecl, EnumDecl, ErrorDecl, VarDeclStmt,
                                     TemplateDecl)):
                    self.names.setdefault(decl.name, decl)

    def qualify(self, name: str) -> str:
        return f'{self.id}.{name}' if self.id else name

    def is_public(self, name: str) -> bool:
        return getattr(self.names.get(name), 'is_public', False)


class ModuleLoader:
    """Loads a program and everything it imports; see the module docstring."""

    def __init__(self, main_file: str, parse_file: ParseFile):
        self.main_file = main_file
        self.root = os.path.dirname(os.path.abspath(main_file))
        self.parse_file = parse_file
        self.modules: Dict[str, Module] = {}   # module id -> Module, each loaded once
        self.errors: List[SemanticError] = []

    # ------------------------------------------------------------------ loading

    def load(self, main_program: ProgramNode) -> ProgramNode:
        """Return the whole program as one ProgramNode (check self.errors)."""
        main = Module('', [(self.main_file, main_program)])
        self._load_imports(main)
        if self.errors:
            return main_program
        for module in list(self.modules.values()) + [main]:
            for file_name, program in module.files:
                self._rewrite_file(module, program)
        declarations = []
        for module in self.modules.values():
            for _, program in module.files:
                declarations.extend(program.declarations)
        declarations.extend(main_program.declarations)
        return ProgramNode(location=main_program.location, declarations=declarations)

    def _load_imports(self, module: Module) -> None:
        for _, program in module.files:
            for imp in program.imports:
                target = self._resolve(imp)
                if target is not None and target[0] not in self.modules:
                    self._load_module(target[0], imp)

    def _resolve(self, imp: ImportDecl) -> Optional[Tuple[str, Optional[str]]]:
        """(module id, imported name or None) for an import line, or None after an error."""
        parts = imp.path
        if imp.star or self._is_module_dir(parts):
            if not self._is_module_dir(parts):
                self._error(f"No module '{'.'.join(parts)}' - expected a folder "
                            f"{'/'.join(parts)}/ with .fusion files next to the main file", imp)
                return None
            return '.'.join(parts), None
        if len(parts) > 1 and self._is_module_dir(parts[:-1]):
            return '.'.join(parts[:-1]), parts[-1]
        self._error(f"No module '{'.'.join(parts)}' - expected a folder {'/'.join(parts)}/ "
                    f"with .fusion files next to the main file", imp)
        return None

    def _module_dir(self, parts: List[str]) -> str:
        return os.path.join(self.root, *parts)

    def _is_module_dir(self, parts: List[str]) -> bool:
        folder = self._module_dir(parts)
        return os.path.isdir(folder) and any(f.endswith('.fusion') for f in os.listdir(folder))

    def _load_module(self, module_id: str, imp: ImportDecl) -> None:
        parts = module_id.split('.')
        for part in parts:
            if '__' in part or part in TYPE_CLASSES:
                self._error(f"'{part}' can't be a module name (it is a built-in type class, "
                            f"or contains '__')", imp)
                return
        folder = self._module_dir(parts)
        files = []
        for name in sorted(os.listdir(folder)):
            if not name.endswith('.fusion'):
                continue
            path = os.path.join(folder, name)
            with open(path, encoding='utf-8') as f:
                source = f.read()
            try:
                files.append((path, self.parse_file(source, path)))
            except Exception as e:   # lexer / parser errors in a module's file
                self._error(f"In module '{module_id}': {e}", imp)
                return
        module = Module(module_id, files)
        self.modules[module_id] = module   # registered before its own imports: no loops
        if 'main' in module.names:
            self._error(f"Module '{module_id}' can't have a main function - only the program's "
                        f"main file can", module.names['main'])
        self._check_public_types(module)
        self._load_imports(module)

    def _check_public_types(self, module: Module) -> None:
        """A public function, struct or enum can't expose a private struct or enum of its own
        module: other modules would get values of a type they can't name (Task 18.4.3)."""
        def private_structs(type_node):
            if isinstance(type_node, StructType):
                decl = module.names.get(type_node.name)
                if isinstance(decl, (StructDecl, EnumDecl, ErrorDecl)) and not decl.is_public:
                    yield type_node.name
            elif is_dataclass(type_node) and not isinstance(type_node, type):
                for f in dataclass_fields(type_node):
                    if f.name not in _SKIP_FIELDS:
                        value = getattr(type_node, f.name)
                        for item in (value if isinstance(value, list) else [value]):
                            yield from private_structs(item)

        for decl in module.names.values():
            if not decl.is_public:
                continue
            if isinstance(decl, FunctionDecl):
                used = [decl.return_type] + [p.param_type for p in decl.parameters]
                what = f"public function '{decl.name}'"
            elif isinstance(decl, EnumDecl):
                used = [f.field_type for v in decl.variants for f in v.fields]
                what = f"public enum '{decl.name}'"
            elif isinstance(decl, ErrorDecl):
                used = [f.field_type for f in decl.fields]
                what = f"public error type '{decl.name}'"
            elif isinstance(decl, VarDeclStmt):
                used = [decl.var_type]
                what = f"public module variable '{decl.name}'"   # Task 44.1
            else:
                used = [f.field_type for f in decl.fields]
                what = f"public struct '{decl.name}'"
            for name in sorted({n for t in used for n in private_structs(t)}):
                kind = {EnumDecl: 'enum', ErrorDecl: 'error type'}.get(
                    type(module.names.get(name)), 'struct')
                self._error(f"The {what} uses the private {kind} '{name}' - make '{name}' "
                            f"public too", decl)

    # ------------------------------------------------------------------ name rewriting

    def _rewrite_file(self, module: Module, program: ProgramNode) -> None:
        """Rewrite one file's names to internal ones (`round` -> `money.round`)."""
        aliases: Dict[str, str] = {}             # prefix -> module id
        direct: Dict[str, Set[str]] = {}         # unprefixed name -> internal names
        explicit: Set[str] = set()               # names from `import M.Name`
        for imp in program.imports:
            target = self._resolve(imp)
            if target is None:
                continue
            module_id, name = target
            imported = self.modules[module_id]
            if name is None and not imp.star:
                prefix = imp.alias or imp.path[-1]
                if prefix in aliases and aliases[prefix] != module_id:
                    self._error(f"Two modules are both named '{prefix}' here: "
                                f"{aliases[prefix]} and {module_id} - give one another name "
                                f"with 'as' (import {module_id} as ...)", imp)
                    continue
                if prefix in module.names:
                    self._error(f"'{prefix}' is both a module and a name declared here - "
                                f"import the module with another name using 'as'", imp)
                    continue
                aliases[prefix] = module_id
            elif name is not None:
                if name not in imported.names:
                    self._error(f"Module '{module_id}' has no '{name}'", imp)
                    continue
                if not imported.is_public(name):
                    self._error(f"'{name}' is private to module '{module_id}' - only names "
                                f"marked public can be imported", imp)
                    continue
                local = imp.alias or name
                if local in module.names:
                    self._error(f"'{local}' is imported from {module_id} and also declared here",
                                imp)
                    continue
                direct.setdefault(local, set()).add(imported.qualify(name))
                explicit.add(local)
            else:
                for name in imported.names:
                    if imported.is_public(name):   # .* brings the public names only
                        direct.setdefault(name, set()).add(imported.qualify(name))

        def lookup(name: str, node: ASTNode) -> str:
            if name in module.names:
                return module.qualify(name)      # the module's own name wins over a .* import
            found = direct.get(name)
            if not found:
                return name                      # a built-in, or undefined (reported later)
            if len(found) > 1:
                self._error(f"'{name}' is ambiguous: " + " or ".join(sorted(found))
                            + " - use the module prefix", node)
            return sorted(found)[0]

        def type_name(name: str, node: ASTNode) -> str:
            if '.' in name:
                prefix, rest = name.split('.', 1)
                if prefix not in aliases:
                    self._error(f"No module '{prefix}' is imported here (for the type '{name}')", node)
                    return name
                target = self.modules[aliases[prefix]]
                if rest not in target.names:
                    self._error(f"Module '{target.id}' has no '{rest}'", node)
                elif not target.is_public(rest) and target is not module:
                    self._error(f"'{rest}' is private to module '{target.id}'", node)
                return target.qualify(rest)
            return lookup(name, node)

        def is_local(name: str, scopes: List[Set[str]]) -> bool:
            return any(name in scope for scope in scopes)

        def walk(node, scopes: List[Set[str]]):
            if isinstance(node, list):
                for item in node:
                    walk(item, scopes)
                return
            if not is_dataclass(node) or isinstance(node, type):
                return
            if isinstance(node, IdentifierExpr):
                if not is_local(node.name, scopes):
                    node.name = lookup(node.name, node)
                return
            if isinstance(node, StructType):
                node.name = type_name(node.name, node)
                return
            if type(node).__name__ == 'MatchPattern' and node.name:
                # `case FileError` / `case files.FileError` - an error type's internal name
                # (Task 26.10); an enum value's bare name is left alone
                internal = type_name(node.name, node) if node.dotted else lookup(node.name, node)
                if isinstance(self._declaration(internal), ErrorDecl):
                    node.name = internal
                return
            if isinstance(node, MemberExpr) and isinstance(node.object, IdentifierExpr) \
                    and node.object.name in aliases and not is_local(node.object.name, scopes) \
                    and node.object.name not in module.names:
                target = self.modules[aliases[node.object.name]]
                if node.member not in target.names:
                    self._error(f"Module '{target.id}' has no '{node.member}'", node)
                elif not target.is_public(node.member) and target is not module:
                    self._error(f"'{node.member}' is private to module '{target.id}'", node)
                # money.round -> the identifier money.round (a call, a value or a struct)
                replacement = IdentifierExpr(location=node.location, name=target.qualify(node.member))
                node.__class__ = IdentifierExpr
                node.__dict__.clear()
                node.__dict__.update(replacement.__dict__)
                return
            if isinstance(node, FunctionDecl):
                walk(node.return_type, scopes)
                walk(node.parameters, scopes)
                walk(node.body, scopes + [{p.name for p in node.parameters}])
                return
            if isinstance(node, LambdaExpr):
                for f in dataclass_fields(node):
                    if f.name not in _SKIP_FIELDS:
                        walk(getattr(node, f.name), scopes + [{p.name for p in node.parameters}])
                return
            if isinstance(node, BlockStmt):
                inner = scopes + [set()]
                for f in dataclass_fields(node):
                    if f.name not in _SKIP_FIELDS:
                        walk(getattr(node, f.name), inner)
                return
            if type(node).__name__ == 'CatchClause':
                walk(node.error_type, scopes)
                walk(node.body, scopes + [{node.name} if node.name else set()])   # Task 26.11
                return
            if isinstance(node, ForStmt):
                for f in dataclass_fields(node):
                    if f.name == 'body':
                        walk(node.body, scopes + [{node.variable}])
                    elif f.name not in _SKIP_FIELDS:
                        walk(getattr(node, f.name), scopes)
                return
            for f in dataclass_fields(node):
                if f.name not in _SKIP_FIELDS:
                    walk(getattr(node, f.name), scopes)
            if isinstance(node, (VarDeclStmt, TemplateDecl)) and scopes:
                scopes[-1].add(node.name)       # visible from the next statement on
                if node.error_name:
                    scopes[-1].add(node.error_name)   # Ship s, Error err = ... (Task 26)

        for decl in program.declarations:
            if module.id and isinstance(decl, (FunctionDecl, StructDecl, EnumDecl, ErrorDecl,
                                               VarDeclStmt, TemplateDecl)):
                decl.name = module.qualify(decl.name)
            if isinstance(decl, ErrorDecl) and decl.parent != 'Error':
                decl.parent = type_name(decl.parent, decl)   # the parent error type (Task 26.9)
            walk(decl, [])

    def _declaration(self, internal: str):
        """The declaration an internal name (`files.FileError`, or a main-file name) means."""
        module_id, _, name = internal.rpartition('.')
        module = self.modules.get(module_id)
        return module.names.get(name) if module is not None else None

    def _error(self, message: str, node) -> None:
        location = getattr(node, 'location', None)
        self.errors.append(SemanticError(message, location))


def load_program(main_file: str, main_program: ProgramNode,
                 parse_file: ParseFile) -> Tuple[ProgramNode, List[SemanticError]]:
    """The whole program - the main file plus every module it imports - as one ProgramNode,
    with any import errors. A program without imports comes back unchanged."""
    if not main_program.imports:
        return main_program, []
    loader = ModuleLoader(main_file, parse_file)
    program = loader.load(main_program)
    return program, loader.errors


# ---------------------------------------------------------------------- shared entry points

def make_file_parser(config=None) -> ParseFile:
    """A function parsing one Fusion file the way main.py does - with the project's lexer
    settings when a ProjectConfig is given. Lexer errors are raised as ValueError."""
    from src.lexer import Lexer
    from src.parser.parser import Parser

    def parse(source: str, path: str) -> ProgramNode:
        options = {}
        if config is not None:
            options = dict(tab_width=config.indentation.tab_width,
                           allow_mixed=config.indentation.allow_mixed,
                           allow_unicode_identifiers=config.source.allow_unicode_identifiers)
        lexer = Lexer(source, path, **options)
        tokens = lexer.tokenize()
        if lexer.diagnostics.errors:
            raise ValueError('; '.join(str(e) for e in lexer.diagnostics.errors))
        return Parser(tokens).parse_program()
    return parse


def load_program_file(main_file: str, config=None) -> Tuple[ProgramNode, List[str]]:
    """Read, parse and load a program file and every module it imports (Task 18.4.4):
    (the whole program, error messages). Used by check.py and tests/verify_examples.py."""
    parse = make_file_parser(config)
    with open(main_file, encoding='utf-8') as f:
        program = parse(f.read(), main_file)
    program, errors = load_program(main_file, program, parse)
    return program, [str(e) for e in errors]


# ---------------------------------------------------------------------- module interfaces

def type_text(type_node, own_module: str = '') -> str:
    """A type as Fusion source (`money.Price` is written `Price` inside module money)."""
    if isinstance(type_node, PrimitiveType):
        return type_node.name
    if isinstance(type_node, StructType):
        prefix = own_module + '.'
        return type_node.name[len(prefix):] if own_module and type_node.name.startswith(prefix) \
            else type_node.name
    if isinstance(type_node, ArrayType):
        size = '' if type_node.size is None else str(type_node.size)
        return f'{type_text(type_node.element_type, own_module)}[{size}]'
    if isinstance(type_node, FunctionType):
        params = ', '.join(type_text(p, own_module) for p in type_node.parameter_types)
        return f'({params}) : {type_text(type_node.return_type, own_module)}'
    return '?'


def module_interface(module: Module) -> List[str]:
    """A module's public interface (Task 18.4.4): its public structs and functions with
    their types - what other modules may rely on. The groundwork for library signatures
    and capability checks (Task 19)."""
    lines = [f'module {module.id}']
    for name in sorted(module.names):
        decl = module.names[name]
        if not decl.is_public:
            continue
        if isinstance(decl, StructDecl):
            lines.append(f'    public struct {name}')
            for f in decl.fields:
                lines.append(f'        {type_text(f.field_type, module.id)} {f.name}')
        elif isinstance(decl, ErrorDecl):
            parent = '' if decl.parent == 'Error' else f' : {decl.parent}'
            lines.append(f'    public error {name}{parent}')   # Task 26.9
            for f in decl.fields:
                lines.append(f'        {type_text(f.field_type, module.id)} {f.name}')
        elif isinstance(decl, VarDeclStmt):
            const = 'const ' if decl.is_const else ''   # a module variable (Task 44.1)
            lines.append(f'    public {const}{type_text(decl.var_type, module.id)} {name}')
        elif isinstance(decl, EnumDecl):
            lines.append(f'    public enum {name}')         # Task 25
            for v in decl.variants:
                data = ', '.join(f'{type_text(f.field_type, module.id)} {f.name}' for f in v.fields)
                value = f' = {v.value}' if v.explicit_value else ''
                lines.append(f'        {v.name}{f"({data})" if v.fields else ""}{value}')
        else:
            params = []
            for p in decl.parameters:
                text = f'{type_text(p.param_type, module.id)} {p.name}'
                if isinstance(p.default_value, LiteralExpr):
                    value = p.default_value.value
                    shown = {'string': f'"{value}"', 'char': f"'{value}'"}.get(
                        p.default_value.type_hint, str(value).lower() if isinstance(value, bool) else str(value))
                    text += f' = {shown}'
                elif p.default_value is not None:
                    text += ' = ...'
                params.append(text)
            marker = ', Error' if decl.returns_error else ''    # can fail (Task 26.7)
            lines.append(f'    public {type_text(decl.return_type, module.id)}{marker} function '
                         f'{name}({", ".join(params)})')
    return lines


def program_interfaces(main_file: str, only: Optional[str] = None,
                       config=None) -> Tuple[List[str], List[str]]:
    """(interface lines of every module the program imports - or just `only`, errors)."""
    parse = make_file_parser(config)
    with open(main_file, encoding='utf-8') as f:
        program = parse(f.read(), main_file)
    loader = ModuleLoader(main_file, parse)
    loader.load(program)
    if loader.errors:
        return [], [str(e) for e in loader.errors]
    if only is not None and only not in loader.modules:
        return [], [f"The program doesn't import a module named '{only}' "
                    f"(it imports: {', '.join(sorted(loader.modules)) or 'none'})"]
    lines = []
    for module_id in sorted(loader.modules):
        if only is None or module_id == only:
            lines += module_interface(loader.modules[module_id]) + ['']
    return lines, []
