# Fusion Compiler Verification Report

**Date:** Fri Oct 16 22:46:03 SAST 2026
**Total Examples:** 16

## Summary

- **Compilation Success:** 16/16
- **Execution Success:** 16/16
- **Output Matches:** 16/16

## Detailed Results

### arrays_demo

**Status:** [OK] All Checks Passed

**Output:**
```
=== Fusion Arrays Demo ===

First score: 10
Updated first score: 99
Number of scores: 5

Buffer: 1.500000, 2.500000, 0.000000

Sum of [10, 20, 30, 40, 50] = 150

All array tests passed!
```

**Expected:**
```
First score: 10
Updated first score: 99
Number of scores: 5
Sum of [10, 20, 30, 40, 50] = 150
All array tests passed!```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### calculator

**Status:** [OK] All Checks Passed

**Output:**
```
Sum: 15
Diff: 5
Prod: 50
```

**Expected:**
```
Sum: 15
Diff: 5
Prod: 50```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### const_demo

**Status:** [OK] All Checks Passed

**Output:**
```
=== Fusion Const Demo ===

MAX_ITERATIONS = 1000

Counting to 10 using const MAX:
  1
  2
  3
  4
  5
  6
  7
  8
  9
  10

BASE (100) * MULTIPLIER (2) = 200

Screen size: 80x24 = 1920 pixels

All const tests passed!
```

**Expected:**
```
MAX_ITERATIONS = 1000
BASE (100) * MULTIPLIER (2) = 200
Screen size: 80x24 = 1920 pixels
All const tests passed!```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### control_flow

**Status:** [OK] All Checks Passed

**Output:**
```
95 -> A
80 -> B
50 -> C
12 -> F
countdown: 3 2 1 go
first primes: 2, 3, 5, 7, 11, 13, 17, 19
row 1: 1 2
row 2: 2 4 6 8
row 3: 3 6 9 12 15 18
15 is at 2, 99 is at -1
pears: sold out
in stock: 10
```

**Expected:**
```
95 -> A
80 -> B
50 -> C
12 -> F
countdown: 3 2 1 go
first primes: 2, 3, 5, 7, 11, 13, 17, 19
row 1: 1 2
row 2: 2 4 6 8
row 3: 3 6 9 12 15 18
15 is at 2, 99 is at -1
pears: sold out
in stock: 10```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### errors_demo

**Status:** [OK] All Checks Passed

**Output:**
```
width = 80
height = 24
skip (1): Not 'name=value': depth
skip (2): A setting needs a name - '=5'
skip: NumberFormatError: '12x' is not a whole number (check with isInt first)
total: 3
total failed: NumberFormatError: 'oops' is not a whole number (check with isInt first)
totals done
FileNotFoundError: no_such_settings.txt
DivideByZeroError: 10 / 0: division by zero
all handled
```

**Expected:**
```
width = 80
height = 24
skip (1): Not 'name=value': depth
skip (2): A setting needs a name - '=5'
skip: NumberFormatError: '12x' is not a whole number (check with isInt first)
total: 3
total failed: NumberFormatError: 'oops' is not a whole number (check with isInt first)
totals done
FileNotFoundError: no_such_settings.txt
DivideByZeroError: 10 / 0: division by zero
all handled```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### expressions

**Status:** [OK] All Checks Passed

**Output:**
```
2 + 3 * 4 = 14   (2 + (3 * 4))
(2 + 3) * 4 = 20   ((2 + 3) * 4)
100 / 5 / 2 - 1 = 9   (((100 / 5) / 2) - 1)
7 = 7   7
```

**Expected:**
```
2 + 3 * 4 = 14   (2 + (3 * 4))
(2 + 3) * 4 = 20   ((2 + 3) * 4)
100 / 5 / 2 - 1 = 9   (((100 / 5) / 2) - 1)
7 = 7   7```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### factorial

**Status:** [OK] All Checks Passed

**Output:**
```
Factorial of 5 is 120
```

**Expected:**
```
Factorial of 5 is 120```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### fizzbuzz

**Status:** [OK] All Checks Passed

**Output:**
```
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
16
17
Fizz
19
Buzz
```

