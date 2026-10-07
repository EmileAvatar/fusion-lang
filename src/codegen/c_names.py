"""C keyword name mangling.

Extracted from c_generator.py (Task 12.5 - C Codegen Module Split) as a
behavior-preserving refactor. mangle_function_name() is a plain function - it doesn't
need generator state, unlike map_type() or the runtime-lowering helpers.
"""

# C reserved keywords that can't be used as function names
_C_KEYWORDS = {
    'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
    'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
    'inline', 'int', 'long', 'register', 'restrict', 'return', 'short',
    'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union',
    'unsigned', 'void', 'volatile', 'while', '_Bool', '_Complex', '_Imaginary'
}


def mangle_function_name(name: str) -> str:
    """Mangle function names that conflict with C keywords.

    Args:
        name: Fusion function name

    Returns:
        C-safe function name
    """
    if name in _C_KEYWORDS:
        return f'fusion_{name}'
    return name


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
