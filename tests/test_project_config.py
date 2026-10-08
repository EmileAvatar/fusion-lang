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


# ============================================================
# [source] section (Task 19.6)
# ============================================================

def test_source_allow_unicode_identifiers_defaults_to_false(tmp_path):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    config = load_project_config(str(source_path))
    assert config.source.allow_unicode_identifiers is False


def test_source_allow_unicode_identifiers_opt_in(tmp_path):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text("[source]\nallow_unicode_identifiers = true\n")
    config = load_project_config(str(source_path))
    assert config.source.allow_unicode_identifiers is True


def test_source_allow_unicode_identifiers_must_be_boolean(tmp_path):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text('[source]\nallow_unicode_identifiers = "yes"\n')
    with pytest.raises(ProjectConfigError, match="allow_unicode_identifiers must be a boolean"):
        load_project_config(str(source_path))


def test_source_config_feeds_lexer(tmp_path):
    """A Unicode identifier is rejected by default but accepted once fusion.toml opts in."""
    source_text = "int caf\u00e9 = 1\n"
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text("[source]\nallow_unicode_identifiers = true\n")
    config = load_project_config(str(source_path))
    lexer = Lexer(source_text, str(source_path),
                  allow_unicode_identifiers=config.source.allow_unicode_identifiers)
    names = [t.value for t in lexer.tokenize() if t.value == "caf\u00e9"]
    assert names == ["caf\u00e9"]


# ============================================================
# [structs] (Task 18.2.1)
# ============================================================

def _load_with(tmp_path, toml_text):
    source_path = tmp_path / "hello.fusion"
    source_path.write_text("")
    (tmp_path / "fusion.toml").write_text(toml_text)
    return load_project_config(str(source_path))


def test_structs_defaults(tmp_path):
    structs = _load_with(tmp_path, "").structs
    assert structs.max_nesting_depth == 3
    assert structs.warn_nesting_depth == 3
    assert structs.string_storage == "owned"
    assert structs.string_mutable is True
    assert structs.string_warn_length == 64
    assert structs.string_max_length == 4096


def test_structs_all_keys(tmp_path):
    structs = _load_with(tmp_path, (
        "[structs]\nmax_nesting_depth = 1\nwarn_nesting_depth = 0\n"
        'string_storage = "pooled"\nstring_mutable = false\n'
        "string_warn_length = 128\nstring_max_length = 8192\n"
    )).structs
    assert (structs.max_nesting_depth, structs.warn_nesting_depth) == (1, 0)
    assert structs.string_storage == "pooled"
    assert structs.string_mutable is False
    assert (structs.string_warn_length, structs.string_max_length) == (128, 8192)


def test_structs_max_memory_means_no_limit(tmp_path):
    assert _load_with(tmp_path, '[structs]\nstring_max_length = "max memory"\n').structs.string_max_length is None


@pytest.mark.parametrize("toml_text, message", [
    ("[structs]\nmax_nesting_depth = 0\n", "max_nesting_depth must be an integer of at least 1"),
    ("[structs]\nmax_nesting_depth = true\n", "max_nesting_depth must be an integer"),
    ("[structs]\nwarn_nesting_depth = -1\n", "warn_nesting_depth must be an integer of at least 0"),
    ('[structs]\nstring_storage = "inline"\n', "string_storage must be one of"),
    ('[structs]\nstring_mutable = "no"\n', "string_mutable must be a boolean"),
    ("[structs]\nstring_warn_length = 1.5\n", "string_warn_length must be an integer"),
    ('[structs]\nstring_max_length = "64 * 64"\n', r"write 64 \* 64 as 4096"),
    ("[structs]\nstring_max_length = 0\n", "string_max_length must be a positive integer"),
    ("[structs]\nstring_warn_length = 100\nstring_max_length = 50\n", "can't be larger than"),
    ("[structs]\nstring_max_lenght = 10\n", "unknown setting structs.string_max_lenght"),
    ("structs = 5\n", r"\[structs\] must be a table"),
])
def test_structs_invalid_values_raise(tmp_path, toml_text, message):
    with pytest.raises(ProjectConfigError, match=message):
        _load_with(tmp_path, toml_text)


def test_structs_config_changes_compiler_behaviour(tmp_path):
    """The [structs] settings reach the compiler through main.py: the same program warns
    with the defaults and is cut to fit with a lower string_max_length."""
    import subprocess
    import sys
    source_file = tmp_path / "book.fusion"
    source_file.write_text(
        'struct Book\n    string title\n\n'
        'void function main()\n    Book b = Book("' + "t" * 100 + '")\n    print("{b.title}")\n',
        encoding="utf-8"
    )
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def compile_it():
        return subprocess.run(
            [sys.executable, "main.py", str(source_file)],
            cwd=repo_root, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=120
        )

    result = compile_it()
    assert result.returncode == 0, result.stderr
    assert "has 100 characters (the project's string_warn_length guideline is 64)" in result.stderr

    (tmp_path / "fusion.toml").write_text("[structs]\nstring_warn_length = 10\nstring_max_length = 20\n")
    result = compile_it()
    assert result.returncode == 0, result.stderr
    assert "cut to the project's string_max_length of 20" in result.stderr
    exe = str(source_file).replace(".fusion", ".exe" if sys.platform == "win32" else "")
    run = subprocess.run([exe], capture_output=True, text=True, timeout=30)
    assert run.stdout.strip() == "t" * 20
