"""Tests for Task 31 - the project settings file in four formats.

settings.toml is the default; settings.yaml / .yml, settings.json and settings.ini are alternatives
(user, 2026-10-28). All four are read into the same settings and checked by the same rules.
In a folder TOML wins, then YAML, JSON, INI. With no settings file a settings.toml is written
from the master template (files/fusionSettings.xml). `[project] fusionSettingFormat` names the
file's format; naming another one rewrites the settings in it and keeps the old file as a
.bak, so only one is active.
"""

import sys

import pytest

from src.config import ProjectConfigError, load_project_config
from src.config.project_config import ProjectConfig
from src.config.settings_files import default_settings, read_template

SAME = {
    'settings.toml': '[indentation]\ntab_width = 2\n[strings]\nmax_length = 100\n'
                   'encoding = "ascii"\n[conditions]\nnumbers = "nonzero"\n',
    'settings.yaml': 'indentation:\n  tabWidth: 2\nstrings:\n  maxLength: 100\n'
                   '  encoding: "ascii"\nconditions:\n  numbers: "nonzero"\n',
    'settings.json': '{"indentation": {"tabWidth": 2}, "strings": {"maxLength": 100, '
                   '"encoding": "ascii"}, "conditions": {"numbers": "nonzero"}}',
    'settings.ini': '; legacy settings\n[indentation]\ntab_width = 2\n[strings]\nmax_length = 100\n'
                  'encoding = ascii\n[conditions]\nnumbers = "nonzero"\n',
}


def load(tmp_path, name, text):
    (tmp_path / 'app.fusion').write_text('')
    if name:
        (tmp_path / name).write_text(text)
    return load_project_config(str(tmp_path / 'app.fusion'))


@pytest.mark.parametrize('name', list(SAME))
def test_the_same_settings_in_every_format(tmp_path, name):
    config = load(tmp_path, name, SAME[name])
    assert (config.indentation.tab_width, config.strings.max_length, config.strings.encoding,
            config.conditions.numbers) == (2, 100, 'ascii', 'nonzero')
    assert config.settings_format == {'settings.toml': 'TOML', 'settings.yaml': 'YAML',
                                      'settings.json': 'JSON', 'settings.ini': 'INI'}[name]


def test_yml_is_yaml_too(tmp_path):
    assert load(tmp_path, 'settings.yml', 'indentation:\n  tabWidth: 3\n').indentation.tab_width == 3


def test_ini_values_become_bools_numbers_and_text(tmp_path):
    config = load(tmp_path, 'settings.ini', '[indentation]\nallow_mixed = FALSE\n'
                                          '[errors]\nexceptions = false\n[stdlib]\nlayer = core\n')
    assert config.indentation.allow_mixed is False and config.errors.exceptions is False
    assert config.stdlib.layer == 'core'


def test_ini_yes_is_not_a_bool(tmp_path):
    with pytest.raises(ProjectConfigError, match='allowMixed must be a boolean'):
        load(tmp_path, 'settings.ini', '[indentation]\nallow_mixed = yes\n')


def test_yaml_unquoted_off_is_caught(tmp_path):
    # the "Norway problem": YAML reads a bare off / no as false - the checks catch it
    with pytest.raises(ProjectConfigError, match='conditions.numbers must be one of'):
        load(tmp_path, 'settings.yaml', 'conditions:\n  numbers: off\n')


def test_broken_files_name_the_file(tmp_path):
    with pytest.raises(ProjectConfigError, match=r'Invalid JSON in .*settings\.json'):
        load(tmp_path, 'settings.json', '{"indentation": ')


def test_without_pyyaml_a_clear_message(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, 'yaml', None)
    with pytest.raises(ProjectConfigError, match='needs the PyYAML package - pip install pyyaml'):
        load(tmp_path, 'settings.yaml', 'indentation:\n  tabWidth: 3\n')


