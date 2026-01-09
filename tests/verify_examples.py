#!/usr/bin/env python3
"""
Verification script to compile and run all Fusion example programs.

This script:
1. Compiles each .fusion file in examples/ to C code
2. Compiles the C code to an executable using GCC
3. Runs each executable and captures output
4. Compares output with expected results
5. Generates a verification report

Usage:
    python verify_examples.py
"""

import os
import subprocess
import sys
from pathlib import Path

# Add project root to path (tests/ -> root)
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lexer import Lexer
from src.parser.parser import Parser
from src.semantic import SemanticAnalyzer
from src.codegen import CCodeGenerator


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class VerificationResult:
    """Stores the result of verifying one example."""
    def __init__(self, name: str):
        self.name = name
        self.fusion_code = ""
        self.c_code = ""
        self.compilation_success = False
        self.compilation_errors = []
        self.executable_path = ""
        self.execution_success = False
        self.stdout = ""
        self.stderr = ""
        self.exit_code = None
        self.expected_output = ""
        self.output_matches = False


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {text}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}[FAIL]{Colors.RESET} {text}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {text}")


def compile_fusion_to_c(fusion_file: Path) -> tuple[bool, str, list[str]]:
    """
    Compile a Fusion source file to C code.

    Args:
        fusion_file: Path to .fusion file

    Returns:
        Tuple of (success, c_code, errors)
    """
    try:
        # Read Fusion source
        with open(fusion_file, 'r') as f:
            fusion_code = f.read()

        # Lexical analysis
        lexer = Lexer(fusion_code, str(fusion_file))
        tokens = lexer.tokenize()

        if lexer.diagnostics.errors:
            return False, "", [str(e) for e in lexer.diagnostics.errors]

        # Parsing
        parser = Parser(tokens)
        ast = parser.parse_program()

        # Semantic analysis
        analyzer = SemanticAnalyzer()
        success = analyzer.analyze(ast)

        if not success:
            return False, "", [str(e) for e in analyzer.get_errors()]

        # Code generation
        generator = CCodeGenerator()
        c_code = generator.generate(ast)

        return True, c_code, []

    except Exception as e:
        return False, "", [f"Unexpected error: {str(e)}"]


def compile_c_to_executable(c_code: str, output_path: Path) -> tuple[bool, str, str]:
    """
    Compile C code to executable using GCC.

    Args:
        c_code: C source code
        output_path: Path for output executable

    Returns:
        Tuple of (success, stdout, stderr)
    """
    try:
        # Write C code to temporary file
        c_file = output_path.with_suffix('.c')
        with open(c_file, 'w') as f:
            f.write(c_code)

        # Compile with GCC
        result = subprocess.run(
            ['gcc', '-o', str(output_path), str(c_file), '-lm'],
            capture_output=True,
            text=True,
            timeout=30
        )

        return result.returncode == 0, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return False, "", "Compilation timeout"
    except FileNotFoundError:
        return False, "", "GCC not found - please install GCC"
    except Exception as e:
        return False, "", f"Unexpected error: {str(e)}"


