"""C for enums (Task 25.2).

A plain enum is an int in C, with a typedef for its name and two helpers:

    typedef int fu_Color;
    static fusion_string fu_Color__text(int v)                       its value's name
    static fu_Color fu_Color__fromString(fusion_string s, where)     a name back to a value

Color.Red is just its number; Color.values() is a list built from the numbers.

An enum whose values carry data (Task 25.4) becomes a struct instead - a `tag` (the value's
number) and every value's fields side by side, `<Value>__<field>`; a field of another value
stays at its default. lower_data_enums() swaps the enum's type for that struct everywhere,
so copying, freeing, == and storing reuse the struct code.

    Token.Number(42)  ->  (fu_Token){0, 42, ""}

A match (Task 25.3) becomes an if / else-if chain, not a C switch. `continue` in a case
acts on the loop around it; `break` jumps to the match's end label (Task 30.12):

    fusion_val_1 = <subject>;                                the subject, evaluated once
    fusion_val_2 = (fusion_val_1 == 0 || ...) ? 1 : ... : 0;  which case runs
    (the statement's temporaries are freed here)
    if (fusion_val_2 == 1) { ... } else if ... else { ... }
"""

from dataclasses import dataclass, fields as dataclass_fields, is_dataclass

from src.parser.ast_nodes import (EnumDecl, EnumStaticCall, EnumType, EnumValueExpr, ListType,
                                  LiteralExpr, MatchStmt, PrimitiveType, StructDecl, StructField,
                                  StructType, TypeNode)
from src.semantic.enums import ENUM_NULL
from .c_names import mangle_function_name, local_c_name
from .c_runtime import escape_c_text


@dataclass
class BoxType(TypeNode):
    """Code generation only (Task 25.5): a field of an enum that holds the enum itself,
    `Add(Expr left, Expr right)` - in C a pointer to a copy on the heap, still a value:
    copying copies what it points to, freeing frees it. NULL while that value isn't the
    one in use."""
    inner: TypeNode = None


