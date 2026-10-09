# Fusion Compiler Verification Report

**Date:** Fri Oct  9 19:47:09 SAST 2026
**Total Examples:** 11

## Summary

- **Compilation Success:** 11/11
- **Execution Success:** 11/11
- **Output Matches:** 11/11

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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
typedef struct { char* data; int len; int owned; } fusion_string;
// Text written in the source: never freed, costs nothing at run time
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), 0})

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

static inline void fusion_runtime_error(const char* where, const char* format, ...) {
    va_list args;
    fflush(stdout);
    fprintf(stderr, "Runtime error%s%s: ", where ? " at " : "", where ? where : "");
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
#ifdef FUSION_LEAK_CHECK
    fusion_leak_skip = 1;
#endif
    exit(1);
}

static inline void* fusion_alloc(size_t size) {
    void* p = malloc(size);
    if (!p) fusion_runtime_error(NULL, "out of memory");
#ifdef FUSION_LEAK_CHECK
    if (!fusion_leak_ready) { fusion_leak_ready = 1; atexit(fusion_leak_report); }
    if (fusion_live_count == fusion_live_cap) {
        fusion_live_cap = fusion_live_cap ? fusion_live_cap * 2 : 64;
        fusion_live = (void**)realloc(fusion_live, (size_t)fusion_live_cap * sizeof(void*));
        if (!fusion_live) fusion_runtime_error(NULL, "out of memory");
    }
    fusion_live[fusion_live_count++] = p;
#endif
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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
typedef struct { char* data; int len; int owned; } fusion_string;
// Text written in the source: never freed, costs nothing at run time
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), 0})

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

static inline void fusion_runtime_error(const char* where, const char* format, ...) {
    va_list args;
    fflush(stdout);
    fprintf(stderr, "Runtime error%s%s: ", where ? " at " : "", where ? where : "");
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
#ifdef FUSION_LEAK_CHECK
    fusion_leak_skip = 1;
#endif
    exit(1);
}

static inline void* fusion_alloc(size_t size) {
    void* p = malloc(size);
    if (!p) fusion_runtime_error(NULL, "out of memory");
#ifdef FUSION_LEAK_CHECK
    if (!fusion_leak_ready) { fusion_leak_ready = 1; atexit(fusion_leak_report); }
    if (fusion_live_count == fusion_live_cap) {
        fusion_live_cap = fusion_live_cap ? fusion_live_cap * 2 : 64;
        fusion_live = (void**)realloc(fusion_live, (size_t)fusion_live_cap * sizeof(void*));
        if (!fusion_live) fusion_runtime_error(NULL, "out of memory");
    }
    fusion_live[fusion_live_count++] = p;
#endif
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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
typedef struct { char* data; int len; int owned; } fusion_string;
// Text written in the source: never freed, costs nothing at run time
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), 0})

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

static inline void fusion_runtime_error(const char* where, const char* format, ...) {
    va_list args;
    fflush(stdout);
    fprintf(stderr, "Runtime error%s%s: ", where ? " at " : "", where ? where : "");
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
#ifdef FUSION_LEAK_CHECK
    fusion_leak_skip = 1;
#endif
    exit(1);
}

static inline void* fusion_alloc(size_t size) {
    void* p = malloc(size);
    if (!p) fusion_runtime_error(NULL, "out of memory");
#ifdef FUSION_LEAK_CHECK
    if (!fusion_leak_ready) { fusion_leak_ready = 1; atexit(fusion_leak_report); }
    if (fusion_live_count == fusion_live_cap) {
        fusion_live_cap = fusion_live_cap ? fusion_live_cap * 2 : 64;
        fusion_live = (void**)realloc(fusion_live, (size_t)fusion_live_cap * sizeof(void*));
        if (!fusion_live) fusion_runtime_error(NULL, "out of memory");
    }
    fusion_live[fusion_live_count++] = p;
#endif
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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
typedef struct { char* data; int len; int owned; } fusion_string;
// Text written in the source: never freed, costs nothing at run time
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), 0})

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

static inline void fusion_runtime_error(const char* where, const char* format, ...) {
    va_list args;
    fflush(stdout);
    fprintf(stderr, "Runtime error%s%s: ", where ? " at " : "", where ? where : "");
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
#ifdef FUSION_LEAK_CHECK
    fusion_leak_skip = 1;
#endif
    exit(1);
}

static inline void* fusion_alloc(size_t size) {
    void* p = malloc(size);
    if (!p) fusion_runtime_error(NULL, "out of memory");
#ifdef FUSION_LEAK_CHECK
    if (!fusion_leak_ready) { fusion_leak_ready = 1; atexit(fusion_leak_report); }
    if (fusion_live_count == fusion_live_cap) {
        fusion_live_cap = fusion_live_cap ? fusion_live_cap * 2 : 64;
        fusion_live = (void**)realloc(fusion_live, (size_t)fusion_live_cap * sizeof(void*));
        if (!fusion_live) fusion_runtime_error(NULL, "out of memory");
    }
    fusion_live[fusion_live_count++] = p;
#endif
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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
typedef struct { char* data; int len; int owned; } fusion_string;
// Text written in the source: never freed, costs nothing at run time
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), 0})

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

