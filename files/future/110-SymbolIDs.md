[< 101 CLICommands](101-CLICommands.md) | [Index](index.md) | [111 Identity >](111-Identity.md) <!-- nav -->

# 110 Symbol IDs

**Status:** idea - no task; an identity for everything is FEATURES 42.28

Contents: [Compiler Infrastructure Enhancements](#compiler-infrastructure-enhancements) | [Core & Additional Packages — Fusion vs Other Languages](#core--additional-packages--fusion-vs-other-languages) | [Additional Specialized Packages (Not Core – Optional Ecosystem Modules)](#additional-specialized-packages-not-core--optional-ecosystem-modules)

## Compiler Infrastructure Enhancements

### Symbol-ID System

**Status:** 📝 Proposed - far future. This depends on infrastructure Fusion doesn't have
any of yet: multiple source files, a module/class system, and a package manager at minimum
(`import` itself has no parser support today - confirmed by source search). Realistically
post-self-hosting territory, not a near-term item. Written down so the idea isn't lost, not
because it's close to being scoped.
**Purpose:** Enable stable refactoring and cross-language interoperability

**What:** Internal symbol referencing using hashed IDs instead of text names, with configurable per-project or per-class activation.

**Update (2026-09-27):** a second, more detailed pass at this same idea arrived via user
notes (`Notes/03/Fusion_Compiler_Symbol_Index_System.md`, written with limited knowledge of
Fusion's current implementation). It fixes a real logical problem in the design below and
adds mechanisms worth folding in - see "Rename-Stability Fix" and "Distributed Refactoring"
after the original design.

#### How It Works

**Traditional approach (name-based):**
```fusion
class UserService
    void function createUser(string name)

// Renaming requires changing everywhere it's used
// 50+ files might reference "createUser"
```

**Symbol-ID approach (ID-based):**
```
Internal representation:
- Symbol: createUser → ID: @A1B2C3D4
- Symbol table maps: @A1B2C3D4 → "createUser"
- Renaming updates only the symbol table
```

#### Symbol Table File

**Example: `symbols.fusion`**
```
// Auto-generated symbol table
@A1B2C3D4 = class UserService
@E5F6G7H8 = function createUser
@I9J0K1L2 = function deleteUser
@M3N4O5P6 = interface IAuthService
@Q7R8S9T0 = enum UserRole
```

**Internal compilation:**
```fusion
// Developer writes:
class UserService
    void function createUser(string name)

// Compiler stores:
class @A1B2C3D4
    void function @E5F6G7H8(string name)
```

#### Benefits

##### 1. Instant Refactoring

**Rename function:**
```
// Change symbol table only
@E5F6G7H8 = function createUser → @E5F6G7H8 = function registerUser

// All code automatically uses new name
// No source file changes needed
```

##### 2. ABI-Safe Linking

**Backend compilation:**
```c
// C backend links to stable ID, not name
void userservice_A1B2C3D4_E5F6G7H8(char* name) {
    // Implementation
}
```

**Renaming doesn't break compiled libraries:**
```
Old version: createUser → @E5F6G7H8
New version: registerUser → @E5F6G7H8
Binary compatibility maintained!
```

##### 3. Cross-Language Interoperability

**Python calling Fusion:**
```python
# Python imports using stable IDs
from fusion_lib import symbol_E5F6G7H8 as create_user

create_user("Alice")
# Works even if Fusion renames the function
```

##### 4. Database-Like Symbol Management

```fusion
// Query symbols
List<Symbol> symbols = SymbolTable.findAll("*User*")
// Returns: UserService, createUser, deleteUser, UserRole

// Symbol metadata
Symbol sym = SymbolTable.get("@E5F6G7H8")
print(sym.name)           // "createUser"
print(sym.type)           // "function"
print(sym.references)     // 47 locations
print(sym.definedIn)      // "UserService.fusion:23"
```

#### Configuration

**Enable/disable per project:**
```toml
# fusion.toml (corrected 2026-09-27 - Fusion's real project config format is TOML,
# decided in Task 12.12; the original JSON example predates that decision)
[symbols]
enabled = true
symbol_table_file = "./symbols.fusion"
```

**Enable/disable per class:**
```fusion
// Enable for this class
@symbolId(enabled: true)
class UserService
    // All symbols in this class use IDs

// Disable for this class
@symbolId(enabled: false)
class LegacyCode
    // Uses traditional name-based approach
```

#### Symbol ID Generation

**Hashing algorithm:**
```
ID = SHA256(fullyQualifiedName + salt)[0:8]

Examples:
- "fusion.auth.UserService.createUser" → @A1B2C3D4
- "fusion.auth.UserService.deleteUser" → @I9J0K1L2
```

**Collision handling:**
```
If hash collision detected:
- Append sequence number: @A1B2C3D4_1, @A1B2C3D4_2
```

**Rename-Stability Fix (2026-09-27) - this hashing scheme has a self-defeating flaw:**
hashing the *fully qualified name* means renaming a symbol changes its name, which changes
the hash input, which changes the ID - exactly the thing this system exists to prevent. A
rename would silently break every reference it was supposed to protect. The fix, taken from
the newer note referenced above: generate the ID **once, at creation, independent of the
name entirely** (a random or creation-time-ordered identifier, e.g. ULID-style
`01J8ZK4M2Q...`), and store the current name as a separate, mutable field that changes
freely on rename. The ID itself never derives from anything that can change - not from the
name, not from the file path, not from anything a refactor would touch. This is a
correction to the mechanism, not to the goal - the SHA256 approach above should not be
implemented as designed; the ID-assigned-at-creation approach below should be, if this ever
gets built.

#### Distributed Refactoring (2026-09-27 addition)

The newer note above adds mechanisms this design didn't originally have, worth keeping
together with it rather than as a separate proposal:

- **Persistent, regenerable database** - `.fusion/symbols.db` (plus dependency/reference/
  type indexes) instead of a single flat `symbols.fusion` file, so large projects don't
  reload and re-derive everything on every compiler invocation. Source remains the single
  source of truth; the database can always be deleted and rebuilt from it.
- **Symbol lifecycle rules**, missing from the original design:
  - **Renamed/moved:** ID unchanged, only name/path/file change.
  - **Copied:** the copy gets a **new** ID - a copy is a new logical entity, not the same
    one appearing twice.
  - **Deleted:** the ID is tombstoned, never reused - so stale references (old branches,
    cached IDE state) get a clear "this symbol was deleted" diagnostic instead of silently
    binding to an unrelated later symbol that happened to reuse the same ID.
- **A committed refactor log** (`fusion/refactors/`, outside the deletable `.fusion/` cache)
  for team/distributed use: every rename/move/delete/split/merge produces an append-only,
  git-committed entry (author, timestamp, before/after, a signature hash to verify the
  entry applies to the symbol the receiver actually has). When a developer pulls new
  changes, their local tooling replays new refactor entries against their own database, so
  everyone's IDE stays in sync with the project's current symbol identities without a
  rename ever silently breaking someone else's branch. Conflict detection (e.g. the same
  ID renamed two different ways on two branches) is surfaced precisely by the compiler, but
  resolution stays the job of source control and the reviewer - not the compiler.
- **A real, acknowledged cost worth deciding explicitly rather than assuming away:**
  embedding the ID directly in the raw source text (with the name kept only as a "backup"
  the compiler verifies against the database) makes plain-text `grep`, diffs, and code
  review noticeably worse without Fusion-aware tooling. A less invasive alternative that
  gets most of the same benefit: keep the same creation-time IDs and the same refactor log,
  but store the ID **only in the out-of-band database** (keyed by file + position + a
  content hash), never touching the source text at all - closer to how Roslyn (C#) and
  rust-analyzer already do stable incremental analysis and safe renames today. Whichever
  approach is chosen, it should be a deliberate decision made with real tooling and
  real-project experience in hand, not assumed by whichever note happened to describe it
  first.

#### IDE Support

**Symbol browser:**
```
📁 Symbol Table
  ├─ @A1B2C3D4 → UserService (class)
  ├─ @E5F6G7H8 → createUser (function) [47 refs]
  ├─ @I9J0K1L2 → deleteUser (function) [12 refs]
  └─ @M3N4O5P6 → IAuthService (interface) [8 refs]
```

**Refactoring:**
```
Right-click createUser → Rename → registerUser
// IDE updates symbol table only
// Shows: "47 references will use new name automatically"
```

#### Limitations & Tradeoffs

**Pros:**
- Instant, safe refactoring
- ABI stability across versions
- Easier cross-language linking
- Centralized symbol management

**Cons:**
- Symbol table file must be maintained
- Debugging shows IDs instead of names (IDE must translate)
- Requires tooling support
- Adds complexity to build system

**When to use:**
- Large projects with frequent refactoring
- Libraries with public APIs (ABI stability)
- Cross-language interop projects
- Enterprise codebases with strict versioning

**When NOT to use:**
- Small scripts/prototypes
- Single-developer projects
- Legacy codebases without tooling support


- user added note: IDE should not show the ID in any case.
- IDE shows a rendered layers including the perfered coding preference (indention, {}, keywords) as part of Fusion core functonality.
- when edditng the raw file format then it will show the ID's like @A1B2C3D4_1 and an internal format that uses {}.
- Symbole table is regenated when rebuild build and is used while editing a file gets automatically updated.

---

User added content - Copied from chat gpt to be reviewd.
## Core & Additional Packages — Fusion vs Other Languages

- Most major languages ship with similar core packages (strings, math, collections, IO, networking, data formats, concurrency).
- Fusion’s standard library exceeds these by integrating 22 modules: Core (5), Additional (12), IDE/Tooling (5).

Fusion matches or exceeds Java, Python, Go, Rust in:
• Networking (TCP/UDP/HTTP/WebSocket)
• Data formats (JSON, XML, YAML, CSV, Markdown, INI)
• Concurrency (threads, goroutines, channels)
• Graphics, GUI, Audio
• Crypto, Database, Web servers
• Reflection, Testing, Diagnostics, Documentation generation

Fusion also provides unique capabilities:
• Multi-syntax support (indent, braces, keywords)
• Multi-backend execution (native, bytecode, interpreter)
• 3-tier memory system (GC, Smart, Raw)
• Auto-thread locking and deadlock detection
• Built-in multi-language compilers (fusionlib.Lang)
• IDE integration module (LSP, formatter, syntax generator)

- Missing or planned features: • Regex module - i think we did dis one already.
- • Physics engine module • DataFrame/Numerics modules (Pandas/NumPy equivalents) • AI/ML expansion • Enhanced DateTime utilities

here is an updated summary from chat gpt to be reviewed as well

- Here is the **clean, concise, ready-to-paste section** for **files/FutureFeatures.md**, following your structure and style.
- It fits naturally into your existing document and uses wording consistent with the rest of the Fusion spec.


## Additional Specialized Packages (Not Core – Optional Ecosystem Modules)

- These packages extend Fusion for domain-specific or high-performance workloads.
- They are **not part of the core 22 modules**, but should be available as **separate optional packages** within the Fusion ecosystem.

[< 101 CLICommands](101-CLICommands.md) | [Index](index.md) | [111 Identity >](111-Identity.md) <!-- nav -->
