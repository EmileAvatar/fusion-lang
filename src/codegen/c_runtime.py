"""Builtin function lowering: print(), len(), and string interpolation.

Extracted from c_generator.py (Task 12.5 - C Codegen Module Split) as a
behavior-preserving refactor: CCodeGenerator now includes RuntimeLoweringMixin instead
of defining these methods itself. No logic changed.

A mixin (not standalone functions) because every method here calls self.visit(...) to
recursively generate code for sub-expressions, and existing tests call some of these
(visit_InterpolatedStringExpr, _generate_interpolated_print) directly as instance
methods on a CCodeGenerator.

Task 12.11 (deferred - see taskSummary2.md) considers going further: replacing this
per-builtin special-casing with a general runtime-API lowering layer, so future stdlib
functions don't each need a new special case here.
"""

from ..parser.ast_nodes import (
    ASTNode, CallExpr, LiteralExpr, InterpolatedStringExpr,
    StringTextPart, StringExprPart, PrimitiveType, ArrayType
)


class RuntimeLoweringMixin:
    """Provides print()/len()/interpolation lowering - mixed into CCodeGenerator."""

    # Fusion primitive type name -> printf format specifier.
    # float is promoted to double by C's default argument promotion in varargs, so %f
    # is correct for both float and double.
    _FORMAT_SPECIFIERS = {
        'int': '%d',
        'float': '%f',
        'double': '%f',
        'string': '%s',
        'char': '%c',
        'bool': '%d',
    }

    def _format_specifier_for_expr(self, expr: ASTNode) -> str:
        """Look up the correct printf format specifier for an expression's resolved type.

        Reads `inferred_type`, populated by the semantic analyzer's TypeChecker (see
        taskSummary2.md Task 12.1-12.3), instead of guessing based on MVP-era defaults.
        Guessing wrong here is exactly the bug class that broke FizzBuzz's numeric output
        (Task 6.2) - so a missing/unrecognized type is a hard compiler error, not a silent
        fallback.

        Args:
            expr: The expression being interpolated/printed

        Returns:
            printf format specifier, e.g. "%d"

        Raises:
            NotImplementedError: If the expression has no inferred_type (semantic analysis
                didn't run, or didn't visit this node) or its type has no known specifier
        """
        inferred_type = getattr(expr, 'inferred_type', None)
        if inferred_type is None:
            raise NotImplementedError(
                f"Internal compiler error: {type(expr).__name__} at {expr.location} has no "
                "inferred_type - semantic analysis must run and resolve every expression's "
                "type before code generation."
            )
        if not isinstance(inferred_type, PrimitiveType) or inferred_type.name not in self._FORMAT_SPECIFIERS:
            type_name = inferred_type.name if isinstance(inferred_type, PrimitiveType) else type(inferred_type).__name__
            raise NotImplementedError(
                f"Internal compiler error: no printf format specifier for type '{type_name}' "
                f"at {expr.location}."
            )
        return self._FORMAT_SPECIFIERS[inferred_type.name]

    def _generate_print_call(self, node: CallExpr) -> str:
        """Generate code for print() built-in function.

        Args:
            node: Call expression node for print

        Returns:
            printf() call
        """
        if len(node.arguments) == 0:
            return 'printf("\\n")'

        arg = node.arguments[0]

        # Handle string interpolation
        if isinstance(arg, InterpolatedStringExpr):
            return self._generate_interpolated_print(arg)

        # Handle plain string literals
        if isinstance(arg, LiteralExpr) and arg.type_hint == 'string':
            escaped = str(arg.value).replace('\\', '\\\\').replace('"', '\\"')
            escaped = escaped.replace('\n', '\\n').replace('\t', '\\t')
            return f'printf("{escaped}\\n")'

        # For other types, use the format specifier matching the expression's actual type
        # (print() is currently declared string-only in the symbol table, so this path is
        # only reachable from codegen-level tests/tools that bypass semantic analysis - it
        # still must not guess)
        arg_code = self.visit(arg)
        format_spec = self._format_specifier_for_expr(arg)
        return f'printf("{format_spec}\\n", {arg_code})'

    def _generate_len_call(self, node: CallExpr) -> str:
        """Generate code for len() built-in function.

        Fusion arrays are fixed-size and their size is always resolved at compile time
        (Task 9 v1), so len(arr) needs no runtime call at all - it compiles directly to
        the array's known size as an integer literal.

        Args:
            node: Call expression node for len

        Returns:
            The array's size as a C integer literal
        """
        arg = node.arguments[0]
        array_type = getattr(arg, 'inferred_type', None)
        if not isinstance(array_type, ArrayType) or array_type.size is None:
            raise NotImplementedError(
                f"Internal compiler error: len() argument at {arg.location} has no resolved "
                "array type/size - semantic analysis must run before code generation."
            )
        return str(array_type.size)

    def visit_InterpolatedStringExpr(self, node: InterpolatedStringExpr) -> str:
        """Generate C code for interpolated string expression.

        Args:
            node: Interpolated string expression node

        Returns:
            C sprintf expression or direct string for printf
        """
        format_str, args = self._build_interpolation_format(node)

        # Return just the format string and args (for use in printf)
        # The caller will wrap this appropriately
        if args:
            return f'"{format_str}", ' + ', '.join(args)
        else:
            return f'"{format_str}"'

    def _generate_interpolated_print(self, node: InterpolatedStringExpr) -> str:
        """Generate printf for interpolated string.

        Args:
            node: Interpolated string node

        Returns:
            printf() with format string and arguments
        """
        format_str, args = self._build_interpolation_format(node)
        format_str += '\\n'

        if args:
            args_str = ', ' + ', '.join(args)
        else:
            args_str = ''

        return f'printf("{format_str}"{args_str})'

    def _build_interpolation_format(self, node: InterpolatedStringExpr) -> tuple:
        """Build a printf format string and argument list from an interpolated string's
        segments, in order, using each interpolated expression's actual resolved type.

        Args:
            node: Interpolated string node

        Returns:
            (escaped_format_string, list_of_c_argument_expressions)
        """
        format_parts = []
        args = []

        for segment in node.segments:
            if isinstance(segment, StringTextPart):
                format_parts.append(segment.text)
            else:  # StringExprPart
                args.append(self.visit(segment.expression))
                format_parts.append(self._format_specifier_for_expr(segment.expression))

        format_str = ''.join(format_parts)

        # Escape the format string
        escaped = format_str.replace('\\', '\\\\').replace('"', '\\"')
        escaped = escaped.replace('\n', '\\n').replace('\t', '\\t')

        return escaped, args
