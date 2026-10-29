#!/usr/bin/env python3
"""One command to verify the Fusion compiler (Task 22.6).

Replaces the commands that used to be run by hand after every change, and prints a short
summary - full output only for what failed:

    python check.py                   everything below
    python check.py --quick           unit tests only
    python check.py --status          open items from FEATURES.md + the next action (no build)
    python check.py --build-examples  write SYNTAX_REFERENCE.md programs to examples/, build
                                      every example (.c + .exe), regenerate #list.csv and
                                      #run.bat (Task 23 - see examples/CLAUDE.md)
    python check.py --fix-ascii       non-ASCII characters -> \\uXXXX escapes, only where the
                                      meaning stays the same; the rest is listed (Task 22.8)
    python check.py --ship "message" [--claude]
                                      every check; only if all pass: commit everything (with
                                      the Claude co-author line if --claude) and push (22.9)
    python check.py --example NAME [args]
                                      build and run one example (a file or a project folder),
                                      compare with its expected output (22.10)
    python check.py --builtins        write files/Builtins.md from the compiler (28.1.4)
    python check.py --runtime         write runtime/fusion_runtime.h from the compiler (28.1.3)
    python check.py --selfhost        build the Fusion-written compiler (selfhost/), build every
                                      tier 1 program with both compilers, compare what they
                                      print (and the leak check), with timings (28.7)

Checks:
    tests     pytest (every end-to-end test already runs under the string leak check)
    examples  tests/verify_examples.py - compile, run, compare output
    leaks     every examples/*.fusion and every SYNTAX_REFERENCE.md program, built with
              -DFUSION_LEAK_CHECK and run: exit 3 = a string never freed, 4 = freed twice
    reference every ```fusion block in SYNTAX_REFERENCE.md compiles and runs (exit 0), and
              its copy in examples/ is up to date
    builtins  files/Builtins.md matches the compiler's built-in functions and methods
    runtime   runtime/fusion_runtime.h matches the run-time the compiler writes into C files
    ascii     no non-ASCII characters in .py / .fusion files (CLAUDE.md Rule 2)

Exit code 0 only if everything passed.
"""

import csv
import datetime
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT / 'examples'
sys.path.insert(0, str(ROOT))

# SYNTAX_REFERENCE.md: `<!-- example: <file name> | task: <task> -->` right above a block
EXAMPLE_MARKER = re.compile(r'<!-- example: (\S+) \| task: (\S+) -->\n```fusion\n(.*?)```', re.S)

# Hand-written demos without "(Task N)" in their first line
DEMO_TASKS = {'arrays_demo': '09', 'const_demo': '08'}


def run(cmd, **kwargs):
    # Empty input: a program that reads input (readLine, Task 18.5.4) sees its end at once
    # instead of waiting for the console
    # FUSION_NO_NEW_CONFIG: compiling never writes a fusion.toml into the repo (Task 31)
    env = dict(os.environ, FUSION_NO_NEW_CONFIG='1')
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                          errors='replace', stdin=subprocess.DEVNULL, env=env, **kwargs)


# ---------------------------------------------------------------- individual checks

def check_tests():
    result = run([sys.executable, '-m', 'pytest', 'tests/', '-q', '-p', 'no:cacheprovider'])
    summary = next((line for line in reversed(result.stdout.splitlines()) if ' in ' in line), '')
    summary = summary.strip('= ').strip()
    detail = '\n'.join(line for line in result.stdout.splitlines()
                       if line.startswith(('FAILED', 'ERROR')))
    return result.returncode == 0, summary or 'no summary', detail or result.stdout[-2000:]


def check_examples():
    result = run([sys.executable, 'tests/verify_examples.py'])
    match = re.search(r'Output Matches:\s+(\d+)/(\d+)', result.stdout)
    if not match:
        return False, 'did not run', result.stdout[-2000:] + result.stderr[-2000:]
    ok = match.group(1) == match.group(2) and result.returncode == 0
    detail = '\n'.join(line for line in result.stdout.splitlines()
                       if 'FAIL' in line or 'Mismatch' in line or 'WARN' in line)
    return ok, f'{match.group(1)}/{match.group(2)}', detail


