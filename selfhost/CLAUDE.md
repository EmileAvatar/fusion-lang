# selfhost/ - the Fusion compiler written in Fusion (Task 28)

Built by the Python compiler (`python main.py ...`). The Python compiler stays the real one
until self-hosting is fully independent (Task 35).

- `prototype/` - measurements for 28.1.2 (task/selfhost_subset.md, "28.1.2 results")
  - `lex_bytes.fusion` - pattern B over `bytes`: the source is read-only, a function returns
    one token, the caller collects them. The pattern the compiler uses
  - `lex_string.fusion` - the same over `string` characters (`text[i]`)
  - `lex_struct.fusion` - pattern A: one struct copied at every step (what not to do)

Rules for the compiler's code (from 28.1.2):
- read the source as `bytes` (`readBytes`), never index a `string` in a loop
- never return a struct holding a big list from a function called per token or node; keep
  big lists read-only parameters or the caller's local variables
