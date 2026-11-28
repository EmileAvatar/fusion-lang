#!/usr/bin/env python3
"""Fusion compiler main entry point.

This is the main entry point for the Fusion compiler. It performs:
1. Lexical analysis (tokenization)
2. Parsing (AST construction)
3. Semantic analysis (type checking, name resolution, validation)
4. Code generation (C code)
5. Compilation (GCC)

Usage:
    python main.py <source.fusion>
    python main.py run <script.fusion> [arguments]     (Task 58.3 - build once, then run it)
"""

import sys
import os
import subprocess
import hashlib
import io
import json
from contextlib import redirect_stderr

# The compiler itself is imported only when something is built (compile_file, print_interfaces) - a script whose
# kept program is current starts without it (Task 58.4: 0.25 s -> about 0.05 s)


# What the last compile_file used - `run` keeps it with the program (Task 58.3)
LAST_BUILD = {'files': [], 'settings': None}


def compile_file(source_path: str, out_base: str = None) -> int:
    """Compile a Fusion source file.

    Args:
        source_path: Path to the Fusion source file

    Returns:
        0 on success, 1 on error
    """
    from src.modules import load_program, make_file_parser
    from src.lexer import Lexer
    from src.parser.parser import Parser, ParserError
    from src.semantic import SemanticAnalyzer
    from src.codegen import CCodeGenerator
    from src.config import load_project_config, ProjectConfigError
    # Read source
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {source_path}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    # Project settings (Tasks 12.12, 31, 58.2) - a Fusion.Settings block first in the file, or settings.toml (or
    # .yaml / .json / .ini) next to the source file or in the current directory; none: every default - nothing is
    # written (D.227)
    try:
        project_config = load_project_config(source_path)
    except ProjectConfigError as e:
        print(f"Project configuration error: {e}", file=sys.stderr)
        return 1
    for message in project_config.messages:
        print(f"  [OK] Settings: {message}", file=sys.stderr)
    for warning in project_config.warnings:
        print(f"Settings warning: {warning}", file=sys.stderr)
    if project_config.source_path:
        print(f"  [OK] Settings from {os.path.basename(project_config.source_path)}", file=sys.stderr)

    # Lexical analysis
    print(f"[1/3] Lexical analysis...", file=sys.stderr)
    lexer = Lexer(
        source,
        source_path,
        tab_width=project_config.indentation.tab_width,
        allow_mixed=project_config.indentation.allow_mixed,
        allow_unicode_identifiers=project_config.source.allow_unicode_identifiers,
    )
    try:
        tokens = lexer.tokenize()
    except Exception as e:
        print(f"Lexer exception: {e}", file=sys.stderr)
        return 1

    # Lexer warnings (e.g. mixed tabs/spaces) were previously collected and then silently
    # dropped - print them, the same way semantic warnings are printed (Task 15.7 / 19.6.4)
    for warning in lexer.diagnostics.warnings:
        print(f"Lexer warning: {warning}", file=sys.stderr)

    if lexer.diagnostics.errors:
        for error in lexer.diagnostics.errors:
            print(f"Lexer error: {error}", file=sys.stderr)
        return 1

    print(f"  [OK] Generated {len(tokens)} tokens", file=sys.stderr)

    # Parsing
    print(f"[2/3] Parsing...", file=sys.stderr)
    parser = Parser(tokens)
    try:
        ast = parser.parse_program()
    except ParserError as e:
        print(f"Parser error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Parser exception: {e}", file=sys.stderr)
        return 1

    print(f"  [OK] Parsed {len(ast.declarations)} declarations", file=sys.stderr)

    # Modules (Task 18.4): load every imported module folder once and merge them in - every program goes
    # through it, for the main file's checks and Fusion's own full names (Fusion.Core.print - 57.5)
    had_imports = bool(ast.imports)
    ast, import_errors = load_program(source_path, ast, make_file_parser(project_config),
                                      project_config.libraries)
    LAST_BUILD['files'] = list(getattr(ast, 'source_files', []))
    LAST_BUILD['settings'] = project_config.source_path if project_config.source_path and \
        os.path.isfile(project_config.source_path) else None
    if import_errors:
        for error in import_errors:
            print(f"Error: {error}", file=sys.stderr)
        print(f"\n{len(import_errors)} error(s) found", file=sys.stderr)
        return 1
    if had_imports:
        print(f"  [OK] Loaded the imported modules", file=sys.stderr)

    # Semantic analysis
    print(f"[3/5] Semantic analysis...", file=sys.stderr)
    analyzer = SemanticAnalyzer.for_project(project_config)
    success = analyzer.analyze(ast)

    if not success:
        analyzer.print_diagnostics()
        return 1

    # Print warnings even on success
    if analyzer.get_warnings():
        analyzer.print_diagnostics()

    # [safety] mode = "strict" (Task 32.0): every warning is an error - absolute strictness
    if project_config.safety_mode == 'strict':
        count = (len(analyzer.get_warnings()) + len(lexer.diagnostics.warnings)
                 + len(project_config.warnings))
        if count:
            print(f"\n{count} warning(s) - errors in strict mode ([safety] mode = \"strict\")",
                  file=sys.stderr)
            return 1

    print(f"  [OK] Semantic analysis passed", file=sys.stderr)

    # Code generation
    print(f"[4/5] Code generation...", file=sys.stderr)
    generator = CCodeGenerator(encoding=project_config.strings.encoding,
                               max_length=project_config.strings.max_length,
                               safety_mode=project_config.safety_mode,
                               max_call_depth=project_config.max_call_depth,
                               wait_at_exit=project_config.build.wait_at_exit,
                               overflow_wrap=project_config.numbers.overflow_wrap)
    generator.rounding = project_config.numbers.rounding      # [numbers] rounding (47.8)
    generator.max_iterations = project_config.max_iterations    # [safety] maxIterations (56.5)
    try:
        c_code = generator.generate(ast)
    except Exception as e:
        print(f"Code generation error: {e}", file=sys.stderr)
        return 1

    # Write C code to file
    c_file = (out_base + '.c') if out_base else source_path.replace('.fusion', '.c')
    try:
        with open(c_file, 'w', encoding='utf-8') as f:
            f.write(c_code)
        print(f"  [OK] Generated C code: {c_file}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing C file: {e}", file=sys.stderr)
        return 1

    # Compile C code with GCC
    print(f"[5/5] Compiling C code...", file=sys.stderr)
    exe_suffix = '.exe' if sys.platform == 'win32' else ''
    exe_file = (out_base + exe_suffix) if out_base else source_path.replace('.fusion', exe_suffix)

    gcc_result = compile_c_to_executable(c_file, exe_file)
    if gcc_result != 0:
        return 1

    print(f"\n[OK] Compilation successful!", file=sys.stderr)
    print(f"  Executable: {exe_file}", file=sys.stderr)
    print(f"  Run with: {exe_file}", file=sys.stderr)

    return 0


