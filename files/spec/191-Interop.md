[< 190 Callbacks](190-Callbacks.md) | [Index](index.md) <!-- nav -->

# 191 Interop

## External Interoperability

**Status:** [DESIGN] (MOD.006) - running another program is built: `run(command)` ([140 Collections](140-Collections.md),
28.1.1); loading a DLL needs `extern` (MOD.003); language modules `Lang.<language>.Fusion` (Task 49)

Description: Integration with external code and systems.

---

### DLL Loading

```
import Fusion.System.DllLoader

DLL lib = DLL.load("mylib.dll")
type AddFunc = int function(int, int)
AddFunc add = lib.getFunction<AddFunc>("add")
int result = add(10, 20)
lib.unload()
```

---

### External Processes

Built today: `int code = run("python script.py")` waits and returns the exit code; capturing the
output and a separate `start` come later. The earlier design:

```
import Fusion.System.Process

Process proc = Process.start("python", ["script.py"])
string output = proc.readOutput()
int exitCode = proc.exitCode
```

---

### Assembly Language

Only in `unsafe` code (files/Object_Lifetime.md 2: `unsafe` is for memory, assembly and devices);
`@Unsafe` below is the earlier way of writing `unsafe void function`.

```
@Unsafe
int function fastAdd(int a, int b)
    int result
    asm
        mov eax, [a]
        add eax, [b]
        mov [result], eax
    return result
```

---

### External Compilers

Next to the language modules (Task 49) - which one loads an outside compiler is open.

```
import Fusion.Lang.Compiler

Compiler msvc = Compiler.loadExternal("fusion-msvc-x64.dll")
msvc.setOptimizationLevel(3)
CompileResult result = msvc.compile("code.fusion")
```

[< 190 Callbacks](190-Callbacks.md) | [Index](index.md) <!-- nav -->
