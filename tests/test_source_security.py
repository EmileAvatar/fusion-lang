"""Tests for source-level attack defenses (Task 19.6).

Covers: rejection of invisible/bidirectional control characters (Trojan Source,
CVE-2021-42574), \\uXXXX escapes, ASCII-only identifiers by default with a Unicode opt-in,
mixed-script and compatibility-character rejection, char literal decoding, safe C
emission of control characters, and '%' escaping in printf format strings (CWE-134).

This file is deliberately pure ASCII: every non-ASCII character below is written as a Python
\\u escape, so the test source itself never contains the characters it tests for.
"""

import os
import subprocess
import sys
import json

import pytest

from src.lexer import Lexer
from src.lexer.token import TokenType
from src.lexer.source_security import (
    DISALLOWED_CODEPOINTS, check_identifier, find_disallowed_character
)
from src.parser.parser import Parser
from src.semantic import SemanticAnalyzer
from src.codegen import CCodeGenerator
from src.codegen.c_runtime import escape_c_text, escape_printf_text
from src.utils.errors import LexerError
from tests.test_end_to_end import compile_and_run


RLO = "\u202e"          # RIGHT-TO-LEFT OVERRIDE
ZWJ = "\u200d"          # ZERO WIDTH JOINER
BOM = "\ufeff"          # BYTE ORDER MARK
CYRILLIC_A = "\u0430"   # looks identical to Latin 'a'
E_ACUTE = "\u00e9"      # e with acute accent (Latin script)
CJK = "\u4e2d\u6587"    # Chinese characters
FULLWIDTH_FOO = "\uff46\uff4f\uff4f"  # fullwidth 'foo'


def lex(source: str, allow_unicode: bool = False):
    return Lexer(source, "test.fusion", allow_unicode_identifiers=allow_unicode).tokenize()


def generate_c(source: str) -> str:
    tokens = lex(source)
    ast = Parser(tokens).parse_program()
    analyzer = SemanticAnalyzer()
    assert analyzer.analyze(ast), analyzer.get_errors()
    return CCodeGenerator().generate(ast)


# ============================================================
# 19.6.1 - Invisible and bidirectional control characters
# ============================================================

@pytest.mark.parametrize("code_point", sorted(DISALLOWED_CODEPOINTS))
def test_every_disallowed_code_point_rejected_in_code(code_point):
    source = f"int x = 1{chr(code_point)}\n"
    with pytest.raises(LexerError):
        lex(source)


def test_bidi_in_comment_rejected():
    with pytest.raises(LexerError, match="Trojan Source"):
        lex(f"int x = 1  // looks harmless {RLO} here\n")


def test_bidi_in_string_rejected():
    with pytest.raises(LexerError, match="U\\+202E"):
        lex(f'string s = "text {RLO} more"\n')


def test_zero_width_inside_identifier_rejected():
    with pytest.raises(LexerError, match="U\\+200D"):
        lex(f"int ad{ZWJ}min = 1\n")


def test_error_reports_exact_location():
    source = "int a = 1\nint b = 2  // x" + RLO + "\n"
    with pytest.raises(LexerError) as info:
        lex(source)
    # Line 2; the RLO follows "int b = 2  // x" (15 characters) -> column 16
    assert info.value.location.line == 2
    assert info.value.location.column == 16


def test_find_disallowed_character_clean_source():
    assert find_disallowed_character("int x = 1 // plain text\n") is None


def test_byte_order_mark_allowed_at_start_of_file():
    tokens = lex(BOM + "int x = 1\n")
    assert tokens[0].value == "int"


def test_byte_order_mark_rejected_elsewhere():
    with pytest.raises(LexerError, match="U\\+FEFF"):
        lex("int x = 1\n" + BOM + "int y = 2\n")


