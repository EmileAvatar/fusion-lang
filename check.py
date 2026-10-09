#!/usr/bin/env python3
"""One command to verify the Fusion compiler (Task 22.6).

Replaces the commands that used to be run by hand after every change, and prints a short
summary - full output only for what failed:

    python check.py            everything below
    python check.py --quick    unit tests only
    python check.py --status   open items from FEATURES.md + the next action (no build)

Checks:
    tests     pytest (every end-to-end test already runs under the string leak check)
    examples  tests/verify_examples.py - compile, run, compare output
    leaks     every examples/*.fusion and every SYNTAX_REFERENCE.md program, built with
              -DFUSION_LEAK_CHECK and run: exit 3 = a string never freed, 4 = freed twice
    reference every ```fusion block in SYNTAX_REFERENCE.md compiles and runs (exit 0)
    ascii     no non-ASCII characters in .py / .fusion files (CLAUDE.md Rule 2)

Exit code 0 only if everything passed.
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def run(cmd, **kwargs):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                          errors='replace', **kwargs)


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

    Returns (exit_code, output) - exit_code None means it didn't compile."""
    from src.lexer import Lexer
    from src.parser.parser import Parser
    from src.semantic import SemanticAnalyzer
    from src.codegen import CCodeGenerator
    from src.config import load_project_config

    config = load_project_config(source_path)
    try:
        lexer = Lexer(source, source_path, tab_width=config.indentation.tab_width,
                      allow_mixed=config.indentation.allow_mixed,
                      allow_unicode_identifiers=config.source.allow_unicode_identifiers)
        ast = Parser(lexer.tokenize()).parse_program()
        analyzer = SemanticAnalyzer(structs_config=config.structs)
        if not analyzer.analyze(ast):
            return None, '\n'.join(str(e) for e in analyzer.get_errors())
        c_code = CCodeGenerator().generate(ast)
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
    text = (ROOT / 'SYNTAX_REFERENCE.md').read_text(encoding='utf-8')
    return re.findall(r'```fusion\n(.*?)```', text, re.S)


def check_leaks():
    programs = [(p.name, p.read_text(encoding='utf-8'), str(p))
                for p in sorted((ROOT / 'examples').glob('*.fusion'))]
    programs += [(f'SYNTAX_REFERENCE #{i}', code, str(ROOT / 'reference.fusion'))
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


def check_ascii():
    files = list((ROOT / 'src').rglob('*.py')) + list((ROOT / 'tests').glob('*.py')) + \
        list((ROOT / 'examples').glob('*.fusion')) + [ROOT / 'main.py', ROOT / 'check.py']
    bad = []
    for path in files:
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if any(ord(ch) > 127 for ch in line):
                bad.append(f'{path.relative_to(ROOT)}:{number}')
    return not bad, 'ok' if not bad else f'{len(bad)} line(s)', '\n'.join(bad[:20])


# ---------------------------------------------------------------- status

def show_status():
    features = (ROOT / 'FEATURES.md').read_text(encoding='utf-8').splitlines()
    open_items = [line.strip() for line in features if line.strip().startswith('[ ]')]
    postponed = [line for line in features if '[POSTPONED' in line]
    done = [line for line in features if '[DONE]' in line]
    print(f'FEATURES.md: {len(done)} done, {len(open_items)} open, {len(postponed)} postponed')
    active = [line.strip() for line in features
              if line.strip().startswith('[ ]') and re.match(r'\[ \] (18|22)\.', line.strip())]
    for line in active:
        print('  ' + line)
    summary = (ROOT / 'taskSummary2.md').read_text(encoding='utf-8').splitlines()
    for line in reversed(summary):
        if 'Next Action' in line:
            print('Next:', line.split('Next Action:**', 1)[-1].strip())
            break


# ---------------------------------------------------------------- main

def main(argv):
    if '--status' in argv:
        show_status()
        return 0
    checks = [('tests', check_tests)]
    if '--quick' not in argv:
        checks += [('examples', check_examples), ('leaks', check_leaks), ('ascii', check_ascii)]
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
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
