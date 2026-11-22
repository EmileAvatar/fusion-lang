"""A List of your own (Task 33.3d1, D.174): `class Ring<T> implements List<T>`.

The class writes the core five - `len()`, `get(i)`, `set(i, v)`, `insert(i, v)`, `removeAt(i)` - and
every other List method it doesn't write itself is added to it here, written in Fusion from the core
five, then attached like the class's own methods (bare `len()` becomes `this.len()` ...; `get` and
`set` are words of `property`, so they are written `this.get(i)` / `this.set(i, v)`).
`E` below stands for the element type written in `List<...>`.

Not added (they need a generic method, or work only for some element types): `map`, `reduce`, `sort`,
`join` - a class may write them itself.
"""
import re

CORE = {'len': 0, 'get': 1, 'set': 2, 'insert': 2, 'removeAt': 1}
CORE_SHOWN = 'len(), get(int i), set(int i, E value), insert(int i, E value), removeAt(int i)'

# name -> its Fusion text; a method may use the ones before it
METHODS = {
    'add': '''void function add(E value)
    insert(len(), value)
''',
    'indexOf': '''int function indexOf(E value)
    int i = 0
    while i < len()
        if this.get(i) == value
            return i
        i = i + 1
    return -1
''',
    'contains': '''bool function contains(E value) : indexOf(value) >= 0
''',
    'remove': '''bool function remove(E value)
    int i = indexOf(value)
    if i < 0
        return false
    removeAt(i)
    return true
''',
    'clear': '''void function clear()
    while len() > 0
        removeAt(len() - 1)
''',
    'toList': '''List<E> function toList()
    List<E> result = []
    int i = 0
    while i < len()
        E item = this.get(i)
        result.add(byVal item)
        i = i + 1
    return result
''',
    'copyPart': '''List<E> function copyPart(int start, int count)
    if start < 0 or start > len()
        throw IndexError(format("copyPart: start {@1} is outside 0...{@2}", start, len()))
    List<E> result = []
    int i = start
    while i < len() and i < start + count
        E item = this.get(i)
        result.add(byVal item)
        i = i + 1
    return result
''',
    'copyPartAt': '''List<E> function copyPartAt(int start, int last)
    if start < 0 or start >= len()
        throw IndexError(format("copyPartAt: start {@1} is outside 0...{@2}", start, len() - 1))
    List<E> result = []
    int i = start
    if start <= last
        while i <= last and i < len()
            E item = this.get(i)
            result.add(byVal item)
            i = i + 1
    else
        while i >= last and i >= 0
            E item = this.get(i)
            result.add(byVal item)
            i = i - 1
    return result
''',
    'slice': '''List<E> function slice(int start, int count) : copyPart(start, count)
''',
    'sliceAt': '''List<E> function sliceAt(int start, int last) : copyPartAt(start, last)
''',
    'filter': '''List<E> function filter((E) : bool keep)
    List<E> result = []
    int i = 0
    while i < len()
        E item = this.get(i)
        if keep(item)
            result.add(byVal item)
        i = i + 1
    return result
''',
    'sortBy': '''void function sortBy((E, E) : int order)
    int i = 1
    while i < len()
        int j = i
        while j > 0 and order(this.get(j - 1), this.get(j)) > 0
            E before = this.get(j - 1)
            E after = this.get(j)
            E a = byVal before
            E b = byVal after
            this.set(j, a)
            this.set(j - 1, b)
            j = j - 1
        i = i + 1
''',
}


def missing_text(written: set, element: str) -> str:
    """The Fusion text of every List method the class doesn't write, for its element type."""
    return '\n'.join(re.sub(r'\bE\b', element, text) for name, text in METHODS.items() if name not in written)
