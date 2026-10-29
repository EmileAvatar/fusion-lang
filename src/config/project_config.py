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

from .settings_files import (SettingsFileError, convert, create_default_file, find_in_folder,
                             format_of, read_settings, read_template, FORMAT_FILES)


CONFIG_FILENAME = "fusion.toml"

DEFAULT_TAB_WIDTH = 4
DEFAULT_ALLOW_MIXED = True
DEFAULT_SAFETY_MODE = "safe"
DEFAULT_BACKEND = "c"

# Identifiers are ASCII-only by default to block homoglyph attacks (Task 19.6) - a project
# that wants non-English identifiers opts in explicitly.
DEFAULT_ALLOW_UNICODE_IDENTIFIERS = False

# "strict" is referenced by files/fusion-language-spec.md (e.g. Weak<T> causing a compile
# error in strict mode) but not enforced by any pass yet - accepted here so a project can
# already declare its intent, same status as the Unique/Shared/Weak keywords.
# safe (default); strict: every warning is an error; unsafe: the whole project may take direct
# control (memory, assembly, devices - Task 32.0, user 2026-10-28). "normal" is the old "safe"
VALID_SAFETY_MODES = ("safe", "strict", "unsafe")

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
# string_warn_length is only a guideline (a longer string is kept in full, with a warning).
# The hard limit moved to [strings] max_length in Task 18.3.4b.
DEFAULT_STRING_WARN_LENGTH = 64

# [strings] (Task 18.3.2b, user decision 2026-10-09): text is Unicode stored as UTF-8 by
# default; "ascii" (English only, one byte per character) is for very small or legacy
# devices. utf-16 / utf-32 are named for the future but not implemented yet.
VALID_ENCODINGS = ("utf-8", "ascii")
RESERVED_ENCODINGS = ("utf-16", "utf-32")
DEFAULT_ENCODING = "utf-8"