**Expected:**
```
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### functions_demo

**Status:** [OK] All Checks Passed

**Output:**
```
=== Fusion Functions Demo ===
Hello, World!
Hello, Fusion!
Welcome, Fusion!
offset(10) = 5, offset(10, 2) = 12
sum: 6, 150, 15
After doubleAll, middle of small = 4
tripled = 15, added = 105, squared = 49, viaName = 21
All function tests passed!
```

**Expected:**
```
Hello, World!
Hello, Fusion!
Welcome, Fusion!
offset(10) = 5, offset(10, 2) = 12
sum: 6, 150, 15
After doubleAll, middle of small = 4
tripled = 15, added = 105, squared = 49, viaName = 21
All function tests passed!```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### hello_world

**Status:** [OK] All Checks Passed

**Output:**
```
Hello, World!
```

**Expected:**
```
Hello, World!```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### max_three

**Status:** [OK] All Checks Passed

**Output:**
```
Maximum of 10, 25, 15 is 25
```

**Expected:**
```
Maximum of 10, 25, 15 is 25```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### shop

**Status:** [OK] All Checks Passed

**Output:**
```
Receipt
-------
Coffee beans.. R 12.99
Mug........... R 8.50
Filters....... R 3.99
-------
Subtotal...... R 25.48
Total + VAT... R 29.30
```

**Expected:**
```
Receipt
-------
Coffee beans.. R 12.99
Mug........... R 8.50
Filters....... R 3.99
-------
Subtotal...... R 25.48
Total + VAT... R 29.30```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### strings_demo

**Status:** [OK] All Checks Passed

**Output:**
```
a = apple, b = banana
original = quiet, loud = LOUD
a == apple: true, a < b: true
Ada 555-0100 / Grace 555-0123
Grace: found, Alan: missing
Ada Lovelace! has 13 characters, starts with A
[Lovelace] [ADA] [spaced]
contains Love: true, index of Love: 4
42 doubled is 84
All string tests passed!
```

**Expected:**
```
a = apple, b = banana
original = quiet, loud = LOUD
a == apple: true, a < b: true
Ada 555-0100 / Grace 555-0123
Grace: found, Alan: missing
Ada Lovelace! has 13 characters, starts with A
[Lovelace] [ADA] [spaced]
contains Love: true, index of Love: 4
42 doubled is 84
All string tests passed!```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### structs_demo

**Status:** [OK] All Checks Passed

**Output:**
```
a = (3, 4), b = (10, 4)
a + b = (13, 8)
Inside moveRight: x = 103
After moveRight: a.x = 3
Ada: health 75.000000, score 15
Newcomer score: 0, health 100.000000
Dune Messiah is available
Origin: (0, 0)
Named point: (7, 8)
Linus: health 100.000000, score 42
Shifted: (8, 9)
Linus (42) beat Ada (15)
box: max.x = 4, bigger max.x = 40
Blue total 22, first position x = 1
Diagonal ends at (9, 9); team now at x = 2; diagonal(4)[1].y = 4
All struct tests passed!
```

**Expected:**
```
a = (3, 4), b = (10, 4)
a + b = (13, 8)
Inside moveRight: x = 103
After moveRight: a.x = 3
Ada: health 75.000000, score 15
Newcomer score: 0, health 100.000000
Dune Messiah is available
Origin: (0, 0)
Named point: (7, 8)
Linus: health 100.000000, score 42
Shifted: (8, 9)
Linus (42) beat Ada (15)
box: max.x = 4, bigger max.x = 40
Blue total 22, first position x = 1
Diagonal ends at (9, 9); team now at x = 2; diagonal(4)[1].y = 4
All struct tests passed!```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### sum_array

**Status:** [OK] All Checks Passed

**Output:**
```
Sum of 1 to 10: 55
```

**Expected:**
```
Sum of 1 to 10: 55```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

### wordcount

**Status:** [OK] All Checks Passed

**Output:**
```
17 words, 10 different
the.....   4
brown...   2
dog.....   2
fox.....   2
quick...   2
```

**Expected:**
```
17 words, 10 different
the.....   4
brown...   2
dog.....   2
fox.....   2
quick...   2```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
// A string is UTF-8 text: `len` bytes holding `chars` characters (Task 18.3.2b). For plain
// ASCII text chars == len, and indexing needs no scanning
typedef struct { char* data; int len; int chars; int owned; } fusion_string;
// One character: any Unicode code point - or one byte when the project uses ascii encoding
#ifdef FUSION_ASCII
typedef unsigned char fusion_char;
#else
typedef uint32_t fusion_char;
#endif
// Text written in the source: never freed, costs nothing at run time. FUSION_STR is for
// ASCII text; FUSION_STRU gives the character count of non-ASCII text
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (int)(sizeof(lit) - 1), 0})
#define FUSION_STRU(lit, n) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), (n), 0})

#ifdef FUSION_LEAK_CHECK
static void** fusion_live = NULL;
static int fusion_live_count = 0, fusion_live_cap = 0, fusion_leak_ready = 0, fusion_leak_skip = 0;
static inline void fusion_leak_report(void) {
    if (fusion_live_count > 0 && !fusion_leak_skip) {
        fflush(stdout);
        fprintf(stderr, "FUSION LEAK CHECK: %d string(s) were never freed\n", fusion_live_count);
        _Exit(3);
    }
}
#endif

// Program start-up: the Windows console shows UTF-8 text correctly only after switching its
// output code page (Task 18.3.2b). Declared directly to avoid including <windows.h>
#ifdef _WIN32
__declspec(dllimport) int __stdcall SetConsoleOutputCP(unsigned int code_page);
__declspec(dllimport) int __stdcall SetConsoleCP(unsigned int code_page);
#endif
// Waiting before the window closes (user request 2026-10-11): a program started by
// double-clicking it would close before its output can be read, so it waits for a key when
// it ends - also after a run-time error. Not when run with --headless, and not when no one
// is at the console (input or output redirected - tests, scripts, pipes)
#ifdef _WIN32
#include <conio.h>
#include <io.h>
#define FUSION_IS_CONSOLE(f) _isatty(_fileno(f))
#else
... (truncated)
```

