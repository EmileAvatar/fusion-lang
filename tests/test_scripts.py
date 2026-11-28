"""Tests for Task 58 - script mode (D.221-D.229, files/spec/170-Build.md - the truth table there).

58.1 (D.222, D.225): a file without `main` holds statements at the top - run in order, as its main; its variables are
the script's (every function sees them); functions, types and imports as in any file; `args` - its arguments; a `#!`
first line skipped; a file with both `main` and statements at the top an error.
"""

import os
import subprocess
import sys

import pytest

from src.parser.parser import ParserError
from tests.test_modules import errors, parse_file, write_project

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_and_run(tmp_path, files: dict, args=()) -> tuple:
    """main.py on main.fusion, then the program with args: (exit code, its output)."""
    for name, text in files.items():
        write_project(str(tmp_path), {name: text})
    built = subprocess.run([sys.executable, os.path.join(REPO, 'main.py'), str(tmp_path / 'main.fusion')], capture_output=True, text=True, encoding='utf-8')
    assert built.returncode == 0, built.stdout + built.stderr
    ran = subprocess.run([str(tmp_path / 'main.exe'), *args], capture_output=True, text=True, encoding='utf-8')
    return ran.returncode, ran.stdout


TIDY = ('int removed = 0\n'
        '\n'
        'void function remove(string name)\n'
        '    removed = removed + 1              // a function sees the script\'s variable\n'
        '\n'
        'struct Item\n'
        '    string name\n'
        '\n'
        'print("start")\n'
        'for name in args\n'
        '    remove(name)\n'
        'int later = removed * 10               // declared after a statement: set here, in order\n'
        'Item it = Item("box")\n'
        'print("{removed} removed, later {later}, {it.name}")\n')


@pytest.mark.parametrize('args, expected', [
    (['a', 'b', 'c'], 'start\n3 removed, later 30, box\n'),
    ([], 'start\n0 removed, later 0, box\n'),                 # none passed - args empty (D.225)
])
def test_a_script(tmp_path, args, expected):
    assert build_and_run(tmp_path, {'main.fusion': TIDY}, args) == (0, expected)


def test_the_hash_bang_line_is_skipped(tmp_path):
    source = '#!/usr/bin/env fusion run\nprint("hi")\nint x = 1 + undefinedName\n'
    found = errors(str(tmp_path), {'main.fusion': source})
    assert "main.fusion:3:" in found                           # the lines keep their numbers


def test_the_exit_code(tmp_path):
    source = 'if args.length == 0\n    print("give a name")\n    exit(2)\nprint("ok")\n'
    assert build_and_run(tmp_path, {'main.fusion': source}) == (2, 'give a name\n')
    assert build_and_run(tmp_path, {'main.fusion': source}, ['x']) == (0, 'ok\n')


def test_types_functions_and_imports_in_a_script(tmp_path):
    files = {'shapes/s.fusion': 'public int function square(int n) : n * n\n',
             'main.fusion': ('import shapes\n\n'
                             'enum Size { SMALL, BIG }\n\n'
                             'interface Named\n    string function name()\n\n'
                             'class Box implements Named\n    public string function name() : "box"\n\n'
                             'Box b = Box()\n'
                             'Size s = Size.BIG\n'
                             'print(format("{@1} {@2} {@3}", b.name(), s, shapes.square(4)))\n'
                             'if s == Size.BIG\n'
                             '    print("big")\n')}
    assert build_and_run(tmp_path, files) == (0, 'box BIG 16\nbig\n')


@pytest.mark.parametrize('source', [
    'x = 1\n',                         # an assignment
    'xs[0] = 1\n',
    'print("x")\n',                    # a call
    'money.show(5)\n',
    'outer: for x in 0...1\n    break outer\n',
    'while false\n    print("x")\n',
    'match 1\n    case 1: print("x")\n    else: print("y")\n',
])
def test_these_are_statements_at_the_top(source):
    assert parse_file('int x = 0\nint[3] xs\n' + source, 'main.fusion').script


@pytest.mark.parametrize('source', [
    'int x = 5\n', 'Box b\n', 'money.Price p\n', 'List<int> xs = [1]\n', 'Point[3] pts\n',
    'Point[2] function corners() : [Point(0, 0), Point(5, 5)]\n', 'Point function origin() : Point(0, 0)\n',
    'Ship, Error function load() : Ship()\n', 'void function main()\n    print("x")\n',
])
def test_these_are_declarations(source):
    assert not parse_file(source, 'main.fusion').script


def test_main_and_statements_at_the_top_is_an_error():
    with pytest.raises(ParserError, match="A file with a main function can't have statements at the top too"):
        parse_file('print("a")\n\nvoid function main()\n    print("b")\n', 'main.fusion')