# [strings] max_length (Task 18.3.4b, user decisions 2026-10-09): strings grow as large as the
# machine allows ("max", the default). A project for a memory-constrained device can set a
# number; a string longer than that is always an error - never cut, because a silent cut
# causes more problems than it solves.
MAX_LENGTH_UNLIMITED = "max"


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
        hold_collections: A struct field may be a List or Map (user decision 2026-10-24: on
            by default, since it is built); False makes such a field a compile error.
    """
    max_nesting_depth: int = DEFAULT_MAX_NESTING_DEPTH
    warn_nesting_depth: int = DEFAULT_WARN_NESTING_DEPTH
    string_storage: str = DEFAULT_STRING_STORAGE
    string_mutable: bool = DEFAULT_STRING_MUTABLE
    string_warn_length: int = DEFAULT_STRING_WARN_LENGTH
    hold_collections: bool = True
    functions: bool = False   # methods inside a struct (Task 32.1; decided 2026-10-24: off)


@dataclass
class StringsConfig:
    """How text is stored (Task 18.3.2b).

    Attributes:
        encoding: "utf-8" (default - any Unicode character; len counts characters, lenb
            bytes) or "ascii" (English only; non-ASCII text is a compile error)
        max_length: The most characters any string may hold, or None for no limit ("max",
            the default) - a longer string is an error (Task 18.3.4b)
    """
    encoding: str = DEFAULT_ENCODING
    max_length: Optional[int] = None


# Standard-library layers (Task 18.5.6): each adds to the one before it
STDLIB_LAYERS = ('core', 'alloc', 'std')


@dataclass
class StdlibConfig:
    """How much of the standard library a project may use (Task 18.5.6).

    Attributes:
        layer: "std" (default - everything: console, files, arguments), "alloc" (no operating
            system: text, bytes, lists, maps, but no print or files) or "core" (no heap:
            numbers, chars, bools, arrays) - for embedded devices
    """
    layer: str = 'std'


@dataclass
class NumbersConfig:
    """How numbers convert (Task 27.2f, user decision 2026-10-17).

    Attributes:
        auto_widening: False (default) - an int used as a float must fit exactly (a float
            holds whole numbers exactly only up to 16,777,216): a written number that doesn't
            is a compile error, any other value is checked while running (PrecisionError).
            True - the int becomes a float automatically; every place it happens gets a
            warning
    """
    auto_widening: bool = False
    overflow_wrap: bool = False   # overflowWrap (Task 32.0): whole-number + - * wraps around


@dataclass
class BuildConfig:
    """What the built program does (user decision 2026-10-28).

    Attributes:
        wait_at_exit: True - the program waits for a key before its window closes, so its
            output (or an error) can be read when it was started by double-clicking - for
            development, the examples and testing, or an app that should show its details to
            the customer. False (the default) - it closes at once, as a finished app should.
            --headless and redirected input / output never wait
    """
    wait_at_exit: bool = False


@dataclass
class ConditionsConfig:
    """Numbers as conditions (Task 30.9, user decisions 2026-10-27).

    Attributes:
        numbers: "positive" (default) - in an `if` / `while` condition a number is true when
            above zero (zero and negatives false); "nonzero" - true when not zero (C, Python,
            JavaScript); "off" - a condition must be a bool. Only conditions: `bool b =
            count` is always an error
    """
    numbers: str = "positive"


CONDITION_NUMBERS = ("positive", "nonzero", "off")


@dataclass
class ModulesConfig:
    """Module settings (Task 44.1, user decision 2026-10-26).

    Attributes:
        variables: Module-level variables - state shared by a module's functions (`int count
            = 0` outside any function). Allowed by default; false makes them a compile error.
            Module-level constants are always allowed
    """
    variables: bool = True


@dataclass
class ErrorsConfig:
    """Which ways of handling errors a project uses (Task 26.5, user decision 2026-10-09:
    both on by default, both can be turned off).

    Attributes:
        returns: Go-style error returns - `T, Error function`, `return Error(...)`, capturing
            `T x, Error err = f()`
        exceptions: try / catch / finally / throw. With both off, an error nobody can
            capture still stops the program with its message
    """
    returns: bool = True
    exceptions: bool = True


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
    strings: StringsConfig = field(default_factory=StringsConfig)
    stdlib: StdlibConfig = field(default_factory=StdlibConfig)
    errors: ErrorsConfig = field(default_factory=ErrorsConfig)
    numbers: NumbersConfig = field(default_factory=NumbersConfig)
    modules: ModulesConfig = field(default_factory=ModulesConfig)
    conditions: ConditionsConfig = field(default_factory=ConditionsConfig)
    build: BuildConfig = field(default_factory=BuildConfig)
    safety_mode: str = DEFAULT_SAFETY_MODE
    max_call_depth: Optional[int] = None   # [safety] max_call_depth - None: "max" (Task 27.2c)
    backend: str = DEFAULT_BACKEND
    source_path: Optional[str] = None
    settings_format: str = "TOML"   # [project] fusionSettingFormat (Task 31)
    messages: list = field(default_factory=list)   # created / converted - main.py prints them
    warnings: list = field(default_factory=list)   # main.py prints them (errors in strict mode)


def find_config_file(source_path: str) -> Optional[str]:
    """Look for fusion.toml next to `source_path`, then in the current working directory.

    This lookup order (source file's own directory first, then cwd) matches Fusion's
    current single-file compilation model - there is no multi-file project/workspace
    concept yet, so a parent-directory walk (like git's .git or npm's package.json) would
    be solving a problem that doesn't exist yet. Revisit if/when Fusion gains a real
    multi-file project structure.
    """
    # Task 31: fusion.toml, fusion.yaml / .yml, fusion.json or fusion.ini - in each folder the
    # first of TOML, YAML, JSON, INI wins
    source_dir = os.path.dirname(os.path.abspath(source_path))
    return find_in_folder(source_dir) or find_in_folder(os.getcwd())


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

    known = {"maxNestingDepth", "warnNestingDepth", "stringStorage", "stringMutable",
             "stringWarnLength", "holdCollections", "functions"}
    if "string_max_length" in section:
        raise ProjectConfigError(
            f"{config_path}: structs.string_max_length has moved to [strings] maxLength (it now "
            f"limits every string, and defaults to \"max\" = no limit)")
    for key in section:
        if key not in known:
            raise ProjectConfigError(
                f"{config_path}: unknown setting structs.{key} (known: {sorted(known)})"
            )

    if "maxNestingDepth" in section:
        value = section["maxNestingDepth"]
        if not _is_int(value) or value < 1:
            raise ProjectConfigError(
                f"{config_path}: structs.maxNestingDepth must be an integer of at least 1 "
                f"(1 = no struct inside another struct), got {value!r}"
            )
        structs.max_nesting_depth = value
    if "warnNestingDepth" in section:
        value = section["warnNestingDepth"]
        if not _is_int(value) or value < 0:
            raise ProjectConfigError(
                f"{config_path}: structs.warnNestingDepth must be an integer of at least 0 "
                f"(0 = never warn), got {value!r}"
            )
        structs.warn_nesting_depth = value
    if "stringStorage" in section:
        value = section["stringStorage"]
        if value not in VALID_STRING_STORAGE:
            raise ProjectConfigError(
                f"{config_path}: structs.stringStorage must be one of "
                f"{list(VALID_STRING_STORAGE)}, got {value!r}"
            )
        structs.string_storage = value
    if "stringMutable" in section:
        value = section["stringMutable"]
        if not isinstance(value, bool):
            raise ProjectConfigError(
                f"{config_path}: structs.stringMutable must be a boolean, got {value!r}"
            )
        structs.string_mutable = value
    if "stringWarnLength" in section:
        value = section["stringWarnLength"]
        if not _is_int(value) or value < 0:
            raise ProjectConfigError(
                f"{config_path}: structs.stringWarnLength must be an integer of at least 0 "
                f"(0 = never warn), got {value!r}"
            )
        structs.string_warn_length = value
    if "functions" in section:
        value = section["functions"]
        if not isinstance(value, bool):
            raise ProjectConfigError(
                f"{config_path}: structs.functions must be a boolean, got {value!r}")
        structs.functions = value
    if "holdCollections" in section:
        value = section["holdCollections"]
        if not isinstance(value, bool):
            raise ProjectConfigError(
                f"{config_path}: structs.holdCollections must be a boolean, got {value!r}")
        structs.hold_collections = value
    return structs


def _load_strings_section(data: dict, config_path: str) -> StringsConfig:
    """Parse and validate the [strings] section (Task 18.3.2b)."""
    strings = StringsConfig()
    section = _require_table(data, "strings", config_path)
    known = {"encoding", "maxLength"}
    for key in section:
        if key not in known:
            raise ProjectConfigError(
                f"{config_path}: unknown setting strings.{key} (known: {sorted(known)})")
    if "maxLength" in section:
        value = section["maxLength"]
        if value == MAX_LENGTH_UNLIMITED:
            strings.max_length = None
        elif _is_int(value) and value >= 1:
            strings.max_length = value
        else:
            raise ProjectConfigError(
                f"{config_path}: strings.maxLength must be \"{MAX_LENGTH_UNLIMITED}\" (no limit) or a "
                f"positive number of characters (TOML can't calculate, so write 64 * 64 as "
                f"4096), got {value!r}")

    if "encoding" in section:
        value = section["encoding"]
        if value in RESERVED_ENCODINGS:
            raise ProjectConfigError(
                f"{config_path}: strings.encoding = {value!r} is reserved for the future, not "
                f"implemented yet - use 'utf-8' or 'ascii'")
        if value not in VALID_ENCODINGS:
            raise ProjectConfigError(
                f"{config_path}: strings.encoding must be one of {list(VALID_ENCODINGS)} "
                f"(utf-16 / utf-32 reserved), got {value!r}")
        strings.encoding = value
    return strings


def _load_stdlib_section(data: dict, config_path: str) -> StdlibConfig:
    """Parse and validate the [stdlib] section (Task 18.5.6)."""
    stdlib = StdlibConfig()
    section = _require_table(data, "stdlib", config_path)
    for key in section:
        if key != "layer":
            raise ProjectConfigError(
                f"{config_path}: unknown setting stdlib.{key} (known: ['layer'])")
    if "layer" in section:
        if section["layer"] not in STDLIB_LAYERS:
            raise ProjectConfigError(
                f"{config_path}: stdlib.layer must be one of {list(STDLIB_LAYERS)}, "
                f"got {section['layer']!r}")
        stdlib.layer = section["layer"]
    return stdlib


def _load_numbers_section(data: dict, config_path: str) -> NumbersConfig:
    """Parse and validate the [numbers] section (Task 27.2f)."""
    numbers = NumbersConfig()
    section = _require_table(data, "numbers", config_path)
    for key, value in section.items():
        if key not in ("autoWidening", "overflowWrap"):
            raise ProjectConfigError(
                f"{config_path}: unknown setting numbers.{key} (known: ['autoWidening', "
                f"'overflowWrap'])")
        if not isinstance(value, bool):
            raise ProjectConfigError(
                f"{config_path}: numbers.{key} must be true or false, got {value!r}")
        if key == "autoWidening":
            numbers.auto_widening = value
        else:
            numbers.overflow_wrap = value   # 255 + 1 in a byte: 0 instead of an OverflowError
    return numbers


def _load_modules_section(data: dict, config_path: str) -> ModulesConfig:
    """Parse and validate the [modules] section (Task 44.1)."""
    modules = ModulesConfig()
    section = _require_table(data, "modules", config_path)
    for key, value in section.items():
        if key != "variables":
            raise ProjectConfigError(
                f"{config_path}: unknown setting modules.{key} (known: ['variables'])")
        if not isinstance(value, bool):
            raise ProjectConfigError(
                f"{config_path}: modules.variables must be true or false, got {value!r}")
        modules.variables = value
    return modules


def _load_build_section(data: dict, config_path: str) -> BuildConfig:
    """Parse and validate the [build] section."""
    build = BuildConfig()
    section = _require_table(data, "build", config_path)
    for key, value in section.items():
        if key != "waitAtExit":
            raise ProjectConfigError(
                f"{config_path}: unknown setting build.{key} (known: ['waitAtExit'])")
        if not isinstance(value, bool):
            raise ProjectConfigError(
                f"{config_path}: build.waitAtExit must be true or false, got {value!r}")
        build.wait_at_exit = value
    return build


def _load_conditions_section(data: dict, config_path: str) -> ConditionsConfig:
    """Parse and validate the [conditions] section (Task 30.9)."""
    conditions = ConditionsConfig()
    section = _require_table(data, "conditions", config_path)
    for key, value in section.items():
        if key != "numbers":
            raise ProjectConfigError(
                f"{config_path}: unknown setting conditions.{key} (known: ['numbers'])")
        if value not in CONDITION_NUMBERS:
            raise ProjectConfigError(
                f"{config_path}: conditions.numbers must be one of {list(CONDITION_NUMBERS)}, "
                f"got {value!r}")
        conditions.numbers = value
    return conditions


def _load_errors_section(data: dict, config_path: str) -> ErrorsConfig:
    """Parse and validate the [errors] section (Task 26.5)."""
    errors = ErrorsConfig()
    section = _require_table(data, "errors", config_path)
    for key, value in section.items():
        if key not in ("returns", "exceptions"):
            raise ProjectConfigError(
                f"{config_path}: unknown setting errors.{key} (known: ['returns', 'exceptions'])")
        if not isinstance(value, bool):
            raise ProjectConfigError(
                f"{config_path}: errors.{key} must be true or false, got {value!r}")
        setattr(errors, key, value)
    return errors


def _canonical_names(data: dict, config_path: str) -> dict:
    """Setting names are camelCase, but read ignoring case and `_` (Task 32.0, user
    2026-10-28): `tab_width`, `tabWidth` and `TABWIDTH` are the same setting. Each known
    section and setting gets the master template's name; an unknown one keeps its own (and is
    reported by its section's checks). The same setting written twice is an error."""
    sections, settings = read_template()
    section_names = {_folded(name): name for name in sections}
    keys = {}
    for s in settings:
        keys.setdefault(s.section, {})[_folded(s.name)] = s.name
    result = {}
    for section, values in data.items():
        name = section_names.get(_folded(section), section) if isinstance(section, str) else section
        if not isinstance(values, dict):
            result[name] = values
            continue
        known = keys.get(name, {})
        out = result.setdefault(name, {})
        for key, value in values.items():
            canonical = known.get(_folded(key), key) if isinstance(key, str) else key
            if canonical in out:
                raise ProjectConfigError(
                    f"{config_path}: {name}.{canonical} is set twice (names ignore case and _)")
            out[canonical] = value
    return result


def _folded(name: str) -> str:
    return name.replace("_", "").lower()


def _load_project_section(data: dict, config_path: str) -> Optional[str]:
    """Parse and validate the [project] section (Task 31): fusionSettingFormat, the format the
    settings file should have - None when not set (the file keeps its format)."""
    section = _require_table(data, "project", config_path)
    for key in section:
        if key != "fusionSettingFormat":
            raise ProjectConfigError(
                f"{config_path}: unknown setting project.{key} (known: ['fusionSettingFormat'])")
    if "fusionSettingFormat" not in section:
        return None
    value = section["fusionSettingFormat"]
    fmt = value.upper() if isinstance(value, str) else value
    if fmt not in FORMAT_FILES:
        raise ProjectConfigError(
            f"{config_path}: project.fusionSettingFormat must be one of {list(FORMAT_FILES)}, "
            f"got {value!r}")
    return fmt


def load_project_config(source_path: str, create_missing: bool = False) -> ProjectConfig:
    """Load project configuration for compiling `source_path`.

    Returns an all-defaults ProjectConfig if no fusion.toml is found next to the source
    file or in the current working directory (see find_config_file). Raises
    ProjectConfigError if a fusion.toml is found but is malformed TOML or has an invalid
    value.
    """
    config_path = find_config_file(source_path)
    messages = []
    try:
        if config_path is None:
            if not create_missing:
                return ProjectConfig()
            # No settings file anywhere: a new fusion.toml from the master template (Task 31)
            config_path = create_default_file(os.path.dirname(os.path.abspath(source_path)))
            messages.append(f"created {os.path.basename(config_path)} - every setting at its default")
        data = read_settings(config_path)
    except SettingsFileError as e:
        raise ProjectConfigError(str(e)) from e
    data = _canonical_names(data, config_path)          # tab_width = tabWidth (Task 32.0)
    warnings = []
    wanted_format = _load_project_section(data, config_path)

    indentation = IndentationConfig()
    indent_section = _require_table(data, "indentation", config_path)
    if "tabWidth" in indent_section:
        tab_width = indent_section["tabWidth"]
        if not isinstance(tab_width, int) or isinstance(tab_width, bool) or tab_width < 1:
            raise ProjectConfigError(
                f"{config_path}: indentation.tabWidth must be a positive integer, "
                f"got {tab_width!r}"
            )
        indentation.tab_width = tab_width
    if "allowMixed" in indent_section:
        allow_mixed = indent_section["allowMixed"]
        if not isinstance(allow_mixed, bool):
            raise ProjectConfigError(
                f"{config_path}: indentation.allowMixed must be a boolean, "
                f"got {allow_mixed!r}"
            )
        indentation.allow_mixed = allow_mixed

    source = SourceConfig()
    source_section = _require_table(data, "source", config_path)
    if "allowUnicodeIdentifiers" in source_section:
        allow_unicode = source_section["allowUnicodeIdentifiers"]
        if not isinstance(allow_unicode, bool):
            raise ProjectConfigError(
                f"{config_path}: source.allowUnicodeIdentifiers must be a boolean, "
                f"got {allow_unicode!r}"
            )
        source.allow_unicode_identifiers = allow_unicode

    structs = _load_structs_section(data, config_path)
    strings = _load_strings_section(data, config_path)
    if strings.max_length is not None and structs.string_warn_length > strings.max_length:
        raise ProjectConfigError(
            f"{config_path}: structs.stringWarnLength ({structs.string_warn_length}) can't be "
            f"larger than strings.maxLength ({strings.max_length})")

    safety_mode = DEFAULT_SAFETY_MODE
    safety_section = _require_table(data, "safety", config_path)
    if "mode" in safety_section:
        mode = safety_section["mode"]
        if isinstance(mode, str):
            mode = mode.lower()
        if mode == "normal":
            mode = "safe"                     # the old name (before Task 32.0)
        if mode == "unsafe":
            # Before Task 32.0 "unsafe" made whole-number arithmetic wrap - now overflowWrap
            warnings.append(f"{config_path}: safety.mode = \"unsafe\" no longer makes "
                            f"arithmetic wrap - set [numbers] overflowWrap = true for that")
        if mode not in VALID_SAFETY_MODES:
            raise ProjectConfigError(
                f"{config_path}: safety.mode must be one of {list(VALID_SAFETY_MODES)}, "
                f"got {mode!r}"
            )
        safety_mode = mode
    # max_call_depth (Task 27.2c, user decision 2026-10-17): "max" (the default) - endless
    # recursion is caught by stack use alone; a number also counts calls, for
    # memory-constrained devices (tuned by profiling)
    max_call_depth = None
    if "maxCallDepth" in safety_section:
        depth = safety_section["maxCallDepth"]
        if depth != "max" and (isinstance(depth, bool) or not isinstance(depth, int) or depth < 1):
            raise ProjectConfigError(
                f"{config_path}: safety.maxCallDepth must be \"max\" or a whole number of 1 or "
                f"more, got {depth!r}")
        max_call_depth = None if depth == "max" else depth
    for key in safety_section:
        if key not in ("mode", "maxCallDepth"):
            raise ProjectConfigError(
                f"{config_path}: unknown setting safety.{key} (known: ['mode', 'maxCallDepth'])")

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

    config = ProjectConfig(
        indentation=indentation,
        source=source,
        structs=structs,
        strings=strings,
        stdlib=_load_stdlib_section(data, config_path),
        errors=_load_errors_section(data, config_path),
        modules=_load_modules_section(data, config_path),
        conditions=_load_conditions_section(data, config_path),
        build=_load_build_section(data, config_path),
        numbers=_load_numbers_section(data, config_path),
        safety_mode=safety_mode,
        max_call_depth=max_call_depth,
        backend=backend,
        source_path=config_path,
        settings_format=wanted_format or format_of(config_path),
        messages=messages,
        warnings=warnings,
    )
    if wanted_format is not None and wanted_format != format_of(config_path):
        # fusionSettingFormat names another format: write the settings in it, keep the old
        # file as a backup - only one settings file is active (Task 31)
        try:
            new_path = convert(config_path, data, wanted_format)
        except (SettingsFileError, OSError) as e:
            raise ProjectConfigError(f"Could not change {config_path} to {wanted_format}: {e}") from e
        messages.append(f"now in {os.path.basename(new_path)} (fusionSettingFormat = "
                        f"{wanted_format}); the old file is kept as "
                        f"{os.path.basename(config_path)}.bak")
        config.source_path = new_path
    return config