static inline void fusion_runtime_error(const char* where, const char* format, ...) {
    va_list args;
    fflush(stdout);
    fprintf(stderr, "Runtime error%s%s: ", where ? " at " : "", where ? where : "");
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
#ifdef FUSION_LEAK_CHECK
    fusion_leak_skip = 1;
#endif
    exit(1);
}

static inline void* fusion_alloc(size_t size) {
    void* p = malloc(size);
    if (!p) fusion_runtime_error(NULL, "out of memory");
#ifdef FUSION_LEAK_CHECK
    if (!fusion_leak_ready) { fusion_leak_ready = 1; atexit(fusion_leak_report); }
    if (fusion_live_count == fusion_live_cap) {
        fusion_live_cap = fusion_live_cap ? fusion_live_cap * 2 : 64;
        fusion_live = (void**)realloc(fusion_live, (size_t)fusion_live_cap * sizeof(void*));
        if (!fusion_live) fusion_runtime_error(NULL, "out of memory");
    }
    fusion_live[fusion_live_count++] = p;
#endif
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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
typedef struct { char* data; int len; int owned; } fusion_string;
// Text written in the source: never freed, costs nothing at run time
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), 0})

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

static inline void fusion_runtime_error(const char* where, const char* format, ...) {
    va_list args;
    fflush(stdout);
    fprintf(stderr, "Runtime error%s%s: ", where ? " at " : "", where ? where : "");
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
#ifdef FUSION_LEAK_CHECK
    fusion_leak_skip = 1;
#endif
    exit(1);
}

static inline void* fusion_alloc(size_t size) {
    void* p = malloc(size);
    if (!p) fusion_runtime_error(NULL, "out of memory");
#ifdef FUSION_LEAK_CHECK
    if (!fusion_leak_ready) { fusion_leak_ready = 1; atexit(fusion_leak_report); }
    if (fusion_live_count == fusion_live_cap) {
        fusion_live_cap = fusion_live_cap ? fusion_live_cap * 2 : 64;
        fusion_live = (void**)realloc(fusion_live, (size_t)fusion_live_cap * sizeof(void*));
        if (!fusion_live) fusion_runtime_error(NULL, "out of memory");
    }
    fusion_live[fusion_live_count++] = p;
#endif
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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
typedef struct { char* data; int len; int owned; } fusion_string;
// Text written in the source: never freed, costs nothing at run time
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), 0})

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

static inline void fusion_runtime_error(const char* where, const char* format, ...) {
    va_list args;
    fflush(stdout);
    fprintf(stderr, "Runtime error%s%s: ", where ? " at " : "", where ? where : "");
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
#ifdef FUSION_LEAK_CHECK
    fusion_leak_skip = 1;
#endif
    exit(1);
}

static inline void* fusion_alloc(size_t size) {
    void* p = malloc(size);
    if (!p) fusion_runtime_error(NULL, "out of memory");
#ifdef FUSION_LEAK_CHECK
    if (!fusion_leak_ready) { fusion_leak_ready = 1; atexit(fusion_leak_report); }
    if (fusion_live_count == fusion_live_cap) {
        fusion_live_cap = fusion_live_cap ? fusion_live_cap * 2 : 64;
        fusion_live = (void**)realloc(fusion_live, (size_t)fusion_live_cap * sizeof(void*));
        if (!fusion_live) fusion_runtime_error(NULL, "out of memory");
    }
    fusion_live[fusion_live_count++] = p;
#endif
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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
typedef struct { char* data; int len; int owned; } fusion_string;
// Text written in the source: never freed, costs nothing at run time
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), 0})

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

static inline void fusion_runtime_error(const char* where, const char* format, ...) {
    va_list args;
    fflush(stdout);
    fprintf(stderr, "Runtime error%s%s: ", where ? " at " : "", where ? where : "");
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
#ifdef FUSION_LEAK_CHECK
    fusion_leak_skip = 1;
#endif
    exit(1);
}

