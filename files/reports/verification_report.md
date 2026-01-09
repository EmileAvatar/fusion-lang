# Fusion Compiler Verification Report

**Date:** Thu, Jan  8, 2026 10:55:37 PM
**Total Examples:** 6

## Summary

- **Compilation Success:** 6/6
- **Execution Success:** 6/6
- **Output Matches:** 6/6

## Detailed Results

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

