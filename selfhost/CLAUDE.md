# selfhost/ - the Fusion compiler written in Fusion (Task 28)

Built by the Python compiler (`python main.py ...`). The Python compiler stays the real one
until self-hosting is fully independent (Task 35).

- `main.fusion` - the driver: `main.exe program.fusion [--tokens] [--runtime DIR]
  [--leak-check]` - writes program.c next to the source and calls GCC (28.6)
- `lexer/lexer.fusion` - source bytes -> tokens, the same tokens as the Python lexer (28.2)
- `parser/ast.fusion` - the syntax tree: enum Node, enum TypeRef (28.3)
- `parser/parser.fusion` - tokens -> tree; each function returns {node, pos} (28.3)
- `codegen/codegen.fusion` - tree -> C, checking types in the same walk (28.4 + 28.5)

Tests: tests/test_selfhost.py builds this with the Python compiler, then compares the tokens
on every example and, for each program in SLICES, what the built program prints.
Language gaps found while writing it: task/selfhost_report.md (28.8).
- `prototype/` - measurements for 28.1.2 (task/selfhost_subset.md, "28.1.2 results")
  - `lex_bytes.fusion` - pattern B over `bytes`: the source is read-only, a function returns
    one token, the caller collects them. The pattern the compiler uses
  - `lex_string.fusion` - the same over `string` characters (`text[i]`)
  - `lex_struct.fusion` - pattern A: one struct copied at every step (what not to do)

The C it writes: the settings' #defines, `#include "fusion_runtime.h"` (`runtime/`, the
run-time shared with the Python compiler - 28.1.3), then the program's own code. Build with
`gcc -I runtime ...`.

Rules for the compiler's code (from 28.1.2):
- read the source as `bytes` (`readBytes`), never index a `string` in a loop
- never return a struct holding a big list from a function called per token or node; keep
  big lists read-only parameters or the caller's local variables
