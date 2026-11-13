[< 033 Currency](033-Currency.md) | [Index](index.md) | [035 HIDL >](035-HIDL.md) <!-- nav -->

# 034 Data Formats

**Status:** planned - FEATURES 43.2 (MOD.009); replaces the compiler's Python readers once it is written in Fusion

## Data Formats Module: JSON, XML, TOML, YAML, INI, MD

**Status:** Idea (user, 2026-11-01) - in fusionlib, not the core (files/FEATURES.md 43.2,
Decisions.md MOD.009 / D.098).

**1. Read into memory, change, save.** Each format is loaded into an in-memory document
that is easy to read and change, then saved again:

- formats: JSON, XML, TOML, YAML, INI, MD (Markdown); CSV and more later
- `load(path)` / `save(path)`, and from or to a string
- recovering from minor syntax mistakes where that is safe (from 43.2)
- once the compiler is written in Fusion, it replaces the compiler's Python readers for
  `fusion.toml` / `.yaml` / `.json` / `.ini` (Task 31)

**2. A document written in the code.** JSON and XML may be written directly in the source,
inside a multi-line string (`"""..."""`, Later in files/FEATURES.md, STR.008), marked with its
format - the user's example:

```fusion
(FILE_LANG.XML)"""
<settings>
    <port>8080</port>
</settings>
""".save("settings.xml")
```

This makes working with embedded XML (or JSON) easy when it's needed: no escaping of quotes,
and the value is a document, not plain text.

**Open questions (for when it is designed):**
- **The marker's form.** The example reads like a cast (D.082 - casts are written in front).
  To settle: the name `FILE_LANG` and its values (an enum of formats?), and whether a short
  form is wanted as well.
- **Checked when compiling.** The compiler could check the embedded document's syntax, so a
  broken XML or JSON literal is a compile error, not an error while running (fits D.086:
  a compile error first).
- **Values inside it.** If `{name}` interpolation is allowed inside, each value must be
  escaped for its format (no XML / JSON injection - "never trust code").
- **Which formats in the code.** JSON and XML first (the user's choice); TOML, YAML, INI and
  MD can still be loaded and saved.

[< 033 Currency](033-Currency.md) | [Index](index.md) | [035 HIDL >](035-HIDL.md) <!-- nav -->
