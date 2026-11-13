"""Navigation lines for the documentation (Task 51.5, user 2026-11-08).

Two groups, each navigable on its own:
- the root documents, in ROOT_ORDER - each also links to the spec index;
- the spec files in files/spec/, in the order files/spec/index.md lists them - they link
  only to each other and to the index, never back to the root (user);
- the future ideas in files/future/, the same way (Task 51.5b).

Every file gets the same line at its top and its bottom:
    [< previous](..) | [Main](Main.md) | [Spec](files/spec/index.md) | [next >](..)
The line ends with NAV_MARK (an HTML comment the viewer hides), so the line is found and
rewritten - never edited by hand.

    python tools/doc_nav.py           rewrite every navigation line
    check.py runs nav_problems()      reports any file whose lines are out of date
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / 'files' / 'spec'
FOLDERS = [SPEC, ROOT / 'files' / 'future']   # each with an index.md listing its files
NAV_MARK = '<!-- nav -->'
ROOT_ORDER = ['Main.md', 'Decisions.md', 'OpenQuestions.md', 'README.md']
SPEC_FILE = re.compile(r'\]\((\d{3}-[A-Za-z0-9-]+\.md)\)')


def spec_order(folder=SPEC):
    index = folder / 'index.md'
    if not index.exists():
        return []
    seen = []
    for name in SPEC_FILE.findall(index.read_text(encoding='utf-8')):
        if name not in seen:
            seen.append(name)
    return seen


def label(name):
    """'010-Philosophy.md' -> '010 Philosophy'; 'Main.md' -> 'Main'."""
    return name[:-3].replace('-', ' ', 1)


def nav_line(previous, middle, following):
    parts = []
    if previous:
        parts.append(f'[< {label(previous)}]({previous})')
    parts += middle
    if following:
        parts.append(f'[{label(following)} >]({following})')
    return ' | '.join(parts) + ' ' + NAV_MARK


def wanted():
    """{path: nav line} for every file that gets one."""
    lines = {}
    for i, name in enumerate(ROOT_ORDER):
        previous = ROOT_ORDER[i - 1] if i > 0 else None
        following = ROOT_ORDER[i + 1] if i + 1 < len(ROOT_ORDER) else None
        middle = ['[Main](Main.md)', '[Spec](files/spec/index.md)']
        lines[ROOT / name] = nav_line(previous, middle, following)
    for folder in FOLDERS:
        order = spec_order(folder)
        for i, name in enumerate(order):
            previous = order[i - 1] if i > 0 else None
            following = order[i + 1] if i + 1 < len(order) else None
            lines[folder / name] = nav_line(previous, ['[Index](index.md)'], following)
    return lines


def with_nav(text, line):
    body = '\n'.join(l for l in text.split('\n') if NAV_MARK not in l).strip('\n')
    return f'{line}\n\n{body}\n\n{line}\n'


def nav_problems():
    problems = []
    for path, line in wanted().items():
        if not path.exists():
            problems.append(f'{path.relative_to(ROOT)}: listed but missing')
            continue
        text = path.read_text(encoding='utf-8')
        if text != with_nav(text, line):
            problems.append(f'{path.relative_to(ROOT)}: navigation out of date - run python tools/doc_nav.py')
    return problems


def main():
    changed = 0
    for path, line in wanted().items():
        text = path.read_text(encoding='utf-8')
        new = with_nav(text, line)
        if new != text:
            path.write_text(new, encoding='utf-8', newline='\n')
            changed += 1
            print(f'wrote     {path.relative_to(ROOT)}')
    print(f'{changed} file(s) updated')
    return 0


if __name__ == '__main__':
    sys.exit(main())
