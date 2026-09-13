"""Fusion type -> C type mapping.

Extracted from c_generator.py (Task 12.5 - C Codegen Module Split) as a
behavior-preserving refactor: CCodeGenerator now includes TypeMapperMixin instead of
defining map_type() itself. No logic changed.
"""

from ..parser.ast_nodes import PrimitiveType, FunctionType, ArrayType, TypeNode


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
            # Function pointer type
            param_types = ', '.join(self.map_type(p) for p in fusion_type.parameter_types)
            return_type = self.map_type(fusion_type.return_type)
            return f'{return_type} (*)({param_types})'

        elif isinstance(fusion_type, ArrayType):
            # Just the element's C type - the array declaration itself needs the size
            # appended after the variable name (`int arr[5]`, not `int[5] arr`), which is
            # built directly in visit_VarDeclStmt rather than through this generic mapping
            return self.map_type(fusion_type.element_type)

        return 'void'
