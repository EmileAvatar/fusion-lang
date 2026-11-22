"""Where the example programs live (examples/CLAUDE.md).

examples/ is split into numbered topic folders (01_basics, 02_functions, ...). A program of one
file is examples/<topic>/<name>.fusion; a project of several files is
examples/13_projects/<name>/main.fusion. Names are unique across the folders, so a program is
found by its name alone - the folder is only for people browsing them.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / 'examples'
PROJECTS = EXAMPLES / '13_projects'

# A topic folder for each hand-written demo (a syntax_* program names its folder in its
# files/SYNTAX_REFERENCE.md marker)
DEMO_FOLDERS = {
    'hello_world': '01_basics', 'control_flow': '01_basics', 'fizzbuzz': '01_basics',
    'factorial': '01_basics', 'max_three': '01_basics', 'calculator': '01_basics',
    'const_demo': '01_basics', 'style_indent': '01_basics', 'style_braces': '01_basics',
    'style_end': '01_basics',
    'functions_demo': '02_functions',
    'strings_demo': '03_strings',
    'arrays_demo': '04_arrays', 'sum_array': '04_arrays',
    'structs_demo': '07_structs',
    'classes_demo': '08_classes',
    'errors_demo': '10_errors_and_null',
}


def topic_folders() -> list:
    """The numbered topic folders, in order (13_projects included)."""
    return sorted(p for p in EXAMPLES.iterdir() if p.is_dir() and p.name[:2].isdigit())


def single_file_examples() -> list:
    """examples/<topic>/<name>.fusion - every program of one file."""
    return sorted((p for folder in topic_folders() for p in folder.glob('*.fusion')),
                  key=lambda p: (p.parent.name, p.name))


def project_examples() -> list:
    """examples/13_projects/<name>/main.fusion - every project of several files."""
    return sorted(PROJECTS.glob('*/main.fusion'))


def example_sources() -> list:
    return single_file_examples() + project_examples()


def example_name(path: Path) -> str:
    """A program's name: its file name, or for a project its folder (shop/main)."""
    path = Path(path)
    return f'{path.parent.name}/{path.stem}' if path.parent.parent == PROJECTS else path.stem


def example_label(path: Path) -> str:
    """Its path inside examples/, for lists and messages: 01_basics/hello_world."""
    return Path(path).relative_to(EXAMPLES).with_suffix('').as_posix()


def example_path(name: str) -> Path:
    """examples/<topic>/NAME.fusion, or the project examples/13_projects/NAME/main.fusion;
    a path that does not exist (under examples/) when there is no such program."""
    for path in single_file_examples():
        if path.stem == name:
            return path
    project = PROJECTS / name / 'main.fusion'
    return project if project.exists() else EXAMPLES / f'{name}.fusion'
