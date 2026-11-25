"""A whole struct as text (Tasks 32.8, 32.13 - user decisions 2026-10-29).

    "{e}"          name : "Jeff",tel : "082",employeeID : "E7"
    e.toCSV()      Person.name,Person.tel,Employee.employeeID       one heading row,
                   "Jeff","082","E7"                                then one row of values

Every field in order, the part a struct builds on first. In "{e}" a field is `name : value`,
joined by a comma with no space; a string is in "", a char in ''; a field both a struct and
the one it builds on have is named with its struct (`Person.tel`); a struct inside a struct
is in braces, `a : {x : 1,y : 2}`. In CSV the heading names each field by its struct
(`Person.name`; a struct inside: `Line.a.x`), the values are separated by the delimiter
(default ","), a string's own " is doubled, and there is no newline after the last row. On a
one-dimensional array or a List of structs, toCSV gives the heading once, then one row each.

Each struct gets small C helpers, made on first use (after any they need) and placed after the
struct definitions: fusion_text_<S>(v), fusion_csvhead_<S>(d), fusion_csvrow_<S>(v, d),
fusion_csv_<S>(v, d) and fusion_csvarr_<S>(a, n, d).
"""

from ..parser.ast_nodes import ArrayType, EnumType, PrimitiveType, StructType
from .c_runtime import escape_c_text


