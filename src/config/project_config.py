"""Project-level configuration for the Fusion compiler (Task 12.12).

Fusion's core concept is per-project configurability (memory model, safety level, backend,
block style - see CLAUDE.md "Core Concept"), but until now the compiler hardcoded its lexer
settings directly (src/lexer/lexer.py used to construct
IndentationTracker(tab_width=4, allow_mixed=True) with no way to override it). This module
reads an optional `fusion.toml` file and produces a ProjectConfig the rest of the compiler
reads instead of hardcoding values.

v1 scope (decided 2026-09-13): only the [indentation] section is actually wired to real
behavior (the lexer's tab_width/allow_mixed). Since then [source] (Task 19.6) reaches the
lexer and [structs] (Task 18.2) reaches the semantic analyzer. [safety] and [backend] are parsed and
validated here but not yet enforced anywhere else in the compiler - reserved for future
work, the same "recognized, not yet implemented" status as the Unique/Shared/Weak keywords
(see Task 12.7). See files/fusion-language-spec.md's "Project Configuration" section for
the full schema and the rationale behind each decision (format, lookup order, v1 scope).

A missing fusion.toml is not an error - it just means every setting uses its default,
matching the compiler's previous hardcoded behavior exactly (existing single-file examples
and tests are unaffected). A *present but malformed* fusion.toml IS an error - deliberately
not silently falling back to defaults, so a typo in the config doesn't silently compile with
different settings than the user intended.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

import tomllib


CONFIG_FILENAME = "fusion.toml"

DEFAULT_TAB_WIDTH = 4
DEFAULT_ALLOW_MIXED = True
DEFAULT_SAFETY_MODE = "normal"
DEFAULT_BACKEND = "c"

# Identifiers are ASCII-only by default to block homoglyph attacks (Task 19.6) - a project
# that wants non-English identifiers opts in explicitly.
DEFAULT_ALLOW_UNICODE_IDENTIFIERS = False

# "strict" is referenced by files/fusion-language-spec.md (e.g. Weak<T> causing a compile
# error in strict mode) but not enforced by any pass yet - accepted here so a project can
# already declare its intent, same status as the Unique/Shared/Weak keywords.
VALID_SAFETY_MODES = ("normal", "strict")

# "llvm" is Task 11's planned backend - not implemented yet, so not accepted as a value
# until that lands. Keeping the set explicit (rather than accepting anything) means a typo
# like "C" or "clang" fails fast instead of silently doing nothing.
VALID_BACKENDS = ("c",)

# [structs] (Task 18.2, user decisions 2026-10-08). Nesting depth counts levels of structs: a
# struct of plain fields is depth 1, a struct holding one of those is depth 2, and so on.
# Defaults: depth 3 compiles with a warning, depth 4 is an error - a project can lower the
# maximum (1 = no struct inside a struct) or raise it.
DEFAULT_MAX_NESTING_DEPTH = 3
DEFAULT_WARN_NESTING_DEPTH = 3
# A string field holds its own value (not pooled) and can be changed, by default. "pooled" is
# accepted here so a project can declare its intent, but compiling with it is an error until
# Task 17 builds string pooling.
VALID_STRING_STORAGE = ("owned", "pooled")
DEFAULT_STRING_STORAGE = "owned"
DEFAULT_STRING_MUTABLE = True
# string_warn_length is only a guideline (a longer string is kept in full, with a warning);
# string_max_length is the one hard cut-off. MAX_MEMORY means no cut-off at all - unsafe.
DEFAULT_STRING_WARN_LENGTH = 64
DEFAULT_STRING_MAX_LENGTH = 4096
MAX_MEMORY = "max memory"


class ProjectConfigError(Exception):
    """Raised when fusion.toml exists but is malformed or contains an invalid value."""


@dataclass
class IndentationConfig:
    """Mirrors src/lexer/indentation.py's IndentationTracker constructor parameters."""
    tab_width: int = DEFAULT_TAB_WIDTH
    allow_mixed: bool = DEFAULT_ALLOW_MIXED


@dataclass
class SourceConfig:
    """Source-text rules passed to the lexer (Task 19.6)."""
    allow_unicode_identifiers: bool = DEFAULT_ALLOW_UNICODE_IDENTIFIERS


