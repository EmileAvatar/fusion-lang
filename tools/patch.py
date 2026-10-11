#!/usr/bin/env python3
"""Apply a list of exact text edits to files - all or nothing (Task 22.11).

    python tools/patch.py edits.py

edits.py defines EDITS, a list of (file, old, new) tuples, applied in order:

    EDITS = [
        ('FEATURES.md', '[ ] 22.11 tools/patch.py', '[DONE] 22.11 tools/patch.py'),
    ]

Each `old` must occur exactly once in its file (after the earlier edits to that file), or
nothing is written at all. An empty `old` appends `new` to the file. Paths are relative to
the current directory. Files are read and written as UTF-8, line endings kept as they are.
"""

import runpy
import sys
from pathlib import Path


def apply_edits(edits):
    """Returns a list of problems; files are written only when it is empty."""
    texts = {}
    problems = []
    for number, (file, old, new) in enumerate(edits, 1):
        path = Path(file)
        if path not in texts:
            if not path.exists():
                problems.append(f'edit {number}: no such file {file}')
                continue
            texts[path] = path.read_text(encoding='utf-8')
        text = texts[path]
        if old == '':
            texts[path] = text + new
            continue
        count = text.count(old)
        if count != 1:
            first_line = old.strip().splitlines()[0] if old.strip() else old
            problems.append(f'edit {number}: {file}: found {count} times, expected once: '
                            f'{first_line[:70]!r}')
            continue
        texts[path] = text.replace(old, new)
    if not problems:
        for path, text in texts.items():
            path.write_text(text, encoding='utf-8', newline='')
    return problems


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    edits = runpy.run_path(argv[0]).get('EDITS')
    if not isinstance(edits, list):
        print(f'{argv[0]} must define EDITS = [(file, old, new), ...]')
        return 2
    problems = apply_edits(edits)
    for problem in problems:
        print(problem)
    if problems:
        print('nothing written')
        return 1
    files = sorted({str(Path(file)) for file, _, _ in edits})
    print(f'{len(edits)} edit(s) applied to {", ".join(files)}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
