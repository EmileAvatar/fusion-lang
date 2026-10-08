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
                'char': 'char',
                'string': 'char*',  # Strings as char pointers
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

    def function_typedef_lines(self) -> list:
        """The typedef declarations for every function type used, in first-use order."""
        lines = []
        for signature, name in getattr(self, 'function_typedefs', {}).items():
            # 'int (*)(int)' -> 'typedef int (*fusion_fn_1)(int);'
            lines.append('typedef ' + signature.replace('(*)', f'(*{name})', 1) + ';')
        return lines