def test_toml_wins_when_there_are_two(tmp_path):
    (tmp_path / 'settings.json').write_text('{"indentation": {"tabWidth": 8}}')
    config = load(tmp_path, 'settings.toml', '[indentation]\ntab_width = 2\n')
    assert config.indentation.tab_width == 2 and config.source_path.endswith('settings.toml')


def test_no_settings_file_is_every_default_and_nothing_is_written(tmp_path):
    # D.227 (Task 58.2b): none means the defaults - no file is written, not even by main.py
    import os
    import subprocess
    config = load(tmp_path, None, None)
    assert config.source_path is None and config == ProjectConfig()
    (tmp_path / 'app.fusion').write_text('void function main()\n    print("hi")\n')
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    built = subprocess.run([sys.executable, os.path.join(root, 'main.py'), str(tmp_path / 'app.fusion')],
                           capture_output=True, text=True, cwd=tmp_path)
    assert built.returncode == 0, built.stderr
    assert sorted(p.name for p in tmp_path.iterdir() if 'settings' in p.name or p.suffix == '.toml') == []


def test_a_fusion_toml_is_not_read(tmp_path):
    # D.229: settings.toml is the name - fusion.toml is the reference in the source, never a program's settings
    config = load(tmp_path, 'fusion.toml', '[indentation]\ntabWidth = 2\n')
    assert config.source_path is None and config.indentation.tab_width == ProjectConfig().indentation.tab_width


@pytest.mark.parametrize('fmt, name', [('YAML', 'settings.yaml'), ('JSON', 'settings.json'),
                                       ('INI', 'settings.ini')])
def test_changing_the_format_rewrites_and_keeps_a_backup(tmp_path, fmt, name):
    config = load(tmp_path, 'settings.toml',
                  f'[project]\nfusionSettingFormat = "{fmt}"\n[indentation]\ntab_width = 2\n')
    assert config.source_path.endswith(name)
    assert (tmp_path / 'settings.toml.bak').exists() and not (tmp_path / 'settings.toml').exists()
    again = load_project_config(str(tmp_path / 'app.fusion'))
    assert again.indentation.tab_width == 2 and again.settings_format == fmt and not again.messages


def test_a_wrong_format_name(tmp_path):
    with pytest.raises(ProjectConfigError, match='fusionSettingFormat must be one of'):
        load(tmp_path, 'settings.toml', '[project]\nfusionSettingFormat = "XML"\n')


def test_every_template_value_is_accepted_and_reserved_ones_are_not(tmp_path):
    """The master template and the compiler agree (files/fusionSettings.xml)."""
    _, settings = read_template()
    for s in settings:
        for value in s.values:
            text = f'[{s.section}]\n{s.name} = "{value}"\n'
            load(tmp_path, 'settings.toml', text)
        for value in s.reserved:
            if (s.section, s.name) == ('structs', 'stringStorage'):
                continue      # "pooled" is refused later, by the struct checks (Task 29.4)
            with pytest.raises(ProjectConfigError):
                load(tmp_path, 'settings.toml', f'[{s.section}]\n{s.name} = "{value}"\n')
    data, _ = default_settings()
    assert set(data) == {'project', 'indentation', 'source', 'structs', 'strings', 'stdlib',
                         'errors', 'numbers', 'modules', 'libraries', 'visibility', 'interfaces', 'generics', 'ranges', 'enums', 'memory', 'collections', 'arrays', 'conditions', 'build',
                         'safety', 'backend'}


PROGRAM = 'void function main()\n    print("x")\n'


def test_structs_hold_collections_can_be_turned_off(tmp_path):
    from src.config import StructsConfig
    from tests.test_structs import errors_of
    assert load(tmp_path, 'settings.toml', '').structs.hold_collections is True
    config = load(tmp_path, 'settings.toml', '[structs]\nhold_collections = false\n')
    assert config.structs.hold_collections is False
    message = errors_of('struct Team\n    List<string> members\n    Map<string, int> score\n\n'
                        + PROGRAM, StructsConfig(hold_collections=False))
    assert "Field 'members' of struct 'Team' is a List" in message
    assert "Field 'score' of struct 'Team' is a Map" in message


