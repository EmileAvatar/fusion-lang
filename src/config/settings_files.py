"""The project settings file in four formats (Task 31, user decisions 2026-10-28).

fusion.toml is the default. fusion.yaml (or .yml), fusion.json and fusion.ini are
alternatives - for a company that standardises on YAML, or INI for legacy hardware and
software. Each format is read into the same plain dictionary ({section: {key: value}}), so
the one set of checks in project_config.py gives all four the same meaning.

- Finding the file: in a folder, the first of TOML, YAML, JSON, INI wins (no warning)
- No settings file anywhere: a new fusion.toml is written from the master template
  (files/fusionSettings.xml - every setting at its default, with a comment each)
- `[project] fusionSettingFormat` names the file's format. When it names another one, the
  settings are written in that format and the old file is kept as a backup (.bak), so only
  one settings file is active. Comments don't survive a change of format - they live on in
  the backup

The readers are Python's (tomllib, json, configparser) and PyYAML (safe_load - never runs
code from the file), loaded only when a project has a YAML file. Fusion's own readers come
with its data-formats module (FEATURES.md 43.2).
"""

import configparser
import json
import os
import re
import tomllib
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class SettingsFileError(Exception):
    """A settings file that can't be read or written - turned into a ProjectConfigError."""


# Format name -> file names, in the order a folder is searched (TOML first)
FORMAT_FILES = {
    'TOML': ('fusion.toml',),
    'YAML': ('fusion.yaml', 'fusion.yml'),
    'JSON': ('fusion.json',),
    'INI': ('fusion.ini',),
}
SETTINGS_FILE_NAMES = [name for names in FORMAT_FILES.values() for name in names]

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'files',
                             'fusionSettings.xml')


def format_of(path: str) -> str:
    """'TOML', 'YAML', 'JSON' or 'INI' for a settings file's name."""
    name = os.path.basename(path)
    return next(fmt for fmt, names in FORMAT_FILES.items() if name in names)


def find_in_folder(folder: str) -> Optional[str]:
    """The settings file a folder holds - TOML first, then YAML, JSON, INI."""
    for name in SETTINGS_FILE_NAMES:
        candidate = os.path.join(folder, name)
        if os.path.isfile(candidate):
            return candidate
    return None


# ---------------------------------------------------------------- reading

def read_settings(path: str) -> dict:
    """The file's settings as {section: {key: value}}."""
    fmt = format_of(path)
    try:
        if fmt == 'TOML':
            with open(path, 'rb') as f:
                data = tomllib.load(f)
        elif fmt == 'JSON':
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
        elif fmt == 'YAML':
            data = _read_yaml(path)
        else:
            data = _read_ini(path)
    except tomllib.TOMLDecodeError as e:
        raise SettingsFileError(f"Invalid TOML in {path}: {e}") from e
    except json.JSONDecodeError as e:
        raise SettingsFileError(f"Invalid JSON in {path}: {e}") from e
    except configparser.Error as e:
        raise SettingsFileError(f"Invalid INI in {path}: {e}") from e
    except OSError as e:
        raise SettingsFileError(f"Could not read {path}: {e}") from e
    if data is None:
        data = {}                              # an empty YAML file
    if not isinstance(data, dict):
        raise SettingsFileError(f"{path}: the settings must be sections of name = value")
    return data


def _read_yaml(path: str):
    try:
        import yaml
    except ImportError as e:
        raise SettingsFileError(
            f"{path}: reading YAML needs the PyYAML package - pip install pyyaml, or use "
            f"fusion.toml") from e
    try:
        with open(path, encoding='utf-8') as f:
            return yaml.safe_load(f)            # safe_load: never runs code from the file
    except yaml.YAMLError as e:
        raise SettingsFileError(f"Invalid YAML in {path}: {e}") from e


_INI_INT = re.compile(r'^[+-]?\d+$')


def _read_ini(path: str) -> dict:
    """INI holds only text: true / false (and nothing else) become bools, whole numbers
    become ints, "quoted" text loses its quotes, any other text stays text."""
    parser = configparser.ConfigParser(interpolation=None, comment_prefixes=('#', ';'),
                                       inline_comment_prefixes=None)
    parser.optionxform = str                    # keep fusionSettingFormat as written
    with open(path, encoding='utf-8') as f:
        parser.read_file(f)
    return {section: {key: _ini_value(text) for key, text in parser.items(section)}
            for section in parser.sections()}


def _ini_value(text: str):
    text = text.strip()
    if text.lower() in ('true', 'false'):
        return text.lower() == 'true'
    if _INI_INT.match(text):
        return int(text)
    if len(text) >= 2 and text[0] == text[-1] and text[0] in '"\'':
        return text[1:-1]
    return text