def compile_and_run_leak_checked(source: str, source_path: str):
    """Compile Fusion source the way main.py does, but with the leak check on, and run it.
    A program with imports brings in its modules (Task 18.4.4).

    Returns (exit_code, output) - exit_code None means it didn't compile."""
    from src.semantic import SemanticAnalyzer
    from src.codegen import CCodeGenerator
    from src.config import load_project_config
    from src.modules import load_program, make_file_parser

    config = load_project_config(source_path)
    try:
        parse = make_file_parser(config)
        ast, import_errors = load_program(source_path, parse(source, source_path), parse)
        if import_errors:
            return None, '\n'.join(str(e) for e in import_errors)
        analyzer = SemanticAnalyzer(structs_config=config.structs, strings_config=config.strings,
                                    stdlib_config=config.stdlib, errors_config=config.errors,
                                    numbers_config=config.numbers,
                                    modules_config=config.modules,
                                    conditions_config=config.conditions)
        if not analyzer.analyze(ast):
            return None, '\n'.join(str(e) for e in analyzer.get_errors())
        c_code = CCodeGenerator(encoding=config.strings.encoding,
                                max_length=config.strings.max_length,
                                safety_mode=config.safety_mode,
                                max_call_depth=config.max_call_depth,
                                overflow_wrap=config.numbers.overflow_wrap).generate(ast)
    except Exception as e:  # report, don't crash the checker
        return None, f'{type(e).__name__}: {e}'

    with tempfile.TemporaryDirectory() as tmp:
        c_file = os.path.join(tmp, 'leak.c')
        exe = os.path.join(tmp, 'leak.exe')
        with open(c_file, 'w', encoding='utf-8') as f:
            f.write(c_code)
        build = run(['gcc', '-DFUSION_LEAK_CHECK', c_file, '-o', exe, '-lm'])
        if build.returncode != 0:
            return None, build.stderr[-1500:]
        program = run([exe], timeout=60)
        return program.returncode, program.stdout + program.stderr


def reference_programs():
    """Every ```fusion block - a single-file example program. A block fenced as
    ```fusion multi-file (part of a project of several files) is documentation only."""
    text = (ROOT / 'SYNTAX_REFERENCE.md').read_text(encoding='utf-8')
    return re.findall(r'```fusion\n(.*?)```', text, re.S)


def reference_examples():
    """(file name, task, code) for every marked SYNTAX_REFERENCE.md program."""
    text = (ROOT / 'SYNTAX_REFERENCE.md').read_text(encoding='utf-8')
    return EXAMPLE_MARKER.findall(text)


def check_reference_sync():
    """Every reference program is marked, and its copy in examples/ matches."""
    examples = reference_examples()
    problems = []
    if len(examples) != len(reference_programs()):
        problems.append('a ```fusion block in SYNTAX_REFERENCE.md has no '
                        '<!-- example: name | task: N --> marker above it')
    for name, _, code in examples:
        path = EXAMPLES / f'{name}.fusion'
        if not path.exists() or path.read_text(encoding='utf-8') != code:
            problems.append(f'examples/{name}.fusion is missing or out of date')
    if problems:
        problems.append('fix: python check.py --build-examples')
    return not problems, f'{len(examples)} in sync' if not problems else 'out of sync', \
        '\n'.join(problems)


def check_builtins():
    """files/Builtins.md is what tools/builtins_doc.py makes from the compiler (28.1.4)."""
    from tools.builtins_doc import render
    text, problems = render()
    path = ROOT / 'files' / 'Builtins.md'
    if not path.exists() or path.read_text(encoding='utf-8') != text:
        problems.append('files/Builtins.md is missing or out of date - fix: python check.py --builtins')
    return not problems, 'up to date' if not problems else 'out of date', '\n'.join(problems)


def write_builtins():
    from tools.builtins_doc import render
    text, problems = render()
    (ROOT / 'files' / 'Builtins.md').write_text(text, encoding='utf-8', newline='\n')
    print('wrote files/Builtins.md')
    for problem in problems:
        print(problem)
    return 1 if problems else 0