@dataclass
class StructsConfig:
    """Struct rules passed to the semantic analyzer (Task 18.2).

    Attributes:
        max_nesting_depth: Deepest allowed struct nesting (1 = no nested structs).
        warn_nesting_depth: Warn when a struct reaches this depth (0 = never warn).
        string_storage: "owned" (each struct holds its own string value) or "pooled"
            (reserved - Task 17).
        string_mutable: False makes a string field unchangeable after construction.
        string_warn_length: Warn when a string field holds more characters than this
            (0 = never warn). The string is still kept in full.
        string_max_length: Hard cut-off for a string field, or None for no limit (the
            unsafe "max memory" setting).
    """
    max_nesting_depth: int = DEFAULT_MAX_NESTING_DEPTH
    warn_nesting_depth: int = DEFAULT_WARN_NESTING_DEPTH
    string_storage: str = DEFAULT_STRING_STORAGE
    string_mutable: bool = DEFAULT_STRING_MUTABLE
    string_warn_length: int = DEFAULT_STRING_WARN_LENGTH
    string_max_length: Optional[int] = DEFAULT_STRING_MAX_LENGTH


@dataclass
class ProjectConfig:
    """Resolved project configuration - either loaded from fusion.toml or all defaults.

    Attributes:
        indentation: Wired to the lexer (Task 12.12 v1 scope).
        source: Wired to the lexer - Unicode identifier opt-in (Task 19.6).
        structs: Wired to the semantic analyzer - nesting depth and string field rules
            (Task 18.2).
        safety_mode: Reserved for future strict-mode enforcement - not yet read by any pass.
        backend: Reserved for Task 11's LLVM backend - not yet read by any pass (only "c"
            exists today, so there is only one legal value right now).
        source_path: Path to the fusion.toml that was loaded, or None if no file was found
            and every field above is a default.
    """
    indentation: IndentationConfig = field(default_factory=IndentationConfig)
    source: SourceConfig = field(default_factory=SourceConfig)
    structs: StructsConfig = field(default_factory=StructsConfig)
    safety_mode: str = DEFAULT_SAFETY_MODE
    backend: str = DEFAULT_BACKEND
    source_path: Optional[str] = None


def find_config_file(source_path: str) -> Optional[str]:
    """Look for fusion.toml next to `source_path`, then in the current working directory.

    This lookup order (source file's own directory first, then cwd) matches Fusion's
    current single-file compilation model - there is no multi-file project/workspace
    concept yet, so a parent-directory walk (like git's .git or npm's package.json) would
    be solving a problem that doesn't exist yet. Revisit if/when Fusion gains a real
    multi-file project structure.
    """
    source_dir = os.path.dirname(os.path.abspath(source_path))
    candidate = os.path.join(source_dir, CONFIG_FILENAME)
    if os.path.isfile(candidate):
        return candidate

    cwd_candidate = os.path.join(os.getcwd(), CONFIG_FILENAME)
    if os.path.isfile(cwd_candidate):
        return cwd_candidate

    return None


def _require_table(data: dict, key: str, config_path: str) -> dict:
    section = data.get(key, {})
    if not isinstance(section, dict):
        raise ProjectConfigError(f"{config_path}: [{key}] must be a table")
    return section


def _is_int(value) -> bool:
    # bool is a subclass of int in Python - `true` must not pass as the number 1
    return isinstance(value, int) and not isinstance(value, bool)


