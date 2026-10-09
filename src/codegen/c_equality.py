"""Equality code generation (Task 18.3.5): ==, !=, === and !==.

Every comparison is generated per type - C's raw `==` is used only on plain numbers, chars
and bools, never on strings, structs or arrays (the root of the old pointer-comparison bug).

The rules (checked by the type checker; this module trusts them):

- `==` compares values. Across types only: a number and text holding a number
  (`2 == "2"`, text that isn't a number is simply unequal), a char and a one-character
  string (`'a' == "a"`), int and float (`2 == 2.0`). Structs compare field by field and
  arrays element by element (same size), with these same rules
- `===` also requires the same type; on two different types it is always false (the type
  checker marks the node `never_equal` and warns)
- `!=` is "not ==" and `!==` is "not ==="

Struct and array comparisons call small helpers, generated on demand and placed after the
struct definitions: `fusion_eq_<A>` (or `fusion_eq_<A>__<B>` for two different struct
types) and `fusion_arr_eq_<A>` / `fusion_arr_eq_<A>__<B>` (lengths, then each element).
"""

from ..parser.ast_nodes import (
    ArrayLiteralExpr, IdentifierExpr, PrimitiveType, StructType, ArrayType,
)
from .c_names import array_length_name

EQUALITY_OPERATORS = ('==', '!=', '===', '!==')


class EqualityMixin:
    """Lowers the equality operators to C. Needs `self.equality_helpers` (an ordered dict
    of helper name -> C lines), set up by `generate()`."""

    def equality_code(self, node) -> str:
        """C expression for an equality BinaryExpr."""
        negate = node.operator in ('!=', '!==')
        left_type, right_type = node.left.inferred_type, node.right.inferred_type
        if isinstance(left_type, ArrayType):
            left, left_len = self._array_operand(node.left, left_type)
            right, right_len = self._array_operand(node.right, right_type)
        else:
            left, right = self.visit(node.left), self.visit(node.right)
        if getattr(node, 'never_equal', False):
            # `===` on two different types: always false, but both sides still run
            return f'((void)({left}), (void)({right}), {1 if negate else 0})'
        if isinstance(left_type, ArrayType):
            helper = self._array_equality_helper(left_type.element_type, right_type.element_type)
            code = f'{helper}({left}, {left_len}, {right}, {right_len})'
        else:
            code = self.value_equality(left, left_type, right, right_type, negate)
            negate = False  # value_equality already applied it
        return f'(!{code})' if negate else code

    def value_equality(self, left: str, left_type, right: str, right_type, negate=False) -> str:
        """C expression: are two (non-array) values equal under `==`'s rules? (or not
        equal, with `negate`)"""
        left_name = getattr(left_type, 'name', None)
        right_name = getattr(right_type, 'name', None)
        if isinstance(left_type, StructType):
            helper = self._struct_equality_helper(left_type, right_type)
        elif left_name == 'string' and right_name == 'string':
            helper = 'fusion_str_eq'
        elif 'string' in (left_name, right_name):
            if left_name == 'string':  # keep the text on the right
                left, left_name, right, right_name = right, right_name, left, left_name
            helper = {'char': 'fusion_char_eq_str',
                      'float': 'fusion_float_eq_str'}.get(left_name, 'fusion_double_eq_str')
        else:
            return f'({left} {"!=" if negate else "=="} {right})'  # numbers, chars, bools
        call = f'{helper}({left}, {right})'
        return f'(!{call})' if negate else call

    # ------------------------------------------------------------------ operands and helpers

    def _array_operand(self, expr, array_type: ArrayType) -> tuple:
        """(C code for the array's first element pointer, C code for its length)."""
        if isinstance(expr, ArrayLiteralExpr):
            element_c = self.map_type(array_type.element_type)
            elements = ', '.join(self.visit(e) for e in expr.elements)
            return f'(({element_c}[]){{{elements}}})', str(len(expr.elements))
        code = self.visit(expr)
        if array_type.size is None and isinstance(expr, IdentifierExpr):
            return code, array_length_name(expr.name)  # an `int[]` parameter (18.1.2)
        return code, str(array_type.size)

    def _equality_key(self, type_node) -> str:
        if isinstance(type_node, StructType):
            return self._struct_c_name(type_node)
        if isinstance(type_node, ArrayType):
            return 'arr_' + self._equality_key(type_node.element_type)
        return type_node.name

    def _helper_name(self, prefix: str, left_type, right_type) -> str:
        left_key, right_key = self._equality_key(left_type), self._equality_key(right_type)
        return f'{prefix}_{left_key}' if left_key == right_key else f'{prefix}_{left_key}__{right_key}'

    def _struct_equality_helper(self, left_type: StructType, right_type: StructType) -> str:
        """Name of the helper comparing two structs field by field (made on first use;
        helpers it needs are made first, so they come earlier in the C file)."""
        name = self._helper_name('fusion_eq', left_type, right_type)
        if name in self.equality_helpers:
            return name
        left_fields = self._struct_decl(left_type).fields
        right_fields = self._struct_decl(right_type).fields
        parts = []
        for left_field, right_field in zip(left_fields, right_fields):
            a = f'a.{self._field_name(left_field.name)}'
            b = f'b.{self._field_name(right_field.name)}'
            if isinstance(left_field.field_type, ArrayType):
                helper = self._array_equality_helper(left_field.field_type.element_type,
                                                     right_field.field_type.element_type)
                parts.append(f'{helper}({a}, {left_field.field_type.size}, '
                             f'{b}, {right_field.field_type.size})')
            else:
                parts.append(self.value_equality(a, left_field.field_type, b, right_field.field_type))
        body = ' && '.join(parts) or 'true'
        self.equality_helpers[name] = [
            f'static inline bool {name}({self.map_type(left_type)} a, '
            f'{self.map_type(right_type)} b) {{ return {body}; }}'
        ]
        return name

    def _array_equality_helper(self, left_element, right_element) -> str:
        """Name of the helper comparing two arrays: same length, then every element."""
        name = self._helper_name('fusion_arr_eq', left_element, right_element)
        if name in self.equality_helpers:
            return name
        element_equal = self.value_equality('a[i]', left_element, 'b[i]', right_element)
        self.equality_helpers[name] = [
            f'static inline bool {name}(const {self.map_type(left_element)}* a, int na, '
            f'const {self.map_type(right_element)}* b, int nb) {{',
            '    if (na != nb) return false;',
            f'    for (int i = 0; i < na; i++) if (!{element_equal}) return false;',
            '    return true;',
            '}',
        ]
        return name

    def equality_helper_lines(self) -> list:
        lines = [line for helper in self.equality_helpers.values() for line in helper]
        return ['// Equality helpers (Task 18.3.5)'] + lines + [''] if lines else []