def run_executable(exe_path: Path, input_data: str = "") -> tuple[int, str, str]:
    """
    Run an executable and capture output.

    Args:
        exe_path: Path to executable
        input_data: Optional stdin input

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            [str(exe_path)],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return -1, "", "Execution timeout"
    except Exception as e:
        return -1, "", f"Execution error: {str(e)}"


def verify_example(fusion_file: Path, expected_outputs: dict) -> VerificationResult:
    """
    Verify a single example program.

    Args:
        fusion_file: Path to .fusion file
        expected_outputs: Dictionary mapping example names to expected output

    Returns:
        VerificationResult object
    """
    result = VerificationResult(fusion_file.stem)

    print(f"\n{Colors.BOLD}Verifying: {fusion_file.name}{Colors.RESET}")
    print("-" * 80)

    # Read source
    with open(fusion_file, 'r') as f:
        result.fusion_code = f.read()

    # Step 1: Compile Fusion -> C
    print("  [1/4] Compiling Fusion -> C...", end=" ")
    success, c_code, errors = compile_fusion_to_c(fusion_file)

    if not success:
        print_error("FAILED")
        result.compilation_errors = errors
        for error in errors:
            print(f"        {error}")
        return result

    result.c_code = c_code
    print_success("OK")

    # Step 2: Compile C -> Executable
    exe_path = fusion_file.parent / f"{fusion_file.stem}.exe"
    print("  [2/4] Compiling C -> Executable...", end=" ")

    success, stdout, stderr = compile_c_to_executable(c_code, exe_path)

    if not success:
        print_error("FAILED")
        result.compilation_errors.append(stderr)
        print(f"        {stderr}")
        return result

    result.compilation_success = True
    result.executable_path = str(exe_path)
    print_success("OK")

    # Step 3: Run executable
    print("  [3/4] Running executable...", end=" ")
    exit_code, stdout, stderr = run_executable(exe_path)

    result.exit_code = exit_code
    result.stdout = stdout
    result.stderr = stderr

    if exit_code != 0:
        print_error(f"FAILED (exit code: {exit_code})")
        if stderr:
            print(f"        stderr: {stderr}")
        result.execution_success = False
        return result

    result.execution_success = True
    print_success("OK")

    # Step 4: Verify output
    print("  [4/4] Verifying output...", end=" ")

    expected = expected_outputs.get(fusion_file.stem, "")
    result.expected_output = expected

    if expected:
        # Check if output contains expected strings
        result.output_matches = all(exp in stdout for exp in expected.split('\n') if exp.strip())

        if result.output_matches:
            print_success("OK")
        else:
            print_error("MISMATCH")
            print(f"        Expected: {repr(expected)}")
            print(f"        Got:      {repr(stdout)}")
    else:
        print_warning("SKIPPED (no expected output defined)")
        result.output_matches = None

    return result


def generate_report(results: list[VerificationResult], report_file: Path):
    """Generate a verification report."""
    with open(report_file, 'w') as f:
        f.write("# Fusion Compiler Verification Report\n\n")
        f.write(f"**Date:** {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}\n")
        f.write(f"**Total Examples:** {len(results)}\n\n")

        # Summary
        compiled = sum(1 for r in results if r.compilation_success)
        executed = sum(1 for r in results if r.execution_success)
        matched = sum(1 for r in results if r.output_matches)

        f.write("## Summary\n\n")
        f.write(f"- **Compilation Success:** {compiled}/{len(results)}\n")
        f.write(f"- **Execution Success:** {executed}/{len(results)}\n")
        f.write(f"- **Output Matches:** {matched}/{len(results)}\n\n")

        # Detailed results
        f.write("## Detailed Results\n\n")

        for result in results:
            f.write(f"### {result.name}\n\n")

            if not result.compilation_success:
                f.write("**Status:** [FAIL] Compilation Failed\n\n")
                f.write("**Errors:**\n```\n")
                for error in result.compilation_errors:
                    f.write(f"{error}\n")
                f.write("```\n\n")
                continue

            if not result.execution_success:
                f.write("**Status:** [FAIL] Execution Failed\n\n")
                f.write(f"**Exit Code:** {result.exit_code}\n")
                f.write(f"**stderr:**\n```\n{result.stderr}\n```\n\n")
                continue

            if result.output_matches is False:
                f.write("**Status:** [WARN] Output Mismatch\n\n")
            elif result.output_matches is None:
                f.write("**Status:** [WARN] No Expected Output\n\n")
            else:
                f.write("**Status:** [OK] All Checks Passed\n\n")

            f.write(f"**Output:**\n```\n{result.stdout}```\n\n")

            if result.expected_output:
                f.write(f"**Expected:**\n```\n{result.expected_output}```\n\n")

            # Show generated C code (first 50 lines)
            c_lines = result.c_code.split('\n')[:50]
            f.write("**Generated C Code (first 50 lines):**\n```c\n")
            f.write('\n'.join(c_lines))
            if len(result.c_code.split('\n')) > 50:
                f.write("\n... (truncated)")
            f.write("\n```\n\n")


def main():
    """Main verification function."""
    print_header("FUSION COMPILER VERIFICATION")

    # Expected outputs for each example
    expected_outputs = {
        'hello_world': 'Hello, World!',
        'factorial': 'Factorial of 5 is 120',
        'fizzbuzz': '1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz',  # First 15 lines
        'calculator': 'Sum: 15\nDiff: 5\nProd: 50',
        'sum_array': 'Sum of 1 to 10: 55',
        'max_three': 'Maximum of 10, 25, 15 is 25',
    }

    # Find all .fusion files in examples/
    examples_dir = Path('examples')
    if not examples_dir.exists():
        print_error(f"Examples directory not found: {examples_dir}")
        return 1

    fusion_files = list(examples_dir.glob('*.fusion'))

    if not fusion_files:
        print_warning("No .fusion files found in examples/")
        return 1

    print(f"Found {len(fusion_files)} example(s) to verify\n")

    # Verify each example
    results = []
    for fusion_file in sorted(fusion_files):
        result = verify_example(fusion_file, expected_outputs)
        results.append(result)

    # Generate report
    report_file = Path('files/reports/verification_report.md')
    generate_report(results, report_file)

    # Print summary
    print_header("VERIFICATION SUMMARY")

    compiled = sum(1 for r in results if r.compilation_success)
    executed = sum(1 for r in results if r.execution_success)
    matched = sum(1 for r in results if r.output_matches)

    print(f"Total Examples:       {len(results)}")
    print(f"Compilation Success:  {compiled}/{len(results)} ", end="")
    if compiled == len(results):
        print("[OK]")
    else:
        print("[FAIL]")

    print(f"Execution Success:    {executed}/{len(results)} ", end="")
    if executed == len(results):
        print("[OK]")
    else:
        print("[FAIL]")

    print(f"Output Matches:       {matched}/{len(results)} ", end="")
    if matched == len(results):
        print("[OK]")
    else:
        print("[WARN]")

    print(f"\nDetailed report saved to: {report_file}")

    # Return exit code
    if compiled == len(results) and executed == len(results):
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
