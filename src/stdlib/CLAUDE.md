# src/stdlib/ - Fusion's own library modules, written in Fusion

A file here is added to a program by the compiler when the program needs it - nothing to import. The folders are the
namespace Fusion (reserved for these - D.210) and its modules: `Fusion/Currency/` is module Fusion.Currency (57.5).
ASCII only (Rule 2): a character past ASCII is written as a `\uXXXX` escape.

| File | What it is |
|---|---|
| `Fusion/Currency/Currency.fusion` | The Currency module - `Fusion.Currency` (Task 47.2b, D.186): every active ISO 4217 currency (its places and its symbol, at most 4 bytes), and money's rules as statics - divide (`m / n`), split / splitBy (parts that add up), percent, round / roundWith / settle, convert (the developer's rate - never fetched), format. Added by `src/semantic/currency.py` when a program uses money |