def test_ordinary_unicode_still_allowed_in_strings_and_comments():
    tokens = lex(f'string s = "caf{E_ACUTE} {CJK}"  // {CJK} comment\n')
    string_tokens = [t for t in tokens if t.type == TokenType.STRING_LIT]
    assert string_tokens
    parts = json.loads(string_tokens[0].value)
    assert parts[0][1] == f"caf{E_ACUTE} {CJK}"


# ============================================================
# 19.6.2 - \uXXXX escapes
# ============================================================

def test_unicode_escape_in_string():
    tokens = lex('string s = "A\\u0042C"\n')
    parts = json.loads([t for t in tokens if t.type == TokenType.STRING_LIT][0].value)
    assert parts[0][1] == "ABC"


def test_unicode_escape_can_express_invisible_character_visibly():
    tokens = lex('string s = "a\\u200Db"\n')
    parts = json.loads([t for t in tokens if t.type == TokenType.STRING_LIT][0].value)
    assert parts[0][1] == "a" + ZWJ + "b"


@pytest.mark.parametrize("bad", ['"\\u12"', '"\\uZZZZ"', '"\\u"'])
def test_malformed_unicode_escape_rejected(bad):
    with pytest.raises(LexerError, match="\\\\u escape"):
        lex(f"string s = {bad}\n")


def test_surrogate_unicode_escape_rejected():
    with pytest.raises(LexerError, match="surrogate"):
        lex('string s = "\\uD800"\n')


def test_char_literal_unicode_escape_ascii():
    tokens = lex("char c = '\\u0041'\n")
    assert any(t.type == TokenType.CHAR_LIT for t in tokens)


def test_char_literal_non_ascii_escape_allowed():
    """A char holds any Unicode character since Task 18.3.2b (ascii encoding still rejects
    it - in semantic analysis, see tests/test_strings.py)."""
    assert any(t.value == "'\\u00E9'" for t in lex("char c = '\\u00E9'\n"))


def test_char_literal_raw_non_ascii_allowed():
    assert any(t.value == f"'{E_ACUTE}'" for t in lex(f"char c = '{E_ACUTE}'\n"))


def test_char_literal_surrogate_rejected():
    with pytest.raises(LexerError, match="surrogate"):
        lex("char c = '\\uD800'\n")


# ============================================================
# 19.6.3 - Confusable (homoglyph) identifiers
# ============================================================

def test_non_ascii_identifier_rejected_by_default():
    with pytest.raises(LexerError, match="allow_unicode_identifiers"):
        lex(f"int {CYRILLIC_A}ge = 5\n")


def test_non_ascii_identifier_in_interpolation_rejected_by_default():
    with pytest.raises(LexerError, match="non-ASCII"):
        lex(f'string s = "value: {{{CYRILLIC_A}ge}}"\n')


def test_unicode_identifier_allowed_with_opt_in():
    tokens = lex(f"int caf{E_ACUTE} = 1\nint {CJK} = 2\n", allow_unicode=True)
    names = [t.value for t in tokens if t.type == TokenType.IDENTIFIER]
    assert f"caf{E_ACUTE}" in names
    assert CJK in names


def test_mixed_script_identifier_rejected_even_with_opt_in():
    with pytest.raises(LexerError, match="look-alike scripts"):
        lex(f"int {CYRILLIC_A}ge = 5\n", allow_unicode=True)


def test_compatibility_characters_rejected_even_with_opt_in():
    with pytest.raises(LexerError, match="compatibility characters"):
        lex(f"int {FULLWIDTH_FOO} = 1\n", allow_unicode=True)


def test_check_identifier_ascii_passes():
    assert check_identifier("player_health2", allow_unicode=False) is None


def test_unicode_digits_are_not_numbers():
    # Arabic-Indic digit three - str.isdigit() is True for it, but it must not start a number
    with pytest.raises(LexerError):
        lex("int x = \u0663\n")


# ============================================================
# Regression - the two attacks verified to compile before Task 19.6
# ============================================================

