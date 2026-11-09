[< 040 Functions](040-Functions.md) | [Index](index.md) | [042 MultipleReturns >](042-MultipleReturns.md) <!-- nav -->

# 041 Lambdas

## Lambda Expressions (Anonymous Functions)

Description: Variables that hold functions. Lambdas are first-class citizens with full type safety.

**Implemented so far (Task 18.1.3 - lambdas v1, no closures):**

```
int function tripler(int x) : x * 3
int function apply((int) : int op, int value) : op(value)    // function-typed parameter

(int) : int op = tripler               // a named function as a value
op = func(int x) : x * 2               // inline lambda - return type inferred from the body
int a = op(5)                          // call through the variable
int b = apply(function(int x) : x - 1, 4)
int c = apply((int x) : x * x, 9)      // short form, no keyword
(int, int) -> int add = func(int p, int q) : p + q    // '->' works as well as ':'
(int) : int function pick() : tripler                 // functions can return functions
```

* Function types: `(paramTypes) : returnType` or `(paramTypes) -> returnType`
* **No closures yet** - a lambda may use only its own parameters and top-level functions;
  using a variable of the surrounding function is a compile error. Captured variables must
  outlive the function that created the lambda, which needs Fusion's heap-ownership rules
  (Task 18.3) first. The closure examples below are the intended design, not yet working
* A function variable must be initialized (no `null` functions yet)
* Lambda bodies are a single expression; the multi-line forms below aren't supported yet
* Lambda parameters can't have defaults or be arrays; builtins (`print`, `len`, `range`)
  can't be used as values; a function with array parameters can't be used as a value
* Note: examples below such as `int multiply = func(int x, int y) : x * y` declare the
  variable as `int` - the implemented form uses a function type:
  `(int, int) : int multiply = func(int x, int y) : x * y`

**Key Concept**: A lambda is a variable that holds a function. Use `func` or `function` keywords interchangeably based on preference.

**Format**: `<returnType> <variableName>(<type> <param> {= default}) : <expression or body>`

---

* **Simple Single-Line Lambdas**

```
// Basic lambda - variable holds function
int add(int x, int y) : x + y

// Use it like a function
int result = add(5, 3)  // result = 8

// Another example
int double(int x) : x * 2
int value = double(10)  // value = 20
```

* **Lambdas with Default Values**

```
// Lambda with default parameter
int addWithOffset(int x, int offset = 5) : x + offset

int result1 = addWithOffset(10)      // result1 = 15 (uses default offset = 5)
int result2 = addWithOffset(10, 2)   // result2 = 12 (uses offset = 2)

// String concatenation with default
string greet(string name, string greeting = "Hello") : greeting + ", " + name
string msg1 = greet("Alice")           // msg1 = "Hello, Alice"
string msg2 = greet("Bob", "Hi")       // msg2 = "Hi, Bob"
```

* **Multi-Line Lambdas with Indentation**

```
// Comparison lambda - multi-line with indentation
int comparator(int a, int b) :
    if a < b
        return -1
    if a > b
        return 1
    return 0

int result = comparator(5, 10)  // result = -1

// Complex calculation
float calculate(float x, float y) :
    float sum = x + y
    float product = x * y
    return sum / product

float answer = calculate(4.0, 5.0)
```

* **Multi-Line Lambdas with Braces**

```
// Using braces instead of indentation (user preference)
int process(int value) : {
    int doubled = value * 2
    int added = doubled + 10
    return added
}

// Braces allow flexible formatting
string format(string text, bool uppercase) : {
    if uppercase
        return text.toUpper()
    return text.toLower()
}
```

* **Using func or function Keywords (Optional)**

```
// Both keywords work - user preference
int multiply = func(int x, int y) : x * y
int divide = function(int x, int y) : x / y

// Multi-line with func
int square = func(int x) :
    return x * x

// Multi-line with function and braces
int cube = function(int x) : {
    return x * x * x
}

// Keywords are completely interchangeable
```

* **Lambdas as Function Parameters**

```
// Function that accepts lambda as parameter
// Type annotation uses : (default) or -> (alternative)
List<int> function mapValues(List<int> values, (int) : int operation)
    List<int> result = List<int>()
    for value in values
        result.add(operation(value))
    end loop
    return result

// Define a lambda
int tripler(int x) : x * 3

// Pass lambda as argument
List<int> numbers = [1, 2, 3, 4, 5]
List<int> tripled = mapValues(numbers, tripler)  // [3, 6, 9, 12, 15]

// Or define lambda inline
List<int> doubled = mapValues(numbers, func(int x) : x * 2)  // [2, 4, 6, 8, 10]
```

* **Closures - Capturing Variables**

```
// Lambda can capture variables from outer scope
int makeAdder(int offset)
    // This lambda captures 'offset' from outer scope
    int adder(int x) : x + offset
    return adder

int add5 = makeAdder(5)
int add10 = makeAdder(10)

int result1 = add5(3)   // result1 = 8  (3 + 5)
int result2 = add10(3)  // result2 = 13 (3 + 10)
```

* **Type Annotations for Lambdas**

```
// Function type syntax: (paramTypes) : returnType
// Alternative syntax: (paramTypes) -> returnType  (both work)

// Declare variable to hold function
(int, int) : int calculator = null

// Assign lambda to it
calculator = func(int a, int b) : a + b
int sum = calculator(5, 3)  // sum = 8

// Change the lambda
calculator = func(int a, int b) : a * b
int product = calculator(5, 3)  // product = 15
```

**Rules**:
* Lambda = variable that holds a function (NOT a separate keyword)
* Return type comes first (consistent with function declarations)
* `func` and `function` keywords are optional and interchangeable
* Single-line: use `:` followed by expression
* Multi-line: use `:` followed by indented block or `{}`
* Type annotation separator: `:` (default) or `->` (alternative)
* Explicit types always required (except in unsafe mode)
* Lambdas can capture variables from outer scope (closures)
* Lambdas are first-class: can be passed as arguments, returned from functions, stored in variables

[< 040 Functions](040-Functions.md) | [Index](index.md) | [042 MultipleReturns >](042-MultipleReturns.md) <!-- nav -->
