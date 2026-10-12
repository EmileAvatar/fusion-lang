"""C for enums (Task 25.2).

A plain enum is an int in C, with a typedef for its name and two helpers:

    typedef int fu_Color;
    static fusion_string fu_Color__text(int v)                       its value's name
    static fu_Color fu_Color__fromString(fusion_string s, where)     a name back to a value

Color.Red is just its number; Color.values() is a list built from the numbers.
"""

from src.parser.ast_nodes import EnumDecl, EnumStaticCall, EnumType, EnumValueExpr, ListType
from .c_names import mangle_function_name
from .c_runtime import escape_c_text


class EnumsMixin:
    """Enum code generation; needs self.enum_decls (generate())."""

    def enum_c_name(self, type_node) -> str:
        return mangle_function_name(type_node.name)

    @staticmethod
    def enum_number(value: int) -> str:
        return f'({value})' if value < 0 else str(value)

    def enum_default_value(self, type_node: EnumType) -> int:
        """A value nobody gave: the enum's first value."""
        return type_node.declaration.variants[0].value

    def enum_section_lines(self, enums) -> list:
        """The typedef and helpers of every enum - right after the runtime, before the list
        types and structs that may hold enums."""
        lines = []
        for enum in enums:
            c = mangle_function_name(enum.name)
            lines += [f'// enum {enum.name} (Task 25)', f'typedef int {c};',
                      f'static inline fusion_string {c}__text(int v) {{', '    switch (v) {']
            for variant in enum.variants:
                text = escape_c_text(variant.name, '"')
                lines.append(f'        case {self.enum_number(variant.value)}: '
                             f'return FUSION_STRU("{text}", {len(variant.name)});')
            lines += ['    }', '    return FUSION_STR("");', '}',
                      f'static inline {c} {c}__fromString(fusion_string s, const char* where) {{']
            for variant in enum.variants:
                text = escape_c_text(variant.name, '"')
                size = len(variant.name.encode('utf-8'))
                lines.append(f'    if (s.len == {size} && memcmp(s.data, "{text}", {size}) == 0) '
                             f'return {self.enum_number(variant.value)};')
            lines += [f'    fusion_runtime_error(where, "\\"%.*s\\" is not a value of enum '
                      f'{escape_c_text(enum.name, chr(34))}", s.len, s.data);',
                      f'    return {self.enum_number(enum.variants[0].value)};', '}', '']
        return lines

    def visit_EnumValueExpr(self, node: EnumValueExpr) -> str:
        return self.enum_number(node.declaration.variant(node.member).value)

    def visit_EnumStaticCall(self, node: EnumStaticCall) -> str:
        decl = node.declaration
        c = mangle_function_name(decl.name)
        if node.method == 'values':
            list_name = self.list_c_name(node.inferred_type)
            numbers = ', '.join(self.enum_number(v.value) for v in decl.variants)
            code = f'{list_name}_from(({c}[]){{{numbers}}}, {len(decl.variants)})'
            if id(node) in getattr(self, 'consumed', set()):
                return code
            return self.fresh_temporary(code, node.inferred_type)   # freed unless stored
        # fromString: the text is borrowed
        return f'{c}__fromString({self.visit(node.arguments[0])}, {self._where(node)})'

    def enum_text_code(self, type_node: EnumType, code: str) -> str:
        """An enum value's name as a (static, never freed) fusion_string."""
        return f'{self.enum_c_name(type_node)}__text({code})'
