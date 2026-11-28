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

# Fusion's own modules (Task 57.5, D.208, D.210) - the namespace Fusion is reserved for them; Fusion.Core (the
# built-ins) is always there, Fusion.Currency is added when a program uses money (src/semantic/currency.py)
FUSION_MODULES = ('Core', 'Currency')

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
                # where it was declared - for `internal` (Task 32.2h)
                decl.module_id, decl.namespace = module_id, program.namespace
                if isinstance(decl, (FunctionDecl, StructDecl, EnumDecl, ErrorDecl, VarDeclStmt,
                                     TemplateDecl)):
                    self.names.setdefault(decl.name, decl)

    def qualify(self, name: str) -> str:
        return f'{self.id}.{name}' if self.id else name

    def is_public(self, name: str) -> bool:
        return getattr(self.names.get(name), 'is_public', False)

    def visible(self, name: str, namespace: Optional[str]) -> bool:
        """Whether code in another module (of `namespace`) may use the name: it is public, or
        internal and that module shares its namespace (Task 32.2h)."""
        decl = self.names.get(name)
        return getattr(decl, 'is_public', False) or (
            getattr(decl, 'is_internal', False) and namespace is not None
            and getattr(decl, 'namespace', None) == namespace)

    def hidden_text(self, name: str) -> str:
        """Why another module can't use the name."""
        decl = self.names.get(name)
        if getattr(decl, 'is_private_top', False):      # a private type - its module (D.212)
            return f"'{name}' is private to module '{self.id}'"
        if getattr(decl, 'is_internal', False) or not isinstance(decl, (VarDeclStmt, TemplateDecl)):
            namespace = getattr(decl, 'namespace', None)
            where = f"namespace {namespace}" if namespace else f"module '{self.id}'"
            return (f"'{name}' is internal to {where} - only names marked public can be used "
                    f"from another module")
        return f"'{name}' is private to module '{self.id}'"   # a module variable


