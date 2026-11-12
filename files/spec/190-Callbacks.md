[< 183 fusionlib-IDE](183-fusionlib-IDE.md) | [Index](index.md) | [191 Interop >](191-Interop.md) <!-- nav -->

# 190 Callbacks

## Callbacks and Events

**Status:** [PARTLY] function values, function types and lambdas are built (18.1.3, SYN.004 - [041 Lambdas](041-Lambdas.md)),
so a callback works today; events (`Event<...>`, `+=`) and type aliases: design, no task yet (MOD.007)

Description: Function pointers and event-driven programming.

**Note** (earlier design, not decided): callbacks not allowed in strict mode where performance matters most -
they add overhead and unpredictability. Today `[safety] mode = "strict"` means every warning is an error;
the hot path (`hotpath`, D.019) is where such a limit would belong.

**Built today** (compiled and run, 2026-11-12):

```fusion
void function processData(int data, (int) -> void onComplete)   // a function type as a parameter
    onComplete(data * 2)

void function show(int r)
    print("Result: {r}")

void function main()
    processData(42, show)                                      // Result: 84
    processData(21, func(int r) : print("Lambda: {r}"))       // Lambda: 42
```

**The earlier design** (type aliases, `lambda r:`, events - not built; the lambda is written
`func(int r) : ...` today):

**Function Types**:
```
// Define callback type
type Callback = void function(int result)
type EventHandler = void function(Object sender, EventArgs args)

// Use callback
void function processAsync(int data, Callback onComplete)
    int result = data * 2
    onComplete(result)

// Lambda callback
processAsync(42, lambda r: print("Result: {r}"))

// Events
class Button
    Event<void function(Button)> onClick
    
    void function click()
        onClick.invoke(this)

Button btn = Button()
btn.onClick += lambda b: print("Clicked!")
```

[< 183 fusionlib-IDE](183-fusionlib-IDE.md) | [Index](index.md) | [191 Interop >](191-Interop.md) <!-- nav -->
