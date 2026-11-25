"""Set the task part of the status bar (tools/claude_status/vscode-extension).

    python tools/claude_status/task_status.py "47.10 parser" 2 5     ->  Task 40%: 47.10 parser (2/5)
    python tools/claude_status/task_status.py "47.10 building"      ->  Task: 47.10 building
    python tools/claude_status/task_status.py "47.10 shipped" --done
    python tools/claude_status/task_status.py --idle

check.py writes the same file by itself while it runs (task_progress).
"""

import json
import sys
import time
from pathlib import Path

# The live status - in tools/local/ (git ignored), where check.py writes it too
STATUS = Path(__file__).resolve().parents[1] / 'local' / 'task_status.json'


def main(argv) -> None:
    if '--idle' in argv:
        data = {'text': '', 'percent': None, 'state': 'idle', 'time': time.time()}
    else:
        words = [a for a in argv if not a.startswith('--')]
        if not words:
            sys.exit(__doc__)
        text = words[0]
        done = int(words[1]) if len(words) > 1 else None
        total = int(words[2]) if len(words) > 2 else None
        percent = round(done * 100 / total) if done is not None and total else None
        state = 'done' if '--done' in argv else 'failed' if '--failed' in argv else 'running'
        data = {'text': text, 'percent': percent, 'done': done, 'total': total, 'state': state, 'time': time.time()}
    STATUS.parent.mkdir(exist_ok=True)
    STATUS.write_text(json.dumps(data), encoding='utf-8')


if __name__ == '__main__':
    main(sys.argv[1:])
