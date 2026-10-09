"""C Code Generator for Fusion.

Generates C source code from Fusion AST nodes using the visitor pattern.
Supports MVP features: functions, basic types, expressions, and statements.

Split into focused modules (Task 12.5 - C Codegen Module Split):
- c_types.py: Fusion type -> C type mapping (TypeMapperMixin)
- c_names.py: C keyword name mangling (mangle_function_name)
- c_runtime.py: print()/len()/interpolation builtin lowering (RuntimeLoweringMixin)
This file keeps AST traversal, statement/declaration codegen, and output management.
"""

from dataclasses import fields as dataclass_fields, is_dataclass
from typing import List, Set
import json
import os
from ..parser.ast_nodes import (
    ASTNode, ProgramNode, FunctionDecl, ParameterDecl,
    PrimitiveType, ArrayType, FunctionType, StructType, StructDecl,
    LiteralExpr, IdentifierExpr, BinaryExpr, UnaryExpr,
    CallExpr, LambdaExpr, NamedArgument,
    ArrayLiteralExpr, IndexExpr, MemberExpr,
    ExpressionStmt, VarDeclStmt, AssignmentStmt, IfStmt,
    WhileStmt, ForStmt, ReturnStmt, BreakStmt, ContinueStmt,
    BlockStmt
)
from .c_types import TypeMapperMixin
from .c_names import mangle_function_name, array_length_name
from .c_runtime import RuntimeLoweringMixin, escape_c_text
from .c_memory import MemoryManagementMixin, RUNTIME_PRELUDE


