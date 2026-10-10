"""How Fusion names become C names (Task 12.5; Task 18.4.1 / 15.8).

- Functions and struct types always get the `fu_` prefix in C (`add` -> `fu_add`, `Point`
  -> `fu_Point`), except `main`. So a Fusion function named `free`, `exit` or `abs` never
  collides with the C library, and none collides with the runtime's `fusion_` names.
  Modules (Task 18.4.2) add their name: `fu_money_round`
- Locals and parameters keep their names, unless the name would break the C: a C keyword,
  a name the generated code relies on (`printf`, `uint8_t`, `NULL`, ...), or one starting
  with a reserved prefix - those get `fu_` too (`auto` -> `fu_auto`)
- Struct fields live in their own C namespace, so only C keywords are changed
"""

# C reserved keywords that can't be used as function names
_C_KEYWORDS = {
    'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
    'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
    'inline', 'int', 'long', 'register', 'restrict', 'return', 'short',
    'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union',
    'unsigned', 'void', 'volatile', 'while', '_Bool', '_Complex', '_Imaginary'
}


# Names the generated code and the headers it includes rely on inside a function: a local
# with one of these names would hide them
_C_RESERVED_NAMES = _C_KEYWORDS | {
    'main', 'printf', 'pow', 'NULL', 'EOF', 'true', 'false', 'bool', 'size_t', 'FILE',
    'int8_t', 'int16_t', 'int32_t', 'int64_t', 'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t',
    'va_list', 'errno', 'stdin', 'stdout', 'stderr', 'inline', 'asm', 'fortran',
}
_RESERVED_PREFIXES = ('fusion_', 'FUSION_', 'fu_', '__')


def mangle_function_name(name: str) -> str:
    """The C name of a Fusion function or struct type: `fu_` + the name, except `main`.

    Args:
        name: Fusion function or struct name

    Returns:
        C-safe global name
    """
    if name == 'main':
        return name
    return f'fu_{name}'


def c_member_name(name: str) -> str:
    """The C name of a struct field: unchanged unless it is a C keyword."""
    if name in _C_KEYWORDS:
        return f'fusion_{name}'
    return name


def local_needs_renaming(name: str) -> bool:
    """True for a local / parameter name that would break the generated C."""
    return name in _C_RESERVED_NAMES or name.startswith(_RESERVED_PREFIXES)


def local_c_name(name: str) -> str:
    """The C name of a local variable or parameter."""
    return f'fu_{name}' if local_needs_renaming(name) else name


def array_length_name(param_name: str) -> str:
    """Name of the hidden C parameter carrying an `int[]` parameter's length (Task 18.1.2).

    C passes an array as a bare pointer and loses its length, so a Fusion parameter
    `int[] values` becomes the two C parameters `int* values, int fusion_len_values`.

    Like mangle_function_name's `fusion_` prefix, this could collide with a user identifier
    spelled the same way - reserving the `fusion_` prefix is tracked in Task 15.

    Args:
        param_name: The Fusion array parameter's name

    Returns:
        The hidden length parameter's C name
    """
    return f'fusion_len_{param_name}'