def check_runtime():
    """runtime/fusion_runtime.h is the compiler's current run-time (28.1.3)."""
    from src.codegen.c_generator import runtime_header_text
    path = ROOT / 'runtime' / 'fusion_runtime.h'
    if path.exists() and path.read_text(encoding='utf-8') == runtime_header_text():
        return True, 'up to date', ''
    return False, 'out of date', 'runtime/fusion_runtime.h is missing or out of date - fix: python check.py --runtime'


def selfhost_report():
    """Task 28.7: the Fusion-written compiler against the Python one, program by program."""
    import shutil
    import time
    from tests.test_runtime_header import TIER_1
    started = time.perf_counter()
    built = run([sys.executable, 'main.py', 'selfhost/main.fusion'], timeout=300)
    if built.returncode != 0:
        print('[FAIL] building selfhost/main.fusion:\n' + built.stdout + built.stderr)
        return 1
    print(f'built selfhost/main.exe in {time.perf_counter() - started:.1f} s')
    exe = ROOT / 'selfhost' / 'main.exe'
    same = 0
    totals = [0.0, 0.0]
    print(f'{"program":36} {"python":>8} {"selfhost":>9}  result')
    for name in TIER_1:
        with tempfile.TemporaryDirectory() as tmp:
            folders = [Path(tmp) / 'python', Path(tmp) / 'selfhost']
            for folder in folders:
                folder.mkdir()
                shutil.copy(EXAMPLES / f'{name}.fusion', folder)
            times = []
            t = time.perf_counter()
            a = run([sys.executable, 'main.py', str(folders[0] / f'{name}.fusion')], timeout=120)
            times.append(time.perf_counter() - t)
            t = time.perf_counter()
            b = run([str(exe), str(folders[1] / f'{name}.fusion'), '--leak-check',
                     '--runtime', str(ROOT / 'runtime')], timeout=120)
            times.append(time.perf_counter() - t)
            totals = [totals[0] + times[0], totals[1] + times[1]]
            if a.returncode != 0 or b.returncode != 0:
                result = 'BUILD FAILED: ' + (b.stdout or a.stderr).strip().splitlines()[-1][:80]
            else:
                outputs = [run([str(f / f'{name}.exe'), '--headless'], timeout=60) for f in folders]
                ok = (outputs[0].returncode, outputs[0].stdout) == (outputs[1].returncode, outputs[1].stdout)
                same += ok
                result = 'same' if ok else f'DIFFERENT (exit {outputs[0].returncode} / {outputs[1].returncode})'
        print(f'{name:36} {times[0]:7.2f}s {times[1]:8.2f}s  {result}')
    print(f'{"total":36} {totals[0]:7.2f}s {totals[1]:8.2f}s')
    print(f'\n{same}/{len(TIER_1)} the same (output, exit code, leak check) - both times include GCC')
    return 0 if same == len(TIER_1) else 1


def write_runtime():
    from src.codegen.c_generator import runtime_header_text
    path = ROOT / 'runtime' / 'fusion_runtime.h'
    path.parent.mkdir(exist_ok=True)
    path.write_text(runtime_header_text(), encoding='utf-8', newline='\n')
    print('wrote runtime/fusion_runtime.h')
    return 0


def example_sources():
    """Every example program: examples/*.fusion, and the main file of each example project
    of several files, examples/<name>/main.fusion (Task 18.4.4)."""
    return sorted(EXAMPLES.glob('*.fusion')) + sorted(EXAMPLES.glob('*/main.fusion'))


def example_name(path: Path) -> str:
    """An example's name: its file name, or for a project its folder (shop/main)."""
    return path.stem if path.parent == EXAMPLES else f'{path.parent.name}/{path.stem}'


def example_task(path: Path, reference_tasks: dict) -> str:
    if path.stem in reference_tasks:
        return reference_tasks[path.stem]
    first = path.read_text(encoding='utf-8').splitlines()[:1]
    match = re.search(r'\(Task ([\w.]+)\)', first[0]) if first else None
    return match.group(1) if match else DEMO_TASKS.get(path.stem, '01-04')