class CCodeGenerator(TypeMapperMixin, RuntimeLoweringMixin, MemoryManagementMixin):
    """Generates C code from Fusion AST.

    Uses visitor pattern to traverse the AST and generate equivalent C code.
    Supports MVP features: functions, basic types, expressions, statements.

    Type mapping (map_type) comes from TypeMapperMixin (c_types.py); print()/len()/
    interpolation lowering comes from RuntimeLoweringMixin (c_runtime.py). Both are
    mixins rather than standalone functions because they need `self` - map_type()
    recurses via self.map_type(...), and the runtime helpers call self.visit(...).

    Attributes:
        output: List of generated C code lines
        indent_level: Current indentation level
        includes: Set of required C header includes
        generated_functions: List of generated function signatures
    """

    def __init__(self):
        """Initialize code generator."""
        self.output: List[str] = []
        self.indent_level: int = 0
        self.includes: Set[str] = set()
        self.generated_functions: List[str] = []

        # Add standard includes
        self.includes.add('<stdio.h>')   # For printf
        self.includes.add('<stdbool.h>') # For bool type
        self.includes.add('<string.h>')  # For string operations
        self.includes.add('<math.h>')    # For math operations (pow, etc.)
        self.includes.add('<stdlib.h>')  # malloc/free for strings (Task 18.3.1)
        self.includes.add('<stdarg.h>')  # run-time error messages (Task 18.3.1)

        # String ownership state (Task 18.3.1), also reset by generate() - set here too so
        # statement and expression visitors work when called directly (unit tests do)
        self.consumed = set()
        self.stmt_temps = []
        self.cleanup_scopes = []
        self.temp_scopes = []
        self.temp_count = 0

    def generate(self, program: ProgramNode) -> str:
        """Generate C code from program AST.

        Args:
            program: Root AST node

        Returns:
            Complete C source code as string
        """
        # Clear previous state
        self.output.clear()
        self.generated_functions.clear()
        self.function_typedefs = {}      # function types -> typedef names (Task 18.1.3)
        self.lambda_definitions = []     # lifted lambda functions, as C lines (Task 18.1.3)
        self.lambda_count = 0
        self.array_wrappers = {}         # returned-array wrapper structs (Task 18.2.4)
        self.temp_scopes = []            # per-function temporary declarations (Task 18.2.2)
        self.temp_count = 0
        self.argument_temps = {}         # id(argument expression) -> its temporary's name
        # Strings and cleanup (Task 18.3.1) - see c_memory.py
        self.consumed = set()            # ids of fresh values something has taken over
        self.stmt_temps = []             # per statement: temporaries to free after it
        self.cleanup_scopes = []         # per block: owned variables to free when it ends

        # Function declarations by name - call lowering needs each callee's parameter
        # types, to add hidden array-length arguments (Task 18.1.2)
        self.function_decls = {
            decl.name: decl for decl in program.declarations if isinstance(decl, FunctionDecl)
        }
        # Struct declarations by name - default values of struct-typed fields and arrays
        # need them (Task 18.2.3)
        self.struct_decls = {
            decl.name: decl for decl in program.declarations if isinstance(decl, StructDecl)
        }

        # Generate includes, then the runtime every program shares (Task 18.3.1)
        self._generate_includes()
        self.output.extend(RUNTIME_PRELUDE.splitlines())
        self.emit()

        # Struct typedefs come first (Task 18.2.1) - function types, forward declarations
        # and function bodies may all use them
        self._generate_struct_definitions(program)
        typedef_index = len(self.output)

        # Generate forward declarations
        self._generate_forward_declarations(program)
        lambda_index = len(self.output)

        # Generate all functions
        # Ensure main() is generated last (C convention)
        main_func = None
        other_funcs = []

        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                if decl.name == 'main':
                    main_func = decl
                else:
                    other_funcs.append(decl)

        # Generate non-main functions first
        for func in other_funcs:
            self.visit(func)

        # Generate main function last
        if main_func:
            self.visit(main_func)

        # Function types and lambdas are only discovered while generating the code above,
        # but C needs them declared first: lifted lambdas go after the forward declarations
        # (they may call any function), and typedefs right after the includes. Insert the
        # later position first so the earlier index stays valid
        if self.lambda_definitions:
            self.output[lambda_index:lambda_index] = self.lambda_definitions
        typedef_lines = self.function_typedef_lines()
        if typedef_lines:
            self.output[typedef_index:typedef_index] = (
                ['// Function types'] + typedef_lines + ['']
            )
        # Wrappers for returned arrays (Task 18.2.4) - after the structs they may hold
        wrapper_lines = self.array_wrapper_lines()
        if wrapper_lines:
            self.output[typedef_index:typedef_index] = (
                ['// Returned arrays'] + wrapper_lines + ['']
            )

        # Return complete C code
        return '\n'.join(self.output)

    # Statements whose temporaries are freed when they finish (Task 18.3.1)
    _STATEMENTS = (ExpressionStmt, VarDeclStmt, AssignmentStmt, ReturnStmt, IfStmt,
                   WhileStmt, ForStmt)

    def visit(self, node: ASTNode) -> str:
        """Visit an AST node and generate C code.

        Args:
            node: AST node to visit

        Returns:
            Generated C code for this node
        """
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        if isinstance(node, self._STATEMENTS) and hasattr(self, 'stmt_temps'):
            self.begin_statement()
            try:
                return visitor(node)
            finally:
                self.end_statement()
        return visitor(node)

    def generic_visit(self, node: ASTNode) -> str:
        """Handle unknown node types."""
        raise NotImplementedError(f"No visitor for {type(node).__name__}")

    def emit(self, code: str = '') -> None:
        """Emit a line of C code with proper indentation.

        Args:
            code: Code to emit (without indentation)
        """
        if code:
            indent = '    ' * self.indent_level
            self.output.append(f'{indent}{code}')
        else:
            self.output.append('')  # Blank line

    def emit_line(self, code: str) -> None:
        """Emit a line of C code with semicolon.

        Args:
            code: Code to emit (semicolon added automatically)
        """
        self.emit(f'{code};')

    def indent(self) -> None:
        """Increase indentation level."""
        self.indent_level += 1

    def dedent(self) -> None:
        """Decrease indentation level."""
        if self.indent_level > 0:
            self.indent_level -= 1

    def emit_block_start(self) -> None:
        """Emit opening brace and increase indentation."""
        self.emit('{')
        self.indent()

    def emit_block_end(self) -> None:
        """Emit closing brace and decrease indentation."""
        self.dedent()
        self.emit('}')

    def _generate_includes(self) -> None:
        """Generate #include directives."""
        for include in sorted(self.includes):
            self.emit(f'#include {include}')
        self.emit()  # Blank line

    # Zero value per primitive type, for struct fields with no default (Task 18.2.1). An
    # empty string rather than NULL, so printing a never-set string field is safe
    _ZERO_VALUES = {
        'int': '0', 'float': '0.0f', 'double': '0.0', 'bool': 'false', 'char': "'\\0'",
        'string': 'FUSION_STR("")',
    }

    # Arrays up to this size whose default isn't all-zero get their defaults spelled out in
    # the initializer; bigger ones are filled in a loop (Task 18.2.3)
    _INLINE_DEFAULTS_LIMIT = 64

    def _generate_struct_definitions(self, program: ProgramNode) -> None:
        """Emit one C typedef per struct (Task 18.2.1):

            typedef struct Point {
                int x;
                int y;
            } Point;

        A string field is a `char*` - it holds a string value exactly like a string variable
        does. Strings can't change at run time yet, so copying the pointer behaves the same
        as copying the text; Task 18.3 gives string fields their own growable buffers.

        An array field is a C array inside the struct (`int scores[3];`), so copying the
        struct copies the array too. C needs a struct defined before another struct can hold
        it, so structs are emitted in dependency order rather than source order (Task
        18.2.3) - semantic analysis has already rejected cycles.
        """
        structs = [d for d in program.declarations if isinstance(d, StructDecl)]
        if not structs:
            return
        by_name = {s.name: s for s in structs}
        ordered, seen = [], set()

        def add(struct):
            if struct.name in seen:
                return
            seen.add(struct.name)
            for field in struct.fields:
                inner = field.field_type
                if isinstance(inner, ArrayType):
                    inner = inner.element_type
                if isinstance(inner, StructType) and inner.name in by_name:
                    add(by_name[inner.name])
            ordered.append(struct)

        for struct in structs:
            add(struct)

        self.emit('// Structs')
        for struct in ordered:
            c_name = self._mangle_function_name(struct.name)
            self.emit(f'typedef struct {c_name} {{')
            self.indent()
            for field in struct.fields:
                name = self._field_name(field.name)
                if isinstance(field.field_type, ArrayType):
                    element = self.map_type(field.field_type.element_type)
                    self.emit_line(f'{element} {name}[{field.field_type.size}]')
                else:
                    self.emit_line(f'{self.map_type(field.field_type)} {name}')
            self.dedent()
            self.emit(f'}} {c_name};')
        self.emit()

        # Copy/free helpers for structs holding strings (Task 18.3.1)
        helpers = self.struct_helper_lines(ordered)
        if helpers:
            self.output.extend(['// Struct copy and cleanup'] + helpers + [''])

    def _field_name(self, name: str) -> str:
        """C name of a struct field - mangled like a function name if it's a C keyword."""
        return self._mangle_function_name(name)

    def _struct_initializer(self, struct: StructDecl, values) -> str:
        """C99 compound literal building a struct: `(Point){3, 4}` (Task 18.2.1).

        Args:
            struct: The struct being built
            values: One AST expression per field, in field order - or None for a field with
                no value given (it gets its default, or else zero)
        """
        parts = []
        for field, value in zip(struct.fields, values):
            if value is None:
                value = field.default_value
            if value is None:
                parts.append(self._default_value_code(field.field_type))
            elif id(value) in getattr(self, 'argument_temps', {}):
                parts.append(self.argument_temps[id(value)])  # already owned (see below)
            else:
                # The struct owns its fields: strings are copied in (Task 18.3.1)
                parts.append(self.owned_value(value, field.field_type))
        return f'({self._mangle_function_name(struct.name)}){{{", ".join(parts)}}}'

    # ========================================================================
    # Default values (Task 18.2.3)
    # ========================================================================

    def _struct_decl(self, type_node: StructType) -> StructDecl:
        return type_node.declaration or getattr(self, 'struct_decls', {})[type_node.name]

    def _is_zero_safe(self, type_node) -> bool:
        """True if C's all-zero value is also the Fusion default for this type. Not for a
        string (zero would be a NULL pointer - Fusion's default is ""), or a struct with a
        field default or a string anywhere inside it."""
        if isinstance(type_node, PrimitiveType):
            return type_node.name != 'string'
        if isinstance(type_node, ArrayType):
            return self._is_zero_safe(type_node.element_type)
        if isinstance(type_node, StructType):
            return all(f.default_value is None and self._is_zero_safe(f.field_type)
                       for f in self._struct_decl(type_node).fields)
        return True

    def _zero_initializer(self, type_node) -> str:
        """An all-zero C initializer with one level of braces per level of nesting -
        `{0}` for int[3], `{{0}}` for Point[3]. C zero-fills the rest either way, but a bare
        `{0}` for nested data draws GCC's -Wmissing-braces warning."""
        if isinstance(type_node, ArrayType):
            return '{' + self._zero_initializer(type_node.element_type) + '}'
        if isinstance(type_node, StructType):
            return '{' + self._zero_initializer(self._struct_decl(type_node).fields[0].field_type) + '}'
        return '0'

    def _default_value_code(self, type_node) -> str:
        """C initializer for a value nobody gave: zero for numbers, false, '\\0', "" for a
        string, a struct's own field defaults, and an array of default elements."""
        if isinstance(type_node, PrimitiveType):
            return self._ZERO_VALUES.get(type_node.name, '0')
        if isinstance(type_node, StructType):
            struct = self._struct_decl(type_node)
            return self._struct_initializer(struct, [None] * len(struct.fields))
        if isinstance(type_node, ArrayType):
            if self._is_zero_safe(type_node.element_type):
                return self._zero_initializer(type_node)
            element = self._default_value_code(type_node.element_type)
            return '{' + ', '.join([element] * type_node.size) + '}'
        return '0'

    # ========================================================================
    # Argument evaluation order (Task 18.2.2)
    # ========================================================================

    def _argument_code(self, value: ASTNode) -> str:
        """C code for one argument: its temporary, if _evaluate_in_written_order stored it
        in one, otherwise the expression itself."""
        temps = getattr(self, 'argument_temps', {})
        return temps.get(id(value)) or self.visit(value)

    # Fields that aren't sub-expressions evaluated at the call: type information, links back
    # to declarations (a function's own body!), and scopes
    _NOT_EVALUATED = ('location', 'inferred_type', 'scope', 'resolved_arguments',
                      'callee_declaration', 'declaration', 'parameters', 'return_type')

    @classmethod
    def _contains(cls, node, node_type) -> bool:
        """True if an expression contains a node of `node_type` anywhere it is evaluated. A
        lambda's body isn't evaluated when the lambda value is created, so it's skipped."""
        if isinstance(node, node_type):
            return True
        if isinstance(node, list):
            return any(cls._contains(item, node_type) for item in node)
        if isinstance(node, LambdaExpr):
            return False
        if is_dataclass(node) and isinstance(node, ASTNode):
            return any(cls._contains(getattr(node, f.name), node_type)
                       for f in dataclass_fields(node) if f.name not in cls._NOT_EVALUATED)
        return False

    @classmethod
    def _contains_call(cls, node) -> bool:
        """True if an expression contains a call - a call may have side effects (changing an
        array passed to it, printing), so its timing can matter."""
        return cls._contains(node, CallExpr)

    @classmethod
    def _order_matters(cls, values) -> bool:
        """Whether evaluating these argument expressions in a different order could change
        the result (Task 18.2.2b). In Fusion a call can only change the caller's data
        through an array passed to it - there are no globals or closures, and structs are
        copies - so the order is visible only when at least one argument contains a call
        and another one also contains a call or reads an array element."""
        calls = sum(1 for v in values if cls._contains_call(v))
        touched = sum(1 for v in values if cls._contains_call(v) or cls._contains(v, IndexExpr))
        return calls >= 1 and touched >= 2

    def _new_temp(self, c_type: str) -> str:
        """Declare a compiler temporary at the top of the C function being generated."""
        self.temp_count = getattr(self, 'temp_count', 0) + 1
        name = f'fusion_arg_{self.temp_count}'
        self.temp_scopes[-1].append(f'{c_type} {name};')
        return name

    def _evaluate_in_written_order(self, node: CallExpr, slot_types: list,
                                   owning: bool = False) -> list:
        """Every call's arguments are evaluated left to right *as written* (Tasks 18.2.2 and
        18.2.2b), but C evaluates a call's arguments in no guaranteed order - and named ones
        have been moved to their parameter's position. So when the order could change the
        result (see _order_matters), each argument is first stored in a temporary, in the
        written order, using C's comma operator (which does guarantee left-to-right):

            f(b = next(), a = next())  ->  (fusion_arg_1 = next(), fusion_arg_2 = next(),
                                            f(fusion_arg_2, fusion_arg_1))

        Array arguments are left in place: they are passed by reference (nothing to
        evaluate early), and C can't copy an array into a temporary.

        Args:
            node: The call (already type-checked - resolved_arguments is set)
            slot_types: The parameter/field type for each entry of resolved_arguments
            owning: True for a struct constructor - its fields own their values, so a
                temporary holds an owned copy (Task 18.3.1); a function only borrows

        Returns:
            The temporary assignments, in written order (empty if none are needed)
        """
        written = [arg.value if isinstance(arg, NamedArgument) else arg for arg in node.arguments]
        if not getattr(self, 'temp_scopes', None) or not self._order_matters(written):
            return []
        assignments = []
        for value in written:
            index = next(i for i, resolved in enumerate(node.resolved_arguments) if resolved is value)
            if isinstance(slot_types[index], ArrayType):
                continue
            code = self.owned_value(value, slot_types[index]) if owning else self.visit(value)
            name = self._new_temp(self.map_type(slot_types[index]))
            assignments.append(f'{name} = {code}')
            self.argument_temps[id(value)] = name
        return assignments

    def _generate_forward_declarations(self, program: ProgramNode) -> None:
        """Generate forward declarations for all functions.

        Args:
            program: Program AST node
        """
        self.emit('// Forward declarations')
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                return_type = self.return_c_type(decl.return_type)
                # Special case: void main() -> int main() in C
                if decl.name == 'main' and return_type == 'void':
                    return_type = 'int'
                func_name = self._mangle_function_name(decl.name)
                params = self._c_parameter_list(decl.parameters)
                self.emit(f'{return_type} {func_name}({params});')
        self.emit()  # Blank line

    def _c_parameter_list(self, parameters) -> str:
        """Build a C parameter list - shared by forward declarations and definitions.

        Array parameters (Task 18.1.2): `int[5] values` stays a C array parameter, `int
        values[5]` (its length is a compile-time constant); `int[] values` accepts any size,
        so it becomes `int* values` plus a hidden length parameter (see array_length_name).

        Args:
            parameters: List of ParameterDecl nodes

        Returns:
            The C parameter list text, or 'void' if there are no parameters
        """
        if not parameters:
            return 'void'
        c_params = []
        for p in parameters:
            if isinstance(p.param_type, ArrayType):
                elem = self.map_type(p.param_type.element_type)
                if p.param_type.size is None:
                    c_params.append(f'{elem}* {p.name}')
                    c_params.append(f'int {array_length_name(p.name)}')
                else:
                    c_params.append(f'{elem} {p.name}[{p.param_type.size}]')
            else:
                c_params.append(f'{self.map_type(p.param_type)} {p.name}')
        return ', '.join(c_params)

    def _mangle_function_name(self, name: str) -> str:
        """Mangle function names that conflict with C keywords.

        See c_names.py (Task 12.5).

        Args:
            name: Fusion function name

        Returns:
            C-safe function name
        """
        return mangle_function_name(name)

    # ========================================================================
    # Expression Visitors
    # ========================================================================

    def visit_LiteralExpr(self, node: LiteralExpr) -> str:
        """Generate C code for literal expression.

        Args:
            node: Literal expression node

        Returns:
            C literal representation
        """
        type_hint = node.type_hint

        if type_hint == 'int':
            return str(node.value)

        elif type_hint == 'float':
            return f'{node.value}f'  # Add 'f' suffix

        elif type_hint == 'double':
            return str(node.value)

        elif type_hint == 'bool':
            return 'true' if node.value else 'false'

        elif type_hint == 'char':
            escaped = escape_c_text(str(node.value), "'")
            return f"'{escaped}'"

        elif type_hint == 'string':
            # Source text as a string value that is never freed (Task 18.3.1)
            escaped = escape_c_text(str(node.value), '"')
            return f'FUSION_STR("{escaped}")'

        elif type_hint == 'null':
            return 'NULL'

        return '0'  # Fallback

    def visit_IdentifierExpr(self, node: IdentifierExpr) -> str:
        """Generate C code for identifier expression.

        Args:
            node: Identifier expression node

        Returns:
            Variable/parameter name
        """
        # A declared function used as a value (Task 18.1.3) - use its C name, which differs
        # from the Fusion name when it collides with a C keyword
        if isinstance(node.inferred_type, FunctionType) and node.name in getattr(self, 'function_decls', {}):
            return self._mangle_function_name(node.name)
        return node.name

    def visit_BinaryExpr(self, node: BinaryExpr) -> str:
        """Generate C code for binary expression.

        Args:
            node: Binary expression node

        Returns:
            C binary operation expression
        """
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.operator

        # Joining strings makes a new string (Task 18.3.2) - held in a temporary unless
        # something takes it over
        if op == '+' and self._is_string(node):
            if self._is_string(node.left) and self._is_string(node.right):
                code = f'fusion_str_concat({left}, {right})'
            elif self._is_string(node.left):
                code = f'fusion_str_concat_char({left}, {right})'
            else:
                code = f'fusion_char_concat_str({left}, {right})'
            if id(node) in self.consumed:
                return code
            return self.fresh_temporary(code, node.inferred_type)

        # Strings compare by their text, never by address (Task 18.3.1 - this was the latent
        # pointer-comparison bug); ordering is alphabetical (byte order)
        if self._is_string(node.left) and self._is_string(node.right):
            if op == '==':
                return f'fusion_str_eq({left}, {right})'
            if op == '!=':
                return f'(!fusion_str_eq({left}, {right}))'
            if op in ('<', '>', '<=', '>='):
                return f'(fusion_str_cmp({left}, {right}) {op} 0)'

        # Map Fusion operators to C operators
        operator_map = {
            # Arithmetic
            '+': '+',
            '-': '-',
            '*': '*',
            '/': '/',
            '%': '%',
            '**': 'pow',  # Power requires math.h

            # Comparison
            '<': '<',
            '>': '>',
            '<=': '<=',
            '>=': '>=',
            '==': '==',
            '!=': '!=',

            # Logical
            'and': '&&',
            'or': '||',
            '&&': '&&',
            '||': '||',
        }

        c_op = operator_map.get(op, op)

        # Special case: power operator
        if op == '**':
            self.includes.add('<math.h>')
            return f'pow({left}, {right})'

        # Add parentheses for clarity
        return f'({left} {c_op} {right})'

    def visit_UnaryExpr(self, node: UnaryExpr) -> str:
        """Generate C code for unary expression.

        Args:
            node: Unary expression node

        Returns:
            C unary operation expression
        """
        operand = self.visit(node.operand)
        op = node.operator

        operator_map = {
            '-': '-',
            '!': '!',
            'not': '!',
        }

        c_op = operator_map.get(op, op)
        return f'({c_op}{operand})'

    @staticmethod
    def _is_string(expr) -> bool:
        inferred = getattr(expr, 'inferred_type', None)
        return isinstance(inferred, PrimitiveType) and inferred.name == 'string'

    def visit_CallExpr(self, node: CallExpr) -> str:
        """A call - whose fresh string (or string-holding) result is held in a temporary
        and freed after the statement, unless something takes it over (Task 18.3.1)."""
        code = self._call_code(node)
        if self.is_fresh(node) and id(node) not in getattr(self, 'consumed', set()):
            return self.fresh_temporary(code, node.inferred_type)
        return code

    def _call_code(self, node: CallExpr) -> str:
        """Generate C code for function call expression.

        Args:
            node: Call expression node

        Returns:
            C function call
        """
        # A struct constructor, Point(3, 4) (Task 18.2.1) - resolved_arguments has every
        # field, with omitted ones filled in from their defaults by the type checker
        if isinstance(node.callee_declaration, StructDecl):
            struct = node.callee_declaration
            ordered = self._evaluate_in_written_order(
                node, [f.field_type for f in struct.fields], owning=True)
            code = self._struct_initializer(struct, node.resolved_arguments)
            return f'({", ".join(ordered + [code])})' if ordered else code

        # Get function name
        if isinstance(node.callee, IdentifierExpr):
            func_name = node.callee.name
            calls_function_value = isinstance(node.callee.inferred_type, FunctionType)

            # Special handling for built-in functions
            if func_name == 'print':
                return self._generate_print_call(node)
            if func_name == 'len':
                return self._generate_len_call(node)
            if func_name in self._STRING_BUILTINS and node.callee_declaration is None:
                return self._string_builtin_call(node)

            # Mangle user-defined function names (a variable holding a function keeps its
            # own name - C calls through a function pointer the same way)
            func = func_name if calls_function_value else self._mangle_function_name(func_name)
        else:
            # Calling the result of an expression, e.g. (func(int x) : x * 2)(5)
            func = f'({self.visit(node.callee)})'

        # Generate arguments - resolved_arguments includes any omitted parameters' default
        # values (Task 18.1.1); it's None only when semantic analysis didn't run
        arguments = node.resolved_arguments if node.resolved_arguments is not None else node.arguments
        # The declared function being called, for its parameter types. The type checker
        # records it (callee_declaration); looking it up by name is only a fallback for
        # code generated without semantic analysis
        callee_decl = node.callee_declaration
        if node.resolved_arguments is None and isinstance(node.callee, IdentifierExpr):
            callee_decl = getattr(self, 'function_decls', {}).get(node.callee.name)
        params = callee_decl.parameters if callee_decl else [None] * len(arguments)

        ordered = []
        if node.resolved_arguments is not None:
            if callee_decl is not None:
                slot_types = [p.param_type for p in params]
            else:
                # A call through a function value: its type has the parameter types
                callee_type = getattr(node.callee, 'inferred_type', None)
                slot_types = callee_type.parameter_types if isinstance(callee_type, FunctionType) else None
            if slot_types is not None:
                ordered = self._evaluate_in_written_order(node, slot_types)

        c_args = []
        for param, arg in zip(params, arguments):
            if param is not None and isinstance(param.param_type, ArrayType):
                c_args.extend(self._array_argument(arg, param.param_type))
            else:
                c_args.append(self._argument_code(arg))
        args = ', '.join(c_args)
        if ordered:
            return f'({", ".join(ordered)}, {func}({args}))'

        return f'{func}({args})'

    # String built-ins (Task 18.3.2): Fusion name -> (C function, takes a "file:line" for
    # run-time errors)
    _STRING_BUILTINS = {
        'substring': ('fusion_str_substring', True), 'contains': ('fusion_str_contains', False),
        'indexOf': ('fusion_str_indexOf', False), 'startsWith': ('fusion_str_startsWith', False),
        'endsWith': ('fusion_str_endsWith', False), 'toUpper': ('fusion_str_toUpper', False),
        'toLower': ('fusion_str_toLower', False), 'trim': ('fusion_str_trim', False),
        'toInt': ('fusion_str_toInt', True), 'toFloat': ('fusion_str_toFloat', True),
        'isInt': ('fusion_str_isInt', False), 'isFloat': ('fusion_str_isFloat', False),
        'toString': (None, False),
    }
    _TO_STRING = {'int': 'fusion_int_to_str', 'float': 'fusion_double_to_str',
                  'double': 'fusion_double_to_str', 'bool': 'fusion_bool_to_str',
                  'char': 'fusion_char_to_str', 'string': 'fusion_str_copy'}

    def _where(self, node) -> str:
        """A C string literal naming a source position, for run-time error messages."""
        location = node.location
        name = os.path.basename(str(getattr(location, 'filename', '')))
        return f'"{escape_c_text(f"{name}:{getattr(location, "line", 0)}", chr(34))}"'

    def _string_builtin_call(self, node: CallExpr) -> str:
        """substring(...), contains(...), toInt(...), ... (Task 18.3.2). Arguments are
        borrowed and evaluated left to right as written."""
        name = node.callee.name
        c_function, needs_where = self._STRING_BUILTINS[name]
        arguments = list(node.arguments)
        if name == 'toString':
            c_function = self._TO_STRING[arguments[0].inferred_type.name]
        codes = [self.visit(arg) for arg in arguments]
        ordered = []
        if self._order_matters(arguments) and self.temp_scopes:
            for i, (arg, code) in enumerate(zip(arguments, codes)):
                temp = self._new_temp(self.map_type(arg.inferred_type))
                ordered.append(f'{temp} = {code}')
                codes[i] = temp
        if needs_where:
            codes.append(self._where(node))
        call = f'{c_function}({", ".join(codes)})'
        return f'({", ".join(ordered)}, {call})' if ordered else call

    def _array_argument(self, arg: ASTNode, param_type: ArrayType) -> list:
        """Lower an argument passed to an array parameter (Task 18.1.2).

        Arrays are passed by reference (C passes a pointer to the first element). An array
        literal becomes a C99 compound literal, `(int[]){1, 2, 3}`, since a bare `{...}` is
        only valid as an initializer. For an `int[]` parameter the array's length follows as
        a second argument: a constant when the size is known, or the caller's own hidden
        length when it is itself forwarding an `int[]` parameter.

        Returns:
            One C argument (`int[N]` parameter) or two (`int[]` parameter: array, length)
        """
        arg_type = arg.inferred_type
        if isinstance(arg, ArrayLiteralExpr):
            elem = self.map_type(arg_type.element_type)
            arg_code = f'({elem}[]){self.visit(arg)}'
        else:
            arg_code = self.visit(arg)

        if param_type.size is not None:
            return [arg_code]
        if arg_type.size is not None:
            return [arg_code, str(arg_type.size)]
        # Forwarding an `int[]` parameter: semantic analysis only allows a bare parameter
        # name here, whose hidden length parameter is in scope
        return [arg_code, array_length_name(arg.name)]

    # _generate_len_call: see RuntimeLoweringMixin (c_runtime.py)

    def visit_ArrayLiteralExpr(self, node: ArrayLiteralExpr) -> str:
        """Generate C code for an array literal: [1, 2, 3] -> {1, 2, 3}

        Only valid as a variable initializer in C (`int arr[3] = {1, 2, 3};`), which is
        the only place Task 9 v1's semantic rules allow an array literal to appear -
        whole-array reassignment and array function arguments are both rejected earlier,
        in the semantic analyzer.

        Args:
            node: Array literal expression node

        Returns:
            C brace-initializer list
        """
        elements_code = ', '.join(self.visit(el) for el in node.elements)
        return '{' + elements_code + '}'

    def visit_IndexExpr(self, node: IndexExpr) -> str:
        """Generate C code for array indexing: arr[i]

        Args:
            node: Index expression node

        Returns:
            C array index expression (valid as both an rvalue and an assignment lvalue)
        """
        array_code = self.visit(node.array)
        index_code = self.visit(node.index)
        # s[i] - one character, bounds-checked (Task 18.3.2)
        if self._is_string(node.array):
            return f'fusion_str_at({array_code}, {index_code}, {self._where(node)})'
        # make()[0] - the returned array is inside its wrapper struct (Task 18.2.4)
        if self._returns_array(node.array):
            return f'{array_code}.data[{index_code}]'
        return f'{array_code}[{index_code}]'

    def visit_NamedArgument(self, node: NamedArgument) -> str:
        """A named argument's C code is its value's - normally codegen reads the values from
        CallExpr.resolved_arguments, already in parameter order (Task 18.2.2)."""
        return self.visit(node.value)

    def visit_MemberExpr(self, node: MemberExpr) -> str:
        """Generate C code for struct field access: point.x (Task 18.2.1)

        Valid as both an rvalue and an assignment lvalue.
        """
        return f'{self.visit(node.object)}.{self._field_name(node.member)}'

    # _FORMAT_SPECIFIERS, _format_specifier_for_expr, _generate_print_call,
    # visit_InterpolatedStringExpr, _generate_interpolated_print,
    # _build_interpolation_format: see RuntimeLoweringMixin (c_runtime.py)

    # ========================================================================
    # Statement Visitors
    # ========================================================================

    def visit_ExpressionStmt(self, node: ExpressionStmt) -> str:
        """Generate C code for expression statement.

        Args:
            node: Expression statement node

        Returns:
            Empty string (code emitted directly)
        """
        expr_code = self.visit(node.expression)
        self.emit_line(expr_code)
        return ''

    def visit_VarDeclStmt(self, node: VarDeclStmt) -> str:
        """Generate C code for variable declaration.

        Args:
            node: Variable declaration node

        Returns:
            Empty string (code emitted directly)
        """
        # A const string (or string-holding) variable is still freed when its block ends,
        # which C's const would forbid - Fusion's own const check already prevents changes
        const_keyword = 'const ' if node.is_const and not self.is_managed(node.var_type) else ''
        try:
            return self._var_decl_code(node, const_keyword)
        finally:
            self.register_owned(node.name, node.var_type, node.location)

    def _var_decl_code(self, node: VarDeclStmt, const_keyword: str) -> str:
        """Emit a variable declaration (see visit_VarDeclStmt)."""
        managed = self.is_managed(node.var_type)

        if isinstance(node.var_type, ArrayType):
            # C array declarator puts the size after the name: `int arr[3]`, not `int[3] arr`
            elem_c_type = self.map_type(node.var_type.element_type)
            size = node.var_type.size
            if size is None:
                raise NotImplementedError(
                    f"Internal compiler error: array '{node.name}' at {node.location} has "
                    "no resolved size - semantic analysis must resolve every array's size "
                    "before code generation."
                )
            if self._returns_array(node.initializer):
                # int[3] a = make() - declared, then the returned array is copied in
                # (Task 18.2.4). Strings start as "" first, since the copy frees the old ones
                wrapper = self.array_wrapper_name(node.initializer.inferred_type)
                if managed:
                    self.emit_line(f'{elem_c_type} {node.name}[{size}] = '
                                   f'{self._default_value_code(node.var_type)}')
                else:
                    self.emit_line(f'{elem_c_type} {node.name}[{size}]')
                self.consumed.add(id(node.initializer))
                self.emit_line(f'{wrapper}_copy({node.name}, {self.visit(node.initializer)})')
            elif node.initializer:
                init_code = self.owned_value(node.initializer, node.var_type)
                self.emit_line(f'{const_keyword}{elem_c_type} {node.name}[{size}] = {init_code}')
            elif self._is_zero_safe(node.var_type.element_type):
                # Zero-initialize, matching Fusion's existing "uninitialized = 0" convention
                # for scalars ({0} zero-fills every element in C, not just the first)
                self.emit_line(f'{const_keyword}{elem_c_type} {node.name}[{size}] = '
                               f'{self._zero_initializer(node.var_type)}')
            elif size <= self._INLINE_DEFAULTS_LIMIT:
                # Strings (and structs with strings or defaults) need each element set - a
                # zero string is a NULL pointer, not "" (Task 18.2.3)
                self.emit_line(f'{const_keyword}{elem_c_type} {node.name}[{size}] = '
                               f'{self._default_value_code(node.var_type)}')
            else:
                # Too many elements to spell out - fill them in a loop
                element = self._default_value_code(node.var_type.element_type)
                self.emit_line(f'{elem_c_type} {node.name}[{size}]')
                self.emit(f'for (int fusion_i = 0; fusion_i < {size}; fusion_i++) {{')
                self.indent()
                self.emit_line(f'{node.name}[fusion_i] = {element}')
                self.dedent()
                self.emit('}')
            return ''

        c_type = self.map_type(node.var_type)
        name = node.name

        # A struct declared without a value starts with every field at its default, or zero
        # (Task 18.2.1)
        if isinstance(node.var_type, StructType) and not node.initializer:
            struct = node.var_type.declaration
            init_code = self._struct_initializer(struct, [None] * len(struct.fields))
            self.emit_line(f'{const_keyword}{c_type} {name} = {init_code}')
            return ''

        if node.initializer:
            init_code = self.owned_value(node.initializer, node.var_type)
            self.emit_line(f'{const_keyword}{c_type} {name} = {init_code}')
        elif managed:
            # A string declared without a value is "" (it used to be an uninitialized
            # pointer)
            self.emit_line(f'{c_type} {name} = {self._default_value_code(node.var_type)}')
        else:
            self.emit_line(f'{const_keyword}{c_type} {name}')

        return ''

    def visit_AssignmentStmt(self, node: AssignmentStmt) -> str:
        """Generate C code for assignment statement.

        Args:
            node: Assignment statement node

        Returns:
            Empty string (code emitted directly)
        """
        # target is an lvalue-producing expression - IdentifierExpr ("x") or IndexExpr
        # ("arr[i]") - both generate valid C lvalue syntax via their own visitor
        target_code = self.visit(node.target)

        # A whole array replaced by one a function returned: moved in (Task 18.2.4)
        if self._returns_array(node.value):
            wrapper = self.array_wrapper_name(node.value.inferred_type)
            self.consumed.add(id(node.value))
            self.emit_line(f'{wrapper}_copy({target_code}, {self.visit(node.value)})')
            return ''

        # Replacing a stored string (or string-holding struct): the new value is made first,
        # then the old one is freed (Task 18.3.1). String and struct assignments need the
        # exact same type, so the value's type is the target's
        value_type = getattr(node.value, 'inferred_type', None)
        if self.is_managed(value_type):
            self.emit(self.set_code(value_type, target_code,
                                    self.owned_value(node.value, value_type)))
            return ''

        value_code = self.visit(node.value)

        self.emit_line(f'{target_code} = {value_code}')
        return ''

    def visit_ReturnStmt(self, node: ReturnStmt) -> str:
        """Generate C code for return statement.

        Args:
            node: Return statement node

        Returns:
            Empty string (code emitted directly)
        """
        return_type = getattr(self, 'current_return_type', None)
        value_code = None
        if node.value and isinstance(return_type, ArrayType):
            # Returned inside the hidden wrapper struct (Task 18.2.4): a literal fills it
            # directly, another call's result already is one, anything else is copied in
            wrapper = self.array_wrapper_name(return_type)
            if isinstance(node.value, ArrayLiteralExpr):
                value_code = f'({wrapper}){{{self.owned_value(node.value, return_type)}}}'
            elif self._returns_array(node.value):
                self.consumed.add(id(node.value))
                value_code = self.visit(node.value)
            else:
                value_code = f'{wrapper}_from({self.visit(node.value)})'
        elif node.value:
            # The caller owns the returned value: a string is copied out (Task 18.3.1)
            value_code = self.owned_value(node.value, return_type)

        # Leaving the function: this statement's temporaries and every owned variable in
        # the function are freed first - after the returned value is safely computed
        owned = self.owned_in_scopes('function') if hasattr(self, 'cleanup_scopes') else []
        if not owned and not self.has_pending_temps():
            self.emit_line(f'return {value_code}' if value_code is not None else 'return')
            return ''
        if value_code is None:
            self.flush_temps()
            self.emit_frees(owned)
            self.emit_line('return')
            return ''
        result = self._declare_temp('ret', self.return_c_type(return_type))
        self.emit_line(f'{result} = {value_code}')
        self.flush_temps()
        self.emit_frees(owned)
        self.emit_line(f'return {result}')
        return ''

    @staticmethod
    def _returns_array(expr) -> bool:
        """True for a call to a function returning an array - whose C value is the hidden
        wrapper struct, not an array (Task 18.2.4)."""
        return isinstance(expr, CallExpr) and isinstance(expr.inferred_type, ArrayType)

    def visit_IfStmt(self, node: IfStmt) -> str:
        """Generate C code for if statement.

        Args:
            node: If statement node

        Returns:
            Empty string (code emitted directly)
        """
        condition = self._settled_condition(self.visit(node.condition))
        self.emit(f'if ({condition}) {{')
        self.indent()

        # Then branch
        self.visit(node.then_branch)

        # Else branch
        if node.else_branch:
            self.dedent()
            self.emit('} else {')
            self.indent()
            self.visit(node.else_branch)

        self.dedent()
        self.emit('}')

        return ''

    def visit_WhileStmt(self, node: WhileStmt) -> str:
        """Generate C code for while loop.

        Args:
            node: While statement node

        Returns:
            Empty string (code emitted directly)
        """
        condition = self.visit(node.condition)
        if self.has_pending_temps():
            # The condition made temporary strings: evaluate it at the top of each pass,
            # free them, then decide (Task 18.3.1)
            self.emit('while (1) {')
            self.indent()
            settled = self._settled_condition(condition)
            self.emit(f'if (!({settled})) break;')
        else:
            self.emit(f'while ({condition}) {{')
            self.indent()

        self.push_scope('loop')
        self.visit(node.body)
        self.pop_scope()

        self.dedent()
        self.emit('}')

        return ''

    def visit_ForStmt(self, node: ForStmt) -> str:
        """Generate C code for for loop.

        Args:
            node: For statement node

        Returns:
            Empty string (code emitted directly)
        """
        # Note: The parser creates ForStmt with variable as a string
        # and iterable as a CallExpr to 'range'

        # For MVP, assume iterable is a range() call
        # Extract start, end, step from range() arguments
        if isinstance(node.iterable, CallExpr):
            callee = node.iterable.callee
            if isinstance(callee, IdentifierExpr) and callee.name == 'range':
                args = node.iterable.arguments

                # range(end) or range(start, end) or range(start, end, step)
                if len(args) == 1:
                    start = '0'
                    end = self.visit(args[0])
                    step = '1'
                elif len(args) == 2:
                    start = self.visit(args[0])
                    end = self.visit(args[1])
                    step = '1'
                elif len(args) >= 3:
                    start = self.visit(args[0])
                    end = self.visit(args[1])
                    step = self.visit(args[2])
                else:
                    # Default fallback
                    start = '0'
                    end = '10'
                    step = '1'
            else:
                # Not a range call - fallback
                start = '0'
                end = '10'
                step = '1'
        else:
            # Not a call expression - fallback
            start = '0'
            end = '10'
            step = '1'

        var_name = node.variable

        # Bounds that made temporary strings are worked out (once) first (Task 18.3.1)
        if self.has_pending_temps():
            start, end, step = (self._settled_value(code, 'int') for code in (start, end, step))

        # Generate for loop header
        # for (int i = start; i < end; i += step)
        self.emit(f'for (int {var_name} = {start}; {var_name} < {end}; {var_name} += {step}) {{')
        self.indent()

        self.push_scope('loop')
        self.visit(node.body)
        self.pop_scope()

        self.dedent()
        self.emit('}')

        return ''

    def visit_BreakStmt(self, node: BreakStmt) -> str:
        """Generate C code for break statement.

        Args:
            node: Break statement node

        Returns:
            Empty string (code emitted directly)
        """
        # Leaving the loop: free what its body owns (Task 18.3.1)
        if hasattr(self, 'cleanup_scopes'):
            self.emit_frees(self.owned_in_scopes('loop'))
        self.emit_line('break')
        return ''

    def visit_ContinueStmt(self, node: ContinueStmt) -> str:
        """Generate C code for continue statement.

        Args:
            node: Continue statement node

        Returns:
            Empty string (code emitted directly)
        """
        if hasattr(self, 'cleanup_scopes'):
            self.emit_frees(self.owned_in_scopes('loop'))
        self.emit_line('continue')
        return ''

    def visit_BlockStmt(self, node: BlockStmt) -> str:
        """Generate C code for block statement.

        Args:
            node: Block statement node

        Returns:
            Empty string (code emitted directly)
        """
        # Each block frees its own strings when it ends (Task 18.3.1)
        if hasattr(self, 'cleanup_scopes'):
            self.push_scope('block')
        for stmt in node.statements:
            self.visit(stmt)
        if hasattr(self, 'cleanup_scopes'):
            self.pop_scope()

        return ''

    def _settled_condition(self, condition: str) -> str:
        """If evaluating a condition made temporary strings, store the result in a bool
        and free them before the branch runs (Task 18.3.1)."""
        return self._settled_value(condition, 'bool')

    def _settled_value(self, code: str, c_type: str) -> str:
        if not self.has_pending_temps():
            return code
        name = self._declare_temp('val', c_type)
        self.emit_line(f'{name} = {code}')
        self.flush_temps()
        return name

    # ========================================================================
    # Function & Declaration Visitors
    # ========================================================================

    def visit_FunctionDecl(self, node: FunctionDecl) -> str:
        """Generate C code for function declaration.

        Args:
            node: Function declaration node

        Returns:
            Empty string (code emitted directly)
        """
        # Generate function signature
        return_type = self.return_c_type(node.return_type)
        func_name = self._mangle_function_name(node.name)
        self.current_return_type = node.return_type

        # Special case: void main() -> int main() in C
        is_void_main = (node.name == 'main' and return_type == 'void')
        if is_void_main:
            return_type = 'int'

        params = self._c_parameter_list(node.parameters)

        # Emit function header
        self.emit(f'{return_type} {func_name}({params}) {{')
        self.indent()

        # Temporaries for argument evaluation order (Task 18.2.2) are found while generating
        # the body, and declared at its top
        if not hasattr(self, 'temp_scopes'):
            self.temp_scopes = []
        self.temp_scopes.append([])
        temp_index = len(self.output)

        # Parameters borrow the caller's values; one the function assigns to gets its own
        # copy first, so the caller's string is never changed or freed (Task 18.3.1)
        if not hasattr(self, 'cleanup_scopes'):
            self.cleanup_scopes, self.stmt_temps, self.consumed = [], [], set()
        self.push_scope('function')
        assigned = self.assigned_roots(node.body)
        for param in node.parameters:
            if param.name in assigned and not isinstance(param.param_type, ArrayType) \
                    and self.is_managed(param.param_type):
                self.emit_line(f'{param.name} = {self.copy_code(param.param_type, param.name)}')
                self.register_owned(param.name, param.param_type, param.location)

        # Generate function body
        if node.body:
            if node.is_lambda:
                # Lambda: single expression or return statement
                self._generate_lambda_body(node)
            else:
                # Regular function: block statement
                self.visit(node.body)

        self.pop_scope()

        # Add return 0 for void main()
        if is_void_main:
            self.emit_line('return 0')

        temps = self.temp_scopes.pop()
        if temps:
            indent = '    ' * self.indent_level
            self.output[temp_index:temp_index] = [indent + line for line in temps]

        self.dedent()
        self.emit('}')
        self.emit()  # Blank line after function

        return ''

    def _generate_lambda_body(self, node: FunctionDecl) -> None:
        """Generate body for lambda function.

        Args:
            node: Function declaration node (lambda)
        """
        # Lambda body is a BlockStmt with single ReturnStmt
        # OR a single expression that should be returned
        body = node.body

        if isinstance(body, BlockStmt):
            # Check if it's a single return statement
            if len(body.statements) == 1 and isinstance(body.statements[0], ReturnStmt):
                # A single return - through visit_ReturnStmt, which also wraps a returned
                # array (`int[3] function f() : [1, 2, 3]`, Task 18.2.4)
                self.visit(body.statements[0])
            else:
                # Multiple statements - treat as regular block
                self.visit(body)
        elif isinstance(body, ReturnStmt):
            # Direct return statement
            self.visit(body)
        else:
            # Single expression - wrap in return (for void functions, this shouldn't happen)
            expr_code = self.visit(body)
            # Check if return type is void
            if isinstance(node.return_type, PrimitiveType) and node.return_type.name == 'void':
                # Expression statement (no return)
                self.emit_line(expr_code)
            else:
                # Return the expression
                self.emit_line(f'return {expr_code}')

    def visit_ParameterDecl(self, node: ParameterDecl) -> str:
        """Generate C code for parameter.

        Note: Parameters are handled inline during function generation.
        This method is here for completeness but typically not called.

        Args:
            node: Parameter declaration node

        Returns:
            Parameter string (type + name)
        """
        c_type = self.map_type(node.param_type)
        return f'{c_type} {node.name}'

    def visit_ProgramNode(self, node: ProgramNode) -> str:
        """Generate C code for entire program.

        This is the main entry point for code generation.
        Already handled by generate() method.

        Args:
            node: Program node

        Returns:
            Empty string (handled by generate())
        """
        # This is handled by generate() method
        return ''

    def visit_LambdaExpr(self, node: LambdaExpr) -> str:
        """Generate C code for lambda expression.

        Note: In MVP, lambdas are only used as function declarations,
        not as first-class values. This method handles the edge case.

        Args:
            node: Lambda expression node

        Returns:
            Function pointer or inline function
        """
        # Lambdas can't capture variables (v1 - enforced by semantic analysis), so each one
        # is lifted to its own private top-level C function, and the lambda expression
        # itself becomes that function's name - a function pointer (Task 18.1.3)
        self.lambda_count = getattr(self, 'lambda_count', 0) + 1
        name = f'fusion_lambda_{self.lambda_count}'
        if not hasattr(self, 'lambda_definitions'):
            self.lambda_definitions = []

        return_type = self.map_type(node.return_type) if node.return_type else 'void'
        params = self._c_parameter_list(node.parameters)
        # Generated into its own buffer, as a function whose body is one return (or
        # expression) statement - so it gets its own temporaries (Task 18.2.2) and string
        # cleanup (Task 18.3.1). A lambda nested in this body is lifted ahead of this one
        if not hasattr(self, 'temp_scopes'):
            self.temp_scopes = []
        if not hasattr(self, 'cleanup_scopes'):
            self.cleanup_scopes, self.stmt_temps, self.consumed = [], [], set()
        saved = (self.output, self.indent_level, getattr(self, 'current_return_type', None),
                 self.cleanup_scopes, self.stmt_temps)
        self.output, self.indent_level = [], 1
        self.current_return_type = node.return_type
        self.cleanup_scopes, self.stmt_temps = [], []
        self.temp_scopes.append([])
        self.push_scope('function')
        if return_type == 'void':
            self.visit(ExpressionStmt(location=node.location, expression=node.body))
        else:
            self.visit(ReturnStmt(location=node.location, value=node.body))
        self.pop_scope()
        temps = self.temp_scopes.pop()
        body_lines = self.output
        (self.output, self.indent_level, self.current_return_type,
         self.cleanup_scopes, self.stmt_temps) = saved
        self.lambda_definitions.extend(
            [f'static {return_type} {name}({params}) {{']
            + [f'    {line}' for line in temps]
            + body_lines + ['}', '']
        )
        return name