def compile_c_to_executable(c_file: str, exe_file: str) -> int:
    """Compile C file to executable using GCC.

    Args:
        c_file: Path to C source file
        exe_file: Path to output executable

    Returns:
        0 on success, 1 on error
    """
    # GCC command
    gcc_cmd = ['gcc', c_file, '-o', exe_file, '-lm']

    try:
        result = subprocess.run(
            gcc_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"GCC compilation failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return 1

        print(f"  [OK] Compiled to executable: {exe_file}", file=sys.stderr)
        return 0

    except FileNotFoundError:
        print("Error: GCC not found. Please install GCC.", file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired:
        print("Error: GCC compilation timed out.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error running GCC: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Fusion Compiler v1.0", file=sys.stderr)
        print("Usage: fusion <source.fusion>", file=sys.stderr)
        print("       fusion <source.fusion> --interface [module]   "
              "(the public interface of the modules it imports)", file=sys.stderr)
        return 1

    if sys.argv[1] == 'run':                               # `run tidy.fusion [arguments]` (58.3, D.221)
        if len(sys.argv) < 3:
            print("Usage: python main.py run <script.fusion> [arguments]", file=sys.stderr)
            return 1
        return run_script(sys.argv[2], sys.argv[3:])
    source_path = sys.argv[1]
    if '--interface' in sys.argv[2:]:
        return print_interfaces(source_path, sys.argv[2:])
    return compile_file(source_path)


# ---------------------------------------------------------------- run: a script built once (Task 58.3, D.221, D.223)

def _file_hash(path: str) -> str:
    try:
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return ''


def compiler_version() -> str:
    """The compiler's own source as one hash - each file's name, size and time (cheap; a changed time, from a sync
    say, at worst builds a script once more) - a kept script is built again when the compiler changes."""
    root = os.path.dirname(os.path.abspath(__file__))
    digest = hashlib.sha256()
    paths = [os.path.abspath(__file__)]
    for folder, _, files in sorted(os.walk(os.path.join(root, 'src'))):
        paths += [os.path.join(folder, n) for n in sorted(files) if n.endswith(('.py', '.fusion'))]
    for path in paths:
        info = os.stat(path)
        digest.update(f'{path}|{info.st_size}|{info.st_mtime_ns}'.encode())
    return digest.hexdigest()


def script_cache_folder(script: str) -> str:
    """Where a script's program is kept (D.223): the user's cache folder - %LOCALAPPDATA%\\Fusion\\cache on
    Windows, ~/.cache/fusion elsewhere (FUSION_CACHE overrides it) - one folder per script; next to the script
    (.fusion-cache) where that can't be written."""
    script = os.path.abspath(script)
    name = os.path.splitext(os.path.basename(script))[0] + '-' + hashlib.sha256(script.encode()).hexdigest()[:12]
    base = os.environ.get('FUSION_CACHE') or (
        os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'Fusion', 'cache')
        if sys.platform == 'win32' else os.path.join(os.path.expanduser('~'), '.cache', 'fusion'))
    for folder in (os.path.join(base, name), os.path.join(os.path.dirname(script), '.fusion-cache', name)):
        try:
            os.makedirs(folder, exist_ok=True)
            probe = os.path.join(folder, '.write-test')
            with open(probe, 'w') as f:
                f.write('ok')
            os.remove(probe)
            return folder
        except OSError:
            continue
    raise OSError(f"can't write the cache folder for {script}, nor next to it")


# src/config/settings_files.py FORMAT_FILES, in its order - here so a cached run needn't load the settings code
# (tests/test_scripts.py keeps the two the same)
SETTINGS_FILE_NAMES = ('settings.toml', 'settings.yaml', 'settings.yml', 'settings.json', 'settings.ini')


def _settings_file_near(script: str):
    """The settings file the compiler would read for the script (find_config_file), or None."""
    for folder in (os.path.dirname(os.path.abspath(script)), os.getcwd()):
        for name in SETTINGS_FILE_NAMES:
            if os.path.isfile(os.path.join(folder, name)):
                return os.path.join(folder, name)
    return None


def _build_record(script: str) -> dict:
    """What a kept build depends on: the compiler, the script, every module file, the settings file."""
    files = [os.path.abspath(script)] + [os.path.abspath(p) for p in LAST_BUILD['files']]
    if LAST_BUILD['settings']:
        files.append(os.path.abspath(LAST_BUILD['settings']))
    return {'compiler': compiler_version(), 'files': {p: _file_hash(p) for p in files}}


def _still_current(record_path: str, script: str) -> bool:
    try:
        with open(record_path, encoding='utf-8') as f:
            record = json.load(f)
    except (OSError, ValueError):
        return False
    if record.get('compiler') != compiler_version():
        return False
    files = record.get('files', {})
    if os.path.abspath(script) not in files:
        return False
    # a settings file that has appeared since - next to the script or in this folder - is a change too
    settings = _settings_file_near(script)
    if settings and os.path.abspath(settings) not in files:
        return False
    return all(_file_hash(p) == h for p, h in files.items())


def run_script(script: str, arguments: list) -> int:
    """`python main.py run tidy.fusion [arguments]` (D.221): build the script when it (or anything it uses) has
    changed - quietly, the messages shown only when the build fails - then run it at once with the arguments and
    pass its exit code back. Nothing is written next to the script (D.223)."""
    if not os.path.isfile(script):
        print(f"Error: File not found: {script}", file=sys.stderr)
        return 1
    try:
        folder = script_cache_folder(script)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    base = os.path.join(folder, 'program')
    exe = base + ('.exe' if sys.platform == 'win32' else '')
    record_path = os.path.join(folder, 'build.json')
    if not (os.path.isfile(exe) and _still_current(record_path, script)):
        messages = io.StringIO()
        with redirect_stderr(messages):
            result = compile_file(script, out_base=base)
        if result != 0:
            sys.stderr.write(messages.getvalue())
            return result
        with open(record_path, 'w', encoding='utf-8') as f:
            json.dump(_build_record(script), f)
    return subprocess.run([exe, *arguments]).returncode


def print_interfaces(source_path: str, args: list) -> int:
    """`fusion main.fusion --interface [module]` (Task 18.4.4): print the public structs
    and functions of every module the program imports, or of one of them."""
    from src.modules import program_interfaces
    from src.parser.parser import ParserError
    from src.config import load_project_config, ProjectConfigError
    rest = [a for a in args if not a.startswith('--')]      # --interface ...
    try:
        project_config = load_project_config(source_path)
        lines, errors = program_interfaces(source_path, rest[0] if rest else None, project_config)
    except (OSError, ValueError, ParserError, ProjectConfigError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    for error in errors:
        print(f"Error: {error}", file=sys.stderr)
    if errors:
        return 1
    print('\n'.join(lines).rstrip() if lines else 'The program imports no modules')
    return 0


if __name__ == '__main__':
    sys.exit(main())
