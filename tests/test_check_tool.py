"""Tests for check.py's own tools (Task 22.8+)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import check  # noqa: E402

E_ACUTE = chr(0xE9)
EMOJI = chr(0x1F600)


def fix(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding='utf-8', newline='')
    fixed, manual = check.fix_ascii_files([path])
    return path.read_text(encoding='utf-8'), fixed, manual


# ---------------------------------------------------------------- 22.8 --fix-ascii

def test_python_string_and_comment_are_escaped(tmp_path):
    text = f"# caf{E_ACUTE}\nname = 'caf{E_ACUTE}'\n"
    new, fixed, manual = fix(tmp_path, 'a.py', text)
    assert new == "# caf\\u00e9\nname = 'caf\\u00e9'\n"
    assert new.isascii() and fixed and not manual


def test_python_character_above_ffff_uses_long_escape(tmp_path):
    new, fixed, _ = fix(tmp_path, 'a.py', f"face = '{EMOJI}'\n")
    assert new == "face = '\\U0001f600'\n" and fixed


def test_python_raw_string_is_left_for_a_manual_fix(tmp_path):
    text = f"name = r'caf{E_ACUTE}'\n"
    new, fixed, manual = fix(tmp_path, 'a.py', text)
    assert new == text and not fixed
    assert 'line(s) 1' in manual[0]


def test_python_identifier_is_left_for_a_manual_fix(tmp_path):
    text = f"caf{E_ACUTE} = 1\n"
    new, _, manual = fix(tmp_path, 'a.py', text)
    assert new == text and manual


def test_fusion_string_char_and_comment_are_escaped(tmp_path):
    text = (f'// caf{E_ACUTE}\nvoid function main()\n'
            f'    print("caf{E_ACUTE}")\n    char c = \'{E_ACUTE}\'\n')
    new, fixed, manual = fix(tmp_path, 'a.fusion', text)
    assert new.isascii() and fixed and not manual
    assert 'print("caf\\u00e9")' in new and "'\\u00e9'" in new


def test_fusion_character_above_ffff_is_left_for_a_manual_fix(tmp_path):
    # Fusion's \u takes exactly four hex digits
    text = f'void function main()\n    print("{EMOJI}")\n'
    new, fixed, manual = fix(tmp_path, 'a.fusion', text)
    assert new == text and not fixed and 'line(s) 2' in manual[0]


def test_ascii_file_is_untouched(tmp_path):
    new, fixed, manual = fix(tmp_path, 'a.py', "x = 1\n")
    assert new == "x = 1\n" and not fixed and not manual


# ---------------------------------------------------------------- 22.9 --ship, 22.10 --example

def test_ship_without_a_message_shows_usage_and_runs_nothing(capsys):
    assert check.main(['--ship']) == 2
    assert check.main(['--ship', '--claude']) == 2
    assert 'usage' in capsys.readouterr().out


def test_find_example_finds_files_and_projects():
    assert check.find_example('hello_world').name == 'hello_world.fusion'
    assert check.find_example('wordcount').parts[-2:] == ('wordcount', 'main.fusion')
    assert check.find_example('no_such_example') is None


def test_unknown_example_lists_the_examples(capsys):
    assert check.main(['--example', 'no_such_example']) == 1
    assert 'wordcount' in capsys.readouterr().out


# ---------------------------------------------------------------- 22.11 tools/patch.py

sys.path.insert(0, str(ROOT / 'tools'))
import patch  # noqa: E402


def test_patch_applies_edits_in_order(tmp_path):
    a = tmp_path / 'a.txt'
    a.write_text('one two\n', encoding='utf-8')
    assert patch.apply_edits([(str(a), 'one', '1'), (str(a), '1 two', '1 2'),
                              (str(a), '', 'three\n')]) == []
    assert a.read_text(encoding='utf-8') == '1 2\nthree\n'


def test_patch_writes_nothing_when_one_edit_fails(tmp_path):
    a, b = tmp_path / 'a.txt', tmp_path / 'b.txt'
    a.write_text('x\n', encoding='utf-8')
    b.write_text('y y\n', encoding='utf-8')
    problems = patch.apply_edits([(str(a), 'x', 'X'), (str(b), 'y', 'Y'),
                                  (str(b), 'zzz', 'Z'), (str(tmp_path / 'c'), 'q', 'Q')])
    assert len(problems) == 3
    assert 'found 2 times' in problems[0] and 'found 0 times' in problems[1]
    assert 'no such file' in problems[2]
    assert a.read_text(encoding='utf-8') == 'x\n'


def test_patch_command_reads_an_edits_file(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'a.txt').write_text('old\n', encoding='utf-8')
    (tmp_path / 'edits.py').write_text("EDITS = [('a.txt', 'old', 'new')]\n", encoding='utf-8')
    assert patch.main(['edits.py']) == 0
    assert (tmp_path / 'a.txt').read_text(encoding='utf-8') == 'new\n'
    assert '1 edit(s) applied' in capsys.readouterr().out
