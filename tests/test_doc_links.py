"""The link check for the Markdown documents (Task 51.6 - tools/doc_links.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
from doc_links import link_problems, slug  # noqa: E402


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    return path


def test_good_links_pass(tmp_path):
    write(tmp_path / 'b.md', '# Title\n\n## Two Words `code`\n\n<a id="task-5"></a>\n')
    a = write(tmp_path / 'a.md', '[b](b.md) [h](b.md#two-words-code) [t](b.md#task-5) [self](#here)\n\n## Here\n')
    assert link_problems(tmp_path, [a]) == []


def test_missing_file_and_anchor_reported(tmp_path):
    write(tmp_path / 'b.md', '# Title\n')
    a = write(tmp_path / 'a.md', '[x](missing.md)\n[y](b.md#nope)\n')
    problems = link_problems(tmp_path, [a])
    assert len(problems) == 2
    assert 'missing.md - no such file' in problems[0]
    assert 'no heading or anchor "nope"' in problems[1]


def test_web_links_and_code_skipped(tmp_path):
    a = write(tmp_path / 'a.md', '[w](https://example.com) `[c](gone.md)`\n```\n[d](gone.md)\n```\n')
    assert link_problems(tmp_path, [a]) == []


def test_repeated_headings_and_links_in_headings(tmp_path):
    a = write(tmp_path / 'a.md', '## Index\n## Same\n## Same\n## Task [index](#index)\n[1](#same) [2](#same-1) [3](#task-index)\n')
    assert link_problems(tmp_path, [a]) == []
    assert slug('Proposed `fusion fmt` - Code') == 'proposed-fusion-fmt---code'
