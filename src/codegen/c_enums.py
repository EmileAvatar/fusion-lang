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

A match (Task 25.3) becomes an if / else-if chain, not a C switch - so `break` and
`continue` in a case still act on the loop around the match:

    fusion_val_1 = <subject>;                                the subject, evaluated once
    fusion_val_2 = (fusion_val_1 == 0 || ...) ? 1 : ... : 0;  which case runs
    (the statement's temporaries are freed here)
    if (fusion_val_2 == 1) { ... } else if ... else { ... }
"""

from dataclasses import fields as dataclass_fields, is_dataclass

from src.parser.ast_nodes import (EnumDecl, EnumStaticCall, EnumType, EnumValueExpr, ListType,
                                  LiteralExpr, MatchStmt, PrimitiveType, StructDecl, StructField,
                                  StructType)
from .c_names import mangle_function_name, local_c_name
from .c_runtime import escape_c_text


class EnumsMixin:
    """Enum code generation; needs self.enum_decls (generate())."""

    def lower_data_enums(self, program) -> None:
        """Give each enum with data a struct, and use it for every value of the enum."""
        structs = {}
        for enum in [d for d in program.declarations if isinstance(d, EnumDecl)]:
            if not any(v.fields for v in enum.variants):
                continue
            first = enum.variants[0].value
            tag = StructField(location=enum.location, name='tag',
                              field_type=PrimitiveType(location=enum.location, name='int'),
                              default_value=LiteralExpr(location=enum.location, value=first,
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
        program.declarations.extend(structs.values())

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
        """A value nobody gave: the enum's first value."""
        return type_node.declaration.variants[0].value

    def enum_section_lines(self, enums) -> list:
        """The typedef and helpers of every enum - right after the runtime, before the list
        types and structs that may hold enums."""
        lines = []
        for enum in enums:
            c = mangle_function_name(enum.name)
            data = getattr(enum, 'struct_decl', None) is not None   # a struct (Task 25.4)
            lines += [f'// enum {enum.name} (Task 25)'] + ([] if data else [f'typedef int {c};'])
            lines += [f'static inline fusion_string {c}__text(int v) {{', '    switch (v) {']
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
            lines += [f'    fusion_runtime_error(where, "\\"%.*s\\" is not a value of enum '
                      f'{escape_c_text(enum.name, chr(34))}", s.len, s.data);',
                      f'    return {self.enum_number(enum.variants[0].value)};', '}', '']
        return lines

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
        if node.method == 'fromString':   # the text is borrowed
            return f'{c}__fromString({self.visit(node.arguments[0])}, {self._where(node)})'
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
        if held:
            # A new value with data (a call's result): kept in an owned local while the
            # cases read its data, freed when the match ends - or by a return / break
            self.push_scope('block')
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
        for number, case in enumerate(node.cases, 1):
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
        if held:
            self.pop_scope()
        return ''

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
            value = self.copy_code(f.field_type, field) if self.is_managed(f.field_type) else field
            self.emit_line(f'{self.map_type(f.field_type)} {name} = {value}')
            self.register_owned(name, f.field_type, case.location)
        self.visit(case.body)
        self.pop_scope()

    def _pattern_test(self, subject: str, subject_type, pattern) -> str:
        if pattern.name is not None:
            struct = self.data_struct(subject_type)
            enum = struct.enum_decl if struct is not None else subject_type.declaration
            number = self.enum_number(enum.variant(pattern.name).value)
            return f'{subject}.tag == {number}' if struct is not None else f'{subject} == {number}'
        return self.value_equality(subject, subject_type, self.visit(pattern.value),
                                   pattern.value.inferred_type)

    def enum_text_code(self, type_node, code: str) -> str:
        """An enum value's name as a (static, never freed) fusion_string - for an enum with
        data, the name of the value only (its data is read through match)."""
        if self.data_struct(type_node) is not None:
            return f'{self.enum_c_name(type_node)}__text(({code}).tag)'
        return f'{self.enum_c_name(type_node)}__text({code})'
