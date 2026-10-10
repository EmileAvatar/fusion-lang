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

How: every declaration of module `money` gets the internal name `money.round`; each file's
names are rewritten (scope-aware - a local variable `round` is left alone) to those
internal names; then all files are merged into one ProgramNode. In C, `money.round`
becomes `fu_money__round` (c_names.py).
"""

import os
from dataclasses import fields as dataclass_fields, is_dataclass
from typing import Callable, Dict, List, Optional, Set, Tuple

from src.parser.ast_nodes import (
    ASTNode, ProgramNode, ImportDecl, FunctionDecl, StructDecl, VarDeclStmt, BlockStmt,
    ForStmt, LambdaExpr, IdentifierExpr, MemberExpr, StructType,
)
from src.semantic.errors import SemanticError
from src.semantic.name_resolver import TYPE_CLASSES

ParseFile = Callable[[str, str], ProgramNode]   # (source text, file name) -> ProgramNode

_SKIP_FIELDS = ('location', 'inferred_type', 'scope', 'declaration', 'callee_declaration',
                'resolved_arguments')


class Module:
    """One loaded module (or the main program, whose id is '')."""

    def __init__(self, module_id: str, files: List[Tuple[str, ProgramNode]]):
        self.id = module_id
        self.files = files
        self.names: Dict[str, ASTNode] = {}   # top-level name -> its declaration
        for _, program in files:
            for decl in program.declarations:
                if isinstance(decl, (FunctionDecl, StructDecl)):
                    self.names.setdefault(decl.name, decl)

    def qualify(self, name: str) -> str:
        return f'{self.id}.{name}' if self.id else name


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
        self._load_imports(module)

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
                local = imp.alias or name
                if local in module.names:
                    self._error(f"'{local}' is imported from {module_id} and also declared here",
                                imp)
                    continue
                direct.setdefault(local, set()).add(imported.qualify(name))
                explicit.add(local)
            else:
                for name in imported.names:
                    if name != 'main':
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
            if isinstance(node, MemberExpr) and isinstance(node.object, IdentifierExpr) \
                    and node.object.name in aliases and not is_local(node.object.name, scopes) \
                    and node.object.name not in module.names:
                target = self.modules[aliases[node.object.name]]
                if node.member not in target.names:
                    self._error(f"Module '{target.id}' has no '{node.member}'", node)
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
            if isinstance(node, VarDeclStmt) and scopes:
                scopes[-1].add(node.name)       # visible from the next statement on

        for decl in program.declarations:
            if module.id and isinstance(decl, (FunctionDecl, StructDecl)):
                decl.name = module.qualify(decl.name)
            walk(decl, [])

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
