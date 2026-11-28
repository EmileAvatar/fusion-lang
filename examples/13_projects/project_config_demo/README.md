# Project Configuration Demo (Task 12.12)

Demonstrates `settings.toml` actually changing compiler behavior - not part of the automated
`tests/verify_examples.py` harness (that script only globs `examples/*.fusion` directly,
non-recursively, so this subdirectory is never swept in and can safely carry a `settings.toml`
without affecting any other example).

`mixed_indent.fusion` has one line indented with two spaces followed by a tab. With no
`settings.toml` present (or `allow_mixed = true`, the default), this only produces a warning
and the file compiles normally. With this directory's `settings.toml` (`allow_mixed = false`)
present, the exact same source file fails to compile with a clear error instead.

Try it yourself:

```
# From the repo root, with this directory's settings.toml present:
python main.py examples/13_projects/project_config_demo/mixed_indent.fusion
# -> Lexer exception: ...mixed_indent.fusion:2:1: error: Mixed tabs and spaces in indentation

# Move or rename settings.toml out of the way and run again:
# -> compiles successfully, printing "Lexer warning: ... Mixed tabs and spaces in
#    indentation" (lexer warnings are shown since Task 19.6 - before that they were
#    silently dropped)
```

See `files/fusion-language-spec.md`'s "Project Configuration" section (under "Build and
Compilation") for the full `settings.toml` schema, and `src/config/project_config.py` for the
implementation.
