"""Tests for Task 49.9 - the Decisions.md check in check.py (CLAUDE.md Rule 3b).

Each test is one way the file can go out of shape; the real file must pass.
"""

import pytest

from check import ROOT, decision_problems

GOOD = """#### SYN - syntax
SYN.001 [BUILT] Three block styles
SYN.002 [PLANNED] Duration literals

#### MEM - memory
MEM.001 [DESIGN] A GC as an option

| ID | Decision | Feature | Since | Detail | Status |
|---|---|---|---|---|---|
| D.001 | Blocks: any style | SYN.001 | 2026-10-31 | - | ACTIVE |
| D.002 | No GC by default | MEM | 2026-10-31 | - | ACTIVE |
| C.001 | **CLASH:** two rules disagree | MEM.001 | - | - | CLASH - check |
"""


def test_a_file_in_shape_has_no_problems():
    assert decision_problems(GOOD) == []


def test_the_real_file_is_in_shape():
    assert decision_problems((ROOT / 'Decisions.md').read_text(encoding='utf-8')) == []


@pytest.mark.parametrize('old, new, problem', [
    ('SYN.002 [PLANNED]', 'SYN.003 [PLANNED]', 'SYN.003 - expected SYN.002'),           # a gap
    ('SYN.002 [PLANNED]', 'SYN.001 [PLANNED]', 'SYN.001 - expected SYN.002'),           # a repeat
    ('SYN.002 [PLANNED]', 'SYN.002 [MAYBE]', 'not "AREA.NNN [BUILT|PLANNED'),           # an unknown status
    ('MEM.001 [DESIGN]', 'SYN.003 [DESIGN]', 'SYN.003 is under the MEM heading'),       # the wrong area
    ('| D.002 |', '| D.003 |', 'D.003 - expected D.002'),                               # decisions out of order
    ('| SYN.001 | 2026', '| SYN.009 | 2026', 'names feature "SYN.009"'),                # a feature that doesn't exist
    ('| C.001 | **CLASH:**', '| C.001 | **NOTE:**', 'C.001 is not marked CLASH'),
])
def test_each_problem_is_reported(old, new, problem):
    broken = GOOD.replace(old, new)
    assert broken != GOOD
    assert any(problem in p for p in decision_problems(broken)), decision_problems(broken)
