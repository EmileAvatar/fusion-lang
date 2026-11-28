"""Task 45.13 - arrays on the stack measured in bytes (D.145): `[arrays] stackWarn = "16KB"` (a
warning), `stackLimit = "64KB"` (a compile error). A growable array, a replaced one and a List live
on the heap and aren't measured. `setBufferType` / `setSize` are an error "not built yet" (D.146).
"""
import pytest

from src.config.project_config import ArraysConfig, ProjectConfigError
from src.semantic import SemanticAnalyzer
from tests.test_settings_formats import load
from tests.test_structs import errors_of, main, parse


def analyze(body: str, before: str = '', **sizes) -> tuple:
    analyzer = SemanticAnalyzer(arrays_config=ArraysConfig(**sizes) if sizes else None)
    analyzer.analyze(parse(before + main(body)))
    return ([e.message for e in analyzer.get_errors()], [w.message for w in analyzer.get_warnings()])


def stack_messages(body, before='', **sizes):
    errors, warnings = analyze(body, before, **sizes)
    return ([e for e in errors if 'on the stack' in e], [w for w in warnings if 'on the stack' in w])


# int is 4 bytes: 16KB = 4,096 ints, 64KB = 16,384 ints
@pytest.mark.parametrize('declaration, errors, warnings', [
    ('int[4096] a', 0, 0),                  # exactly 16KB - not above it
    ('int[4097] a', 0, 1),                  # 16,388 bytes - a warning
    ('int[16384] a', 0, 1),                 # exactly 64KB
    ('int[16385] a', 1, 0),                 # above 64KB - an error
    ('fixed int[20000] a', 1, 0),           # fixed is on the stack too
    ('int a[20000]', 1, 0),                 # brackets after the name: the same array
    ('double[2100] a', 0, 1),               # 16,800 bytes
    ('byte[16000] a', 0, 0),                # 1 byte each
    ('string[700] a', 0, 1),                # 24 bytes each: 16,800
    ('int:[] a', 0, 0),                     # growable - on the heap
    ('List<int> a', 0, 0),
])
def test_default_limits(declaration, errors, warnings):
    found_errors, found_warnings = stack_messages(declaration)
    assert (len(found_errors), len(found_warnings)) == (errors, warnings)


def test_the_messages_name_the_sizes():
    errors, _ = stack_messages('int[20000] big')
    assert errors == ["'big' takes 80,000 bytes on the stack - more than [arrays] stackLimit (65,536 bytes); "
                      "make it smaller, use a growable array (int:[]) or a List - both live on the heap - or "
                      "raise stackLimit (D.145)"]
    _, warnings = stack_messages('int[5000] mid')
    assert warnings[0].startswith("'mid' takes 20,000 bytes on the stack - more than [arrays] stackWarn (16,384 bytes)")


def test_a_replaced_array_is_on_the_heap():
    errors, warnings = stack_messages('int[20000] a\na = [1, 2]')
    assert (errors, warnings) == ([], [])


def test_a_struct_holding_a_large_array():
    struct = 'struct Big\n    int[20000] data\n    string name\n\n'
    errors, _ = stack_messages('Big b = Big()', struct)
    assert len(errors) == 1 and "'b' takes 80,024 bytes" in errors[0]


def test_an_array_of_objects_counts_references():
    cls = 'class Car\n    public string color\n\n'
    _, warnings = stack_messages('Car[2100] cars', cls)
    assert len(warnings) == 1 and '16,800 bytes' in warnings[0]


def test_an_embedded_project_lowers_both():
    errors, warnings = stack_messages('int[200] a\nint[300] b', stack_warn=512, stack_limit=1024)
    assert len(warnings) == 1 and "'a' takes 800 bytes" in warnings[0]
    assert len(errors) == 1 and "'b' takes 1,200 bytes" in errors[0]


@pytest.mark.parametrize('text, warn, limit', [
    ('', 16384, 65536),
    ('stackWarn = "1KB"\nstackLimit = "4KB"', 1024, 4096),
    ('stackWarn = "512B"\nstackLimit = 2048', 512, 2048),
    ('stackLimit = "1MB"', 16384, 1048576),
    ('stack_warn = "8kb"', 8192, 65536),
])
def test_the_settings(tmp_path, text, warn, limit):
    config = load(tmp_path, 'settings.toml', '[arrays]\n' + text + '\n')
    assert (config.arrays.stack_warn, config.arrays.stack_limit) == (warn, limit)


@pytest.mark.parametrize('text, message', [
    ('stackWarn = "16 apples"', 'must be a size in bytes'),
    ('stackWarn = 0', 'at least 1 byte'),
    ('stackWarn = "128KB"', 'is above arrays.stackLimit'),
    ('stackSize = "1KB"', 'unknown setting arrays.stackSize'),
])
def test_wrong_settings(tmp_path, text, message):
    with pytest.raises(ProjectConfigError, match=message):
        load(tmp_path, 'settings.toml', '[arrays]\n' + text + '\n')


@pytest.mark.parametrize('body', ['int[10] a\na.setBufferType(TWO)', 'int:[] a\na.setSize(1024)',
                                  'int[] a = [1]\na = [2, 3]\na.setSize(512)'])
def test_buffers_are_not_built_yet(body):
    assert 'is not built yet - buffers for large arrays come after self-hosting' in errors_of(main(body))