def test_regression_homoglyph_variables_rejected():
    source = (
        "void function main()\n"
        f"    int {CYRILLIC_A}ge = 5\n"
        "    int age = 7\n"
        '    print("{age}")\n'
        "End function\n"
    )
    with pytest.raises(LexerError, match="non-ASCII"):
        lex(source)


def test_regression_trojan_source_rejected():
    source = (
        "void function main()\n"
        f"    // comment with a bidi override {RLO} here\n"
        f'    print("bidi in string {RLO} here")\n'
        "End function\n"
    )
    with pytest.raises(LexerError, match="Trojan Source"):
        lex(source)


# ============================================================
# Char literal decoding + safe C emission
# ============================================================

def test_char_literal_compiles_to_correct_c():
    c_code = generate_c("void function main()\n    char c = 'a'\nEnd function\n")
    assert "char c = 'a';" in c_code


def test_char_literal_end_to_end_prints_the_character():
    # Before Task 19.6 this printed a quote mark: the literal reached C as '\'a\''
    exit_code, stdout, stderr = compile_and_run(
        "void function main()\n"
        "    char c = 'a'\n"
        '    print("{c}")\n'
        "End function\n"
    )
    assert exit_code == 0, stderr
    assert stdout.strip() == "a"


def test_escape_c_text_writes_control_characters_as_octal():
    assert escape_c_text("a" + ZWJ + "b", '"') == "a\\342\\200\\215b"


def test_escape_c_text_keeps_printable_unicode_and_handles_quotes():
    assert escape_c_text(f'caf{E_ACUTE} "q"', '"') == f'caf{E_ACUTE} \\"q\\"'
    assert escape_c_text("it's", "'") == "it\\'s"


def test_invisible_character_from_escape_is_never_raw_in_generated_c():
    c_code = generate_c('void function main()\n    print("a\\u200Db")\nEnd function\n')
    assert ZWJ not in c_code
    assert "\\342\\200\\215" in c_code


# ============================================================
# Format-string safety - '%' in printed text (CWE-134, Task 18.3 bug fix)
# ============================================================

def test_escape_printf_text_doubles_percent():
    assert escape_printf_text("100% done") == "100%% done"
    assert escape_printf_text("%%") == "%%%%"
    assert escape_printf_text("no percent") == "no percent"


def test_percent_in_plain_print_is_escaped_in_c():
    c_code = generate_c('void function main()\n    print("100% done")\nEnd function\n')
    assert 'printf("100%% done\\n");' in c_code


def test_percent_in_interpolated_text_escaped_but_specifier_kept():
    c_code = generate_c(
        'void function main()\n    int x = 7\n    print("{x}% %s")\nEnd function\n'
    )
    assert 'printf("%d%% %%s\\n", x);' in c_code


def test_percent_end_to_end_prints_literally():
    # Before the fix, "100% done" printed "100 1134633984one": printf read "% d" as a
    # directive and pulled garbage off the stack
    exit_code, stdout, stderr = compile_and_run(
        "void function main()\n"
        "    int x = 7\n"
        '    print("Progress: 100% done")\n'
        '    print("{x}% of 100%, %d %s %n literal")\n'
        "End function\n"
    )
    assert exit_code == 0, stderr
    assert stdout.splitlines() == ["Progress: 100% done", "7% of 100%, %d %s %n literal"]


# ============================================================
# 19.6.4 - Lexer warnings are surfaced by main.py (Task 15.7)
# ============================================================

def test_main_prints_lexer_warnings(tmp_path):
    # Two spaces then a tab: mixed indentation is a warning (allow_mixed defaults to true).
    # Before Task 19.6 main.py collected this warning and then dropped it silently.
    source_file = tmp_path / "mixed.fusion"
    source_file.write_text(
        'void function main()\n  \tprint("hi")\nEnd function\n', encoding="utf-8"
    )
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run(
        [sys.executable, "main.py", str(source_file)],
        cwd=repo_root, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=60
    )
    assert "Lexer warning" in result.stderr
    assert "Mixed tabs and spaces" in result.stderr