def _load_structs_section(data: dict, config_path: str) -> StructsConfig:
    """Parse and validate the [structs] section (Task 18.2)."""
    structs = StructsConfig()
    section = _require_table(data, "structs", config_path)

    known = {"max_nesting_depth", "warn_nesting_depth", "string_storage", "string_mutable",
             "string_warn_length", "string_max_length"}
    for key in section:
        if key not in known:
            raise ProjectConfigError(
                f"{config_path}: unknown setting structs.{key} (known: {sorted(known)})"
            )

    if "max_nesting_depth" in section:
        value = section["max_nesting_depth"]
        if not _is_int(value) or value < 1:
            raise ProjectConfigError(
                f"{config_path}: structs.max_nesting_depth must be an integer of at least 1 "
                f"(1 = no struct inside another struct), got {value!r}"
            )
        structs.max_nesting_depth = value
    if "warn_nesting_depth" in section:
        value = section["warn_nesting_depth"]
        if not _is_int(value) or value < 0:
            raise ProjectConfigError(
                f"{config_path}: structs.warn_nesting_depth must be an integer of at least 0 "
                f"(0 = never warn), got {value!r}"
            )
        structs.warn_nesting_depth = value
    if "string_storage" in section:
        value = section["string_storage"]
        if value not in VALID_STRING_STORAGE:
            raise ProjectConfigError(
                f"{config_path}: structs.string_storage must be one of "
                f"{list(VALID_STRING_STORAGE)}, got {value!r}"
            )
        structs.string_storage = value
    if "string_mutable" in section:
        value = section["string_mutable"]
        if not isinstance(value, bool):
            raise ProjectConfigError(
                f"{config_path}: structs.string_mutable must be a boolean, got {value!r}"
            )
        structs.string_mutable = value
    if "string_warn_length" in section:
        value = section["string_warn_length"]
        if not _is_int(value) or value < 0:
            raise ProjectConfigError(
                f"{config_path}: structs.string_warn_length must be an integer of at least 0 "
                f"(0 = never warn), got {value!r}"
            )
        structs.string_warn_length = value
    if "string_max_length" in section:
        value = section["string_max_length"]
        if value == MAX_MEMORY:
            structs.string_max_length = None
        elif _is_int(value) and value >= 1:
            structs.string_max_length = value
        else:
            raise ProjectConfigError(
                f"{config_path}: structs.string_max_length must be a positive integer (TOML "
                f"can't calculate, so write 64 * 64 as 4096) or \"{MAX_MEMORY}\", got {value!r}"
            )

    if structs.string_max_length is not None and structs.string_warn_length > structs.string_max_length:
        raise ProjectConfigError(
            f"{config_path}: structs.string_warn_length ({structs.string_warn_length}) can't be "
            f"larger than structs.string_max_length ({structs.string_max_length})"
        )
    return structs


def load_project_config(source_path: str) -> ProjectConfig:
    """Load project configuration for compiling `source_path`.

    Returns an all-defaults ProjectConfig if no fusion.toml is found next to the source
    file or in the current working directory (see find_config_file). Raises
    ProjectConfigError if a fusion.toml is found but is malformed TOML or has an invalid
    value.
    """
    config_path = find_config_file(source_path)
    if config_path is None:
        return ProjectConfig()

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ProjectConfigError(f"Invalid TOML in {config_path}: {e}") from e
    except OSError as e:
        raise ProjectConfigError(f"Could not read {config_path}: {e}") from e

    indentation = IndentationConfig()
    indent_section = _require_table(data, "indentation", config_path)
    if "tab_width" in indent_section:
        tab_width = indent_section["tab_width"]
        if not isinstance(tab_width, int) or isinstance(tab_width, bool) or tab_width < 1:
            raise ProjectConfigError(
                f"{config_path}: indentation.tab_width must be a positive integer, "
                f"got {tab_width!r}"
            )
        indentation.tab_width = tab_width
    if "allow_mixed" in indent_section:
        allow_mixed = indent_section["allow_mixed"]
        if not isinstance(allow_mixed, bool):
            raise ProjectConfigError(
                f"{config_path}: indentation.allow_mixed must be a boolean, "
                f"got {allow_mixed!r}"
            )
        indentation.allow_mixed = allow_mixed

    source = SourceConfig()
    source_section = _require_table(data, "source", config_path)
    if "allow_unicode_identifiers" in source_section:
        allow_unicode = source_section["allow_unicode_identifiers"]
        if not isinstance(allow_unicode, bool):
            raise ProjectConfigError(
                f"{config_path}: source.allow_unicode_identifiers must be a boolean, "
                f"got {allow_unicode!r}"
            )
        source.allow_unicode_identifiers = allow_unicode

    structs = _load_structs_section(data, config_path)

    safety_mode = DEFAULT_SAFETY_MODE
    safety_section = _require_table(data, "safety", config_path)
    if "mode" in safety_section:
        mode = safety_section["mode"]
        if mode not in VALID_SAFETY_MODES:
            raise ProjectConfigError(
                f"{config_path}: safety.mode must be one of {list(VALID_SAFETY_MODES)}, "
                f"got {mode!r}"
            )
        safety_mode = mode

    backend = DEFAULT_BACKEND
    backend_section = _require_table(data, "backend", config_path)
    if "target" in backend_section:
        target = backend_section["target"]
        if target not in VALID_BACKENDS:
            raise ProjectConfigError(
                f"{config_path}: backend.target must be one of {list(VALID_BACKENDS)} "
                f"('llvm' is reserved for Task 11, not implemented yet), got {target!r}"
            )
        backend = target

    return ProjectConfig(
        indentation=indentation,
        source=source,
        structs=structs,
        safety_mode=safety_mode,
        backend=backend,
        source_path=config_path,
    )