def first_added(path: Path) -> str:
    """The date a file first appeared in git, or today for a new one."""
    result = run(['git', 'log', '--diff-filter=A', '--follow', '--format=%as', '--',
                  str(path.relative_to(ROOT))])
    dates = result.stdout.split()
    return dates[-1] if dates else datetime.date.today().isoformat()


def build_examples():
    """Task 23: write the reference programs to examples/, build every example, and
    regenerate #list.csv and #run.bat (both local-only, see examples/CLAUDE.md)."""
    examples = reference_examples()
    reference_tasks = {name: task for name, task, _ in examples}
    for name, _, code in examples:
        path = EXAMPLES / f'{name}.fusion'
        if not path.exists() or path.read_text(encoding='utf-8') != code:
            path.write_text(code, encoding='utf-8', newline='')
            print(f'wrote     examples/{path.name}')

    failures = []
    sources = example_sources()
    for path in sources:
        result = run([sys.executable, 'main.py', str(path.relative_to(ROOT))])
        if result.returncode != 0:
            failures.append(f'{path.name}:\n{result.stderr[-800:]}')

    list_file = EXAMPLES / '#list.csv'
    previous = {}
    if list_file.exists():
        with open(list_file, newline='', encoding='utf-8') as f:
            previous = {row['fusion']: row for row in csv.DictReader(f)}
    with open(list_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['fusion', 'c', 'exe', 'task', 'added'])
        for path in sources:
            name = example_name(path)
            added = previous.get(f'{name}.fusion', {}).get('added') or first_added(path)
            writer.writerow([f'{name}.fusion', f'{name}.c', f'{name}.exe',
                             example_task(path, reference_tasks), added])

    lines = ['@echo off', 'rem Generated by "python check.py --build-examples" - do not edit',
             'cd /d "%~dp0"']
    for path in sources:
        exe = example_name(path).replace('/', '\\') + '.exe'
        # --headless: each program closes by itself - the script pauses once at the end;
        # < nul: a program reading input (readLine) gets none instead of stopping the script
        lines += ['echo.', 'echo.', f'echo ---- {exe} ----', 'echo.', 'echo.',
                  f'".\\{exe}" --headless < nul']
    lines += ['echo.', 'pause']
    (EXAMPLES / '#run.bat').write_text('\r\n'.join(lines) + '\r\n', encoding='ascii')

    print(f'built     {len(sources) - len(failures)}/{len(sources)} examples; '
          f'#list.csv and #run.bat updated')
    for failure in failures:
        print('\n' + failure)
    return 0 if not failures else 1


def check_leaks():
    # Reference programs are checked from SYNTAX_REFERENCE.md itself; their copies in
    # examples/ (syntax_*) would only repeat them
    programs = [(example_name(p), p.read_text(encoding='utf-8'), str(p))
                for p in example_sources() if not p.name.startswith('syntax_')]
    # built as if in examples/ - where they live - so examples/fusion.toml applies
    programs += [(f'SYNTAX_REFERENCE #{i}', code, str(ROOT / 'examples' / 'reference.fusion'))
                 for i, code in enumerate(reference_programs(), 1)]
    failures = []
    for name, code, path in programs:
        exit_code, output = compile_and_run_leak_checked(code, path)
        if exit_code != 0:
            what = {None: 'did not compile', 3: 'string never freed', 4: 'string freed twice'}
            failures.append(f'{name}: {what.get(exit_code, f"exit {exit_code}")}\n'
                            f'{output.strip()[-800:]}')
    clean = len(programs) - len(failures)
    return not failures, f'{clean}/{len(programs)} clean', '\n\n'.join(failures)


def ascii_checked_files():
    return list((ROOT / 'src').rglob('*.py')) + list((ROOT / 'tests').glob('*.py')) + \
        list((ROOT / 'tools').rglob('*.py')) + \
        list((ROOT / 'examples').rglob('*.fusion')) + list((ROOT / 'files' / 'showcase').glob('*')) + \
        list((ROOT / 'selfhost').rglob('*.fusion')) + \
        [ROOT / 'main.py', ROOT / 'check.py']


