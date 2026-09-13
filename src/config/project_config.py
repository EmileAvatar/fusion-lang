"""Project-level configuration for the Fusion compiler (Task 12.12).

Fusion's core concept is per-project configurability (memory model, safety level, backend,
block style - see CLAUDE.md "Core Concept"), but until now the compiler hardcoded its lexer
settings directly (src/lexer/lexer.py used to construct
IndentationTracker(tab_width=4, allow_mixed=True) with no way to override it). This module
reads an optional `fusion.toml` file and produces a ProjectConfig the rest of the compiler
reads instead of hardcoding values.

v1 scope (decided 2026-09-13): only the [indentation] section is actually wired to real
behavior (the lexer's tab_width/allow_mixed). [safety] and [backend] are parsed and
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

# "strict" is referenced by files/fusion-language-spec.md (e.g. Weak<T> causing a compile
# error in strict mode) but not enforced by any pass yet - accepted here so a project can
# already declare its intent, same status as the Unique/Shared/Weak keywords.
VALID_SAFETY_MODES = ("normal", "strict")

# "llvm" is Task 11's planned backend - not implemented yet, so not accepted as a value
# until that lands. Keeping the set explicit (rather than accepting anything) means a typo
# like "C" or "clang" fails fast instead of silently doing nothing.
VALID_BACKENDS = ("c",)


class ProjectConfigError(Exception):
    """Raised when fusion.toml exists but is malformed or contains an invalid value."""


@dataclass
class IndentationConfig:
    """Mirrors src/lexer/indentation.py's IndentationTracker constructor parameters."""
    tab_width: int = DEFAULT_TAB_WIDTH
    allow_mixed: bool = DEFAULT_ALLOW_MIXED


@dataclass
class ProjectConfig:
    """Resolved project configuration - either loaded from fusion.toml or all defaults.

    Attributes:
        indentation: Wired to the lexer (Task 12.12 v1 scope).
        safety_mode: Reserved for future strict-mode enforcement - not yet read by any pass.
        backend: Reserved for Task 11's LLVM backend - not yet read by any pass (only "c"
            exists today, so there is only one legal value right now).
        source_path: Path to the fusion.toml that was loaded, or None if no file was found
            and every field above is a default.
    """
    indentation: IndentationConfig = field(default_factory=IndentationConfig)
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
        safety_mode=safety_mode,
        backend=backend,
        source_path=config_path,
    )
