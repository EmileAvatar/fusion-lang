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