def test_return_at_the_top_is_still_an_error():
    with pytest.raises(ParserError, match="Unexpected token 'return' at top level"):
        parse_file('return 42\n', 'main.fusion')


def test_statements_at_the_top_of_a_module_are_an_error(tmp_path):
    files = {'tools/t.fusion': 'print("loaded")\n', 'main.fusion': 'import tools\n\nprint("x")\n'}
    assert "tools/t.fusion has statements at the top - only the file that starts the program (a script) runs " \
           "them" in errors(str(tmp_path), files)


# 58.2 (D.224, D.226, D.228): a Fusion.Settings block, first in the file - instead of the settings file

LIMITED = ('int n = 0\n'
           'try\n'
           '    while true\n'
           '        n = n + 1\n'
           'catch LoopLimitError e\n'
           '    print("stopped at {n}")\n')


@pytest.mark.parametrize('block', [
    'Fusion.Settings {\n    maxIterations = 50\n}\n',                    # braces
    'Fusion.Settings\n    maxIterations = 50\n',                          # indented
    'Fusion.Settings\n{\n    safety.maxIterations = 50   // with its section\n}\n',
    '#!/usr/bin/env fusion run\n// settings first\n\nFusion.Settings {\n    maxIterations = 50\n}\n',
])
def test_a_settings_block(tmp_path, block):
    assert build_and_run(tmp_path, {'main.fusion': block + '\n' + LIMITED}) == (0, 'stopped at 50\n')


def test_the_block_is_used_instead_of_the_settings_file(tmp_path):
    files = {'settings.toml': '[safety]\nmaxIterations = 5\n',
             'main.fusion': 'Fusion.Settings {\n    maxIterations = 50\n}\n\n' + LIMITED}
    assert build_and_run(tmp_path, files) == (0, 'stopped at 50\n')


def test_a_block_in_a_program_with_main(tmp_path):
    body = ''.join('    ' + line + '\n' for line in LIMITED.splitlines())
    files = {'main.fusion': 'Fusion.Settings {\n    maxIterations = 7\n}\n\nvoid function main()\n' + body}
    assert build_and_run(tmp_path, files) == (0, 'stopped at 7\n')


def test_a_block_in_an_imported_file_is_ignored_with_a_warning(tmp_path):
    from src.modules import load_program
    from src.semantic import SemanticAnalyzer
    files = {'tools/t.fusion': 'Fusion.Settings {\n    maxIterations = 3\n}\n\npublic int function two() : 2\n',
             'main.fusion': 'import tools\n\nprint(format("{@1}", tools.two()))\n'}
    main_file = write_project(str(tmp_path), files)
    with open(main_file, encoding='utf-8') as f:
        program = parse_file(f.read(), main_file)
    program, problems = load_program(main_file, program, parse_file)
    assert problems == []
    analyzer = SemanticAnalyzer()
    assert analyzer.analyze(program)
    assert any("tools/t.fusion: its Fusion.Settings block is ignored - the program starts in main.fusion" in str(w)
               for w in analyzer.get_warnings())


@pytest.mark.parametrize('block, message', [
    ('Fusion.Settings {\n    noSuchThing = 1\n}\n', "no setting named 'noSuchThing'"),
    ('Fusion.Settings {\n    nope.maxIterations = 1\n}\n', "no settings section 'nope'"),
    ('Fusion.Settings {\n    maxIterations = lots\n}\n', "can't read the value of 'maxIterations'"),
    ('Fusion.Settings {\n    maxIterations\n}\n', "expected 'name = value' in Fusion.Settings"),
    ('Fusion.Settings {\n    maxIterations = 5\n', "Fusion.Settings has no closing '}'"),
    ('Fusion.Settings {\n    maxIterations = -5\n}\n', "safety.maxIterations must be a whole number"),
])
def test_settings_block_errors(tmp_path, block, message):
    from src.config import ProjectConfigError, load_project_config
    (tmp_path / 'main.fusion').write_text(block + 'print("x")\n', encoding='utf-8')
    with pytest.raises(ProjectConfigError, match=message):
        load_project_config(str(tmp_path / 'main.fusion'))


def test_a_name_in_two_sections_needs_its_section(monkeypatch):
    from src.config import settings_files
    from src.config.settings_block import read_settings_block
    sections, settings = settings_files.read_template()
    twin = next(s for s in settings if s.name == 'rounding')          # [numbers] rounding
    fake = settings + [type(twin)(**{**twin.__dict__, 'section': 'money'})]
    monkeypatch.setattr(settings_files, 'read_template', lambda: (sections, fake))
    with pytest.raises(ValueError, match=r"'rounding' is in \[numbers\] and \[money\] - write numbers.rounding or "
                                         r"money.rounding"):
        read_settings_block('Fusion.Settings {\n    rounding = "halfUp"\n}\n', 'main.fusion')


