"""A `Fusion.Settings { ... }` block - first in the file - used instead of the settings file (Task 58.2, D.224, D.226).

    Fusion.Settings {                       Fusion.Settings
        maxIterations = 100000                  maxIterations = 100000
        money.rounding = "halfUp"               money.rounding = "halfUp"
    }

Only blank lines, `//` comments and a `#!` line may come before it. A name alone is enough when one section has it;
otherwise `section.name` (an error says which sections have it). The values are written as in the settings file.
Only the block of the file that starts the program is used; the lexer blanks it out of every file, so the lines keep
their numbers.
"""

import re
import tomllib
from typing import Optional, Tuple

_START = re.compile(r'\s*Fusion\.Settings\s*(\{)?\s*(?://.*)?$')


def _block_lines(source: str) -> Optional[Tuple[int, int, bool]]:
    """(first line, last line, braced) of a block first in the source - 0-based, inclusive - or None."""
    lines = source.split('\n')
    i = 0
    if lines and lines[0].startswith('#!'):
        i = 1
    while i < len(lines) and (not lines[i].strip() or lines[i].strip().startswith('//')):
        i += 1
    if i >= len(lines):
        return None
    match = _START.match(lines[i])
    if match is None:
        return None
    braced = match.group(1) is not None
    if not braced and i + 1 < len(lines) and lines[i + 1].strip() == '{':
        braced, start_body = True, i + 2                    # the brace on the next line
    else:
        start_body = i + 1
    j = start_body
    if braced:
        while j < len(lines) and lines[j].strip() != '}':
            j += 1
        if j >= len(lines):
            raise ValueError(f"line {i + 1}: Fusion.Settings has no closing '}}'")
        return i, j, True
    while j < len(lines) and (not lines[j].strip() or lines[j][:1] in (' ', '\t')):
        j += 1
    while j - 1 > i and not lines[j - 1].strip():
        j -= 1
    return i, j - 1, False


def blank_settings_block(source: str) -> Tuple[str, bool]:
    """The source with a first `Fusion.Settings` block turned into empty lines, and whether there was one."""
    try:
        found = _block_lines(source)
    except ValueError:
        return source, False                                # reported when the settings are read
    if found is None:
        return source, False
    first, last, _ = found
    lines = source.split('\n')
    for k in range(first, last + 1):
        lines[k] = ''
    return '\n'.join(lines), True


def read_settings_block(source: str, label: str) -> Optional[dict]:
    """The block's settings as a settings file's dictionary ({section: {name: value}}), or None without a block.
    A name it can't place, or a value it can't read, raises ValueError naming the line."""
    found = _block_lines(source)
    if found is None:
        return None
    first, last, braced = found
    from src.config.settings_files import read_template
    sections, settings = read_template()
    where = {}
    for s in settings:
        where.setdefault(s.name, []).append(s.section)
    data: dict = {}
    lines = source.split('\n')
    body = range(first + 1, last) if braced else range(first + 1, last + 1)
    if braced and lines[first + 1].strip() == '{':
        body = range(first + 2, last)
    for k in body:
        text = re.sub(r'\s//.*$', '', lines[k]).strip()
        if not text or text.startswith('//'):
            continue
        if '=' not in text:
            raise ValueError(f"{label}:{k + 1}: expected 'name = value' in Fusion.Settings")
        name, value = (part.strip() for part in text.split('=', 1))
        if '.' in name:
            section, name = name.rsplit('.', 1)
            if section not in sections:
                raise ValueError(f"{label}:{k + 1}: no settings section '{section}' (sections: "
                                 f"{', '.join(sorted(sections))})")
        else:
            places = where.get(name, [])
            if not places:
                raise ValueError(f"{label}:{k + 1}: no setting named '{name}' (files/fusionSettings.xml lists "
                                 f"every one)")
            if len(places) > 1:
                raise ValueError(f"{label}:{k + 1}: '{name}' is in " + ' and '.join(f'[{p}]' for p in places)
                                 + ' - write ' + ' or '.join(f'{p}.{name}' for p in places))
            section = places[0]
        try:
            parsed = tomllib.loads(f'v = {value}')['v']
        except tomllib.TOMLDecodeError:
            raise ValueError(f"{label}:{k + 1}: can't read the value of '{name}' - {value} (write it as in "
                             f"the settings file: 5, true, \"text\")") from None
        data.setdefault(section, {})[name] = parsed
    return data
