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
"""

import sys
import os
import subprocess
from src.modules import load_program, make_file_parser, program_interfaces
from src.lexer import Lexer
from src.parser.parser import Parser, ParserError
from src.semantic import SemanticAnalyzer
from src.codegen import CCodeGenerator
from src.config import load_project_config, ProjectConfigError


def compile_file(source_path: str) -> int:
    """Compile a Fusion source file.

    Args:
        source_path: Path to the Fusion source file

    Returns:
        0 on success, 1 on error
    """
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

    # Project settings (Tasks 12.12, 31) - fusion.toml (or .yaml / .json / .ini) next to the
    # source file or in the current directory. None anywhere: a new fusion.toml is written,
    # every setting at its default - unless --no-new-config or FUSION_NO_NEW_CONFIG=1 (build
    # scripts and the test runs, which must not write files)
    create = '--no-new-config' not in sys.argv[2:] and os.environ.get('FUSION_NO_NEW_CONFIG') != '1'
    try:
        project_config = load_project_config(source_path, create_missing=create)
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

    # Modules (Task 18.4): load every imported module folder once and merge them in
    if ast.imports:
        ast, import_errors = load_program(source_path, ast, make_file_parser(project_config))
        if import_errors:
            for error in import_errors:
                print(f"Error: {error}", file=sys.stderr)
            print(f"\n{len(import_errors)} error(s) found", file=sys.stderr)
            return 1
        print(f"  [OK] Loaded the imported modules", file=sys.stderr)

    # Semantic analysis
    print(f"[3/5] Semantic analysis...", file=sys.stderr)
    analyzer = SemanticAnalyzer(structs_config=project_config.structs,
                                strings_config=project_config.strings,
                                stdlib_config=project_config.stdlib,
                                errors_config=project_config.errors,
                                numbers_config=project_config.numbers,
                                modules_config=project_config.modules,
                                conditions_config=project_config.conditions)
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
    try:
        c_code = generator.generate(ast)
    except Exception as e:
        print(f"Code generation error: {e}", file=sys.stderr)
        return 1

    # Write C code to file
    c_file = source_path.replace('.fusion', '.c')
    try:
        with open(c_file, 'w', encoding='utf-8') as f:
            f.write(c_code)
        print(f"  [OK] Generated C code: {c_file}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing C file: {e}", file=sys.stderr)
        return 1

    # Compile C code with GCC
    print(f"[5/5] Compiling C code...", file=sys.stderr)
    exe_file = source_path.replace('.fusion', '.exe' if sys.platform == 'win32' else '')

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
        print("       --no-new-config   don't write a fusion.toml when the project has no "
              "settings file", file=sys.stderr)
        return 1

    source_path = sys.argv[1]
    if '--interface' in sys.argv[2:]:
        return print_interfaces(source_path, sys.argv[2:])
    return compile_file(source_path)


def print_interfaces(source_path: str, args: list) -> int:
    """`fusion main.fusion --interface [module]` (Task 18.4.4): print the public structs
    and functions of every module the program imports, or of one of them."""
    rest = [a for a in args if a != '--interface']
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