# ---------------------------------------------------------------- writing

def settings_text(data: dict, fmt: str, comments: Dict[str, str] = None) -> str:
    """The settings written in a format. comments: 'section' or 'section.key' -> a comment
    line (TOML, YAML and INI only - JSON has no comments)."""
    comments = comments or {}
    if fmt == 'JSON':
        return json.dumps(data, indent=2) + '\n'
    lines = []
    for section, values in data.items():
        if lines:
            lines.append('')
        if comments.get(section):
            lines.append(f'# {comments[section]}')
        lines.append(f'{section}:' if fmt == 'YAML' else f'[{section}]')
        for key, value in values.items():
            note = comments.get(f'{section}.{key}')
            if note:
                lines.append(('  # ' if fmt == 'YAML' else '# ') + note)
            text = _value_text(value)
            lines.append(f'  {key}: {text}' if fmt == 'YAML' else f'{key} = {text}')
    return '\n'.join(lines) + '\n'


def _value_text(value) -> str:
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, int):
        return str(value)
    return json.dumps(str(value))   # "text" - valid TOML, YAML and INI (read back unquoted)


def write_settings(path: str, data: dict, fmt: str, comments: Dict[str, str] = None) -> None:
    try:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(settings_text(data, fmt, comments))
    except OSError as e:
        raise SettingsFileError(f"Could not write {path}: {e}") from e


# ---------------------------------------------------------------- the master template

@dataclass
class TemplateSetting:
    section: str
    name: str
    type: str                  # bool, int, choice, int-or-max
    default: object
    description: str
    values: List[str] = field(default_factory=list)      # choice: the allowed values
    reserved: List[str] = field(default_factory=list)    # choice: named for the future
    minimum: Optional[int] = None


def read_template(path: str = TEMPLATE_PATH):
    """(section descriptions, settings) from files/fusionSettings.xml."""
    root = ElementTree.parse(path).getroot()
    sections, settings = {}, []
    for section in root.findall('section'):
        name = section.get('name')
        sections[name] = section.get('description', '')
        for item in section.findall('setting'):
            kind = item.get('type')
            text = item.get('default')
            values = [v.text for v in item.findall('value') if v.get('reserved') != 'true']
            reserved = [v.text for v in item.findall('value') if v.get('reserved') == 'true']
            if kind == 'bool':
                default = text == 'true'
            elif kind == 'int' or (kind == 'int-or-max' and text != 'max'):
                default = int(text)
            else:
                default = text
            settings.append(TemplateSetting(
                section=name, name=item.get('name'), type=kind, default=default,
                description=(item.findtext('description') or '').strip(), values=values,
                reserved=reserved,
                minimum=int(item.get('min')) if item.get('min') is not None else None))
    return sections, settings


def default_settings(fmt: str = 'TOML'):
    """(data, comments) for a new settings file: every setting at its default."""
    sections, settings = read_template()
    data, comments = {}, {}
    for name, description in sections.items():
        data[name] = {}
        comments[name] = description
    for s in settings:
        data[s.section][s.name] = s.default
        allowed = ''
        if s.type == 'choice':
            allowed = ' (' + ' / '.join(s.values) + ')'
        elif s.type == 'int-or-max':
            allowed = f' ("max" or a whole number of at least {s.minimum})'
        comments[f'{s.section}.{s.name}'] = s.description + allowed
    data['project']['fusionSettingFormat'] = fmt
    return data, comments


def create_default_file(folder: str) -> str:
    """A new fusion.toml in folder, from the master template. Returns its path."""
    data, comments = default_settings('TOML')
    path = os.path.join(folder, 'fusion.toml')
    header = ('# Fusion project settings - every setting at its default. The full list, with '
              'the values\n# each can have: files/fusionSettings.xml (the master template)\n\n')
    try:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(header + settings_text(data, 'TOML', comments))
    except OSError as e:
        raise SettingsFileError(f"Could not write {path}: {e}") from e
    return path


def convert(path: str, data: dict, fmt: str) -> str:
    """Write the settings as fmt next to path, keep path as a backup (.bak) - and any file
    already there under the new name too. Returns the new file's path."""
    folder = os.path.dirname(path)
    new_path = os.path.join(folder, FORMAT_FILES[fmt][0])
    for old in (new_path, path):
        if os.path.isfile(old):
            backup = old + '.bak'
            if os.path.exists(backup):
                os.remove(backup)
            os.rename(old, backup)
    write_settings(new_path, data, fmt, default_settings(fmt)[1])   # the template's comments
    return new_path
