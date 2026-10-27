# Fusion - Working File (active task plans)

**What this file is (Task 22, 2026-10-09):** only the task being worked on now - its detailed
plan, the next action, and the latest session note. Keep it small: it is read often.
- Status of every task and feature: `FEATURES.md` (`[ ]` open, `[DONE]`, `[POSTPONED to ...]`)
- Finished tasks and sub-tasks, old sessions: `task/taskSummaryArchive.md` (verbatim)
- Not-started task write-ups: `task/taskBacklog.md` (verbatim)
- Rules (plan first, no emojis in code, ...): `CLAUDE.md`

---

## Current status (2026-10-11)

**Task 18 (core language foundation) is COMPLETE** and archived (plans, notes and the
FEATURES.md detail are in `task/taskSummaryArchive.md`). Task 10.2 is met.

---

## Current plan: the roadmap (FEATURES.md, renumbered 2026-10-11)

Done tasks keep their numbers; open tasks were renumbered from 25 into three phases (the
approved plan is archived). Phase 1 = 25 enums, 26 error handling, 27 semantic contract and
safety (bounds checks, the three-block-style check), 28 self-hosting test run.

---

## TASK 29: Strings - editing, fixed, templates, pooling - ACTIVE (approved 2026-10-27)

**Answers (user, 2026-10-27):** 1. prefix table agreed; 2. templates use `t"..."`;
3. 29.4 pooling postponed (to Task 38). 29.1 done.

Source: FEATURES.md Task 29, backlog write-up (task/taskBacklog.md "TASK 29"),
FutureFeatures.md "Mutable vs. Fixed Strings". User notes 2026-10-27: pooling off by default;
`p"Andrew"` forces pooling; changing a pooled variable changes only that variable; prefixes
`m"` mutable, `f"` fixed, `a"` ASCII-only (embedded / legacy calls).

**What is true today (checked 2026-10-27):**
- Strings are values: `b = a` gives an independent copy; changing `b` never changes `a`
- A literal is stored once in the exe and shared by every variable that holds it until that
  variable gets new text (owned = 0, never freed; GCC merges equal literals). So literals are
  already "pooled" for free - `p"Andrew"` would change nothing
- `const string name = "Andrew"` works (locals and module constants): never changes
- `s[0] = 'X'` is a compile error; `[strings] encoding = "ascii"` exists (whole project)
- Struct fields: `[structs] string_mutable` / `string_storage = "owned"` ("pooled" reserved)

**Prefix review (recommendations):**

| Prefix | Meaning proposed | Recommendation |
|---|---|---|
| `m"..."` | mutable | Reject - a plain string already is; two spellings for one thing |
| `f"..."` | fixed | Reject - `const string` already does it; `f"` reads as "formatted" to Python / C# users; fixed-ness belongs to the variable, not the text |
| `a"..."` | ASCII only | Postpone to `extern` / legacy calls (FEATURES Later) - the project setting covers embedded; a per-call ASCII conversion belongs at the call boundary, since run-time values cross it too |
| `p"..."` | pooled | Reject on literals (already shared); pooling matters for text built at run time -> `pool(s)` (29.4) |
| `r"..."` | raw, no escapes | Already in FEATURES Later - worth adding (Windows paths) |
| `"""..."""` | multi-line | Already in FEATURES Later |
| `b"..."` | bytes literal | Idea - FEATURES Later |

**Sub-tasks:**
- **29.1 In-place editing** `s[i] = c` on a string variable: bounds-checked (IndexError); a
  literal-held string is copied first (the literal never changes); a char of a different byte
  width rebuilds the text; the hint cache (44.6) is cleared. Not allowed on `const`
- **29.2 Fixed strings = `const`** (no new type): `s[i] = c` on a const is a compile error;
  struct fields keep `string_mutable`. Document; spec + SYNTAX_REFERENCE
- **29.3 Templated strings** (user design 2026-10-27, no `t"` prefix):
  `template string greet = "Hello {@1}, you are {@2}"` - `template` marks the string
  constant and makes it an internal function: `string function greet(@1, @2)` whose body is
  the interpolated text. `greet("Ann", 30)` calls it. Each `{@N}` takes any printable value;
  the argument count comes from the highest `{@N}` (a gap such as `{@1} {@3}` is a compile
  error). `{name}` is ordinary interpolation, read when the template is called; an unknown
  name is a compile error. Local and module-level. `template` is a modifier word kept open
  for other uses later (contextual, so it still works as a name). Built by lifting a
  function around `format()` - no new run-time
- **29.4 String pooling** - setting `[strings] pooling = false` (default) and a built-in
  `pool(s)`: equal run-time text shares one copy (a reference count, copy-on-write on edit,
  freed when the last one goes). Never visible to a correct program. This adds a count to
  every string in the run-time and the self-hosted compiler's output - the biggest part;
  could be **postponed** until a profile shows the need (backlog note)
