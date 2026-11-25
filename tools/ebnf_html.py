"""files/fusion.ebnf as a page to read: files/fusion.ebnf.html (user, 2026-11-25).

    python tools/ebnf_html.py           write the page
    python tools/ebnf_html.py --check   the page matches the grammar (part of the "ebnf" check in check.py)

Each entry of the grammar - its comment, then its rules - becomes one card:

    [task] [status] [ the comment, in a grey box                          ] [top]
    [ the rules, coloured                                                   ]

The task is the first one its comment names (Task 47.7, (33.2f)), linked to files/FEATURES.md (or the archive when
the task is done); a decision (D.176, SYN.014) links to Decisions.md. The status comes from where the entry is:
above the PLANNED part it is built; in it, planned (a task or decision named), postponed, rejected, or not built
yet (an idea, or nothing named). Colours: built green, planned / postponed / partial orange, rejected red, not built
blue. A comment may also say [built], [partial], [planned], [postponed], [rejected] or [idea] to set it.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EBNF = ROOT / 'files' / 'fusion.ebnf'
PAGE = ROOT / 'files' / 'fusion.ebnf.html'
FEATURES = ROOT / 'files' / 'FEATURES.md'

STATUS_LOOK = {          # status -> (label, css class)
    'built': ('built', 'built'),
    'partial': ('partial', 'planned'),
    'planned': ('planned', 'planned'),
    'postponed': ('postponed', 'planned'),
    'rejected': ('rejected', 'rejected'),
    'idea': ('not built', 'notbuilt'),
}

BANNER = re.compile(r'^\(\* =+ \*\)$')
SECTION = re.compile(r'^\(\* =+ (.+?) =+ \*\)$')
TASK = re.compile(r'Task (\d+(?:\.\d+[a-z]?\d*)?)|\((\d{2}\.\d+[a-z]?\d*)')
DECISION = re.compile(r'\b(D\.\d{3}|[A-Z]{3}\.\d{3})\b')


def task_anchors() -> set:
    return set(re.findall(r'<a id="task-(\d+)"', FEATURES.read_text(encoding='utf-8')))


def read_sections(text: str) -> list:
    """[(title, planned, [paragraph lines])] - the grammar split at its section headings, then at blank lines."""
    sections, planned = [], False
    title, body = 'About this grammar', []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        heading = SECTION.match(line)
        if BANNER.match(line) and i + 2 < len(lines) and BANNER.match(lines[i + 2]):
            if body:
                sections.append((title, planned, body))
            inner = lines[i + 1].strip()[2:-2].strip()
            if inner.startswith('PLANNED'):
                planned = True
                title, body = 'Planned - designed, not built', []
                i += 3
                continue
            title, body = 'About this grammar', []          # the opening banner
            i += 1
            while i < len(lines) and not BANNER.match(lines[i]):
                body.append(lines[i])
                i += 1
            i += 1
            continue
        if heading:
            if body:
                sections.append((title, planned, body))
            title, body = heading.group(1).strip(), []
        else:
            body.append(line)
        i += 1
    if body:
        sections.append((title, planned, body))
    return sections


def paragraphs(body: list) -> list:
    """Blocks of lines between blank lines - a comment block inside never splits."""
    out, current, in_comment = [], [], False
    for line in body:
        if not line.strip() and not in_comment:
            if current:
                out.append(current)
            current = []
            continue
        current.append(line)
        opened = line.count('(*') - line.count('*)')
        in_comment = in_comment + opened > 0 if opened else in_comment
    if current:
        out.append(current)
    return out


def split_entry(lines: list) -> tuple:
    """(comment text, code lines) - the comments at the start of the paragraph, then the rules."""
    comment, i = [], 0
    while i < len(lines) and lines[i].startswith('(*'):
        depth = 0
        while i < len(lines):
            line = lines[i]
            comment.append(line)
            depth += line.count('(*') - line.count('*)')
            i += 1
            if depth <= 0:
                break
    text = '\n'.join(comment)
    text = re.sub(r'^\(\*\s?', '', text)
    text = re.sub(r'\s?\*\)$', '', text)
    text = re.sub(r'\s?\*\)\n\(\*\s?', '\n', text)
    return text.strip(), lines[i:]


def status_of(comment: str, planned: bool) -> str:
    written = re.search(r'\[(built|partial|planned|postponed|rejected|idea)\]', comment)
    if written:
        return written.group(1)
    if not planned:
        return 'built'
    if 'REJECTED' in comment or 'rejected' in comment:
        return 'rejected'
    if 'POSTPONED' in comment:
        return 'postponed'
    if re.search(r'\ban idea\b', comment) or not (TASK.search(comment) or DECISION.search(comment)):
        return 'idea'
    return 'planned'


def reference(comment: str, anchors: set) -> tuple:
    """(text, link) for the first task the comment names, else its first decision, else ('-', None)."""
    found = TASK.search(comment)
    if found:
        number = found.group(1) or found.group(2)
        whole = number.split('.')[0]
        if whole in anchors:
            return number, f'FEATURES.md#task-{whole}'
        return number, '../task/featuresArchive.md'
    found = DECISION.search(comment)
    if found:
        return found.group(1), '../Decisions.md'
    return '-', None


TOKEN = re.compile(r'''(?P<comment>\(\*.*?\*\))|(?P<string>"[^"]*"|'[^']*')|(?P<special>\?[^?]*\?)'''
                   r'''|(?P<name>[A-Za-z_][A-Za-z0-9_]*)|(?P<op>[|=;{}\[\]()]|\.\.)''', re.S)


def colour(code: str) -> str:
    """The rules as HTML: a rule's own name bold, names, "terminals", ? specials ?, operators, (* notes *)."""
    out, pos = [], 0
    defined = set(re.findall(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=', code, re.M))
    for m in TOKEN.finditer(code):
        out.append(html.escape(code[pos:m.start()]))
        text = html.escape(m.group(0))
        kind = m.lastgroup
        if kind == 'name':
            line_start = code.rfind('\n', 0, m.start()) + 1
            cls = 'rule' if m.group(0) in defined and m.start() == line_start else 'nt'
            out.append(f'<span class="{cls}">{text}</span>')
        else:
            out.append(f'<span class="{ {"comment": "c", "string": "s", "special": "sp", "op": "o"}[kind] }">{text}</span>')
        pos = m.end()
    out.append(html.escape(code[pos:]))
    return ''.join(out)


def slug(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


CSS = """
:root { --bg: #f6f7f9; --card: #ffffff; --line: #d9dee3; --text: #1f2933; --muted: #5b6672;
  --built: #1a7f37; --planned: #b35900; --rejected: #c62828; --notbuilt: #0b5cad;
  --comment-bg: #eef0f3; --code-bg: #fbfcfd; }
@media (prefers-color-scheme: dark) { :root { --bg: #16191d; --card: #1f2328; --line: #343a40; --text: #e6e8eb;
  --muted: #a0a8b0; --built: #3fb950; --planned: #f0a040; --rejected: #ff6b6b; --notbuilt: #6cb6ff;
  --comment-bg: #2a2f35; --code-bg: #1b1f24; } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font: 15px/1.5 "Segoe UI", Arial, sans-serif; }
header { padding: 20px 24px 8px; }
h1 { margin: 0 0 4px; font-size: 24px; }
.sub { color: var(--muted); margin: 0 0 12px; }
.legend span { margin-right: 14px; white-space: nowrap; }
.intro { margin-top: 12px; background: var(--comment-bg); color: var(--muted); border-radius: 6px; padding: 8px 12px;
  white-space: pre-wrap; font-size: 13.5px; }
.layout { display: flex; gap: 20px; padding: 0 24px 40px; align-items: flex-start; }
nav { position: sticky; top: 12px; width: 260px; flex: none; max-height: calc(100vh - 24px); overflow-y: auto;
  background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px; font-size: 13px; }
nav a { color: var(--text); text-decoration: none; display: block; padding: 2px 0; }
nav a:hover { text-decoration: underline; }
nav .sec { font-weight: 600; margin-top: 8px; }
nav .rules { color: var(--muted); padding-left: 10px; font-size: 12px; }
nav .rules a { display: inline; color: var(--muted); }
main { flex: 1; min-width: 0; }
h2 { font-size: 19px; margin: 26px 0 10px; padding-bottom: 4px; border-bottom: 2px solid var(--line); }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 8px; margin: 0 0 12px; overflow: hidden; }
.head { display: flex; gap: 8px; align-items: flex-start; padding: 8px; }
.task, .status, .top { flex: none; font-size: 12px; font-weight: 600; border-radius: 4px; padding: 3px 8px; white-space: nowrap; }
.task { border: 1px solid var(--line); color: var(--text); text-decoration: none; min-width: 64px; text-align: center; }
a.task:hover { border-color: var(--notbuilt); }
.status { color: #fff; min-width: 76px; text-align: center; }
.status.built { background: var(--built); } .status.planned { background: var(--planned); }
.status.rejected { background: var(--rejected); } .status.notbuilt { background: var(--notbuilt); }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 4px; vertical-align: -1px; }
.dot.built { background: var(--built); } .dot.planned { background: var(--planned); }
.dot.rejected { background: var(--rejected); } .dot.notbuilt { background: var(--notbuilt); }
.comment { flex: 1; min-width: 0; background: var(--comment-bg); color: var(--muted); border-radius: 4px; padding: 4px 10px;
  white-space: pre-wrap; font-size: 13.5px; }
.top { color: var(--muted); text-decoration: none; border: 1px solid var(--line); }
pre { margin: 0; padding: 10px 14px; background: var(--code-bg); border-top: 1px solid var(--line); overflow-x: auto;
  font: 14px/1.5 Consolas, "Courier New", monospace; }
.rule { color: var(--text); font-weight: 700; } .nt { color: #8a3ffc; } .s { color: var(--built); }
.sp { color: var(--planned); font-style: italic; } .o { color: var(--muted); } .c { color: var(--muted); font-style: italic; }
@media (prefers-color-scheme: dark) { .nt { color: #d2a8ff; } }
@media (max-width: 800px) { .layout { flex-direction: column; } nav { position: static; width: 100%; max-height: none; } }
"""


def build_page(text: str) -> str:
    anchors = task_anchors()
    nav, body, counts = [], [], {}
    intro = ''
    for title, planned, lines in read_sections(text):
        sid = slug(title)
        if title == 'About this grammar':
            words = [re.sub(r'^\(\*\s?|\s*\*\)$', '', line).rstrip() for line in lines if not BANNER.match(line)]
            intro = f'<div class="intro">{html.escape(chr(10).join(words).strip())}</div>'
            continue
        entries, rule_links = [], []
        for para in paragraphs(lines):
            comment, code = split_entry(para)
            inline = ' '.join(c.strip()[2:-2].strip() for c in re.findall(r'\(\*.*?\*\)', '\n'.join(code), re.S))
            if not comment:
                comment = inline                       # the rule's own notes, when nothing comes before it
            status = status_of(comment + ' ' + inline, planned)
            label, cls = STATUS_LOOK[status]
            counts[cls] = counts.get(cls, 0) + 1
            number, link = reference(comment + ' ' + inline, anchors)
            if number == '-':
                number, link = reference(title, anchors)  # the section's task: Enums (Task 25)
            names = re.findall(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=', '\n'.join(code), re.M)
            eid = f'{sid}-{slug(names[0])}' if names else f'{sid}-{len(entries) + 1}'
            rule_links += [f'<a href="#{eid}">{html.escape(n)}</a>' for n in names]
            task = (f'<a class="task" href="{link}">{html.escape(number)}</a>' if link
                    else f'<span class="task">{html.escape(number)}</span>')
            card = [f'<div class="card" id="{eid}">', '<div class="head">', task,
                    f'<span class="status {cls}">{label}</span>',
                    f'<div class="comment">{html.escape(comment) if comment else "&nbsp;"}</div>',
                    '<a class="top" href="#top">top</a>', '</div>']
            if any(line.strip() for line in code):
                card.append(f'<pre>{colour(chr(10).join(code).rstrip())}</pre>')
            card.append('</div>')
            entries.append('\n'.join(card))
        if not entries:
            continue
        nav.append(f'<a class="sec" href="#{sid}">{html.escape(title)}</a>')
        if rule_links:
            nav.append(f'<div class="rules">{", ".join(rule_links)}</div>')
        body.append(f'<h2 id="{sid}">{html.escape(title)}</h2>\n' + '\n'.join(entries))
    legend = ''.join(f'<span><i class="dot {cls}"></i>{name} ({counts.get(cls, 0)})</span>'
                     for name, cls in (('built', 'built'), ('planned / postponed / partial', 'planned'),
                                       ('rejected', 'rejected'), ('not built yet', 'notbuilt')))
    return '\n'.join([
        '<!DOCTYPE html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<title>Fusion Grammar</title>', f'<style>{CSS}</style>', '</head>', '<body>',
        '<header id="top"><h1>Fusion grammar</h1>',
        '<p class="sub">files/fusion.ebnf, one card per entry - written by tools/ebnf_html.py; do not edit by hand. '
        'A task links to files/FEATURES.md (a finished one to the archive), a decision to Decisions.md.</p>',
        f'<div class="legend">{legend}</div>', intro, '</header>',
        '<div class="layout">', '<nav>' + '\n'.join(nav) + '</nav>', '<main>', '\n'.join(body), '</main>', '</div>',
        '</body>', '</html>', ''])


def main(argv) -> int:
    page = build_page(EBNF.read_text(encoding='utf-8'))
    if '--check' in argv:
        if not PAGE.exists() or PAGE.read_text(encoding='utf-8') != page:
            print('files/fusion.ebnf.html is out of date - fix: python tools/ebnf_html.py')
            return 1
        return 0
    PAGE.write_text(page, encoding='ascii', newline='\n')
    print(f'wrote {PAGE.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
