"""Task 48.11 - `[memory] ownership = "strict" | "relaxed"` (D.124), replacing `assignment`."""
import pytest

from src.config.project_config import MemoryConfig, ProjectConfigError, load_project_config


def load(tmp_path, memory: str):
    (tmp_path / 'fusion.toml').write_text('[memory]\n' + memory + '\n', encoding='utf-8')
    (tmp_path / 'main.fusion').write_text('void function main()\n    print("x")\n', encoding='utf-8')
    return load_project_config(str(tmp_path / 'main.fusion'))


def test_strict_is_the_default():
    assert MemoryConfig().ownership == 'strict'
    assert MemoryConfig().assignment == 'move'


@pytest.mark.parametrize('value, assignment', [('strict', 'move'), ('relaxed', 'share')])
def test_ownership_sets_every_rule(tmp_path, value, assignment):
    config = load(tmp_path, f'ownership = "{value}"')
    assert config.memory.ownership == value
    assert config.memory.assignment == assignment
    assert config.warnings == []


@pytest.mark.parametrize('old, new', [('move', 'strict'), ('share', 'relaxed')])
def test_the_old_name_is_read_with_a_warning(tmp_path, old, new):
    config = load(tmp_path, f'assignment = "{old}"')
    assert config.memory.ownership == new
    assert any(f'is now written memory.ownership = "{new}"' in w for w in config.warnings)


def test_both_names_is_an_error(tmp_path):
    with pytest.raises(ProjectConfigError, match='the same setting'):
        load(tmp_path, 'ownership = "strict"\nassignment = "move"')


def test_a_wrong_value_is_an_error(tmp_path):
    with pytest.raises(ProjectConfigError, match='must be "strict" or "relaxed"'):
        load(tmp_path, 'ownership = "loose"')
