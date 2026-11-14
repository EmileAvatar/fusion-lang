"""The link check for the Markdown documents (Task 51.6, user 2026-11-13).

Every relative link `[text](path)` or `[text](path#anchor)` in a .md file must lead somewhere:
- the file (or folder) exists, relative to the document;
- an anchor names a heading in that file (the GitHub slug, with -1, -2 for repeated headings)
  or an explicit `<a id="...">`.

Skipped: web links (http, https, mailto), links inside code blocks and `inline code`, and the
folders Notes/ (git-ignored), task/ (archives keep their old paths), .git, examples/ output.

    python tools/doc_links.py          list every broken link
    check.py runs link_problems()      the `links` check
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {'Notes', 'task', '.git', '.claude', 'node_modules', '__pycache__', 'debug'}
LINK = re.compile(r'(?<!!)\[(?:[^\[\]]|\[[^\]]*\])*\]\((<[^>]+>|[^)\s]+)(?:\s+"[^"]*")?\)')
IMAGE = re.compile(r'!\[[^\]]*\]\((<[^>]+>|[^)\s]+)\)')
ANCHOR_ID = re.compile(r'<a\s+(?:id|name)="([^"]+)"', re.I)
HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*#*\s*$')


def slug(text):
    """GitHub's anchor for a heading: the text as shown (a link counts as its text), lower case,
    only letters, digits, spaces, '-' and '_' kept, each space a '-'."""
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'[^\w\- ]', '', text.lower(), flags=re.UNICODE).replace(' ', '-')


def strip_code(text, inline=True):
    """The text with code blocks (and, when inline, `inline code`) blanked out - line numbers kept."""
    out, fence = [], False
    for line in text.split('\n'):
        if line.lstrip().startswith(('```', '~~~')):
            fence = not fence
            out.append('')
            continue
        out.append('' if fence else (re.sub(r'`[^`\n]*`', '', line) if inline else line))
    return out


def anchors(path, cache={}):
    if path not in cache:
        found, seen = set(), {}
        for line in strip_code(path.read_text(encoding='utf-8', errors='replace'), inline=False):
            for a in ANCHOR_ID.findall(line):
                found.add(a)
            m = HEADING.match(line)
            if m:
                s = slug(m.group(2))
                n = seen.get(s, 0)
                found.add(s if n == 0 else f'{s}-{n}')
                seen[s] = n + 1
        cache[path] = found
    return cache[path]


def documents(root):
    for path in sorted(root.rglob('*.md')):
        rel = path.relative_to(root)
        if rel.parts and rel.parts[0] in SKIP_DIRS:
            continue
        if any(p in SKIP_DIRS for p in rel.parts):
            continue
        yield path


def link_problems(root=ROOT, files=None):
    problems = []
    for path in (files if files is not None else documents(root)):
        lines = strip_code(path.read_text(encoding='utf-8', errors='replace'))
        for number, line in enumerate(lines, 1):
            for m in list(LINK.finditer(line)) + list(IMAGE.finditer(line)):
                target = m.group(1).strip('<>')
                if re.match(r'[a-z][a-z0-9+.-]*:', target, re.I):     # http:, mailto:, ...
                    continue
                file_part, _, anchor = target.partition('#')
                where = path if not file_part else (path.parent / file_part.replace('%20', ' '))
                rel = path.relative_to(root) if root in path.parents else path
                if not where.exists():
                    problems.append(f'{rel}:{number}: {target} - no such file')
                    continue
                if anchor and where.is_file() and where.suffix == '.md' and anchor not in anchors(where):
                    problems.append(f'{rel}:{number}: {target} - no heading or anchor "{anchor}"')
    return problems


def main():
    problems = link_problems()
    for p in problems:
        print(p)
    print(f'{len(problems)} broken link(s)')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
