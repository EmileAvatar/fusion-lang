"""Builtin function lowering: print(), len(), and string interpolation.

Extracted from c_generator.py (Task 12.5 - C Codegen Module Split) as a
behavior-preserving refactor: CCodeGenerator now includes RuntimeLoweringMixin instead
of defining these methods itself. No logic changed.

A mixin (not standalone functions) because every method here calls self.visit(...) to
recursively generate code for sub-expressions, and existing tests call some of these
(visit_InterpolatedStringExpr, _generate_interpolated_print) directly as instance
methods on a CCodeGenerator.

Task 12.11 (decided 2026-09-13, see taskSummary2.md) considered replacing this per-builtin
special-casing with a general runtime-API lowering layer (Fusion stdlib call -> runtime API
-> backend-specific implementation), so future stdlib functions wouldn't each need a new
special case here. Decision: defer - only 2 builtins exist (print, len) and `import` has no
parser support yet, so there is no real stdlib to lower. Revisit once Fusion's first real
import/fusionlib module is scoped for implementation.
"""

import unicodedata

from ..parser.ast_nodes import (
    ASTNode, CallExpr, LiteralExpr, InterpolatedStringExpr,
    StringTextPart, StringExprPart, StringPositionalPart, PrimitiveType, ArrayType, IdentifierExpr
)
from .c_names import array_length_name


_SIMPLE_C_ESCAPES = {
    '\\': '\\\\',
    '\n': '\\n',
    '\t': '\\t',
    '\r': '\\r',
    '\0': '\\000',  # three octal digits, so a following digit can't extend the escape
}


def escape_c_text(value: str, quote: str) -> str:
    """Escape text for use inside a C string ("...") or char ('...') literal.

    Single shared implementation - this logic was previously duplicated in four places.

    Control and invisible/format characters (Unicode categories Cc and Cf - e.g. a zero-width
    joiner written as \\u200D in Fusion source) are emitted as octal escapes of their UTF-8
    bytes, so they are never written raw - and invisible - into the generated C (Task 19.6).
    Octal escapes are used rather than \\x because C's \\x consumes every following hex digit,
    while an octal escape stops at three digits. Ordinary printable text, including printable
    Unicode such as accented letters, is emitted unchanged.

    Args:
        value: The text to escape
        quote: The enclosing quote character - '"' for strings, "'" for chars

    Returns:
        The escaped text, without the surrounding quotes
    """
    out = []
    for ch in value:
        if ch in _SIMPLE_C_ESCAPES:
            out.append(_SIMPLE_C_ESCAPES[ch])
        elif ch == quote:
            out.append('\\' + quote)
        elif unicodedata.category(ch) in ('Cc', 'Cf'):
            out.append(''.join(f'\\{byte:03o}' for byte in ch.encode('utf-8')))
        else:
            out.append(ch)
    return ''.join(out)


