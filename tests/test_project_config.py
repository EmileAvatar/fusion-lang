"""Unit tests for project-level configuration (Task 12.12).

Covers src/config/project_config.py: fusion.toml discovery, parsing, validation, and the
default-when-absent behavior. Uses pytest's tmp_path fixture for filesystem isolation so
these tests never touch a real fusion.toml that might exist in the repo or cwd.
"""

import os
import pytest

from src.config import (
    ProjectConfig,
    IndentationConfig,
    ProjectConfigError,
    find_config_file,
    load_project_config,
)
from src.lexer.lexer import Lexer


# ============================================================
# Defaults (no fusion.toml present)
# ============================================================

def test_no_config_file_returns_defaults(tmp_path):
    """Missing fusion.toml must produce exactly the compiler's old hardcoded defaults."""
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("void function main()\n    print(\"hi\")\n")

    config = load_project_config(str(source_path))

    assert config.indentation.tab_width == 4
    assert config.indentation.allow_mixed is True
    assert config.safety_mode == "normal"
    assert config.backend == "c"
    assert config.source_path is None


def test_find_config_file_returns_none_when_absent(tmp_path):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    assert find_config_file(str(source_path)) is None


# ============================================================
# Discovery / lookup order
# ============================================================

def test_find_config_file_next_to_source(tmp_path):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    config_path = tmp_path / "fusion.toml"
    config_path.write_text("[indentation]\ntab_width = 2\n")

    found = find_config_file(str(source_path))

    assert found == str(config_path)


def test_source_directory_takes_priority_over_cwd(tmp_path, monkeypatch):
    """If fusion.toml exists both next to the source file and in cwd, the source file's
    own directory wins - it's the more specific location."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    source_path = project_dir / "hello.fusion"
    source_path.write_text("")
    near_source = project_dir / "fusion.toml"
    near_source.write_text("[indentation]\ntab_width = 2\n")

    other_dir = tmp_path / "cwd"
    other_dir.mkdir()
    (other_dir / "fusion.toml").write_text("[indentation]\ntab_width = 8\n")
    monkeypatch.chdir(other_dir)

    found = find_config_file(str(source_path))

    assert found == str(near_source)


def test_falls_back_to_cwd(tmp_path, monkeypatch):
    source_path = tmp_path / "src_dir" / "hello.fusion"
    source_path.parent.mkdir()
    source_path.write_text("")

    cwd_dir = tmp_path / "cwd_dir"
    cwd_dir.mkdir()
    cwd_config = cwd_dir / "fusion.toml"
    cwd_config.write_text("[indentation]\ntab_width = 8\n")
    monkeypatch.chdir(cwd_dir)

    found = find_config_file(str(source_path))

    assert found == str(cwd_config)


# ============================================================
# Valid configuration
# ============================================================

def test_valid_indentation_overrides(tmp_path):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text(
        "[indentation]\ntab_width = 2\nallow_mixed = false\n"
    )

    config = load_project_config(str(source_path))

    assert config.indentation.tab_width == 2
    assert config.indentation.allow_mixed is False
    assert config.source_path == str(tmp_path / "fusion.toml")


def test_valid_safety_mode_strict(tmp_path):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text('[safety]\nmode = "strict"\n')

    config = load_project_config(str(source_path))

    assert config.safety_mode == "strict"


def test_valid_backend_c(tmp_path):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text('[backend]\ntarget = "c"\n')

    config = load_project_config(str(source_path))

    assert config.backend == "c"


def test_partial_config_keeps_other_defaults(tmp_path):
    """Setting only tab_width must not disturb allow_mixed/safety_mode/backend defaults."""
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text("[indentation]\ntab_width = 3\n")

    config = load_project_config(str(source_path))

    assert config.indentation.tab_width == 3
    assert config.indentation.allow_mixed is True
    assert config.safety_mode == "normal"
    assert config.backend == "c"


def test_empty_config_file_is_all_defaults(tmp_path):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text("")

    config = load_project_config(str(source_path))

    assert config == ProjectConfig(
        indentation=IndentationConfig(),
        safety_mode="normal",
        backend="c",
        source_path=str(tmp_path / "fusion.toml"),
    )


# ============================================================
# Invalid configuration - must raise ProjectConfigError, never silently fall back
# ============================================================

def test_malformed_toml_raises(tmp_path):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text("this is not [valid toml")

    with pytest.raises(ProjectConfigError, match="Invalid TOML"):
        load_project_config(str(source_path))


def test_indentation_not_a_table_raises(tmp_path):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text("indentation = 4\n")

    with pytest.raises(ProjectConfigError, match=r"\[indentation\] must be a table"):
        load_project_config(str(source_path))


@pytest.mark.parametrize("bad_value", ["0", "-1", "true", '"4"', "4.5"])
def test_invalid_tab_width_raises(tmp_path, bad_value):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text(f"[indentation]\ntab_width = {bad_value}\n")

    with pytest.raises(ProjectConfigError, match="tab_width must be a positive integer"):
        load_project_config(str(source_path))


def test_invalid_allow_mixed_raises(tmp_path):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text('[indentation]\nallow_mixed = "yes"\n')

    with pytest.raises(ProjectConfigError, match="allow_mixed must be a boolean"):
        load_project_config(str(source_path))


def test_invalid_safety_mode_raises(tmp_path):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text('[safety]\nmode = "yolo"\n')

    with pytest.raises(ProjectConfigError, match="safety.mode must be one of"):
        load_project_config(str(source_path))


def test_llvm_backend_rejected_with_helpful_message(tmp_path):
    """llvm is a real future value (Task 11), so the error should say so rather than just
    listing it as unknown."""
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text('[backend]\ntarget = "llvm"\n')

    with pytest.raises(ProjectConfigError, match="reserved for Task 11"):
        load_project_config(str(source_path))


def test_unknown_backend_rejected(tmp_path):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text('[backend]\ntarget = "clang"\n')

    with pytest.raises(ProjectConfigError, match="backend.target must be one of"):
        load_project_config(str(source_path))


# ============================================================
# Lexer wiring (the actual gap this task closes)
# ============================================================

def test_lexer_defaults_match_old_hardcoded_behavior():
    lexer = Lexer("void function main()\n    print(\"hi\")\n")
    assert lexer.indent_tracker.tab_width == 4
    assert lexer.indent_tracker.allow_mixed is True


def test_lexer_accepts_config_overrides():
    lexer = Lexer("source", "<test>", tab_width=2, allow_mixed=False)
    assert lexer.indent_tracker.tab_width == 2
    assert lexer.indent_tracker.allow_mixed is False


def test_project_config_feeds_lexer_end_to_end(tmp_path):
    """Load a real fusion.toml and confirm its values reach the lexer's indent tracker -
    the concrete gap Task 12.12 exists to close, exercised end to end rather than just at
    each layer in isolation."""
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("void function main()\n    print(\"hi\")\n")
    (tmp_path / "fusion.toml").write_text("[indentation]\ntab_width = 2\n")

    config = load_project_config(str(source_path))
    lexer = Lexer(
        source_path.read_text(),
        str(source_path),
        tab_width=config.indentation.tab_width,
        allow_mixed=config.indentation.allow_mixed,
    )

    assert lexer.indent_tracker.tab_width == 2