class ModuleLoader:
    """Loads a program and everything it imports; see the module docstring."""

    def __init__(self, main_file: str, parse_file: ParseFile, libraries: Optional[Dict[str, str]] = None):
        self.main_file = main_file
        self.root = os.path.dirname(os.path.abspath(main_file))
        self.parse_file = parse_file
        self.modules: Dict[str, Module] = {}   # module id -> Module, each loaded once
        self.errors: List[SemanticError] = []
        # `[libraries]` (Task 57.3, D.206, D.213): a namespace -> its folder, searched after the program's own
        self.libraries = {ns: os.path.join(self.root, folder) for ns, folder in (libraries or {}).items()}
        self.folders: Dict[str, str] = {}       # module id -> the folder it was loaded from
        self.wants_currency = False             # `import Fusion.Currency` (57.5)
        self._reported: Set[str] = set()        # errors about where a module is, each said once

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
                if imp.path[0] == 'Fusion' and imp.root is None:     # Fusion's own (57.5, D.210)
                    self._fusion_import(imp)
                    continue
                namespace = self._namespace_import(imp)
                if namespace is not None:          # `import SQL as Q` - the modules Q.X... uses (57.4)
                    for parts in _dotted_uses(program, imp.alias or imp.path[-1]):
                        found = self._namespace_module(namespace, parts[1:], imp)
                        if found is None:
                            self._error_once(f"Namespace {namespace} has no module '{parts[1]}' (in "
                                             f"'{'.'.join(parts)}')", imp)
                        elif found not in self.modules:
                            self._load_module(found, imp)
                    continue
                target = self._resolve(imp)
                if target is not None and target[0] not in self.modules:
                    self._load_module(target[0], imp)

    def _fusion_import(self, imp: ImportDecl) -> None:
        """`import Fusion.Core` (always there - nothing to do) / `import Fusion.Currency` (added with money)."""
        name = imp.path[1] if len(imp.path) > 1 else None
        if name not in FUSION_MODULES or imp.star or len(imp.path) > 2:
            self._error_once(f"Fusion has no module '{'.'.join(imp.path[1:]) or '?'}' - its own modules so far: "
                             f"{', '.join('Fusion.' + m for m in FUSION_MODULES)}; the namespace Fusion is "
                             f"reserved for them (D.210)", imp)
        elif imp.alias is not None:
            self._error_once(f"Fusion.{name} is imported without 'as' - write Fusion.{name}.x or the name "
                             f"alone", imp)
        elif name == 'Currency':
            self.wants_currency = True

    def _namespace_import(self, imp: ImportDecl) -> Optional[str]:
        """`import SQL` / `import SQL as Q` where SQL is a namespace - a folder of module folders, with no
        .fusion files of its own (Task 57.4, D.208): the namespace, or None."""
        if imp.star or self._find(imp.path, imp) is not None:
            return None
        for place in self._places(imp.path, imp):
            if os.path.isdir(place) and any(self._is_module_dir(os.path.join(place, entry))
                                            or os.path.isdir(os.path.join(place, entry))
                                            for entry in os.listdir(place)):
                return '.'.join(imp.path)
        return None

    def _namespace_module(self, namespace: str, rest: List[str], imp: ImportDecl) -> Optional[str]:
        """The module of `namespace` the names `rest` start with (Database in Q.Database.name), or None."""
        base = namespace.split('.')
        for k in range(1, len(rest) + 1):
            parts = base + rest[:k]
            folder = self._find(parts, ImportDecl(location=imp.location, path=parts, root=imp.root))
            if folder is not None:
                return self._found('.'.join(parts), folder, imp) and '.'.join(parts)
        return None

    def _resolve(self, imp: ImportDecl) -> Optional[Tuple[str, Optional[str]]]:
        """(module id, imported name or None) for an import line, or None after an error."""
        parts = imp.path
        folder = self._find(parts, imp)
        if imp.star or folder is not None:
            if folder is None:
                self._error(self._missing_text(parts, imp), imp)
                return None
            return self._found('.'.join(parts), folder, imp)
        if len(parts) > 1:
            folder = self._find(parts[:-1], imp)
            if folder is not None:
                found = self._found('.'.join(parts[:-1]), folder, imp)
                return None if found is None else (found[0], parts[-1])
        self._error(self._missing_text(parts, imp), imp)
        return None

    def _found(self, module_id: str, folder: str, imp: ImportDecl) -> Optional[Tuple[str, None]]:
        """One module, one folder: the same module found in another folder by another import is an error."""
        known = self.folders.setdefault(module_id, folder)
        if os.path.normcase(os.path.abspath(known)) != os.path.normcase(os.path.abspath(folder)):
            self._error_once(f"Module '{module_id}' is imported from two folders: {known} and {folder} - "
                             f"keep one", imp)
            return None
        return module_id, None

    def _places(self, parts: List[str], imp: ImportDecl) -> List[str]:
        """Where module `parts` may be (D.206): a path written in the import (`import "C:/vendor".SQL.Database`),
        or the program's folder, then each `[libraries]` namespace it starts with."""
        if imp.root is not None:
            return [os.path.join(self.root, imp.root, *parts)]
        places = [os.path.join(self.root, *parts)]
        for namespace, folder in self.libraries.items():
            names = namespace.split('.')
            if parts[:len(names)] == names:
                places.append(os.path.join(folder, *parts[len(names):]))
        return places

    @staticmethod
    def _is_module_dir(folder: str) -> bool:
        return os.path.isdir(folder) and any(f.endswith('.fusion') for f in os.listdir(folder))

    def _find(self, parts: List[str], imp: ImportDecl) -> Optional[str]:
        """The folder of module `parts`, or None; found in two places is an error naming both."""
        found = [p for p in self._places(parts, imp) if self._is_module_dir(p)]
        if len(found) > 1:
            self._error_once(f"Module '{'.'.join(parts)}' is in two places: {found[0]} and {found[1]} - "
                             f"keep one, or import it with its path", imp)
        return found[0] if found else None

    def _missing_text(self, parts: List[str], imp: ImportDecl) -> str:
        where = (f"in {os.path.join(imp.root, *parts)}" if imp.root is not None else
                 f"next to the main file, or in a library listed in [libraries]")
        return (f"No module '{'.'.join(parts)}' - expected a folder {'/'.join(parts)}/ with .fusion files "
                f"{where}")

    def _error_once(self, message: str, node) -> None:
        if message not in self._reported:
            self._reported.add(message)
            self._error(message, node)

    def _load_module(self, module_id: str, imp: ImportDecl) -> None:
        parts = module_id.split('.')
        for part in parts:
            if '__' in part or part in TYPE_CLASSES:
                self._error(f"'{part}' can't be a module name (it is a built-in type class, "
                            f"or contains '__')", imp)
                return
        folder = self.folders[module_id]
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
        for path, program in files:
            self._check_lines(module_id, path, program)
        module = Module(module_id, files)
        self.modules[module_id] = module   # registered before its own imports: no loops
        if 'main' in module.names:
            self._error(f"Module '{module_id}' can't have a main function - only the program's "
                        f"main file can", module.names['main'])
        self._check_public_types(module)
        self._load_imports(module)

    def _check_lines(self, module_id: str, path: str, program: ProgramNode) -> None:
        """A file's `namespace` / `module` lines must match its folder, which gives both: SQL/Database/ is
        namespace SQL, module Database; money/ is module money without a namespace (Task 57.1, D.204). The
        folder's namespace is then the file's - what `internal` shares (D.207)."""
        parts = module_id.split('.')
        namespace, name = '.'.join(parts[:-1]) or None, parts[-1]
        folder = '/'.join(parts) + '/'
        file_name = folder + os.path.basename(path)
        if parts[0] == 'Fusion':
            self._error(f"{file_name}: the namespace Fusion is reserved for Fusion's own modules (D.210) - "
                        f"give the folder another name", program)
        if program.namespace is not None and program.namespace != namespace:
            if namespace is None:
                fix = (f"move the module into a folder {program.namespace.replace('.', '/')}/ "
                       f"({program.namespace.replace('.', '/')}/{name}/), or remove the line")
                where = f"its folder {folder} is a module without a namespace"
            else:
                fix = f"write 'namespace {namespace}', or move the file"
                where = f"its folder {folder} makes it namespace {namespace}"
            self._error(f"{file_name} says 'namespace {program.namespace}', but {where} - {fix}", program)
        if program.module is not None and program.module != name:
            self._error(f"{file_name} says 'module {program.module}', but its folder {folder} makes it "
                        f"module {name} - write 'module {name}', or move the file", program)
        program.namespace = namespace
        if namespace is not None:          # a structured module (D.211): its functions and variables static
            for decl in program.declarations:
                if getattr(decl, 'static_written', False) or getattr(decl, 'method_of', None):
                    continue
                if isinstance(decl, FunctionDecl) and not getattr(decl, 'is_static_setup', False):
                    decl.static_missing = ('function', decl.name, module_id)
                elif isinstance(decl, VarDeclStmt) and not decl.is_const:
                    decl.static_missing = ('variable', decl.name, module_id)

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
                self._error(f"The {what} uses the internal {kind} '{name}' - make '{name}' "
                            f"public too", decl)

    # ------------------------------------------------------------------ name rewriting

    def _rewrite_file(self, module: Module, program: ProgramNode) -> None:
        """Rewrite one file's names to internal ones (`round` -> `money.round`)."""
        aliases: Dict[str, str] = {}             # prefix -> module id (`Database`, `SQL.Database` - 57.4)
        spaces: Dict[str, str] = {}              # a namespace's prefix -> the namespace (`Q` -> `SQL` - 57.4)
        direct: Dict[str, Set[str]] = {}         # unprefixed name -> internal names
        explicit: Set[str] = set()               # names from `import M.Name`
        for imp in program.imports:
            if imp.path[0] == 'Fusion' and imp.root is None:
                continue                                 # Fusion's own - checked when loading (57.5)
            namespace = self._namespace_import(imp)
            if namespace is not None:
                prefix = imp.alias or imp.path[-1]
                if prefix in module.names:
                    self._error(f"'{prefix}' is both a namespace and a name declared here - import the "
                                f"namespace with another name using 'as'", imp)
                    continue
                if spaces.get(prefix, namespace) != namespace:
                    self._error(f"Two namespaces are both named '{prefix}' here: {spaces[prefix]} and "
                                f"{namespace} - give one another name with 'as'", imp)
                    continue
                spaces[prefix] = namespace
                continue
            target = self._resolve(imp)
            if target is None:
                continue
            module_id, name = target
            imported = self.modules[module_id]
            aliases.setdefault(module_id, module_id)   # the full name, once imported (D.208)
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
                if not imported.visible(name, program.namespace):
                    self._error(imported.hidden_text(name), imp)
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
                    if imported.visible(name, program.namespace):   # .*: the public names only
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

        def module_of(parts: List[str]) -> Optional[Tuple[str, int]]:
            """(module id, how many of the parts name it) - the longest prefix that is an imported module:
            `Database`, `SQL.Database`, or a namespace's `Q.Database` (57.4)."""
            for k in range(len(parts) - 1, 0, -1):
                key = '.'.join(parts[:k])
                if key in aliases:
                    return aliases[key], k
                if k > 1 and parts[0] in spaces:
                    module_id = '.'.join([spaces[parts[0]]] + parts[1:k])
                    if module_id in self.modules:
                        return module_id, k
            return None

        def type_name(name: str, node: ASTNode) -> str:
            if '.' in name:
                parts = name.split('.')
                found = module_of(parts)
                if found is None or found[1] != len(parts) - 1:
                    self._error(f"No module '{'.'.join(parts[:-1])}' is imported here (for the type '{name}')",
                                node)
                    return name
                rest = parts[-1]
                target = self.modules[found[0]]
                if rest not in target.names:
                    self._error(f"Module '{target.id}' has no '{rest}'", node)
                elif not target.visible(rest, program.namespace) and target is not module:
                    self._error(target.hidden_text(rest), node)
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
            path = _member_path(node) if isinstance(node, MemberExpr) else None
            found = module_of(path) if path and not is_local(path[0], scopes) \
                and path[0] not in module.names else None
            if found is not None and found[1] == len(path) - 1:
                target = self.modules[found[0]]
                if node.member not in target.names:
                    self._error(f"Module '{target.id}' has no '{node.member}'", node)
                elif not target.visible(node.member, program.namespace) and target is not module:
                    self._error(target.hidden_text(node.member), node)
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
                if getattr(decl, 'interface_of', None):      # an interface's function names it in full too
                    decl.interface_of = module.qualify(decl.interface_of)
                if getattr(decl, 'method_of', None):         # so does a class's function (its private fields)
                    decl.method_of = module.qualify(decl.method_of)
            if isinstance(decl, ErrorDecl) and decl.parent != 'Error':
                decl.parent = type_name(decl.parent, decl)   # the parent error type (Task 26.9)
            if isinstance(decl, StructDecl):          # what it implements / inherits, by full name (57.2)
                decl.interfaces = [type_name(n, decl) for n in decl.interfaces]
                if decl.class_parent:
                    decl.class_parent = type_name(decl.class_parent, decl)
                if decl.parent:
                    decl.parent = type_name(decl.parent, decl)
            walk(decl, [])

    def _declaration(self, internal: str):
        """The declaration an internal name (`files.FileError`, or a main-file name) means."""
        module_id, _, name = internal.rpartition('.')
        module = self.modules.get(module_id)
        return module.names.get(name) if module is not None else None

    def _error(self, message: str, node) -> None:
        location = getattr(node, 'location', None)
        self.errors.append(SemanticError(message, location))


