"""Test code generation for array declarations, indexing, and len().

Tests that:
- int[] arr = [1, 2, 3] generates a real C array declaration: int arr[3] = {1, 2, 3};
- int[5] arr (no initializer) zero-initializes: int arr[5] = {0};
- arr[i] read/write generates plain C indexing (a valid C lvalue and rvalue)
- len(arr) compiles to the array's size as a literal, not a runtime call
- const arrays emit the const keyword
- Generated code actually compiles and runs correctly with GCC
"""

import os
import subprocess
import tempfile

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.semantic.semantic_analyzer import SemanticAnalyzer
from src.codegen.c_generator import CCodeGenerator


def compile_and_generate(code: str) -> str:
    """Helper to compile Fusion code to C."""
    lexer = Lexer(code, "test.fusion")
    parser = Parser(list(lexer.tokenize()))
    program = parser.parse_program()

    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(program)

    if not success:
        errors = analyzer.get_errors()
        raise Exception(f"Semantic analysis failed: {errors}")

    generator = CCodeGenerator()
    return generator.generate(program)


def test_array_literal_declaration_codegen():
    """int[] arr = [1, 2, 3] -> int arr[3] = {1, 2, 3};"""
    code = """
void function main()
    int[] arr = [1, 2, 3]
End function
"""
    c_code = compile_and_generate(code)
    assert 'int arr[3] = {1, 2, 3};' in c_code, f"Got:\n{c_code}"


def test_array_explicit_size_no_init_codegen():
    """int[5] arr (no initializer) -> int arr[5] = {0}; (zero-initialized)"""
    code = """
void function main()
    int[5] arr
End function
"""
    c_code = compile_and_generate(code)
    assert 'int arr[5] = {0};' in c_code, f"Got:\n{c_code}"


def test_array_index_read_codegen():
    """int x = arr[0] -> int x = arr[0];"""
    code = """
void function main()
    int[] arr = [1, 2, 3]
    int x = arr[0]
End function
"""
    c_code = compile_and_generate(code)
    assert 'int x = arr[0];' in c_code, f"Got:\n{c_code}"


def test_array_index_write_codegen():
    """arr[0] = 99 -> arr[0] = 99;"""
    code = """
void function main()
    int[] arr = [1, 2, 3]
    arr[0] = 99
End function
"""
    c_code = compile_and_generate(code)
    assert 'arr[0] = 99;' in c_code, f"Got:\n{c_code}"


def test_len_compiles_to_constant():
    """len(arr) compiles to the array's size, not a runtime function call."""
    code = """
void function main()
    int[] arr = [1, 2, 3, 4, 5]
    int n = len(arr)
End function
"""
    c_code = compile_and_generate(code)
    assert 'int n = 5;' in c_code, f"Got:\n{c_code}"
    assert 'len(' not in c_code, f"len() should not appear as a runtime call:\n{c_code}"


def test_const_array_codegen():
    """const int[] arr = [1, 2, 3] -> const int arr[3] = {1, 2, 3};"""
    code = """
void function main()
    const int[] arr = [1, 2, 3]
End function
"""
    c_code = compile_and_generate(code)
    assert 'const int arr[3] = {1, 2, 3};' in c_code, f"Got:\n{c_code}"


def test_float_array_codegen():
    """float[] arr uses float as the C element type, and int literals promote."""
    code = """
void function main()
    float[] arr = [1, 2, 3]
End function
"""
    c_code = compile_and_generate(code)
    assert 'float arr[3]' in c_code, f"Got:\n{c_code}"


def test_array_end_to_end_gcc_compiles_and_runs():
    """Full pipeline: array declaration, indexing, mutation, and len() all compile
    with GCC and produce the correct runtime result."""
    code = """
int function sumArray()
    int[] scores = [10, 20, 30, 40, 50]
    int total = 0
    for i in range(0, len(scores))
        total = total + scores[i]
    return total

int function main()
    int result = sumArray()
    return result
End function
"""
    c_code = compile_and_generate(code)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        c_file = f.name
        f.write(c_code)

    try:
        exe_file = c_file.replace('.c', '.exe')
        compile_result = subprocess.run(
            ['gcc', c_file, '-o', exe_file, '-std=c11'],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert compile_result.returncode == 0, \
            f"GCC compilation failed:\n{compile_result.stderr}\n\nC code:\n{c_code}"

        run_result = subprocess.run([exe_file], capture_output=True, timeout=10)
        # sumArray returns 10+20+30+40+50 = 150, which becomes main()'s exit code
        assert run_result.returncode == 150, \
            f"Expected exit code 150 (sum of array), got {run_result.returncode}"

        if os.path.exists(exe_file):
            os.remove(exe_file)
    finally:
        if os.path.exists(c_file):
            os.remove(c_file)
