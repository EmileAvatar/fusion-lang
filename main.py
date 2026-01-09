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
from src.lexer import Lexer
from src.parser.parser import Parser, ParserError
from src.semantic import SemanticAnalyzer
from src.codegen import CCodeGenerator


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

    # Lexical analysis
    print(f"[1/3] Lexical analysis...", file=sys.stderr)
    lexer = Lexer(source, source_path)
    try:
        tokens = lexer.tokenize()
    except Exception as e:
        print(f"Lexer exception: {e}", file=sys.stderr)
        return 1

    if lexer.diagnostics.errors:
        for error in lexer.diagnostics.errors:
            print(f"Lexer error: {error}", file=sys.stderr)
        return 1

    print(f"  ✓ Generated {len(tokens)} tokens", file=sys.stderr)

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

    print(f"  ✓ Parsed {len(ast.declarations)} declarations", file=sys.stderr)

    # Semantic analysis
    print(f"[3/5] Semantic analysis...", file=sys.stderr)
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)

    if not success:
        analyzer.print_diagnostics()
        return 1

    # Print warnings even on success
    if analyzer.get_warnings():
        analyzer.print_diagnostics()

    print(f"  ✓ Semantic analysis passed", file=sys.stderr)

    # Code generation
    print(f"[4/5] Code generation...", file=sys.stderr)
    generator = CCodeGenerator()
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
        print(f"  ✓ Generated C code: {c_file}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing C file: {e}", file=sys.stderr)
        return 1

    # Compile C code with GCC
    print(f"[5/5] Compiling C code...", file=sys.stderr)
    exe_file = source_path.replace('.fusion', '.exe' if sys.platform == 'win32' else '')

    gcc_result = compile_c_to_executable(c_file, exe_file)
    if gcc_result != 0:
        return 1

    print(f"\n✓ Compilation successful!", file=sys.stderr)
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

        print(f"  ✓ Compiled to executable: {exe_file}", file=sys.stderr)
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
        return 1

    source_path = sys.argv[1]
    return compile_file(source_path)


if __name__ == '__main__':
    sys.exit(main())
