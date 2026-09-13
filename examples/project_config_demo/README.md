# Project Configuration Demo (Task 12.12)

Demonstrates `fusion.toml` actually changing compiler behavior - not part of the automated
`tests/verify_examples.py` harness (that script only globs `examples/*.fusion` directly,
non-recursively, so this subdirectory is never swept in and can safely carry a `fusion.toml`
without affecting any other example).

`mixed_indent.fusion` has one line indented with two spaces followed by a tab. With no
`fusion.toml` present (or `allow_mixed = true`, the default), this only produces a warning
and the file compiles normally. With this directory's `fusion.toml` (`allow_mixed = false`)
present, the exact same source file fails to compile with a clear error instead.

Try it yourself:

```
# From the repo root, with this directory's fusion.toml present:
python main.py examples/project_config_demo/mixed_indent.fusion
# -> Lexer exception: ...mixed_indent.fusion:2:1: error: Mixed tabs and spaces in indentation

# Move or rename fusion.toml out of the way and run again:
# -> compiles successfully (warning only, not yet surfaced to stderr - a pre-existing gap,
#    unrelated to Task 12.12)
```

See `files/fusion-language-spec.md`'s "Project Configuration" section (under "Build and
Compilation") for the full `fusion.toml` schema, and `src/config/project_config.py` for the
implementation.