def test_wait_at_exit_is_off_by_default_and_a_define_when_on(tmp_path):
    from src.codegen import CCodeGenerator
    from src.lexer import Lexer
    from src.parser.parser import Parser
    assert load(tmp_path, 'settings.toml', '').build.wait_at_exit is False
    assert load(tmp_path, 'settings.toml', '[build]\nwait_at_exit = true\n').build.wait_at_exit

    def c_code(**settings):
        program = Parser(Lexer(PROGRAM, 't').tokenize()).parse_program()
        return CCodeGenerator(**settings).generate(program)
    assert '#define FUSION_WAIT_AT_EXIT' not in c_code()
    assert '#define FUSION_WAIT_AT_EXIT 1' in c_code(wait_at_exit=True)


# ---------------------------------------------------------------- Task 32.0

@pytest.mark.parametrize('written', ['tabWidth', 'tab_width', 'TABWIDTH', 'Tab_Width'])
def test_names_ignore_case_and_underscores(tmp_path, written):
    assert load(tmp_path, 'settings.toml', f'[Indentation]\n{written} = 3\n').indentation.tab_width == 3


def test_the_same_setting_twice_is_an_error(tmp_path):
    with pytest.raises(ProjectConfigError, match='tabWidth is set twice'):
        load(tmp_path, 'settings.toml', '[indentation]\ntab_width = 3\ntabWidth = 2\n')


def test_safety_modes_and_the_old_names(tmp_path):
    assert ProjectConfig().safety_mode == 'safe'
    assert load(tmp_path, 'settings.toml', '[safety]\nmode = "normal"\n').safety_mode == 'safe'
    assert load(tmp_path, 'settings.toml', '[safety]\nmode = "strict"\n').safety_mode == 'strict'
    config = load(tmp_path, 'settings.toml', '[safety]\nmode = "unsafe"\n')
    assert config.safety_mode == 'unsafe'
    assert any('no longer makes arithmetic wrap' in w for w in config.warnings)


def test_overflow_wrap_setting(tmp_path):
    from tests.test_end_to_end import compile_and_run
    assert load(tmp_path, 'settings.toml', '').numbers.overflow_wrap is False
    assert load(tmp_path, 'settings.toml', '[numbers]\noverflowWrap = true\n').numbers.overflow_wrap
    program = 'void function main()\n    int n = 2147483647\n    n = n + 1\n    print("{n}")\n'
    code, out, err = compile_and_run(program, overflow_wrap=True)
    assert code == 0 and out.strip() == '-2147483648'
    code, out, err = compile_and_run(program)
    assert code != 0 and "doesn't fit in an int" in err      # an OverflowError by default


def test_strict_mode_turns_warnings_into_errors(tmp_path):
    import os
    import subprocess
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    (tmp_path / 'app.fusion').write_text('template string unused = "x"\n\n'
                                         'void function main()\n    print("hi")\n')
    (tmp_path / 'settings.toml').write_text('[safety]\nmode = "strict"\n')
    strict = subprocess.run([sys.executable, os.path.join(root, 'main.py'),
                             str(tmp_path / 'app.fusion')],
                            capture_output=True, text=True, cwd=tmp_path)
    assert strict.returncode == 1 and 'errors in strict mode' in strict.stderr
    (tmp_path / 'settings.toml').write_text('[safety]\nmode = "safe"\n')
    safe = subprocess.run([sys.executable, os.path.join(root, 'main.py'),
                           str(tmp_path / 'app.fusion')],
                          capture_output=True, text=True, cwd=tmp_path)
    assert safe.returncode == 0, safe.stderr
