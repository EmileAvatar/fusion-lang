"""Fusion type -> C type mapping.

Extracted from c_generator.py (Task 12.5 - C Codegen Module Split) as a
behavior-preserving refactor: CCodeGenerator now includes TypeMapperMixin instead of
defining map_type() itself. No logic changed.
"""

from ..parser.ast_nodes import PrimitiveType, FunctionType, ArrayType, StructType, TypeNode
from .c_names import mangle_function_name


class TypeMapperMixin:
    """Provides map_type() - mixed into CCodeGenerator.

    A mixin (not a standalone function) because map_type() recurses on itself via
    self.map_type(...) for FunctionType/ArrayType, and existing tests call
    generator.map_type(...) directly as an instance method.
    """

    def map_type(self, fusion_type: TypeNode) -> str:
        """Map Fusion type to C type.

        Args:
            fusion_type: Fusion type node

        Returns:
            Equivalent C type string
        """
        if isinstance(fusion_type, PrimitiveType):
            type_map = {
                'int': 'int',
                'float': 'float',
                'double': 'double',
                'bool': 'bool',
                'char': 'fusion_char',  # any Unicode character (Task 18.3.2b)
                'string': 'fusion_string',  # an owned string value (Task 18.3.1)
                'byte': 'uint8_t',          # one raw byte, 0-255 (Task 18.3.8)
                'bytes': 'fusion_bytes',    # raw bytes - the string struct, any bytes (18.3.8)
                'void': 'void'
            }
            return type_map.get(fusion_type.name, 'void')

        elif isinstance(fusion_type, FunctionType):
            # A function pointer, named through a typedef (Task 18.1.3). C's raw declarator
            # syntax wraps around the name - `int (*op)(int)`, and for a function returning
            # one, `int (*pick(bool b))(int)` - so one typedef per distinct function type
            # keeps variables, parameters and return types all as plain `<type> <name>`
            return self.function_typedef_name(fusion_type)

        elif isinstance(fusion_type, ArrayType):
            # Just the element's C type - the array declaration itself needs the size
            # appended after the variable name (`int arr[5]`, not `int[5] arr`), which is
            # built directly in visit_VarDeclStmt rather than through this generic mapping
            return self.map_type(fusion_type.element_type)

        elif isinstance(fusion_type, StructType):
            # A typedef'd C struct of the same name (Task 18.2.1), mangled like a function
            # name if it collides with a C keyword
            return mangle_function_name(fusion_type.name)

        return 'void'

    def function_typedef_name(self, fusion_type: FunctionType) -> str:
        """Return the C typedef name for a function type, registering it on first use.

        Typedefs are collected in self.function_typedefs (C signature -> name) and emitted
        near the top of the C file by generate(). Identical function types share a name.
        Uses the `fusion_` prefix, like the other compiler-generated names (see Task 15.8).
        """
        if not hasattr(self, 'function_typedefs'):
            self.function_typedefs = {}
        param_types = ', '.join(self.map_type(p) for p in fusion_type.parameter_types) or 'void'
        return_type = self.map_type(fusion_type.return_type)
        signature = f'{return_type} (*)({param_types})'
        if signature not in self.function_typedefs:
            self.function_typedefs[signature] = f'fusion_fn_{len(self.function_typedefs) + 1}'
        return self.function_typedefs[signature]

    def return_c_type(self, fusion_type: TypeNode) -> str:
        """C type for a function's return value - like map_type, except that an array is
        returned inside its hidden wrapper struct (Task 18.2.4), since C can't return one."""
        if isinstance(fusion_type, ArrayType):
            return self.array_wrapper_name(fusion_type)
        return self.map_type(fusion_type)

    def array_wrapper_name(self, fusion_type: ArrayType) -> str:
        """The hidden struct a fixed-size array is returned in (Task 18.2.4), registering
        it on first use - e.g. int[3] -> fusion_arr_int_3:

            typedef struct { int data[3]; } fusion_arr_int_3;

        Uses the `fusion_` prefix like the other compiler-generated names (Task 15.8)."""
        if not hasattr(self, 'array_wrappers'):
            self.array_wrappers = {}
        element = fusion_type.element_type
        key = mangle_function_name(element.name) if isinstance(element, StructType) else element.name
        name = f'fusion_arr_{key}_{fusion_type.size}'
        self.array_wrappers[name] = (self.map_type(element), fusion_type.size, element)
        return name

    def array_wrapper_lines(self) -> list:
        """The wrapper typedefs, plus helpers: `_from` copies an array into a wrapper (for
        `return arr`), `_copy` moves a returned wrapper into an array (for `int[3] a =
        make()` and `a = make()`). `static inline`, so unused ones don't warn.

        For elements holding strings (Task 18.3.1) `_from` makes independent copies, `_copy`
        frees the array's old elements before moving the new ones in, and `_free` releases
        a wrapper nobody took over."""
        lines = []
        for name, (element, size, element_type) in getattr(self, 'array_wrappers', {}).items():
            lines.append(f'typedef struct {{ {element} data[{size}]; }} {name};')
            if not self.is_managed(element_type):
                lines += [
                    f'static inline {name} {name}_from(const void* src) {{ {name} r; '
                    f'memcpy(r.data, src, sizeof r.data); return r; }}',
                    f'static inline void {name}_copy(void* dst, {name} v) {{ '
                    f'memcpy(dst, v.data, sizeof v.data); }}',
                ]
                continue
            free_one = ' '.join(self.free_lines(element_type, 'dst[i]'))
            free_own = ' '.join(self.free_lines(element_type, 'w->data[i]'))
            copy_one = self.copy_code(element_type, 'r.data[i]')
            lines += [
                f'static inline {name} {name}_from(const {element}* src) {{ {name} r; '
                f'memcpy(r.data, src, sizeof r.data); '
                f'for (int i = 0; i < {size}; i++) r.data[i] = {copy_one}; return r; }}',
                f'static inline void {name}_copy({element}* dst, {name} v) {{ '
                f'for (int i = 0; i < {size}; i++) {{ {free_one} }} '
                f'memcpy(dst, v.data, sizeof v.data); }}',
                f'static inline void {name}_free({name}* w) {{ '
                f'for (int i = 0; i < {size}; i++) {{ {free_own} }} }}',
            ]
        return lines

    def function_typedef_lines(self) -> list:
        """The typedef declarations for every function type used, in first-use order."""
        lines = []
        for signature, name in getattr(self, 'function_typedefs', {}).items():
            # 'int (*)(int)' -> 'typedef int (*fusion_fn_1)(int);'
            lines.append('typedef ' + signature.replace('(*)', f'(*{name})', 1) + ';')
        return lines
