"""Tests for Task 31 - the project settings file in four formats.

fusion.toml is the default; fusion.yaml / .yml, fusion.json and fusion.ini are alternatives
(user, 2026-10-28). All four are read into the same settings and checked by the same rules.
In a folder TOML wins, then YAML, JSON, INI. With no settings file a fusion.toml is written
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
    'fusion.toml': '[indentation]\ntab_width = 2\n[strings]\nmax_length = 100\n'
                   'encoding = "ascii"\n[conditions]\nnumbers = "nonzero"\n',
    'fusion.yaml': 'indentation:\n  tab_width: 2\nstrings:\n  max_length: 100\n'
                   '  encoding: "ascii"\nconditions:\n  numbers: "nonzero"\n',
    'fusion.json': '{"indentation": {"tab_width": 2}, "strings": {"max_length": 100, '
                   '"encoding": "ascii"}, "conditions": {"numbers": "nonzero"}}',
    'fusion.ini': '; legacy settings\n[indentation]\ntab_width = 2\n[strings]\nmax_length = 100\n'
                  'encoding = ascii\n[conditions]\nnumbers = "nonzero"\n',
}


def load(tmp_path, name, text, create=False):
    (tmp_path / 'app.fusion').write_text('')
    if name:
        (tmp_path / name).write_text(text)
    return load_project_config(str(tmp_path / 'app.fusion'), create_missing=create)


@pytest.mark.parametrize('name', list(SAME))
def test_the_same_settings_in_every_format(tmp_path, name):
    config = load(tmp_path, name, SAME[name])
    assert (config.indentation.tab_width, config.strings.max_length, config.strings.encoding,
            config.conditions.numbers) == (2, 100, 'ascii', 'nonzero')
    assert config.settings_format == {'fusion.toml': 'TOML', 'fusion.yaml': 'YAML',
                                      'fusion.json': 'JSON', 'fusion.ini': 'INI'}[name]


def test_yml_is_yaml_too(tmp_path):
    assert load(tmp_path, 'fusion.yml', 'indentation:\n  tab_width: 3\n').indentation.tab_width == 3


def test_ini_values_become_bools_numbers_and_text(tmp_path):
    config = load(tmp_path, 'fusion.ini', '[indentation]\nallow_mixed = FALSE\n'
                                          '[errors]\nexceptions = false\n[stdlib]\nlayer = core\n')
    assert config.indentation.allow_mixed is False and config.errors.exceptions is False
    assert config.stdlib.layer == 'core'


def test_ini_yes_is_not_a_bool(tmp_path):
    with pytest.raises(ProjectConfigError, match='allow_mixed must be a boolean'):
        load(tmp_path, 'fusion.ini', '[indentation]\nallow_mixed = yes\n')


def test_yaml_unquoted_off_is_caught(tmp_path):
    # the "Norway problem": YAML reads a bare off / no as false - the checks catch it
    with pytest.raises(ProjectConfigError, match='conditions.numbers must be one of'):
        load(tmp_path, 'fusion.yaml', 'conditions:\n  numbers: off\n')


def test_broken_files_name_the_file(tmp_path):
    with pytest.raises(ProjectConfigError, match=r'Invalid JSON in .*fusion\.json'):
        load(tmp_path, 'fusion.json', '{"indentation": ')


def test_without_pyyaml_a_clear_message(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, 'yaml', None)
    with pytest.raises(ProjectConfigError, match='needs the PyYAML package - pip install pyyaml'):
        load(tmp_path, 'fusion.yaml', 'indentation:\n  tab_width: 3\n')


def test_toml_wins_when_there_are_two(tmp_path):
    (tmp_path / 'fusion.json').write_text('{"indentation": {"tab_width": 8}}')
    config = load(tmp_path, 'fusion.toml', '[indentation]\ntab_width = 2\n')
    assert config.indentation.tab_width == 2 and config.source_path.endswith('fusion.toml')


def test_no_file_creates_fusion_toml_with_every_default(tmp_path):
    config = load(tmp_path, None, None, create=True)
    assert (tmp_path / 'fusion.toml').exists() and config.messages
    again = load_project_config(str(tmp_path / 'app.fusion'))
    for name in ('indentation', 'source', 'structs', 'strings', 'stdlib', 'errors', 'numbers',
                 'modules', 'conditions', 'build', 'safety_mode', 'max_call_depth', 'backend'):
        assert getattr(again, name) == getattr(ProjectConfig(), name), name


def test_without_create_nothing_is_written(tmp_path):
    config = load(tmp_path, None, None)
    assert config.source_path is None and not (tmp_path / 'fusion.toml').exists()


@pytest.mark.parametrize('fmt, name', [('YAML', 'fusion.yaml'), ('JSON', 'fusion.json'),
                                       ('INI', 'fusion.ini')])
def test_changing_the_format_rewrites_and_keeps_a_backup(tmp_path, fmt, name):
    config = load(tmp_path, 'fusion.toml',
                  f'[project]\nfusionSettingFormat = "{fmt}"\n[indentation]\ntab_width = 2\n')
    assert config.source_path.endswith(name)
    assert (tmp_path / 'fusion.toml.bak').exists() and not (tmp_path / 'fusion.toml').exists()
    again = load_project_config(str(tmp_path / 'app.fusion'))
    assert again.indentation.tab_width == 2 and again.settings_format == fmt and not again.messages


def test_a_wrong_format_name(tmp_path):
    with pytest.raises(ProjectConfigError, match='fusionSettingFormat must be one of'):
        load(tmp_path, 'fusion.toml', '[project]\nfusionSettingFormat = "XML"\n')


def test_every_template_value_is_accepted_and_reserved_ones_are_not(tmp_path):
    """The master template and the compiler agree (files/fusionSettings.xml)."""
    _, settings = read_template()
    for s in settings:
        for value in s.values:
            text = f'[{s.section}]\n{s.name} = "{value}"\n'
            load(tmp_path, 'fusion.toml', text)
        for value in s.reserved:
            if (s.section, s.name) == ('structs', 'string_storage'):
                continue      # "pooled" is refused later, by the struct checks (Task 29.4)
            with pytest.raises(ProjectConfigError):
                load(tmp_path, 'fusion.toml', f'[{s.section}]\n{s.name} = "{value}"\n')
    data, _ = default_settings()
    assert set(data) == {'project', 'indentation', 'source', 'structs', 'strings', 'stdlib',
                         'errors', 'numbers', 'modules', 'conditions', 'build', 'safety',
                         'backend'}


PROGRAM = 'void function main()\n    print("x")\n'


def test_structs_hold_collections_can_be_turned_off(tmp_path):
    from src.config import StructsConfig
    from tests.test_structs import errors_of
    assert load(tmp_path, 'fusion.toml', '').structs.hold_collections is True
    config = load(tmp_path, 'fusion.toml', '[structs]\nhold_collections = false\n')
    assert config.structs.hold_collections is False
    message = errors_of('struct Team\n    List<string> members\n    Map<string, int> score\n\n'
                        + PROGRAM, StructsConfig(hold_collections=False))
    assert "Field 'members' of struct 'Team' is a List" in message
    assert "Field 'score' of struct 'Team' is a Map" in message


def test_wait_at_exit_is_off_by_default_and_a_define_when_on(tmp_path):
    from src.codegen import CCodeGenerator
    from src.lexer import Lexer
    from src.parser.parser import Parser
    assert load(tmp_path, 'fusion.toml', '').build.wait_at_exit is False
    assert load(tmp_path, 'fusion.toml', '[build]\nwait_at_exit = true\n').build.wait_at_exit

    def c_code(**settings):
        program = Parser(Lexer(PROGRAM, 't').tokenize()).parse_program()
        return CCodeGenerator(**settings).generate(program)
    assert '#define FUSION_WAIT_AT_EXIT' not in c_code()
    assert '#define FUSION_WAIT_AT_EXIT 1' in c_code(wait_at_exit=True)
