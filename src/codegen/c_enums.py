"""C for enums (Task 25.2).

A plain enum is an int in C, with a typedef for its name and two helpers:

    typedef int fu_Color;
    static fusion_string fu_Color__text(int v)                       its value's name
    static fu_Color fu_Color__fromString(fusion_string s, where)     a name back to a value

Color.Red is just its number; Color.values() is a list built from the numbers.

A match (Task 25.3) becomes an if / else-if chain, not a C switch - so `break` and
`continue` in a case still act on the loop around the match:

    fusion_val_1 = <subject>;                                the subject, evaluated once
    fusion_val_2 = (fusion_val_1 == 0 || ...) ? 1 : ... : 0;  which case runs
    (the statement's temporaries are freed here)
    if (fusion_val_2 == 1) { ... } else if ... else { ... }
"""

from src.parser.ast_nodes import (EnumDecl, EnumStaticCall, EnumType, EnumValueExpr, ListType,
                                  MatchStmt)
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

    def visit_MatchStmt(self, node: MatchStmt) -> str:
        subject_type = node.subject.inferred_type
        subject = self._declare_temp('val', self.map_type(subject_type))
        self.emit_line(f'{subject} = {self.visit(node.subject)}')
        choice = '0'
        for number in range(len(node.cases), 0, -1):
            tests = ' || '.join(self._pattern_test(subject, subject_type, p)
                                for p in node.cases[number - 1].patterns)
            choice = f'({tests}) ? {number} : {choice}'
        chosen = self._declare_temp('val', 'int')
        self.emit_line(f'{chosen} = {choice}')
        self.flush_temps()          # a temporary subject is no longer needed
        keyword = 'if'
        for number, case in enumerate(node.cases, 1):
            self.emit(f'{keyword} ({chosen} == {number}) {{')
            self.indent()
            self.visit(case.body)
            self.dedent()
            keyword = '} else if'
        if node.else_body is not None:
            self.emit('} else {')
            self.indent()
            self.visit(node.else_body)
            self.dedent()
        self.emit('}')
        return ''

    def _pattern_test(self, subject: str, subject_type, pattern) -> str:
        if pattern.name is not None:
            variant = subject_type.declaration.variant(pattern.name)
            return f'{subject} == {self.enum_number(variant.value)}'
        return self.value_equality(subject, subject_type, self.visit(pattern.value),
                                   pattern.value.inferred_type)

    def enum_text_code(self, type_node: EnumType, code: str) -> str:
        """An enum value's name as a (static, never freed) fusion_string."""
        return f'{self.enum_c_name(type_node)}__text({code})'