class StructTextMixin:
    """Needs `self.text_helpers` (an ordered dict of helper name -> C lines), set up by
    `generate()`."""

    # ------------------------------------------------------------------ the fields

    def _text_fields(self, struct_type, access: str = 'v') -> list:
        """(struct name, field name, C code, type) for every field - the part a struct
        builds on first, its fields in its place."""
        decl = self._struct_decl(struct_type)
        result = []
        for field in decl.fields:
            code = f'{access}.{self._field_name(field.name)}'
            if getattr(field, 'is_parent', False):
                result.extend(self._text_fields(field.field_type, code))
            else:
                result.append((decl.name, field.name, code, field.field_type))
        return result

    def _text_labels(self, fields) -> list:
        """A field's name - with its struct's name when another field has the same name."""
        names = [name for _, name, _, _ in fields]
        return [f'{owner}.{name}' if names.count(name) > 1 else name
                for owner, name, _, _ in fields]

    def _value_piece(self, kind, code: str, csv: bool, number: int, lines: list, frees: list):
        """(format text, [C arguments]) for one value; a value made for it goes into a
        temporary in `lines`, freed by `frees`."""
        def temporary(make):
            lines.append(f'    fusion_string t{number} = {make};')
            frees.append(f'    fusion_str_free(&t{number});')
            return f't{number}.data'

        if self.is_class_type(kind):
            # an object field (D.097): its toString(), else its class name; null - null
            if self.has_to_string():
                return '%s', [temporary(f'fusion_object_text({code})')]
            return '%s', [f'fusion_class_name({code})']
        if isinstance(kind, StructType):
            if csv:
                return '%s', [temporary(f'{self._csv_row_helper(kind)}({code}, d)')]
            return '{%s}', [temporary(f'{self.struct_text_helper(kind)}({code})')]
        name = kind.name if isinstance(kind, PrimitiveType) else None
        if name == 'string':
            if csv:   # a " inside is doubled, as CSV does
                return '"%s"', [temporary(f'fusion_str_replace({code}, FUSION_STR("\\""), '
                                          f'FUSION_STR("\\"\\""), "")')]
            return '"%s"', [f'{code}.data']
        if name == 'bytes':
            return '%s', [temporary(f'fusion_bytes_rawToHex({code}, "")')]
        if name == 'char':
            return ('"%s"' if csv else "'%s'"), [f'fusion_char_text({code}).bytes']
        if name == 'bool':
            return '%s', [f'(({code}) ? "true" : "false")']
        if name in ('int128', 'int256', 'decimal'):
            return '%s', [f'fusion_{name}_text({code}).bytes']      # 47.7, 47.8
        if isinstance(kind, EnumType) or self.data_struct(kind) is not None:
            return '%s', [f'{self.enum_text_code(kind, code)}.data']
        if type(kind).__name__ == 'ErrorType':
            return '%s', [f'fusion_error_text({code})']
        return self._FORMAT_SPECIFIERS[name], [code]

    def _helper(self, name: str, signature: str, lines: list, call: str, frees: list) -> None:
        self.text_helpers[name] = ([f'static fusion_string {name}({signature}) {{'] + lines
                                   + [f'    fusion_string r = {call};'] + frees
                                   + ['    return r;', '}'])

    @staticmethod
    def _format_call(text: str, args: list) -> str:
        return f'fusion_str_format("{escape_c_text(text, chr(34))}"' + ''.join(f', {a}' for a in args) + ')'

    # ------------------------------------------------------------------ "{e}"

    def struct_text_helper(self, struct_type) -> str:
        """Name of the helper giving a struct as text: name : "Jeff",age : 30."""
        name = f'fusion_text_{self._struct_c_name(struct_type)}'
        if name in self.text_helpers:
            return name
        fields = self._text_fields(struct_type)
        parts, args, lines, frees = [], [], [], []
        for number, (label, (_, _, code, kind)) in enumerate(zip(self._text_labels(fields), fields)):
            text, values = self._value_piece(kind, code, False, number, lines, frees)
            parts.append(f'{label} : {text}')
            args.extend(values)
        self._helper(name, f'{self.map_type(struct_type)} v', lines,
                     self._format_call(','.join(parts), args), frees)
        return name

    # ------------------------------------------------------------------ toCSV

    def _csv_labels(self, struct_type, prefix=None) -> list:
        """The heading: Person.name, ...; a struct inside a struct: Line.a.x."""
        fields = self._text_fields(struct_type)
        result = []
        for label, (owner, field, _, kind) in zip(self._text_labels(fields), fields):
            heading = f'{prefix}.{label}' if prefix else f'{owner}.{field}'
            if isinstance(kind, StructType):
                result.extend(self._csv_labels(kind, heading))
            else:
                result.append(heading)
        return result

    def _csv_head_helper(self, struct_type) -> str:
        name = f'fusion_csvhead_{self._struct_c_name(struct_type)}'
        if name not in self.text_helpers:
            labels = [label.replace('%', '%%') for label in self._csv_labels(struct_type)]
            self._helper(name, 'const char* d', [],
                         self._format_call('%s'.join(labels), ['d'] * (len(labels) - 1)), [])
        return name

    def _csv_row_helper(self, struct_type) -> str:
        name = f'fusion_csvrow_{self._struct_c_name(struct_type)}'
        if name in self.text_helpers:
            return name
        parts, args, lines, frees = [], [], [], []
        for number, (_, _, code, kind) in enumerate(self._text_fields(struct_type)):
            text, values = self._value_piece(kind, code, True, number, lines, frees)
            if parts:
                args.append('d')
            parts.append(text)
            args.extend(values)
        self._helper(name, f'{self.map_type(struct_type)} v, const char* d', lines,
                     self._format_call('%s'.join(parts), args), frees)
        return name

    # ------------------------------------------------------------------ toCSV of plain values (45.11b)

    CSV_BUFFER = [
        '// toCSV of plain values (45.11b, D.151): a growing buffer; a field holding a delimiter, a quote',
        '// or a line break is wrapped in quotes, a quote inside doubled (the CSV rules); a null one empty',
        'typedef struct { char* p; int len; int cap; } fusion_csvbuf;',
        'static void fusion_csv_raw(fusion_csvbuf* b, const char* s, int n) {',
        '    if (b->len + n + 1 > b->cap) {',
        '        int c = b->cap ? b->cap : 64;',
        '        while (c < b->len + n + 1) c *= 2;',
        '        b->p = (char*)realloc(b->p, (size_t)c);',
        '        if (!b->p) { fprintf(stderr, "out of memory\\n"); exit(1); }',
        '        b->cap = c;',
        '    }',
        '    memcpy(b->p + b->len, s, (size_t)n);',
        '    b->len += n;',
        '}',
        'static int fusion_csv_has(const char* v, const char* d) { return d && *d && strstr(v, d) != NULL; }',
        'static void fusion_csv_field(fusion_csvbuf* b, const char* v, const char* d, const char* s, const char* l) {',
        '    if (!v) return;',
        '    if (!(strchr(v, \'"\') || strchr(v, \'\\n\') || strchr(v, \'\\r\') || fusion_csv_has(v, d)',
        '          || fusion_csv_has(v, s) || fusion_csv_has(v, l))) { fusion_csv_raw(b, v, (int)strlen(v)); return; }',
        '    fusion_csv_raw(b, "\\"", 1);',
        '    for (const char* c = v; *c; c++) fusion_csv_raw(b, *c == \'"\' ? "\\"\\"" : c, *c == \'"\' ? 2 : 1);',
        '    fusion_csv_raw(b, "\\"", 1);',
        '}',
        'static fusion_string fusion_csv_done(fusion_csvbuf* b) {',
        '    fusion_string r = fusion_str_make(b->p ? b->p : "", b->len);',
        '    free(b->p);',
        '    return r;',
        '}']

    def _csv_text(self, element, code: str) -> tuple:
        """(C lines before, a `const char*` C expression) for one plain value; NULL for a null one."""
        name = element.name if isinstance(element, PrimitiveType) else None
        if isinstance(element, EnumType):
            return [], f'(({code}) == FUSION_ENUM_NULL ? NULL : {self.enum_text_code(element, code)}.data)'
        if name == 'string':
            return [], f'({code}).data'
        if name == 'bool':
            return [], f'(({code}) ? "true" : "false")'
        if name == 'char':
            return ['char fusion_v[5] = {0};', f'fusion_utf8_encode({code}, fusion_v);'], 'fusion_v'
        if name in ('int128', 'int256', 'decimal'):         # 47.7, 47.8: its digits
            return [f'fusion_{name}_buf fusion_v = fusion_{name}_text({code});'], 'fusion_v.bytes'
        spec, cast = (('%g', 'double') if name in ('float', 'double')
                      else ('%lld', 'long long') if name == 'long' else ('%d', 'int'))     # long: 47.1
        return [f'char fusion_v[32]; snprintf(fusion_v, sizeof fusion_v, "{spec}", ({cast})({code}));'], 'fusion_v'

    def _csv_delimiter(self, number: int, argument, default: str) -> list:
        """C lines setting `fusion_d<number>` (a const char*) to a delimiter."""
        if argument is None:
            return [f'const char* fusion_d{number} = "{default}";']
        code = self.visit(argument)
        if getattr(argument.inferred_type, 'name', None) == 'char':
            return [f'char fusion_dc{number}[5] = {{0}}; fusion_utf8_encode({code}, fusion_dc{number});',
                    f'const char* fusion_d{number} = fusion_dc{number};']
        return [f'const char* fusion_d{number} = ({code}).data;']

    def plain_csv_code(self, node) -> str:
        """`a.toCSV(",", "#", "\\n")` on an array of plain values (45.11b, D.151)."""
        self.text_helpers.setdefault('fusion_csv_buffer', self.CSV_BUFFER)
        receiver = node.callee.object
        primary, secondary, line = node.csv_delimiters
        lines = (self._csv_delimiter(0, primary, ',') + self._csv_delimiter(1, secondary, '#')
                 + self._csv_delimiter(2, line, '\\n') + ['fusion_csvbuf fusion_b = {0};'])
        element = receiver.inferred_type.element_type

        def put(value_code, sheets):
            before, text = self._csv_text(element, value_code)
            return ('{ ' + ' '.join(before) + f' fusion_csv_field(&fusion_b, {text}, fusion_d0, '
                    f'{"fusion_d1" if sheets else "NULL"}, fusion_d2); }}')

        def sep(counter, delimiter):
            return f'if ({counter}) fusion_csv_raw(&fusion_b, {delimiter}, (int)strlen({delimiter}));'

        if node.csv == 'plain':
            kind = receiver.inferred_type
            if isinstance(kind, ArrayType):
                items, count = self._array_operand(receiver, kind)
            else:
                code = self.visit(receiver)               # on the heap: a counted block
                lines.append(f'{self.map_type(kind)} fusion_a = {code};')
                items, count = 'fusion_a->data', 'fusion_a->len'
            lines.append(f'for (int fusion_i = 0; fusion_i < {count}; fusion_i++) {{ {sep("fusion_i", "fusion_d0")} '
                         f'{put(f"{items}[fusion_i]", False)} }}')
        else:
            root, slots, full, steps, open_dims = node.csv_dims
            lines.insert(0, f'int fusion_off = {self._slot_position(slots, full, steps, node)};')
            counters = {k: f'fusion_t{k}' for k in open_dims}
            position = ' + '.join(['fusion_off'] + [c if steps[k] == 1 else f'{c} * {steps[k]}'
                                                    for k, c in counters.items()])
            value = f'{self.visit(root)}[{position}]'
            sheets = len(open_dims) >= 3
            # rows the lines, columns the values; 3 dimensions: each line that row of every sheet
            walk = list(open_dims)
            if len(walk) == 1:
                levels = [(walk[0], 'fusion_d0')]
            elif len(walk) == 2:
                levels = [(walk[0], 'fusion_d2'), (walk[1], 'fusion_d0')]
            else:
                levels = [(walk[0], 'fusion_d2'), (walk[2], 'fusion_d1'), (walk[1], 'fusion_d0')]
            loop = put(value, sheets)
            for k, delimiter in reversed(levels):
                c = counters[k]
                loop = f'for (int {c} = 0; {c} < {full[k]}; {c}++) {{ {sep(c, delimiter)} {loop} }}'
            lines.append(loop)
        return '__extension__ ({ ' + ' '.join(lines) + ' fusion_csv_done(&fusion_b); })'

    def csv_code(self, node) -> str:
        """x.toCSV(delimiter) on a struct, a one-dimensional array or a List of structs."""
        receiver, kind = node.callee.object, node.csv
        if kind in ('plain', 'dims'):
            return self.plain_csv_code(node)
        receiver_type = receiver.inferred_type
        delimiter = '","'
        if node.arguments:
            argument = node.arguments[0]
            code = self.visit(argument)
            is_char = getattr(argument.inferred_type, 'name', None) == 'char'
            delimiter = f'fusion_char_text({code}).bytes' if is_char else f'({code}).data'
        if kind == 'struct':
            return f'{self._csv_one_helper(receiver_type)}({self.visit(receiver)}, {delimiter})'
        element = receiver_type.element_type
        if kind == 'array':
            items, count = self._array_operand(receiver, receiver_type)
        else:
            code = self.visit(receiver)       # a List of your own too: its data copied (33.3d2)
            list_c = self.map_type(receiver_type)
            items, count = f'{list_c}_data({code})', f'{list_c}_len({code})'
        return f'{self._csv_many_helper(element)}({items}, {count}, {delimiter})'

    def _csv_one_helper(self, struct_type) -> str:
        name = f'fusion_csv_{self._struct_c_name(struct_type)}'
        if name not in self.text_helpers:
            head, row = self._csv_head_helper(struct_type), self._csv_row_helper(struct_type)
            self._helper(name, f'{self.map_type(struct_type)} v, const char* d',
                         [f'    fusion_string h = {head}(d), w = {row}(v, d);'],
                         'fusion_str_format("%s\\n%s", h.data, w.data)',
                         ['    fusion_str_free(&h);', '    fusion_str_free(&w);'])
        return name

    def _csv_many_helper(self, struct_type) -> str:
        name = f'fusion_csvarr_{self._struct_c_name(struct_type)}'
        if name not in self.text_helpers:
            head, row = self._csv_head_helper(struct_type), self._csv_row_helper(struct_type)
            self._helper(name, f'const {self.map_type(struct_type)}* a, int n, const char* d', [
                f'    fusion_string out = {head}(d);',
                '    for (int i = 0; i < n; i++) {',
                f'        fusion_string w = {row}(a[i], d);',
                '        fusion_string next = fusion_str_format("%s\\n%s", out.data, w.data);',
                '        fusion_str_free(&out);',
                '        fusion_str_free(&w);',
                '        out = next;',
                '    }'], 'out', [])
        return name

    def text_helper_lines(self) -> list:
        lines = [line for helper in self.text_helpers.values() for line in helper]
        return ['// A whole struct as text (Tasks 32.8, 32.13)'] + lines + [''] if lines else []