def check_ascii():
    bad = []
    for path in ascii_checked_files():
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if any(ord(ch) > 127 for ch in line):
                bad.append(f'{path.relative_to(ROOT)}:{number}')
    return not bad, 'ok' if not bad else f'{len(bad)} line(s)', '\n'.join(bad[:20])


def escape_non_ascii(text: str) -> str:
    return ''.join(ch if ord(ch) < 128 else
                   ('\\u%04x' % ord(ch) if ord(ch) <= 0xFFFF else '\\U%08x' % ord(ch))
                   for ch in text)


def python_meaning(text: str, path: Path):
    import ast
    return ast.dump(ast.parse(text, str(path)))


def fusion_meaning(text: str, path: Path):
    """The token list without positions - string and char literals decoded, so `\\u00e9`
    and the character itself compare equal. Comments are not tokens."""
    from src.lexer.lexer import Lexer
    from src.lexer.token import TokenType
    from src.lexer.literals import decode_char_literal
    tokens = Lexer(text, str(path)).tokenize()
    return [(t.type, decode_char_literal(t.value) if t.type == TokenType.CHAR_LIT else t.value)
            for t in tokens]


def fix_ascii():
    """Task 22.8: turn non-ASCII characters into \\uXXXX escapes in the files the ascii check
    covers - but only where that changes nothing: a .py file must parse to the same AST, a
    .fusion file must lex to the same tokens. Anything else is listed for a manual fix."""
    fixed, manual = fix_ascii_files(ascii_checked_files())
    for line in fixed + manual:
        print(line)
    if not fixed and not manual:
        print('ascii     nothing to fix')
    return 0 if not manual else 1


def fix_ascii_files(paths):
    """Returns (fixed, manual) report lines."""
    fixed, manual = [], []
    for path in paths:
        text = path.read_text(encoding='utf-8')
        if text.isascii():
            continue
        new_text = escape_non_ascii(text)
        meaning = python_meaning if path.suffix == '.py' else fusion_meaning
        try:
            same = meaning(text, path) == meaning(new_text, path)
        except Exception:  # the escaped text no longer parses / lexes
            same = False
        name = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        if same:
            path.write_text(new_text, encoding='utf-8', newline='')
            fixed.append(f'fixed     {name}')
        else:
            lines = [n for n, line in enumerate(text.splitlines(), 1) if not line.isascii()]
            manual.append(f'by hand   {name}: line(s) {", ".join(map(str, lines[:10]))} - '
                          'escaping would change the meaning (raw string, identifier, ...)')
    return fixed, manual


# ---------------------------------------------------------------- status

def show_status():
    features = (ROOT / 'FEATURES.md').read_text(encoding='utf-8').splitlines()
    open_items = [line.strip() for line in features if line.strip().startswith('[ ]')]
    postponed = [line for line in features if '[POSTPONED' in line]
    # Finished items live in task/featuresArchive.md (archived 2026-10-27)
    archive = ROOT / 'task' / 'featuresArchive.md'
    archived = archive.read_text(encoding='utf-8').splitlines() if archive.exists() else []
    done = [line for line in archived + features if line.strip().startswith('[DONE]')
            or (line.startswith('#### ') and line.rstrip().endswith('[DONE]'))]
    print(f'FEATURES.md: {len(done)} done (task/featuresArchive.md), {len(open_items)} open, '
          f'{len(postponed)} postponed')
    # The next open sub-tasks, in the order FEATURES.md lists them
    for line in [item for item in open_items if re.match(r'\[ \] \d+\.', item)][:8]:
        print('  ' + line)
    summary = (ROOT / 'taskSummary2.md').read_text(encoding='utf-8').splitlines()
    for line in reversed(summary):
        if 'Next Action' in line:
            print('Next:', line.split('Next Action:**', 1)[-1].strip())
            break


# ---------------------------------------------------------------- one example

def find_example(name: str):
    """examples/NAME.fusion, or the project examples/NAME/main.fusion."""
    for path in (EXAMPLES / f'{name}.fusion', EXAMPLES / name / 'main.fusion'):
        if path.exists():
            return path
    return None


