"""The usage status for chat (CLAUDE.md Rule 9) and the status-bar extension (vscode-extension/).

    python tools/claude_status/usage_status.py           (--json for the extension)

Runs ccusage over this PC's Claude Code logs and prints:

    Estimate Used: 19.1 million tokens, which is 14.5% of the estimated limit.

    Estimate Left: 112.5 million tokens (85.5%), with 3h 14m to go.

    ---

The limit is ccusage's estimate - the largest completed 5-hour block in the logs (`-t max`), not the plan's own
limit (the Account & Usage button shows that). `--limit N` uses N tokens instead.
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone


def blocks() -> list:
    npx = shutil.which('npx') or shutil.which('npx.cmd')
    if npx is None:
        sys.exit('npx not found - install Node.js')
    result = subprocess.run([npx, '--yes', 'ccusage@latest', 'blocks', '--json'],
                            capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        sys.exit(result.stderr.strip() or 'ccusage failed')
    return json.loads(result.stdout)['blocks']


def millions(tokens: float) -> str:
    return f'{tokens / 1_000_000:.1f} million'


def main() -> None:
    limit = None
    if '--limit' in sys.argv:
        limit = int(sys.argv[sys.argv.index('--limit') + 1])
    all_blocks = [b for b in blocks() if not b.get('isGap')]
    active = next((b for b in all_blocks if b.get('isActive')), None)
    if active is None:
        if '--json' in sys.argv:
            print(json.dumps({'used': 0, 'limit': None, 'percent': 0, 'leftMinutes': None, 'leftTime': ''}))
            return
        print('Estimate: no active 5-hour block - nothing used yet in this one.')
        return
    if limit is None:
        done = [b['totalTokens'] for b in all_blocks if not b.get('isActive')]
        limit = max(done) if done else None
    used = active['totalTokens']
    end = datetime.fromisoformat(active['endTime'].replace('Z', '+00:00'))
    minutes = max(0, int((end - datetime.now(timezone.utc)).total_seconds() // 60))
    left_time = f'{minutes // 60}h {minutes % 60}m'
    if '--json' in sys.argv:              # for the status-bar extension
        print(json.dumps({'used': used, 'limit': limit, 'percent': round(used / limit * 100, 1) if limit else None,
                          'leftMinutes': minutes, 'leftTime': left_time}))
        return
    if not limit:
        print(f'Estimate Used: {millions(used)} tokens - no earlier block to estimate a limit from.')
        print()
        print(f'Estimate Left: {left_time} to go.')
    else:
        share = used / limit * 100
        print(f'Estimate Used: {millions(used)} tokens, which is {share:.1f}% of the estimated limit.')
        print()
        print(f'Estimate Left: {millions(max(0, limit - used))} tokens ({100 - share:.1f}%), with {left_time} to go.')
        if share >= 90:
            print()
            print('STOP: 90% of the estimated limit used - no coding task goes on (CLAUDE.md Rule 9).')
    print()
    print('---')


if __name__ == '__main__':
    main()
