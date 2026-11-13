[< 110 SymbolIDs](110-SymbolIDs.md) | [Index](index.md) | [120 Threads >](120-Threads.md) <!-- nav -->

# 111 Identity

**Status:** idea - FEATURES 42.28

## An Identity for Everything: a GUID per Name, a Small Database of the Hierarchy

**Status:** Idea for future consideration (user, 2026-11-02) - recheck later (files/FEATURES.md
42.28). Related: SET.024 (an IDE module with a symbol database), 36.5 (language server),
36.6 (the thread view), and "Threads, Schedulers and Services" above.

**The idea:** every namespace, module, class, function, variable and nested field gets its
own GUID, plus a readable path - the user's example:
`namespace:Core.Class:Main.Thread:CarService.Car:car.Engine.engine.int:Horsepower`

**Why (the user):**
- **The compiler checks by GUID alone** whether a variable or object is used in a thread -
  so it knows when an explicit or automatic service, or a group service, is needed
- **A hierarchy stored in a small database**, together with the code's hashes: which
  namespace holds which module, class, function and variable, and which threads and group
  services use each. The compiler reads it to tell which variables / objects are in a thread
  or group service
- **Refactoring:** in future, each name refers to its GUID instead of being written by hand
  everywhere - a rename changes the index, not every file

**Done before:** Unison stores code by content hash, names being only labels (renames never
break anything - but its source of truth isn't text files); C# / Roslyn give every symbol an
ID string (`M:Core.Car.Drive(System.Int32)`) used for rename refactoring; Fusion's compiler
already mangles names for C (`fu_Car__drive`).

#### Two different things inside it

| | A readable path | A stable ID (GUID) |
|---|---|---|
| Example | `Core.Main.CarService.car.engine.horsepower` | `7f3c...` |
| Comes from | the code's structure | stored (the database) |
| On a rename | changes | stays the same |
| Cost | small - the symbol table knows it already | an index kept in step with the files |
| Serves | diagnostics, the thread map, the profiler heatmap, deciding services | renames across files and libraries |

#### Points to settle (from the discussion)

1. **A thread isn't a container:** a variable belongs to its function or class in the code;
   *which threads use it* is worked out by the compiler (and can differ between runs). Keep
   the thread out of the ID and record it as a link - "used by thread CarService" - in the
   database. That link is what decides a service
2. **The type isn't identity:** `int` -> `long` would change the ID; keep the type as
   information about the ID
3. **Overloads and repeated names:** several constructors share a name; two blocks can each
   declare `i` - a signature or position tells them apart
4. **A declaration vs an object:** one declared `car` can have many `Car` objects while
   running - the heatmap and thread view need both the declaration's ID (fixed when
   compiling) and each object's own number (made while running)
5. **Short numbers while running:** GUIDs are 128 bits - small integers mapped to them keep
   the program fast; the GUIDs stay in the database. Random GUIDs (version 4), never ones
   holding the machine's address
6. **Problems with stored IDs:** git merges (two people adding names change the database at
   once), copy-paste duplicating an ID, edits made outside Fusion's tools leaving the database
   out of step, other projects still seeing a library's names (a public rename needs an alias)

#### A path that fits "simple first"

1. **With the Task 42 thread work:** the compiler gives every declaration its path and a
   number per build, and records which thread uses which variable - for diagnostics, the
   profiler, the heatmap and deciding services. No files change
2. **With the language server (36.5):** rename refactoring through the compiler's symbol
   table, as C# and Java do - most of the "change once" benefit, with no stored IDs
3. **Far future:** stable GUIDs in the small database with the code's hashes (or content
   hashes as in Unison); libraries publish old name -> ID -> new name

[< 110 SymbolIDs](110-SymbolIDs.md) | [Index](index.md) | [120 Threads >](120-Threads.md) <!-- nav -->