def _member_path(node) -> Optional[List[str]]:
    """`SQL.Database.name` as ['SQL', 'Database', 'name'] - a chain of members on a name, or None."""
    parts = []
    while isinstance(node, MemberExpr):
        parts.append(node.member)
        node = node.object
    if not isinstance(node, IdentifierExpr):
        return None
    return [node.name] + parts[::-1]


def _dotted_uses(program: ProgramNode, prefix: str) -> List[List[str]]:
    """Every dotted name in a file starting with `prefix` - member chains and types (`Q.Database.name`,
    `Q.Database.Conn c`): which modules a namespace import needs (57.4)."""
    uses = []

    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
            return
        if not is_dataclass(node) or isinstance(node, type):
            return
        if isinstance(node, MemberExpr):
            path = _member_path(node)
            if path and path[0] == prefix and len(path) > 1:
                uses.append(path)
                return
        if isinstance(node, StructType) and node.name.startswith(prefix + '.'):
            uses.append(node.name.split('.'))
        for f in dataclass_fields(node):
            if f.name not in _SKIP_FIELDS:
                walk(getattr(node, f.name))
    walk(program.declarations)
    return uses


def load_program(main_file: str, main_program: ProgramNode, parse_file: ParseFile,
                 libraries: Optional[Dict[str, str]] = None) -> Tuple[ProgramNode, List[SemanticError]]:
    """The whole program - the main file plus every module it imports - as one ProgramNode,
    with any import errors. A program without imports comes back unchanged."""
    if main_program.namespace is not None or main_program.module is not None:
        line = (f"namespace {main_program.namespace}" if main_program.namespace is not None
                else f"module {main_program.module}")
        return main_program, [SemanticError(
            f"The main file is the program - it belongs to no namespace or module, so '{line}' can't be "
            f"written in it; a module is a folder of files next to it (D.204)", main_program.location)]
    if not main_program.imports:
        return main_program, fusion_names(main_program)
    loader = ModuleLoader(main_file, parse_file, libraries)
    program = loader.load(main_program)
    program.wants_currency = loader.wants_currency
    return program, loader.errors + (fusion_names(program) if not loader.errors else [])