def escape_printf_text(text: str) -> str:
    """Double every '%' in literal text that will become part of a printf format string.

    Without this, `print("100% done")` hands printf the directive `% d` and prints garbage
    read from the stack - the format-string bug class (CWE-134), where `%n` can even write
    to memory. Only literal text is escaped; the specifiers codegen itself inserts for
    interpolated values (`%d`, `%s`, ...) must not be.

    Args:
        text: Literal text from a Fusion string

    Returns:
        The text with each '%' written as '%%'
    """
    return text.replace('%', '%%')


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

        # Handle string interpolation, including {@N} placeholders for the arguments after
        # the text (Task 18.2.2b)
        if isinstance(arg, InterpolatedStringExpr):
            assignments, positional = self._print_argument_codes(arg, node.arguments[1:])
            call = self._generate_interpolated_print(arg, positional)
            return f'({", ".join(assignments + [call])})' if assignments else call

        # Handle plain string literals - the text becomes printf's format string, so any
        # literal '%' must be doubled (see escape_printf_text)
        if isinstance(arg, LiteralExpr) and arg.type_hint == 'string':
            escaped = escape_c_text(escape_printf_text(str(arg.value)), '"')
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

        Fusion arrays are fixed-size, and usually their size is resolved at compile time
        (Task 9 v1), so len(arr) compiles directly to the size as an integer literal. The
        exception is an `int[]` parameter (Task 18.1.2), which accepts arrays of any size -
        its len() compiles to the hidden length parameter passed alongside it.

        Args:
            node: Call expression node for len

        Returns:
            The array's size as a C integer literal
        """
        arg = node.arguments[0]
        array_type = getattr(arg, 'inferred_type', None)
        if isinstance(array_type, ArrayType) and array_type.size is None and isinstance(arg, IdentifierExpr):
            return array_length_name(arg.name)
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

    def _print_argument_codes(self, text: InterpolatedStringExpr, extras) -> tuple:
        """C code for print's extra arguments, which {@N} placeholders refer to (Task
        18.2.2b).

        Each argument is evaluated exactly once, left to right as written - whatever order
        the placeholders use, and however often. An argument goes into a temporary first
        when that's needed for this guarantee: when the order could change the result, or
        when it contains a call and isn't used exactly once (a repeated {@1} mustn't re-run
        the call, and an unused argument's call must still run).

        Returns:
            (temporary assignments in written order, [(c_code, format_specifier)] per
            argument)
        """
        uses = {}
        for segment in text.segments:
            if isinstance(segment, StringPositionalPart):
                uses[segment.index] = uses.get(segment.index, 0) + 1

        order_matters = self._order_matters(extras)
        assignments, positional = [], []
        for number, extra in enumerate(extras, start=1):
            code = self.visit(extra)
            if order_matters or (self._contains_call(extra) and uses.get(number, 0) != 1):
                name = self._new_temp(self.map_type(extra.inferred_type))
                assignments.append(f'{name} = {code}')
                code = name
            positional.append((code, self._format_specifier_for_expr(extra)))
        return assignments, positional

    def _generate_interpolated_print(self, node: InterpolatedStringExpr, positional=None) -> str:
        """Generate printf for interpolated string.

        Args:
            node: Interpolated string node
            positional: (c_code, format_specifier) per print argument after the text, for
                {@N} placeholders (Task 18.2.2b)

        Returns:
            printf() with format string and arguments
        """
        format_str, args = self._build_interpolation_format(node, positional)
        format_str += '\\n'

        if args:
            args_str = ', ' + ', '.join(args)
        else:
            args_str = ''

        return f'printf("{format_str}"{args_str})'

    def _build_interpolation_format(self, node: InterpolatedStringExpr, positional=None) -> tuple:
        """Build a printf format string and argument list from an interpolated string's
        segments, in order, using each interpolated expression's actual resolved type.

        Args:
            node: Interpolated string node
            positional: (c_code, format_specifier) per print argument after the text - a
                {@N} placeholder uses entry N-1 (Task 18.2.2b)

        Returns:
            (escaped_format_string, list_of_c_argument_expressions)
        """
        format_parts = []
        args = []

        for segment in node.segments:
            if isinstance(segment, StringTextPart):
                # Literal text only - the specifiers appended below must stay unescaped
                format_parts.append(escape_printf_text(segment.text))
            elif isinstance(segment, StringPositionalPart):
                if positional is None or not 1 <= segment.index <= len(positional):
                    raise NotImplementedError(
                        f"Internal compiler error: {{@{segment.index}}} at {node.location} has "
                        "no matching print argument - semantic analysis must reject it."
                    )
                code, spec = positional[segment.index - 1]
                args.append(code)
                format_parts.append(spec)
            else:  # StringExprPart
                args.append(self.visit(segment.expression))
                format_parts.append(self._format_specifier_for_expr(segment.expression))

        format_str = ''.join(format_parts)

        # Escape the format string
        escaped = escape_c_text(format_str, '"')

        return escaped, args
