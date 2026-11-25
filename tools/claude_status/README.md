# Claude Status - usage and task progress in VS Code's status bar

A small helper for working on Fusion with Claude Code (CLAUDE.md Rule 9). In the status bar, on the left:

```text
Claude 18% · 3h 1m left  |  Task 23%: check.py: examples (3/13)
```

- **Claude 18% · 3h 1m left** - the current 5-hour block: how much is used and how long is left. An **estimate**
  from [ccusage](https://github.com/ccusage/ccusage), which reads Claude Code's logs on this PC; the limit is the
  largest earlier block in those logs, not your plan's own limit (the Account & Usage button in Claude Code shows
  that). Refreshed every 5 minutes; yellow from 75%, red from 90%. Hover for the details, click to refresh now
- **Task 23%: ...** - what is running: `python check.py` writes each stage as it runs, and anyone (or Claude) can set
  it with `task_status.py`; it shows a tick when done, a cross when failed, and nothing when idle

## Files

| File | What it does |
|---|---|
| `usage_status.py` | Runs `npx ccusage blocks --json` and prints the estimate - two lines for chat, `--json` for the extension, `--limit N` for a limit of your own |
| `task_status.py` | Sets the task: `python tools/claude_status/task_status.py "47.10 parser" 2 5` (40%, 2/5); `--done`, `--failed`, `--idle` |
| `vscode-extension/` | The VS Code extension (`package.json`, `extension.js` - no build step) |

The live task status is `tools/local/task_status.json` - `tools/local/` is git ignored; the extension creates it.

## Install

Needs Node.js (for `npx ccusage`) and Python on the PATH.

1. Copy `vscode-extension/` into VS Code's extensions folder as `local.claude-status-0.0.1`:
   - Windows (PowerShell): `Copy-Item -Recurse tools\claude_status\vscode-extension "$env:USERPROFILE\.vscode\extensions\local.claude-status-0.0.1"`
   - macOS / Linux: `cp -r tools/claude_status/vscode-extension ~/.vscode/extensions/local.claude-status-0.0.1`
2. In VS Code: `Ctrl+Shift+P` -> **Developer: Reload Window**
3. Open the Fusion folder - the item appears in the status bar (only in a folder that has `tools/claude_status/`)

After changing `extension.js`, copy it again and reload the window.

Settings (File > Preferences > Settings, "Claude Status"): `claudeStatus.python` (the Python to run, default
`python`), `claudeStatus.refreshMinutes` (default 5).
