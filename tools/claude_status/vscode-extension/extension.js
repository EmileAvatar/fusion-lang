// Claude Status: in VS Code's status bar -
//   Claude 14% - 3h 12m left  |  Task 40%: check.py: tests (1/13)
// The usage part runs tools/claude_status/usage_status.py --json (an estimate from ccusage) every few minutes;
// the task part watches tools/local/task_status.json (git ignored), written by check.py and
// tools/claude_status/task_status.py.
// Yellow from 75% used, red from 90% (CLAUDE.md Rule 9). Click: refresh the usage now.
const vscode = require('vscode');
const cp = require('child_process');
const fs = require('fs');
const path = require('path');

function activate(context) {
  const folder = (vscode.workspace.workspaceFolders || []).map(f => f.uri.fsPath)
    .find(p => fs.existsSync(path.join(p, 'tools', 'claude_status', 'usage_status.py')));
  if (!folder) {
    return;
  }
  const scripts = path.join(folder, 'tools', 'claude_status');
  const local = path.join(folder, 'tools', 'local');
  fs.mkdirSync(local, { recursive: true });            // git ignored - check.py writes its progress here once it exists
  const statusFile = path.join(local, 'task_status.json');
  const item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  item.command = 'claudeStatus.refresh';
  item.show();
  context.subscriptions.push(item);

  let usage = 'Claude ...';
  let usageTip = 'Reading the usage estimate...';
  let percent = null;
  let task = '';
  let taskTip = '';
  let busy = false;

  function render() {
    item.text = `$(sparkle) ${usage}` + (task ? `  |  ${task}` : '');
    item.tooltip = `${usageTip}\n\n${taskTip || 'No task running'}\n\nClick to refresh the usage now.`;
    item.backgroundColor = percent === null ? undefined
      : percent >= 90 ? new vscode.ThemeColor('statusBarItem.errorBackground')
      : percent >= 75 ? new vscode.ThemeColor('statusBarItem.warningBackground') : undefined;
  }

  function refreshUsage() {
    if (busy) {
      return;
    }
    busy = true;
    const python = vscode.workspace.getConfiguration('claudeStatus').get('python', 'python');
    cp.execFile(python, [path.join(scripts, 'usage_status.py'), '--json'], { cwd: folder, timeout: 180000, windowsHide: true },
      (error, stdout) => {
        busy = false;
        try {
          if (error) {
            throw error;
          }
          const data = JSON.parse(stdout.trim().split(/\r?\n/).pop());
          percent = data.percent;
          usage = percent === null ? 'Claude ?' : `Claude ${Math.round(percent)}%` + (data.leftTime ? ` \u00b7 ${data.leftTime} left` : '');
          const millions = n => (n / 1000000).toFixed(1) + ' million';
          usageTip = data.limit
            ? `Estimate Used: ${millions(data.used)} tokens, ${percent}% of the estimated limit (${millions(data.limit)}).\n` +
              `Estimate Left: ${millions(Math.max(0, data.limit - data.used))} tokens, with ${data.leftTime} to go.\n` +
              'An estimate from ccusage - the Account & Usage button shows the plan\'s own figure.'
            : 'No active 5-hour block yet.';
        } catch (e) {
          usage = 'Claude ?';
          usageTip = `The usage estimate failed: ${e.message || e}`;
        }
        render();
      });
  }

  function readTask() {
    let data = null;
    try {
      data = JSON.parse(fs.readFileSync(statusFile, 'utf8'));
    } catch (e) {
      data = null;
    }
    if (!data || data.state === 'idle' || !data.text) {
      task = '';
      taskTip = '';
    } else {
      const minutes = Math.round((Date.now() / 1000 - data.time) / 60);
      const count = data.total ? ` (${data.done}/${data.total})` : '';
      const share = data.percent !== null && data.percent !== undefined ? ` ${data.percent}%` : '';
      if (data.state === 'done') {
        task = `$(check) Task done: ${data.text}`;
      } else if (data.state === 'failed') {
        task = `$(error) Task failed: ${data.text}`;
      } else {
        const stale = minutes >= 60 ? ' (no news for an hour)' : '';
        task = `$(sync~spin) Task${share}: ${data.text}${stale}`;
      }
      taskTip = `Task: ${data.text}${count} - ${data.state}, updated ${minutes} min ago`;
    }
    render();
  }

  context.subscriptions.push(vscode.commands.registerCommand('claudeStatus.refresh', () => {
    usage = 'Claude ...';
    render();
    refreshUsage();
  }));
  fs.watchFile(statusFile, { interval: 1000 }, readTask);
  context.subscriptions.push({ dispose: () => fs.unwatchFile(statusFile) });
  const minutes = vscode.workspace.getConfiguration('claudeStatus').get('refreshMinutes', 5);
  const timer = setInterval(refreshUsage, Math.max(1, minutes) * 60000);
  context.subscriptions.push({ dispose: () => clearInterval(timer) });
  readTask();
  refreshUsage();
}

function deactivate() {}

module.exports = { activate, deactivate };
