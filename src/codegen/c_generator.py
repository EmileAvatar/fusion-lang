"""C Code Generator for Fusion.

Generates C source code from Fusion AST nodes using the visitor pattern.
Supports MVP features: functions, basic types, expressions, and statements.

Split into focused modules (Task 12.5 - C Codegen Module Split):
- c_types.py: Fusion type -> C type mapping (TypeMapperMixin)
- c_names.py: C keyword name mangling (mangle_function_name)
- c_runtime.py: print()/len()/interpolation builtin lowering (RuntimeLoweringMixin)
This file keeps AST traversal, statement/declaration codegen, and output management.
"""

from typing import List, Set
import json
from ..parser.ast_nodes import (
    ASTNode, ProgramNode, FunctionDecl, ParameterDecl,
    PrimitiveType, ArrayType,
    LiteralExpr, IdentifierExpr, BinaryExpr, UnaryExpr,
    CallExpr, LambdaExpr,
    ArrayLiteralExpr, IndexExpr,
    ExpressionStmt, VarDeclStmt, AssignmentStmt, IfStmt,
    WhileStmt, ForStmt, ReturnStmt, BreakStmt, ContinueStmt,
    BlockStmt
)
from .c_types import TypeMapperMixin
from .c_names import mangle_function_name
from .c_runtime import RuntimeLoweringMixin


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

        # Generate includes
        self._generate_includes()

        # Generate forward declarations
        self._generate_forward_declarations(program)

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
                params = ', '.join(
                    f'{self.map_type(p.param_type)} {p.name}'
                    for p in decl.parameters
                ) if decl.parameters else 'void'
                self.emit(f'{return_type} {func_name}({params});')
        self.emit()  # Blank line

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
            # Escape special characters
            char_val = str(node.value)
            escaped = char_val.replace('\\', '\\\\').replace("'", "\\'")
            # Handle common escape sequences
            escaped = escaped.replace('\n', '\\n').replace('\t', '\\t')
            escaped = escaped.replace('\r', '\\r').replace('\0', '\\0')
            return f"'{escaped}'"

        elif type_hint == 'string':
            # Escape special characters
            str_val = str(node.value)
            escaped = str_val.replace('\\', '\\\\').replace('"', '\\"')
            # Handle common escape sequences
            escaped = escaped.replace('\n', '\\n').replace('\t', '\\t')
            escaped = escaped.replace('\r', '\\r').replace('\0', '\\0')
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
        # Get function name
        if isinstance(node.callee, IdentifierExpr):
            func_name = node.callee.name

            # Special handling for built-in functions
            if func_name == 'print':
                return self._generate_print_call(node)
            if func_name == 'len':
                return self._generate_len_call(node)

            # Mangle user-defined function names
            func = self._mangle_function_name(func_name)
        else:
            func = self.visit(node.callee)

        # Generate arguments
        args = ', '.join(self.visit(arg) for arg in node.arguments)

        return f'{func}({args})'

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

        # Generate parameters
        if node.parameters:
            params = ', '.join(
                f'{self.map_type(p.param_type)} {p.name}'
                for p in node.parameters
            )
        else:
            params = 'void'

        # Emit function header
        self.emit(f'{return_type} {func_name}({params}) {{')
        self.indent()

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
        # For MVP, lambdas are converted to named functions
        # This would require generating an anonymous function
        # and returning a function pointer

        # Simplified: return placeholder
        # Full implementation deferred post-MVP
        return '/* <lambda> */'