def run_example(name: str, program_args):
    """Task 22.10: build one example, run it (headless, no input, with any arguments given
    after its name) and compare with its expected output in tests/verify_examples.py."""
    path = find_example(name)
    if path is None:
        names = ', '.join(example_name(p).replace('/main', '') for p in example_sources())
        print(f'No example called {name!r}. Examples: {names}')
        return 1
    build = run([sys.executable, 'main.py', str(path.relative_to(ROOT))])
    if build.returncode != 0:
        print(f'build     [FAIL]\n{(build.stdout + build.stderr).strip()[-2000:]}')
        return 1
    program = run([str(path.with_suffix('.exe')), '--headless', *program_args], timeout=60)
    print(program.stdout + program.stderr, end='')
    sys.path.insert(0, str(ROOT / 'tests'))
    from verify_examples import EXPECTED_OUTPUTS
    expected = EXPECTED_OUTPUTS.get(path.parent.name if path.name == 'main.fusion' else path.stem)
    if program.returncode != 0:
        print(f'example   [FAIL] exit code {program.returncode}')
        return 1
    if expected is None or program_args:
        print('example   [OK]   ran (no expected output to compare)')
        return 0
    missing = [line for line in expected.split('\n')
               if line.strip() and line not in program.stdout]
    print('example   ' + ('[OK]   output matches' if not missing else
                          '[FAIL] expected but missing:\n  ' + '\n  '.join(missing)))
    return 0 if not missing else 1


# ---------------------------------------------------------------- ship

CO_AUTHOR = 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'


def ship(message: str, claude: bool):
    """Task 22.9: every check, then - only if all pass - commit everything and push."""
    if not message or message.startswith('--'):
        print('usage: python check.py --ship "commit message" [--claude]')
        return 2
    if not run_checks(quick=False):
        print('\nnot shipped - a check failed')
        return 1

    def git(*args):
        return run(['git', *args])

    git('add', '-A')
    if git('diff', '--cached', '--quiet').returncode == 0:
        print('\nnothing to commit')
        return 0
    full_message = message + (f'\n\n{CO_AUTHOR}' if claude else '')
    commit = git('commit', '-q', '-m', full_message)
    if commit.returncode != 0:
        print(f'\ncommit failed:\n{commit.stdout}{commit.stderr}')
        return 1
    print('\ncommitted ' + git('log', '--oneline', '-1').stdout.strip())
    push = git('push', '-q')
    if push.returncode != 0:
        print(f'push failed:\n{push.stderr.strip()}')
        return 1
    print('pushed')
    return 0


# ---------------------------------------------------------------- main

def option_value(argv, option):
    index = argv.index(option)
    return argv[index + 1] if index + 1 < len(argv) else ''


def main(argv):
    if '--status' in argv:
        show_status()
        return 0
    if '--build-examples' in argv:
        return build_examples()
    if '--fix-ascii' in argv:
        return fix_ascii()
    if '--builtins' in argv:
        return write_builtins()
    if '--runtime' in argv:
        return write_runtime()
    if '--selfhost' in argv:
        return selfhost_report()
    if '--example' in argv:
        index = argv.index('--example')
        return run_example(option_value(argv, '--example'), argv[index + 2:])
    if '--ship' in argv:
        return ship(option_value(argv, '--ship'), '--claude' in argv)
    return 0 if run_checks(quick='--quick' in argv) else 1


def run_checks(quick: bool) -> bool:
    checks = [('tests', check_tests)]
    if not quick:
        checks += [('examples', check_examples), ('leaks', check_leaks),
                   ('reference', check_reference_sync), ('builtins', check_builtins),
                   ('runtime', check_runtime),
                   ('ascii', check_ascii)]
    all_ok = True
    details = []
    for name, check in checks:
        ok, summary, detail = check()
        all_ok &= ok
        print(f'{name:9} {"[OK]  " if ok else "[FAIL]"} {summary}')
        if not ok and detail:
            details.append(f'--- {name} ---\n{detail}')
    for block in details:
        print('\n' + block)
    return all_ok


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
