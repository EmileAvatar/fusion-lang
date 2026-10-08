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


class CCodeGenerator(TypeMapperMixin, RuntimeLoweringMixin):
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
        self.temp_scopes = []            # per-function temporary declarations (Task 18.2.2)
        self.temp_count = 0
        self.argument_temps = {}         # id(argument expression) -> its temporary's name

        # Function declarations by name - call lowering needs each callee's parameter
        # types, to add hidden array-length arguments (Task 18.1.2)
        self.function_decls = {
            decl.name: decl for decl in program.declarations if isinstance(decl, FunctionDecl)
        }

        # Generate includes
        self._generate_includes()

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

        # Return complete C code
        return '\n'.join(self.output)

    def visit(self, node: ASTNode) -> str:
        """Visit an AST node and generate C code.

        Args:
            node: AST node to visit

        Returns:
            Generated C code for this node
        """
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
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
        'string': '""',
    }

    def _generate_struct_definitions(self, program: ProgramNode) -> None:
        """Emit one C typedef per struct (Task 18.2.1):

            typedef struct Point {
                int x;
                int y;
            } Point;

        A string field is a `char*` - it holds a string value exactly like a string variable
        does. Strings can't change at run time yet, so copying the pointer behaves the same
        as copying the text; Task 18.3 gives string fields their own growable buffers.
        """
        structs = [d for d in program.declarations if isinstance(d, StructDecl)]
        if not structs:
            return
        self.emit('// Structs')
        for struct in structs:
            c_name = self._mangle_function_name(struct.name)
            self.emit(f'typedef struct {c_name} {{')
            self.indent()
            for field in struct.fields:
                self.emit_line(f'{self.map_type(field.field_type)} {self._field_name(field.name)}')
            self.dedent()
            self.emit(f'}} {c_name};')
        self.emit()

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
                parts.append(self._ZERO_VALUES.get(field.field_type.name, '0'))
            else:
                parts.append(self._argument_code(value))
        return f'({self._mangle_function_name(struct.name)}){{{", ".join(parts)}}}'

    # ========================================================================
    # Argument evaluation order (Task 18.2.2)
    # ========================================================================

    def _argument_code(self, value: ASTNode) -> str:
        """C code for one argument: its temporary, if _evaluate_in_written_order stored it
        in one, otherwise the expression itself."""
        temps = getattr(self, 'argument_temps', {})
        return temps.get(id(value)) or self.visit(value)

    @classmethod
    def _contains_call(cls, node) -> bool:
        """True if an expression contains a call anywhere inside it - a call may have side
        effects (changing an array passed to it, printing), so its timing can matter."""
        if isinstance(node, CallExpr):
            return True
        if isinstance(node, list):
            return any(cls._contains_call(item) for item in node)
        if is_dataclass(node) and isinstance(node, ASTNode):
            return any(cls._contains_call(getattr(node, f.name)) for f in dataclass_fields(node)
                       if f.name not in ('location', 'inferred_type', 'scope'))
        return False

    def _new_temp(self, c_type: str) -> str:
        """Declare a compiler temporary at the top of the C function being generated."""
        self.temp_count = getattr(self, 'temp_count', 0) + 1
        name = f'fusion_arg_{self.temp_count}'
        self.temp_scopes[-1].append(f'{c_type} {name};')
        return name

    def _evaluate_in_written_order(self, node: CallExpr, slot_types: list) -> list:
        """Named arguments (Task 18.2.2) are evaluated left to right *as written*, but C
        evaluates a call's arguments in no guaranteed order - and named ones have been moved
        to their parameter's position. So when a call with named arguments contains another
        call, each argument is first stored in a temporary, in the written order, using C's
        comma operator (which does guarantee left-to-right):

            f(b = next(), a = next())  ->  (fusion_arg_1 = next(), fusion_arg_2 = next(),
                                            f(fusion_arg_2, fusion_arg_1))

        Array arguments are left in place: they are passed by reference (nothing to
        evaluate early), and C can't copy an array into a temporary.

        Args:
            node: The call (already type-checked - resolved_arguments is set)
            slot_types: The parameter/field type for each entry of resolved_arguments

        Returns:
            The temporary assignments, in written order (empty if none are needed)
        """
        if not any(isinstance(arg, NamedArgument) for arg in node.arguments):
            return []
        written = [arg.value if isinstance(arg, NamedArgument) else arg for arg in node.arguments]
        if not any(self._contains_call(value) for value in written) or not self.temp_scopes:
            return []
        assignments = []
        for value in written:
            index = next(i for i, resolved in enumerate(node.resolved_arguments) if resolved is value)
            if isinstance(slot_types[index], ArrayType):
                continue
            code = self.visit(value)
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
                return_type = self.map_type(decl.return_type)
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
            escaped = escape_c_text(str(node.value), '"')
            return f'"{escaped}"'

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

    def visit_CallExpr(self, node: CallExpr) -> str:
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
            ordered = self._evaluate_in_written_order(node, [f.field_type for f in struct.fields])
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
        if callee_decl is not None and node.resolved_arguments is not None:
            ordered = self._evaluate_in_written_order(node, [p.param_type for p in params])

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
        const_keyword = 'const ' if node.is_const else ''

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
            if node.initializer:
                init_code = self.visit(node.initializer)
                self.emit_line(f'{const_keyword}{elem_c_type} {node.name}[{size}] = {init_code}')
            else:
                # Zero-initialize, matching Fusion's existing "uninitialized = 0" convention
                # for scalars ({0} zero-fills every element in C, not just the first)
                self.emit_line(f'{const_keyword}{elem_c_type} {node.name}[{size}] = {{0}}')
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
            init_code = self.visit(node.initializer)
            self.emit_line(f'{const_keyword}{c_type} {name} = {init_code}')
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
        if node.value:
            value_code = self.visit(node.value)
            self.emit_line(f'return {value_code}')
        else:
            self.emit_line('return')

        return ''

    def visit_IfStmt(self, node: IfStmt) -> str:
        """Generate C code for if statement.

        Args:
            node: If statement node

        Returns:
            Empty string (code emitted directly)
        """
        condition = self.visit(node.condition)
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
        self.emit(f'while ({condition}) {{')
        self.indent()

        self.visit(node.body)

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

        # Generate for loop header
        # for (int i = start; i < end; i += step)
        self.emit(f'for (int {var_name} = {start}; {var_name} < {end}; {var_name} += {step}) {{')
        self.indent()

        self.visit(node.body)

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
        self.emit_line('break')
        return ''

    def visit_ContinueStmt(self, node: ContinueStmt) -> str:
        """Generate C code for continue statement.

        Args:
            node: Continue statement node

        Returns:
            Empty string (code emitted directly)
        """
        self.emit_line('continue')
        return ''

    def visit_BlockStmt(self, node: BlockStmt) -> str:
        """Generate C code for block statement.

        Args:
            node: Block statement node

        Returns:
            Empty string (code emitted directly)
        """
        for stmt in node.statements:
            self.visit(stmt)

        return ''

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
        return_type = self.map_type(node.return_type)
        func_name = self._mangle_function_name(node.name)

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

        # Generate function body
        if node.body:
            if node.is_lambda:
                # Lambda: single expression or return statement
                self._generate_lambda_body(node)
            else:
                # Regular function: block statement
                self.visit(node.body)

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
                # Extract the return expression
                return_stmt = body.statements[0]
                if return_stmt.value:
                    expr_code = self.visit(return_stmt.value)
                    self.emit_line(f'return {expr_code}')
                else:
                    self.emit_line('return')
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
        # Generated before this lambda's lines are added, so a lambda nested in this body
        # is lifted (and defined) ahead of this one. A lambda is its own C function, so it
        # gets its own temporaries (Task 18.2.2)
        if not hasattr(self, 'temp_scopes'):
            self.temp_scopes = []
        self.temp_scopes.append([])
        body_code = self.visit(node.body)
        temps = self.temp_scopes.pop()
        statement = body_code if return_type == 'void' else f'return {body_code}'
        self.lambda_definitions.extend(
            [f'static {return_type} {name}({params}) {{']
            + [f'    {line}' for line in temps]
            + [f'    {statement};', '}', '']
        )
        return name
