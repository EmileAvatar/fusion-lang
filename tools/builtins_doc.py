"""files/Builtins.md - every built-in function and method, generated from the compiler (28.1.4).

    python check.py --builtins      write the file
    python check.py                 the "builtins" check fails when the file is out of date

Signatures, defaults, layers and "can fail" come from the compiler itself. Only the topic
of each function (TOPICS) and the method descriptions (LIST_METHODS / MAP_METHODS) are
written here by hand; a function with no topic is listed under "Other", and a method the
compiler has but this file doesn't describe makes the check fail.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TOPICS = [
    ('Program, output and input', ['print', 'format', 'exit', 'readLine', 'isEndOfInput', 'run']),
    ('Files', ['readText', 'readLines', 'writeText', 'appendText', 'readBytes', 'writeBytes',
               'fileExists', 'deleteFile']),
    ('Core', ['len', 'range', 'charCode', 'fromCharCode', 'toByte', 'wrapAdd', 'wrapSub',
              'wrapMul']),
    ('Text - inspect and search', ['isEmpty', 'isBlank', 'isDigits', 'isLetters', 'isAscii',
                                   'isInt', 'isFloat', 'contains', 'containsAny', 'startsWith',
                                   'endsWith', 'indexOf', 'lastIndexOf', 'countOf', 'lenb']),
    ('Text - compare', ['equalsIgnoreCase', 'compareIgnoreCase', 'compareNatural']),
    ('Text - extract and change', ['substring', 'left', 'right', 'insert', 'remove', 'replace',
                                   'replaceFirst', 'repeat', 'reverse', 'truncate', 'trim',
                                   'trimStart', 'trimEnd', 'toUpper', 'toLower', 'capitalize',
                                   'toTitle', 'padLeft', 'padRight', 'center', 'asciiOnly',
                                   'digitsOnly']),
    ('Text - split and join', ['split', 'join', 'lines', 'words']),
    ('Text - masks', ['mask', 'maskEmail', 'formatMask']),
    ('Conversions and formatting', ['toString', 'toInt', 'toFloat', 'parseInt', 'formatNumber']),
    ('Number bases', ['toHex', 'toBinary', 'toOctal', 'toBase', 'fromHex', 'fromBinary',
                      'fromOctal']),
    ('Raw bytes', ['toBytes', 'newBytes', 'byteAt', 'getInt', 'getInt16', 'getUInt16', 'setInt',
                   'setInt16', 'slice', 'isText', 'rawToHex', 'hexToRaw', 'bytesToHex',
                   'hexToBytes']),
]

# Built-ins the type checker handles specially (their registered type is only a placeholder):
# name -> (call, returns)
SPECIAL = {
    'print': ('print(string text, any...)', 'void'),
    'format': ('format(string text, any...)', 'string'),
    'len': ('len(string | array | bytes)', 'int'),
    'range': ('range(int from, int to, int step = 1)', 'the numbers, for a loop'),
    'toString': ('toString(int | float | double | bool | char | byte | bytes)', 'string'),
}

# (call, returns, can fail, what it does) - List<T> methods (Task 18.5.1)
LIST_METHODS = [
    ('add(T x)', 'void', False, 'add at the end'),
    ('insert(int at, T x)', 'void', True, 'insert before position at (IndexError)'),
    ('removeAt(int at)', 'void', True, 'remove the element at a position (IndexError)'),
    ('remove(T x)', 'bool', False, 'remove the first element equal to x; false if none'),
    ('clear()', 'void', False, 'remove every element'),
    ('len()', 'int', False, 'the number of elements'),
    ('contains(T x)', 'bool', False, 'whether an element equals x'),
    ('indexOf(T x)', 'int', False, 'the first position of x, or -1'),
    ('join(string separator)', 'string', False, 'List<string> only: the elements joined'),
    ('slice(int start, int count)', 'List<T>', True, 'a copy of count elements from start (IndexError)'),
    ('sort()', 'void', False, 'sort in place (numbers, chars, text, bools)'),
    ('sortBy((T, T) : int compare)', 'void', False, 'sort in place by a function'),
    ('filter((T) : bool keep)', 'List<T>', False, 'the elements the function keeps'),
    ('map((T) : U f)', 'List<U>', False, 'the function applied to each element'),
    ('reduce(U start, (U, T) : U f)', 'U', False, 'combine every element into one value'),
]

# Map<K, V> methods (Task 18.5.2)
MAP_METHODS = [
    ('has(K key)', 'bool', False, 'whether the key is there'),
    ('get(K key, V default)', 'V', False, 'the value, or the default when the key is missing'),
    ('remove(K key)', 'bool', False, 'remove the key; false if it was not there'),
    ('keys()', 'List<K>', False, 'the keys, in the order they were added'),
    ('values()', 'List<V>', False, 'the values, in the same order'),
    ('len()', 'int', False, 'the number of keys'),
    ('clear()', 'void', False, 'remove every key'),
]


def type_name(t) -> str:
    kind = type(t).__name__
    if kind == 'PrimitiveType':
        return t.name
    if kind == 'ListType':
        return f'List<{type_name(t.element_type)}>'
    if kind == 'MapType':
        return f'Map<{type_name(t.key_type)}, {type_name(t.value_type)}>'
    if kind == 'ArrayType':
        return f'{type_name(t.element_type)}[]'
    if kind == 'FunctionType':
        params = ', '.join(type_name(p) for p in t.parameter_types)
        return f'({params}) : {type_name(t.return_type)}'
    return getattr(t, 'name', kind)


def literal_text(value, type_hint) -> str:
    if type_hint == 'char':
        return repr(value).replace('"', "'")
    if type_hint == 'bool':
        return 'true' if value else 'false'
    return str(value)


def compiler_methods(path: Path) -> set:
    """Every method name the collection rules check for (`method == 'x'`, `method in (...)`)."""
    names = set()
    for line in path.read_text(encoding='utf-8').splitlines():
        if re.search(r"\bmethod\s*(==|in)\s", line):
            names.update(re.findall(r"'(\w+)'", line))
    return names


def render() -> tuple:
    """(the Markdown text, problems) - problems are methods this file doesn't describe."""
    from src.semantic import SemanticAnalyzer
    from src.semantic.name_resolver import (BUILTIN_DEFAULTS, FLEXIBLE_FIRST_ARG, TYPE_CLASSES,
                                            CLASS_STATICS, NOT_METHODS, builtin_layer)
    from src.codegen.c_generator import CCodeGenerator

    symbols = SemanticAnalyzer().symbol_table.current_scope.symbols
    functions = {n: s for n, s in symbols.items() if s.symbol_type == 'function'}
    failing = {n for n, (_, fails) in CCodeGenerator._STRING_BUILTINS.items() if fails}

    def signature(name) -> tuple:
        if name in SPECIAL:
            return SPECIAL[name]
        ftype = functions[name].data_type
        params = [type_name(p) for p in ftype.parameter_types]
        if name in FLEXIBLE_FIRST_ARG and params:
            params[0] = ' | '.join(FLEXIBLE_FIRST_ARG[name])
        defaults = BUILTIN_DEFAULTS.get(name, [])
        for i, (value, hint) in enumerate(defaults):
            at = len(params) - len(defaults) + i
            params[at] += ' = ' + literal_text(value, hint)
        return f'{name}({", ".join(params)})', type_name(ftype.return_type)

    lines = ['# Built-in functions and methods', '',
             '**Generated from the compiler** by `python check.py --builtins` (Task 28.1.4) - '
             'do not edit by hand.',
             '`python check.py` fails when this file no longer matches the compiler.', '',
             f'{len(functions)} functions, {len(LIST_METHODS)} List methods, '
             f'{len(MAP_METHODS)} Map methods. Examples of each are in `SYNTAX_REFERENCE.md`.',
             '', '- **Layer:** the lowest `[stdlib] layer` that allows it - `core` (no heap), '
             '`alloc` (no operating system), `std` (everything)',
             '- **Fails:** it can raise an error (catch it with `try`, or capture it); any '
             'function that makes text can also fail with StringTooLongError when '
             '`[strings] max_length` is set',
             '- **Methods:** a function can also be called as a method on its first argument - '
             '`name.trim()` is `trim(name)` - and through its type class - '
             '`String.trim(name)` (not ' + ', '.join(f'`{n}`' for n in sorted(NOT_METHODS)) +
             ')', '']

    listed = set()
    topics = TOPICS + [('Other', sorted(n for n in functions
                                        if n not in {x for _, ns in TOPICS for x in ns}))]
    for topic, names in topics:
        names = [n for n in names if n in functions]
        if not names:
            continue
        lines += [f'#### {topic}', '', '| Function | Returns | Layer | Fails |', '|---|---|---|---|']
        for name in names:
            call, returns = (part.replace('|', '\\|') for part in signature(name))
            lines.append(f'| `{call}` | `{returns}` | {builtin_layer(name)} | '
                         f'{"yes" if name in failing else ""} |')
            listed.add(name)
        lines.append('')

    lines += ['#### Type classes', '',
              'Each built-in type has a class holding its functions as methods (Task 18.3.7):', '',
              '| Class | Type | Also (not taking the type first) |', '|---|---|---|']
    for cls, typ in TYPE_CLASSES.items():
        statics = ', '.join(f'`{cls}.{s}`' for s in sorted(CLASS_STATICS.get(cls, ())))
        lines.append(f'| `{cls}` | `{typ}` | {statics} |')
    lines.append('')

    for title, methods in (('List<T> methods', LIST_METHODS), ('Map<K, V> methods', MAP_METHODS)):
        lines += [f'#### {title}', '', '| Method | Returns | Fails | What it does |',
                  '|---|---|---|---|']
        for call, returns, fails, what in methods:
            lines.append(f'| `.{call}` | `{returns}` | {"yes" if fails else ""} | {what} |')
        lines.append('')

    described = {m[0].split('(')[0] for m in LIST_METHODS + MAP_METHODS}
    missing = compiler_methods(ROOT / 'src' / 'semantic' / 'collection_rules.py') - described
    problems = [f'method .{m} is in the compiler but not described in tools/builtins_doc.py'
                for m in sorted(missing)]
    return '\n'.join(lines).rstrip() + '\n', problems


if __name__ == '__main__':
    text, problems = render()
    print(text)
    print('\n'.join(problems), file=sys.stderr)