- 29.5 secure strings: stays postponed (fusionlib.Crypto)
- **29.6** examples, spec "String Implementation", Builtins.md, FEATURES

**Questions:**
1. Prefixes: agree with the table (no `m"` / `f"` / `p"`; `a"` later with extern)?
2. 29.3 syntax: `template greet = "..."` (new keyword) or `t"..."` prefix
   (`greet = t"Hello {@1}"`, like Python 3.14's t-strings)?
3. 29.4: build now, or postpone to Task 38 (memory model - Shared is the same reference
   count) / until a profile shows the need?

---

## TASK 44: Lessons from the self-hosting test run - COMPLETE (2026-10-26)

Long lines inside ( ) [ ] (44.3), `end` / `var` as names and `_` documented (44.5), fast
text[i] (44.6), module-level variables and constants (44.1), any function as a method
(44.2); 44.4 postponed. Plan: task/taskSummaryArchive.md.

---

## TASK 28: Self-hosting phase 1 - the test run - COMPLETE (2026-10-26)

A Fusion compiler written in Fusion (selfhost/, ~3,500 lines) builds all 18 tier 1 programs;
each prints what the Python-built one prints, leak-free (`python check.py --selfhost`).
Report: task/selfhost_report.md. Plans and notes: task/taskSummaryArchive.md.

---

## TASK 23.9: Fusion_showcase.fusion - COMPLETE (2026-10-23)

files/showcase/Fusion_showcase.fusion + fusion.toml: every feature tagged [built] /
[designed] / [idea] / [rejected] with a one-line description. Plan: task/taskSummaryArchive.md.

---

## TASK 27: Semantic contract and safety - COMPLETE (2026-10-17)

Bounds checks, three block styles, overflow / wrapping / unsafe mode, endless recursion,
interaction tests, changing a collection while looping, the contract (spec "The Semantic
Contract"), int to float ([numbers] auto_widening, 27.2f). Plan: task/taskSummaryArchive.md.

---

## TASK 26: Error handling - COMPLETE (2026-10-16)

Error values, functions that can fail, capturing, bubbling, try / catch / finally / throw,
every built-in failure catchable, `[errors]` switches, examples/errors_demo. Part 2 (26.7-26.13):
implicit errors, untyped capture, custom error types, err.kind, match on error types, typed
catch, Fusion's own error types. Plan and notes:
`task/taskSummaryArchive.md`.

---

## TASK 25: Enums and tagged unions - COMPLETE (2026-10-12)

Plain enums, `match`, enums with data, enums holding themselves, and the expressions
example. Plan and notes: `task/taskSummaryArchive.md`.

---

## TASK 22 (housekeeping) - ACTIVE (user: "do the housekeeping first and the ascii issue first")

Kept under Task 22 until the renumbering is approved.

- 22.8-22.11 DONE (tools; detail archived)
- 16.1 DONE - examples/control_flow
- 22.7a DONE - README reduced to goals + pointers
- 22.7b DONE - spec status lines (Task 22 complete)
- Each one: FEATURES.md line, `task/automation.md` row marked Automated, check, commit

---

## Working Notes

### Session 31 (2026-10-09 .. 10-11 - 18.3.5 to 18.5.7)
- Done: 18.3.5 equality, 18.3.5b bool printing, 18.3.6 string library (a-f, masking design
  and build), 18.3.7 type classes / methods, 18.3.8 bytes, 18.4 modules (1-4), 23.7 / 23.8
  (wait at exit, --headless, .fusion preview), Task 24 added (editor support), 18.5 (1-7)
- User preferences saved to memory: as little typing as possible; never change values
  silently
- Task 18 archived (FEATURES.md detail too); 3 automation candidates added
- 22.8-22.11 done: check.py --fix-ascii / --ship / --example, tools/patch.py
- 16.1 done: examples/control_flow; map literals noticed missing (FEATURES.md Later)
- 22.7a done: README is goals + pointers (554 -> 321 lines); 22.7b waits for the renumbering
- User answered: numbers from 25, classes / generics in Phase 2. ChatGPT review read:
  fixed arrays are not bounds-checked (segfault) -> new Task 27 "semantic contract and safety"
- FEATURES.md reorganized into phases and renumbered (22.12); the user asked for 27.1
  (bounds checks for fixed arrays) and 27.4 (one app in 3 block styles -> identical C)
- 2026-10-12: 22.7b done - a status line under each of the spec's 31 major sections; Task 22
  complete
- Task 25 plan approved (all 4 recommended answers)
- 25.2 plain enums and 25.3 `match` done
- 25.4 enums with data done
- 25.5 enums holding themselves done
- Task 25 complete (25.6: examples/expressions)
- Task 26 plan approved (bubble up, capture any call, all built-ins catchable, one catch)
- 26.2 done
- 26.3 done
- 26.4 done
- 26.5 done
- Task 26 complete (26.6: examples/errors_demo)
- Task 26 part 2 planned, 4 questions answered
- Plan updated (default message, match on error types, typed catch now, built-in
  error type list)
- 26.7 done
- 26.8 done
- 26.9 done
- 26.10 done
- 26.11 done
- 26.12 done
- Task 26 part 2 complete (26.7-26.13)
- Task 27 plan approved (bounds always; wrapAdd functions; stack use + max_call_depth; unchecked blocks)
- 27.1 done
- 27.5 and 27.4 done
- 27.2b and 27.2d done
- 27.2c done
- 27.3 done (found: changing a list while looping over it skips elements)
- Task 27 complete; 27.2f done ([numbers] auto_widening, default false)
- 23.9 done: files/showcase (Fusion_showcase.fusion + fusion.toml); user answered: files/showcase/,
  tags built / designed / idea / rejected + one-line description each
- 28.1 done: the subset measured (task/selfhost_subset.md, tools/example_subset.py)
- User: tier 1 is the test-run target; 28.1.1-28.1.3 sub-tasks; 28.1.4 builtins list proposed
- Plan approved (user: 28.1.4, then 28.1.1). 28.1.4 done: files/Builtins.md, generated and
  checked
- 28.1.1 done: run(command), ProcessError, tests, SYNTAX_REFERENCE example
- 28.1.2 done: measured (selfhost/prototype/) - pattern B over bytes is fast; no compiler
  change needed; slow string indexing found (FEATURES.md Later)
- 28.1.3 done: runtime/fusion_runtime.h; all 45 examples print the same with it
- 28.1 complete (plan archived)
- 28.2-28.8 planned (taskSummary2.md); gap found: no literal { in strings -> 28.1.5
- Plan approved (one walk, leak-free, errors end the program, braces, 28.1.5 first)
- 28.1.5 done: \{ and \} escapes
- User moved the old task-1.x-4.x files to task/archive/ (links updated)
- 28.2 done: the lexer in Fusion matches the Python lexer on all 53 example files; a
  Python compiler bug found and fixed (bare return in void main)
- Slice 1 done: hello_world compiled by the Fusion-written compiler - its C is the Python
  compiler's line for line, the program passes the leak check. Gaps logged in
  task/selfhost_report.md
- Slice 2 done: the parser is complete for tier 1 (all 18 programs parse; --ast); the
  code generator checks types in the same walk; 8 of 18 programs print the same as the
  Python-built ones, leak-free
- Slice 3 done: string ownership (fresh vs borrowed, freed in statement expressions - no
  temporaries), floats / chars / bools, format(), default and named arguments - 12 of 18
- Slice 4 done: fixed arrays, function values / types, lambdas (lifted to C functions,
  named by line + a hash of their text) - 15 of 18
- Slice 5 done: structs, equality across types - **all 18 tier 1 programs print the same,
  leak-free**: 28.3-28.6 done
- 28.7 done: check.py --selfhost - 18/18 the same; 28.8 done: task/selfhost_report.md
- **Task 28 complete - Phase 1 complete** (plan archived)
- The report's six suggestions scheduled as FEATURES.md Task 44 (Phase 2)
- User picked Task 44 ("so that it's easier going forward"); plan written
- Task 44 approved (order as planned; globals a setting, on by default; methods: any function)
- 44.3 done: a line break inside ( ) or [ ] continues the line (both lexers)
- 44.4 postponed (user: option A); 44.5 done (`_` was already built - documented; end / var
  ordinary names in both lexers)
- 44.6 done: fast text[i] (a one-entry cache in the run-time, cleared when memory is freed -
  safer than changing the string struct); 52 s -> 0.03 s
- 44.1 done: module-level variables and constants ([modules] variables, default true)
- 44.2 done: any function as a method (p.moved(1, 2)); Task 44 complete (44.4 postponed)
- FEATURES.md: every [DONE] task and item moved to task/featuresArchive.md (user, 2026-10-27);
  it keeps only open and postponed ones; check.py --status counts done from the archive
- User picked Task 29; plan written (prefix review + 29.1-29.6, 3 questions)
- Task 29 approved (no m/f/p prefixes, t"..." templates, pooling postponed to 38)
- 29.1 done: s[i] = c (fusion_str_put; copies, literals and callers' strings unchanged)
- Comparison with other languages added to Notes/Program lang Compare.txt (user request)
- 29.2 done: const string = fixed (inside const structs / arrays too); spec "Constants"
- 29.3 design: user dropped t"..." - `template string greet = "..."` becomes an internal
  function; option A (local templates expanded where called) + 4b (passed as a function value)
- 29.3 done: src/semantic/templates.py expands every use before analysis; names inside {...}
  now report the string's line (was 1:1); the module loader keeps templates per module
- **Next Action:** 29.6 (examples, spec, Builtins) - then Task 29 is complete (29.4 / 29.5
  postponed)
