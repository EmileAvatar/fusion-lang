[< 120 Threads](120-Threads.md) | [Index](index.md) <!-- nav -->

# 130 Far Future

**Status:** idea - after self-hosting (Task 35)

## Far Future (after self-hosting): traits from variables, types made while running, DLCs and mods

**Status:** 💭 Far-future discussion (user, 2026-10-31) - not in files/FEATURES.md or Decisions.md
yet; recheck after self-hosting (Task 35). Beyond the current scope.

### 1. Interfaces held in a variable, used as traits

- A basic interface has no methods with code - default methods are a setting, off (Decisions.md D.006)
- Instead, a **variable** implements the interface, and its functions get their code in the
  form B set-up block `{ ... }`
- That variable can then be **added to classes** as needed - as a trait (reusable behaviour),
  or as a variable inside the class

```fusion
// a sketch only - the syntax is to be designed
Drivable wheels = Drivable() {
    wheels.drive = function(int speed) : print("driving at {speed}")
}

class Car
    uses wheels                // added as a trait - Car can drive
class Truck
    Drivable motion = wheels   // or held as a variable in the class
```

### 2. Interfaces and structs made while the program runs (enterprise flexibility)

- For enterprise systems that need the most flexibility: new interfaces and structs created
  while the program runs
- A **struct is the template**: it only holds the names and types of the members to make -
  the functions for a new interface, the fields for a new struct
- A **special class** (a type builder) reads the template and generates the new interface or
  struct
- Structs still never implement an interface (Decisions.md STC.005) - here a struct only
  describes what to make
- To work out then: Fusion compiles to static C, so this needs type information at run time
  and calls looked up at run time - kept to the code that asks for it, so the rest of the
  program stays static and fast

### 3. DLCs, mods and frameworks for the compiler

**Terms (user):**

| Term | What it is | Who makes it |
|---|---|---|
| **DLC** | A major add-on pack that enhances the base Fusion - officially supported | The Fusion team |
| **Mod** | A modification of the base Fusion that adds functionality: a team mod that didn't make a DLC and isn't planned for Fusion, or one made by fans / customers for their own needs; shared as needed (Steam Workshop as the model) | The Fusion team, fans, customers |
| **Framework** | The rules for **how, where and when** a DLC or mod may change things | The Fusion team |

**How it works (user):**
- The **Fusion compiler stays the same** - a mod never patches it
- The framework builds the DLC / mod into a **second binary** holding the new code; the
  compiler uses it through the framework
- A mod developer implements a **minimal set of features** the framework asks for - for
  example how an editor understands and shows the new syntax, and how the compiler compiles it
- What a mod may change (each allowed by the framework's rules): how code compiles, new
  types, parsing, the editor / IDE, the GUI, settings
- Instead of asking for a language feature, a developer can add it as a mod; a mod that
  becomes very popular can be added to Fusion itself

**The goal (user):** Fusion covers about 85% of the features of C, C++, C#, VB.NET, Java,
Rust and Python in one language; the other ~15% - features that don't suit Fusion's core -
come as DLCs and mods.

**Prior art:** Haskell (GHC) language extensions switched on per file, the popular ones later
folded into the standard set (GHC2021); Babel plugins trying JavaScript syntax before it
enters the standard; Racket (`#lang`: a language as a library); Kotlin / Scala compiler
plugins; Rust procedural macros; RimWorld's Harmony (a base mod other mods build on).

**Points to design then (Claude's notes, 2026-10-31):**
- **Fragmentation:** every mod lowers to base Fusion or the IR (Task 40); a tool shows the
  plain result; a module's public interface stays expressible in base Fusion, so code with
  and without a mod works together (files/FutureFeaturesCaution.md, Caution 3)
- **Security:** a mod runs code while building - sandboxed, with capability signatures
  (Task 39); official DLCs signed; tiers: DLC, verified mod, community mod
- **Compiler updates:** the framework is a stable, versioned API; each mod states the API
  version it supports
- **Two mods changing the same thing:** detected when they load, with a declared order - an
  error, never a silent winner
- **Settings:** a project lists its DLCs and mods in `fusion.toml` - features already become
  settings, so they are the first built-in "mods"
- **The 85% goal:** some features exclude each other (GC and ownership, exceptions and error
  returns); measure by what developers can do, not by a count of features
  (files/FutureFeaturesCaution.md, Caution 2)




---

**End of Future Features Document**

**Status:** Documented, pending implementation
**Next Review:** After MVP compiler completion
**Last Updated:** 2026-09-27

[< 120 Threads](120-Threads.md) | [Index](index.md) <!-- nav -->