def fusion_names(program: ProgramNode) -> List[SemanticError]:
    """Fusion's own modules by their full names (Task 57.5, D.208): `Fusion.Core.print(...)` is `print(...)`,
    `Fusion.Currency.Currency.round(m)` is `Currency.round(m)`, a type `Fusion.Currency.Currency` is `Currency`.
    A program can't declare a name Fusion of its own (the namespace is reserved - D.210), so no scope is needed."""
    errors: List[SemanticError] = []

    def check(parts: List[str], node) -> bool:
        if parts[1] in FUSION_MODULES:
            return True
        errors.append(SemanticError(f"Fusion has no module '{parts[1]}' - its own modules so far: "
                                    f"{', '.join('Fusion.' + m for m in FUSION_MODULES)}", node.location))
        return False

    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
            return
        if not is_dataclass(node) or isinstance(node, type):
            return
        if isinstance(node, MemberExpr):
            path = _member_path(node)
            if path and path[0] == 'Fusion' and len(path) == 3:
                if check(path, node):
                    replacement = IdentifierExpr(location=node.location, name=path[2])
                    node.__class__ = IdentifierExpr
                    node.__dict__.clear()
                    node.__dict__.update(replacement.__dict__)
                return
        if isinstance(node, StructType) and node.name.startswith('Fusion.'):
            parts = node.name.split('.')
            if len(parts) == 3 and check(parts, node):
                node.name = parts[2]
            return
        for f in dataclass_fields(node):
            if f.name not in _SKIP_FIELDS:
                walk(getattr(node, f.name))
    walk(program.declarations)
    return errors


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
    program, errors = load_program(main_file, program, parse, config.libraries if config is not None else None)
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
    """A module's interface (Task 18.4.4): its public and internal structs and functions with
    their types - what other modules may rely on; never private ones (D.115, Task 50.5). A
    readonly result is shown with its function (D.110). The groundwork for library signatures
    and capability checks (Task 19)."""
    lines = [f'module {module.id}']
    for name in sorted(module.names):
        decl = module.names[name]
        if not (decl.is_public or getattr(decl, 'is_internal', False)):
            continue                                   # private: never shown (D.115)
        level = 'public' if decl.is_public else 'internal'
        if isinstance(decl, StructDecl):
            lines.append(f"    {level} {'class' if decl.is_class else 'struct'} {name}")
            for f in decl.fields:
                lines.append(f'        {type_text(f.field_type, module.id)} {f.name}')
        elif isinstance(decl, ErrorDecl):
            parent = '' if decl.parent == 'Error' else f' : {decl.parent}'
            lines.append(f'    {level} error {name}{parent}')   # Task 26.9
            for f in decl.fields:
                lines.append(f'        {type_text(f.field_type, module.id)} {f.name}')
        elif isinstance(decl, VarDeclStmt):
            const = 'const ' if decl.is_const else ''   # a module variable (Task 44.1)
            lines.append(f'    {level} {const}{type_text(decl.var_type, module.id)} {name}')
        elif isinstance(decl, EnumDecl):
            lines.append(f'    {level} enum {name}')         # Task 25
            for v in decl.variants:
                data = ', '.join(f'{type_text(f.field_type, module.id)} {f.name}' for f in v.fields)
                value = f' = {v.value}' if v.explicit_value else ''
                lines.append(f'        {v.name}{f"({data})" if v.fields else ""}{value}')
        else:
            params = []
            for p in decl.parameters:
                text = f'{type_text(p.param_type, module.id)} {p.name}'
                if getattr(p, 'is_readonly', False):
                    text = 'readonly ' + text            # only read, never changed (32.2e)
                if getattr(p, 'kept', False):
                    text += ' (kept)'        # the function keeps it: a call moves the argument (D.100, 33.7)
                if isinstance(p.default_value, LiteralExpr):
                    value = p.default_value.value
                    shown = {'string': f'"{value}"', 'char': f"'{value}'"}.get(
                        p.default_value.type_hint, str(value).lower() if isinstance(value, bool) else str(value))
                    text += f' = {shown}'
                elif p.default_value is not None:
                    text += ' = ...'
                params.append(text)
            marker = ', Error' if decl.returns_error else ''    # can fail (Task 26.7)
            readonly = 'readonly ' if getattr(decl, 'returns_readonly', False) else ''   # 50.5
            lines.append(f'    {level} {readonly}{type_text(decl.return_type, module.id)}{marker} function '
                         f'{name}({", ".join(params)})')
    return lines


def program_interfaces(main_file: str, only: Optional[str] = None,
                       config=None) -> Tuple[List[str], List[str]]:
    """(interface lines of every module the program imports - or just `only`, errors)."""
    parse = make_file_parser(config)
    with open(main_file, encoding='utf-8') as f:
        program = parse(f.read(), main_file)
    loader = ModuleLoader(main_file, parse)
    whole = loader.load(program)
    if loader.errors:
        return [], [str(e) for e in loader.errors]
    try:
        # analysed, so the ownership pass marks the parameters a function keeps (33.7, D.100); its errors
        # are the compiler's to report - the interface is printed from what is known
        from src.semantic import SemanticAnalyzer
        SemanticAnalyzer.for_project(config).analyze(whole)
    except Exception:            # noqa: BLE001 - a program that doesn't compile still has an interface
        pass
    if only is not None and only not in loader.modules:
        return [], [f"The program doesn't import a module named '{only}' "
                    f"(it imports: {', '.join(sorted(loader.modules)) or 'none'})"]
    lines = []
    for module_id in sorted(loader.modules):
        if only is None or module_id == only:
            lines += module_interface(loader.modules[module_id]) + ['']
    return lines, []