class EnumsMixin:
    """Enum code generation; needs self.enum_decls (generate())."""

    def lower_data_enums(self, program) -> None:
        """Give each enum with data a struct, and use it for every value of the enum."""
        structs = {}
        self.boxed_enums = {}
        for enum in [d for d in program.declarations if isinstance(d, EnumDecl)]:
            if not any(v.fields for v in enum.variants):
                continue
            tag = StructField(location=enum.location, name='tag',     # unset: null (30.11)
                              field_type=PrimitiveType(location=enum.location, name='int'),
                              default_value=LiteralExpr(location=enum.location, value=ENUM_NULL,
                                                        type_hint='int'))
            fields = [tag] + [StructField(location=f.location, name=f'{v.name}__{f.name}',
                                          field_type=f.field_type)
                              for v in enum.variants for f in v.fields]
            struct = StructDecl(location=enum.location, name=enum.name, fields=fields)
            struct.enum_decl = enum
            enum.struct_decl = struct
            structs[enum.name] = struct
        if not structs:
            return
        skip = ('location', 'declaration', 'callee_declaration', 'scope', 'struct_decl', 'enum_decl')

        def convert(node):
            if isinstance(node, EnumType) and node.name in structs:
                return StructType(location=node.location, name=node.name,
                                  declaration=structs[node.name])
            return None

        seen = set()

        def walk(node):
            if isinstance(node, list):
                for i, item in enumerate(node):
                    new = convert(item)
                    if new is not None:
                        node[i] = new
                    walk(node[i])
                return
            if not is_dataclass(node) or isinstance(node, type) or id(node) in seen:
                return
            seen.add(id(node))
            for f in dataclass_fields(node):
                if f.name in skip:
                    continue
                value = getattr(node, f.name)
                new = convert(value)
                if new is not None:
                    setattr(node, f.name, new)
                    value = new
                walk(value)

        walk(program.declarations)
        walk([s.fields for s in structs.values()])
        # A field holding its own enum is boxed (Task 25.5)
        for struct in structs.values():
            for field in struct.fields:
                if isinstance(field.field_type, StructType) and field.field_type.name == struct.name:
                    field.field_type = BoxType(location=field.location, inner=field.field_type)
                    self.boxed_enums[struct.name] = field.field_type.inner
        program.declarations.extend(structs.values())

    def box_prototype_lines(self) -> list:
        lines = []
        for inner in getattr(self, 'boxed_enums', {}).values():
            c = self.map_type(inner)
            lines += [f'static inline struct {c}* fusion_box_make_{c}({c} v);',
                      f'static inline struct {c}* fusion_box_copy_{c}(struct {c}* p);',
                      f'static inline void fusion_box_free_{c}(struct {c}** p);',
                      f'static int fusion_box_eq_{c}(struct {c}* a, struct {c}* b);']
        return ['// Enums holding themselves (Task 25.5)'] + lines + [''] if lines else []

    def box_body_lines(self) -> list:
        """make / copy / free - after the struct's own copy and free helpers."""
        lines = []
        for inner in getattr(self, 'boxed_enums', {}).values():
            c = self.map_type(inner)
            lines += [
                f'static inline struct {c}* fusion_box_make_{c}({c} v) {{ {c}* p = ({c}*)'
                f'fusion_alloc(sizeof({c})); *p = v; return p; }}',
                f'static inline struct {c}* fusion_box_copy_{c}(struct {c}* p) {{ return p ? '
                f'fusion_box_make_{c}(fusion_copy_{c}(*p)) : NULL; }}',
                f'static inline void fusion_box_free_{c}(struct {c}** p) {{ if (*p) {{ '
                f'fusion_free_{c}(*p); fusion_dealloc(*p); *p = NULL; }} }}']
        return lines

    def box_equality_lines(self) -> list:
        """== on what two boxes point to - after the equality helpers it may call."""
        lines = []
        for inner in getattr(self, 'boxed_enums', {}).values():
            c = self.map_type(inner)
            same = self.value_equality('(*a)', inner, '(*b)', inner)
            lines.append(f'static int fusion_box_eq_{c}(struct {c}* a, struct {c}* b) {{ '
                         f'if (!a || !b) return a == b; return {same}; }}')
        return lines

    @staticmethod
    def data_struct(type_node):
        """The struct of an enum with data, if type_node is one (Task 25.4)."""
        decl = getattr(type_node, 'declaration', None)
        return decl if getattr(decl, 'enum_decl', None) is not None else None

    def enum_c_name(self, type_node) -> str:
        return mangle_function_name(type_node.name)

    @staticmethod
    def enum_number(value: int) -> str:
        return f'({value})' if value < 0 else str(value)

    def enum_default_value(self, type_node: EnumType) -> int:
        """A value nobody gave: null (Task 30.11 - it was the first value)."""
        return ENUM_NULL

    def enum_section_lines(self, enums) -> list:
        """The typedef and helpers of every enum - right after the runtime, before the list
        types and structs that may hold enums."""
        lines = []
        for enum in enums:
            c = mangle_function_name(enum.name)
            data = getattr(enum, 'struct_decl', None) is not None   # a struct (Task 25.4)
            lines += [f'// enum {enum.name} (Task 25)'] + ([] if data else [f'typedef int {c};'])
            lines += [f'static inline fusion_string {c}__text(int v) {{', '    switch (v) {',
                      '        case FUSION_ENUM_NULL: return FUSION_STR("null");']   # 30.11
            for variant in enum.variants:
                text = escape_c_text(variant.name, '"')
                lines.append(f'        case {self.enum_number(variant.value)}: '
                             f'return FUSION_STRU("{text}", {len(variant.name)});')
            lines += ['    }', '    return FUSION_STR("");', '}']
            if data:
                lines.append('')
                continue
            lines += [f'static inline {c} {c}__fromString(fusion_string s, const char* where) {{']
            for variant in enum.variants:
                text = escape_c_text(variant.name, '"')
                size = len(variant.name.encode('utf-8'))
                lines.append(f'    if (s.len == {size} && memcmp(s.data, "{text}", {size}) == 0) '
                             f'return {self.enum_number(variant.value)};')
            lines += [f'    fusion_fail(FUSION_KIND_UnknownValueError, where, "\\"%.*s\\" is not a value of enum '
                      f'{escape_c_text(enum.name, chr(34))}", s.len, s.data);',
                      f'    return {self.enum_number(enum.variants[0].value)};', '}', '']
        return lines

    def enum_null_code(self, type_node) -> str:
        """null as a value of an enum (Task 30.11)."""
        struct = self.data_struct(type_node)
        if struct is None:
            return 'FUSION_ENUM_NULL'
        tag = LiteralExpr(location=struct.location, value=ENUM_NULL, type_hint='int')
        return self._struct_initializer(struct, [tag] + [None] * (len(struct.fields) - 1))

    def visit_IsNullExpr(self, node) -> str:
        """x == null / x is null / x?.null (Task 30.11)."""
        code = self.visit(node.operand)
        if not getattr(node, 'can_be_null', False):
            return f'((void)({code}), {1 if node.negated else 0})'   # never null (a warning)
        operator = '!=' if node.negated else '=='
        if self.is_class_type(node.operand.inferred_type):
            return f'(({code}) {operator} NULL)'          # an object (Task 32.10b)
        if self.data_struct(node.operand.inferred_type) is not None:
            return f'(({code}).tag {operator} FUSION_ENUM_NULL)'
        return f'(({code}) {operator} FUSION_ENUM_NULL)'

    def visit_EnumValueExpr(self, node: EnumValueExpr) -> str:
        number = node.declaration.variant(node.member).value
        struct = getattr(node.declaration, 'struct_decl', None)
        if struct is None:
            return self.enum_number(number)
        # A value without data of an enum with data: its tag, every field at its default
        tag = LiteralExpr(location=node.location, value=number, type_hint='int')
        return self._struct_initializer(struct, [tag] + [None] * (len(struct.fields) - 1))

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
        if node.method == 'fromString':   # the text is borrowed; an unknown name fails (26.4)
            return self.checked_code(f'{c}__fromString({self.visit(node.arguments[0])}, '
                                     f'{self._where(node)})', c)
        # Token.Number(42) - its tag and its own fields (Task 25.4)
        struct = decl.struct_decl
        variant = decl.variant(node.method)
        given = dict(zip((f'{variant.name}__{f.name}' for f in variant.fields),
                         node.resolved_arguments or node.arguments))
        tag = LiteralExpr(location=node.location, value=variant.value, type_hint='int')
        values = [tag] + [given.get(f.name) for f in struct.fields[1:]]
        code = self._struct_initializer(struct, values)
        if not self.is_managed(node.inferred_type) or id(node) in getattr(self, 'consumed', set()):
            return code
        return self.fresh_temporary(code, node.inferred_type)   # freed unless stored

    def visit_MatchStmt(self, node: MatchStmt) -> str:
        subject_type = node.subject.inferred_type
        held = self.data_struct(subject_type) is not None and self.is_fresh(node.subject) \
            and self.is_managed(subject_type)
        # The match's own scope: `break` in a case jumps to its end label (Task 30.12)
        self.match_count = getattr(self, 'match_count', 0) + 1
        self.push_scope('match')
        self.cleanup_scopes[-1].update(label=f'fusion_match_end_{self.match_count}', used=False,
                                       finally_depth=len(getattr(self, 'finally_stack', None) or []))
        if held:
            # A new value with data (a call's result): kept in an owned local while the
            # cases read its data, freed when the match ends - or by a return / break
            subject = self._declare_temp('match', self.map_type(subject_type))
            self.emit_line(f'{subject} = {self.owned_value(node.subject, subject_type)}')
            self.register_owned(subject, subject_type)
        else:
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
        # Every value has a case: the last one runs whenever the others don't - so C
        # (and GCC's "end of non-void function" check) sees that one always runs
        covers_all = node.else_body is None and getattr(node, 'exhaustive', False)
        if covers_all and self.can_be_null_enum(subject_type) and not getattr(node, 'has_null_case', False):
            # Every value has a case, but null has none and there is no else: a NullError
            # (Task 30.11) - checked first, so C still sees one case always run
            test = (f'{subject}.tag' if self.data_struct(subject_type) is not None else subject)
            name = escape_c_text(getattr(subject_type, 'name', 'enum'), '"')
            self.emit(f'if ({test} == FUSION_ENUM_NULL) {{')
            self.indent()
            self.emit_line(self.checked_code(f'fusion_null_fail({self._where(node)}, "a match '
                                             f'on a null {name} with no case for null")', None))
            self.dedent()
            self.emit('}')
        if node.falls:
            self._fall_cases(node, chosen, covers_all)
        else:
            for number, case in enumerate(node.cases, 1):
                if covers_all and number == len(node.cases):
                    self.emit('{' if number == 1 else '} else {')
                else:
                    self.emit(f'{keyword} ({chosen} == {number}) {{')
                self.indent()
                self._case_body(case, subject, subject_type)
                self.dedent()
                keyword = '} else if'
            if node.else_body is not None:
                self.emit('} else {')
                self.indent()
                self.visit(node.else_body)
                self.dedent()
            self.emit('}')
        if self.cleanup_scopes[-1]['used']:
            self.emit(f"{self.cleanup_scopes[-1]['label']}:;")
        self.pop_scope()
        return ''

    def visit_MatchExpr(self, node) -> str:
        """A match that gives a value (Task 46.2) - C's own `?:`, one test per case:

            (fusion_val_3 = n, (fusion_val_3 == 6 || fusion_val_3 == 7) ? "Weekend" : "Weekday")

        The subject is read once. A string (or other managed) result: every value is made
        owned, as `?:` does (Task 30.7). With no `_` the last case is the fallback - every
        value has a case; a null enum with no null case is a NullError, as in a statement."""
        subject_type, result_type = node.subject.inferred_type, node.inferred_type
        subject = self._declare_temp('val', self.map_type(subject_type))
        managed = self.is_managed(result_type)

        def value(expr):
            return self.owned_value(expr, result_type) if managed else self.visit(expr)

        tests = [' || '.join(self._pattern_test(subject, subject_type, p) for p in case.patterns)
                 for case in node.cases]
        values = [value(case.value) for case in node.cases]
        if node.else_body is not None:
            code = value(node.else_body)
        else:
            code, tests, values = values[-1], tests[:-1], values[:-1]
            if self.can_be_null_enum(subject_type) and not getattr(node, 'has_null_case', False):
                test = f'{subject}.tag' if self.data_struct(subject_type) is not None else subject
                name = escape_c_text(getattr(subject_type, 'name', 'enum'), '"')
                fail = self.checked_code(f'fusion_null_fail({self._where(node)}, "a match on a '
                                         f'null {name} with no case for null")', None)
                code = (f'({test} == FUSION_ENUM_NULL ? ({fail}, '
                        f'{self._default_value_code(result_type)}) : {code})')
        for test, choice in zip(reversed(tests), reversed(values)):
            code = f'({test}) ? {choice} : {code}'
        code = f'({subject} = {self.visit(node.subject)}, {code})'
        if managed and id(node) not in self.consumed:
            return self.fresh_temporary(code, result_type)
        return code

    def _fall_cases(self, node, chosen: str, covers_all: bool) -> None:
        """`fall match` (Task 30.13): the matching case runs, then each case below it, until a
        break (which jumps to the match's end) - and the else, which also runs when nothing
        matched. When every value has a case, the last one always runs (null was checked
        first), so C sees it too."""
        for number, case in enumerate(node.cases, 1):
            if covers_all and number == len(node.cases):
                self.emit('{')
            else:
                self.emit(f'if ({chosen} != 0 && {chosen} <= {number}) {{')
            self.indent()
            self.visit(case.body)
            self.dedent()
            self.emit('}')
        if node.else_body is not None:
            self.emit('{')
            self.indent()
            self.visit(node.else_body)
            self.dedent()
            self.emit('}')

    def _case_body(self, case, subject: str, subject_type) -> None:
        """A case's body - after `case Number(n)`, n holds a copy of the value's data."""
        pattern = case.patterns[0]
        if not pattern.bindings:
            self.visit(case.body)
            return
        struct = self.data_struct(subject_type)
        self.push_scope('block')
        for name, f in zip(pattern.bindings, struct.enum_decl.variant(pattern.name).fields):
            if name == '_':
                continue
            field = f'{subject}.{self._field_name(f"{pattern.name}__{f.name}")}'
            if isinstance(self._stored_field_type(struct, f"{pattern.name}__{f.name}"), BoxType):
                field = f'(*{field})'               # an enum holding itself (Task 25.5)
            value = self.copy_code(f.field_type, field) if self.is_managed(f.field_type) else field
            self.emit_line(f'{self.map_type(f.field_type)} {name} = {value}')
            self.register_owned(name, f.field_type, case.location)
        self.visit(case.body)
        self.pop_scope()

    @staticmethod
    def _stored_field_type(struct, name: str):
        return next(f.field_type for f in struct.fields if f.name == name)

    def _pattern_test(self, subject: str, subject_type, pattern) -> str:
        if pattern.is_null:
            # case null (Task 30.12) - only an enum can be null today
            if not self.can_be_null_enum(subject_type):
                return '0'
            test = f'{subject}.tag' if self.data_struct(subject_type) is not None else subject
            return f'{test} == FUSION_ENUM_NULL'
        if type(subject_type).__name__ == 'ErrorType':
            # case FileError: that type or a subtype (Task 26.10); case Error: any error
            number = self.error_kind_number(getattr(pattern, 'error_declaration', None))
            return f'({subject}.active && fusion_error_is({subject}.kind, {number}))'
        if pattern.name is not None:
            struct = self.data_struct(subject_type)
            enum = struct.enum_decl if struct is not None else subject_type.declaration
            number = self.enum_number(enum.variant(pattern.name).value)
            return f'{subject}.tag == {number}' if struct is not None else f'{subject} == {number}'
        return self.value_equality(subject, subject_type, self.visit(pattern.value),
                                   pattern.value.inferred_type)

    def can_be_null_enum(self, type_node) -> bool:
        return isinstance(type_node, EnumType) or self.data_struct(type_node) is not None

    def enum_text_code(self, type_node, code: str) -> str:
        """An enum value's name as a (static, never freed) fusion_string - for an enum with
        data, the name of the value only (its data is read through match)."""
        if self.data_struct(type_node) is not None:
            return f'{self.enum_c_name(type_node)}__text(({code}).tag)'
        return f'{self.enum_c_name(type_node)}__text({code})'
