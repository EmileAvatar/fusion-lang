# Fusion Compiler Verification Report

**Date:** Sun Sep 13 21:05:02 SAST 2026
**Total Examples:** 8

## Summary

- **Compilation Success:** 8/8
- **Execution Success:** 8/8
- **Output Matches:** 8/8

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
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

// Forward declarations
int sumArray(void);
int main(void);

int sumArray(void) {
    int scores[5] = {10, 20, 30, 40, 50};
    int total = 0;
    for (int i = 0; i < 5; i += 1) {
        total = (total + scores[i]);
    }
    return total;
}

int main(void) {
    printf("=== Fusion Arrays Demo ===\n");
    printf("\n");
    int scores[5] = {10, 20, 30, 40, 50};
    int first = scores[0];
    printf("First score: %d\n", first);
    scores[0] = 99;
    int updated = scores[0];
    printf("Updated first score: %d\n", updated);
    int count = 5;
    printf("Number of scores: %d\n", count);
    printf("\n");
    float buffer[3] = {0};
    buffer[0] = 1.5f;
    buffer[1] = 2.5f;
    float b0 = buffer[0];
    float b1 = buffer[1];
    float b2 = buffer[2];
    printf("Buffer: %f, %f, %f\n", b0, b1, b2);
    printf("\n");
    int total = sumArray();
    printf("Sum of [10, 20, 30, 40, 50] = %d\n", total);
    printf("\n");
    printf("All array tests passed!\n");
    return 0;
}

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
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

// Forward declarations
int add(int a, int b);
int subtract(int a, int b);
int multiply(int a, int b);
int main(void);

int add(int a, int b) {
    return (a + b);
}

int subtract(int a, int b) {
    return (a - b);
}

int multiply(int a, int b) {
    return (a * b);
}

int main(void) {
    int x = 10;
    int y = 5;
    int sum = add(x, y);
    int diff = subtract(x, y);
    int prod = multiply(x, y);
    printf("Sum: %d\n", sum);
    printf("Diff: %d\n", diff);
    printf("Prod: %d\n", prod);
    return 0;
}

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
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

// Forward declarations
int main(void);

int main(void) {
    printf("=== Fusion Const Demo ===\n");
    printf("\n");
    const int MAX_ITERATIONS = 1000;
    printf("MAX_ITERATIONS = %d\n", MAX_ITERATIONS);
    printf("\n");
    printf("Counting to 10 using const MAX:\n");
    const int MAX = 10;
    int i = 1;
    while ((i <= MAX)) {
        printf("  %d\n", i);
        i = (i + 1);
    }
    printf("\n");
    const int BASE = 100;
    const int MULTIPLIER = 2;
    int result = (BASE * MULTIPLIER);
    printf("BASE (%d) * MULTIPLIER (%d) = %d\n", BASE, MULTIPLIER, result);
    printf("\n");
    const int WIDTH = 80;
    const int HEIGHT = 24;
    int total_pixels = (WIDTH * HEIGHT);
    printf("Screen size: %dx%d = %d pixels\n", WIDTH, HEIGHT, total_pixels);
    printf("\n");
    printf("All const tests passed!\n");
    return 0;
}

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
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

// Forward declarations
int factorial(int n);
int main(void);

int factorial(int n) {
    if ((n <= 1)) {
        return 1;
    }
    return (n * factorial((n - 1)));
}

int main(void) {
    int result = factorial(5);
    printf("Factorial of 5 is %d\n", result);
    return 0;
}

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
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

// Forward declarations
int main(void);

int main(void) {
    int i = 1;
    while ((i <= 20)) {
        if (((i % 15) == 0)) {
            printf("FizzBuzz\n");
        } else {
            if (((i % 3) == 0)) {
                printf("Fizz\n");
            } else {
                if (((i % 5) == 0)) {
                    printf("Buzz\n");
                } else {
                    printf("%d\n", i);
                }
            }
        }
        i = (i + 1);
    }
    return 0;
}

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
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

// Forward declarations
int main(void);

int main(void) {
    printf("Hello, World!\n");
    return 0;
}

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
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

// Forward declarations
int max(int a, int b, int c);
int main(void);

int max(int a, int b, int c) {
    int result = a;
    if ((b > result)) {
        result = b;
    }
    if ((c > result)) {
        result = c;
    }
    return result;
}

int main(void) {
    int x = 10;
    int y = 25;
    int z = 15;
    int maximum = max(x, y, z);
    printf("Maximum of %d, %d, %d is %d\n", x, y, z, maximum);
    return 0;
}

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
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

// Forward declarations
int sum_range(int start, int end);
int main(void);

int sum_range(int start, int end) {
    int total = 0;
    for (int i = start; i < end; i += 1) {
        total = (total + i);
    }
    return total;
}

int main(void) {
    int result = sum_range(1, 11);
    printf("Sum of 1 to 10: %d\n", result);
    return 0;
}

```