def test_the_block_must_be_first():
    with pytest.raises(ParserError, match="Fusion.Settings must be first in the file"):
        parse_file('print("x")\nFusion.Settings {\n    maxIterations = 5\n}\n', 'main.fusion')


# 58.3 (D.221, D.223): python main.py run tidy.fusion [arguments] - built once into the cache folder, run at once

def run_cmd(tmp_path, script, *args, cache=None):
    env = dict(os.environ, FUSION_CACHE=str(cache if cache is not None else tmp_path / 'cache'))
    done = subprocess.run([sys.executable, os.path.join(REPO, 'main.py'), 'run', str(script), *args],
                          capture_output=True, text=True, encoding='utf-8', env=env)
    return done.returncode, done.stdout, done.stderr


def kept_builds(tmp_path) -> int:
    cache = tmp_path / 'cache'
    return sum(1 for _ in cache.rglob('build.json')) if cache.exists() else 0


def test_run_builds_once_then_runs_the_kept_program(tmp_path):
    script = tmp_path / 'tidy.fusion'
    script.write_text(TIDY, encoding='utf-8')
    assert run_cmd(tmp_path, script, 'a', 'b') == (0, 'start\n2 removed, later 20, box\n', '')   # only its output
    record = next((tmp_path / 'cache').rglob('build.json'))
    built_at = record.stat().st_mtime_ns
    assert run_cmd(tmp_path, script, 'a') == (0, 'start\n1 removed, later 10, box\n', '')
    assert record.stat().st_mtime_ns == built_at                           # not built again
    assert sorted(p.name for p in tmp_path.iterdir()) == ['cache', 'tidy.fusion']     # nothing next to it


def test_a_change_builds_again(tmp_path):
    script = tmp_path / 'tidy.fusion'
    script.write_text('print("one")\n', encoding='utf-8')
    assert run_cmd(tmp_path, script)[1] == 'one\n'
    script.write_text('print("two")\n', encoding='utf-8')                  # the script
    assert run_cmd(tmp_path, script)[1] == 'two\n'
    (tmp_path / 'words').mkdir()
    (tmp_path / 'words' / 'w.fusion').write_text('public string function word() : "three"\n', encoding='utf-8')
    script.write_text('import words\n\nprint(words.word())\n', encoding='utf-8')
    assert run_cmd(tmp_path, script)[1] == 'three\n'
    (tmp_path / 'words' / 'w.fusion').write_text('public string function word() : "four"\n', encoding='utf-8')
    assert run_cmd(tmp_path, script)[1] == 'four\n'                         # an imported file
    script.write_text(LIMITED, encoding='utf-8')
    (tmp_path / 'settings.toml').write_text('[safety]\nmaxIterations = 9\n', encoding='utf-8')
    assert run_cmd(tmp_path, script)[1] == 'stopped at 9\n'                 # a settings file appeared
    (tmp_path / 'settings.toml').write_text('[safety]\nmaxIterations = 4\n', encoding='utf-8')
    assert run_cmd(tmp_path, script)[1] == 'stopped at 4\n'                 # the settings changed
    assert kept_builds(tmp_path) == 1                                       # one kept build per script


def test_the_exit_code_is_passed_back(tmp_path):
    script = tmp_path / 'check.fusion'
    script.write_text('if args.length == 0\n    exit(3)\nprint("ok")\n', encoding='utf-8')
    assert run_cmd(tmp_path, script)[0] == 3
    assert run_cmd(tmp_path, script, 'x')[:2] == (0, 'ok\n')


def test_a_failing_build_shows_its_messages(tmp_path):
    script = tmp_path / 'bad.fusion'
    script.write_text('print(undefinedName)\n', encoding='utf-8')
    code, out, err = run_cmd(tmp_path, script)
    assert code == 1 and out == '' and 'undefinedName' in err


def test_where_the_cache_cant_be_written_next_to_the_script(tmp_path):
    blocked = tmp_path / 'not-a-folder'
    blocked.write_text('a file where the cache folder would be', encoding='utf-8')
    script = tmp_path / 'tidy.fusion'
    script.write_text('print("hi")\n', encoding='utf-8')
    assert run_cmd(tmp_path, script, cache=blocked)[:2] == (0, 'hi\n')
    assert any((tmp_path / '.fusion-cache').rglob('build.json'))


def test_run_needs_a_script(tmp_path):
    code, _, err = run_cmd(tmp_path, tmp_path / 'missing.fusion')
    assert code == 1 and 'File not found' in err