static inline void* fusion_alloc(size_t size) {
    void* p = malloc(size);
    if (!p) fusion_runtime_error(NULL, "out of memory");
#ifdef FUSION_LEAK_CHECK
    if (!fusion_leak_ready) { fusion_leak_ready = 1; atexit(fusion_leak_report); }
    if (fusion_live_count == fusion_live_cap) {
        fusion_live_cap = fusion_live_cap ? fusion_live_cap * 2 : 64;
        fusion_live = (void**)realloc(fusion_live, (size_t)fusion_live_cap * sizeof(void*));
        if (!fusion_live) fusion_runtime_error(NULL, "out of memory");
    }
    fusion_live[fusion_live_count++] = p;
#endif
... (truncated)
```

### strings_demo

**Status:** [OK] All Checks Passed

**Output:**
```
a = apple, b = banana
original = quiet, loud = LOUD
a == apple: 1, a < b: 1
Ada 555-0100 / Grace 555-0123
Grace: found, Alan: missing
Ada Lovelace! has 13 bytes, starts with A
[Lovelace] [ADA] [spaced]
contains Love: 1, index of Love: 4
42 doubled is 84
All string tests passed!
```

**Expected:**
```
a = apple, b = banana
original = quiet, loud = LOUD
a == apple: 1, a < b: 1
Ada 555-0100 / Grace 555-0123
Grace: found, Alan: missing
Ada Lovelace! has 13 bytes, starts with A
[Lovelace] [ADA] [spaced]
contains Love: 1, index of Love: 4
42 doubled is 84
All string tests passed!```

**Generated C Code (first 50 lines):**
```c
#include <math.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
typedef struct { char* data; int len; int owned; } fusion_string;
// Text written in the source: never freed, costs nothing at run time
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), 0})

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

static inline void fusion_runtime_error(const char* where, const char* format, ...) {
    va_list args;
    fflush(stdout);
    fprintf(stderr, "Runtime error%s%s: ", where ? " at " : "", where ? where : "");
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
#ifdef FUSION_LEAK_CHECK
    fusion_leak_skip = 1;
#endif
    exit(1);
}

static inline void* fusion_alloc(size_t size) {
    void* p = malloc(size);
    if (!p) fusion_runtime_error(NULL, "out of memory");
#ifdef FUSION_LEAK_CHECK
    if (!fusion_leak_ready) { fusion_leak_ready = 1; atexit(fusion_leak_report); }
    if (fusion_live_count == fusion_live_cap) {
        fusion_live_cap = fusion_live_cap ? fusion_live_cap * 2 : 64;
        fusion_live = (void**)realloc(fusion_live, (size_t)fusion_live_cap * sizeof(void*));
        if (!fusion_live) fusion_runtime_error(NULL, "out of memory");
    }
    fusion_live[fusion_live_count++] = p;
#endif
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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
typedef struct { char* data; int len; int owned; } fusion_string;
// Text written in the source: never freed, costs nothing at run time
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), 0})

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

static inline void fusion_runtime_error(const char* where, const char* format, ...) {
    va_list args;
    fflush(stdout);
    fprintf(stderr, "Runtime error%s%s: ", where ? " at " : "", where ? where : "");
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
#ifdef FUSION_LEAK_CHECK
    fusion_leak_skip = 1;
#endif
    exit(1);
}

static inline void* fusion_alloc(size_t size) {
    void* p = malloc(size);
    if (!p) fusion_runtime_error(NULL, "out of memory");
#ifdef FUSION_LEAK_CHECK
    if (!fusion_leak_ready) { fusion_leak_ready = 1; atexit(fusion_leak_report); }
    if (fusion_live_count == fusion_live_cap) {
        fusion_live_cap = fusion_live_cap ? fusion_live_cap * 2 : 64;
        fusion_live = (void**)realloc(fusion_live, (size_t)fusion_live_cap * sizeof(void*));
        if (!fusion_live) fusion_runtime_error(NULL, "out of memory");
    }
    fusion_live[fusion_live_count++] = p;
#endif
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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ---- Fusion runtime: strings and run-time errors (Task 18.3.1) ----
typedef struct { char* data; int len; int owned; } fusion_string;
// Text written in the source: never freed, costs nothing at run time
#define FUSION_STR(lit) ((fusion_string){(char*)(lit), (int)(sizeof(lit) - 1), 0})

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

static inline void fusion_runtime_error(const char* where, const char* format, ...) {
    va_list args;
    fflush(stdout);
    fprintf(stderr, "Runtime error%s%s: ", where ? " at " : "", where ? where : "");
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
#ifdef FUSION_LEAK_CHECK
    fusion_leak_skip = 1;
#endif
    exit(1);
}

static inline void* fusion_alloc(size_t size) {
    void* p = malloc(size);
    if (!p) fusion_runtime_error(NULL, "out of memory");
#ifdef FUSION_LEAK_CHECK
    if (!fusion_leak_ready) { fusion_leak_ready = 1; atexit(fusion_leak_report); }
    if (fusion_live_count == fusion_live_cap) {
        fusion_live_cap = fusion_live_cap ? fusion_live_cap * 2 : 64;
        fusion_live = (void**)realloc(fusion_live, (size_t)fusion_live_cap * sizeof(void*));
        if (!fusion_live) fusion_runtime_error(NULL, "out of memory");
    }
    fusion_live[fusion_live_count++] = p;
#endif
... (truncated)
```

