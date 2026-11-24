[Main](Main.md) | [Spec](files/spec/index.md) | [Decisions >](Decisions.md) <!-- nav -->

# Fusion - Start Here

**What Fusion is for:** a language where each project chooses what it needs - safety, memory
model, concurrency, backend - in `fusion.toml`, instead of picking a different language for
each trade-off. Memory-safe by ownership (no GC by default); a million requests on one
machine without data races. Today: a compiler in Python, Fusion -> C -> a native program
(GCC); next a compiler written in Fusion. The full pitch: [README.md](README.md).

This file is the map: every document, one line each. Rules for working on the project:
[CLAUDE.md](CLAUDE.md). A file added, moved or removed is updated here in the same session.

**Read first, by question:** what Fusion has, at a glance -> [FeatureTree.md](FeatureTree.md); what is decided -> [Decisions.md](Decisions.md); what is open -> [OpenQuestions.md](OpenQuestions.md);
what is being worked on -> [files/FEATURES.md](files/FEATURES.md) and [files/taskSummary2.md](files/taskSummary2.md); what works today ->
[files/SYNTAX_REFERENCE.md](files/SYNTAX_REFERENCE.md).

---

#### The root
| File | What it holds |
|---|---|
| [README.md](README.md) | Fusion's goals - never its status |
| [CLAUDE.md](CLAUDE.md) | Rules and how to run things (loaded every session) |
| [Main.md](Main.md) | This map |
| [Decisions.md](Decisions.md) | Every feature in one line (`AREA.NNN [STATUS]`) and every decision with its why (`D.NNN`) |
| [OpenQuestions.md](OpenQuestions.md) | Questions not decided yet, each with an example (`Q.NNN`) |
| [FeatureTree.md](FeatureTree.md) | At a glance: what Fusion has and still needs - a simple tree by group, one line per feature |
| [main.py](main.py) / [check.py](check.py) | The compiler's command line / every check, `--status`, `--ship` |

#### Status and planning
| File | What it holds |
|---|---|
| [files/FEATURES.md](files/FEATURES.md) | Every open and postponed task and feature, one line each |
| [files/taskSummary2.md](files/taskSummary2.md) | The active task's plan and the next action |
| [task/featuresArchive.md](task/featuresArchive.md) / [task/taskSummaryArchive.md](task/taskSummaryArchive.md) | Finished tasks: their lines / their detail |
| [task/taskBacklog.md](task/taskBacklog.md) | Tasks not started yet, written up |
| [task/taskSummary.md](task/taskSummary.md) | MVP history (Tasks 1-4) |
| [task/automation.md](task/automation.md) | Commands we repeat / could automate |
| [task/Revisit.md](task/Revisit.md) | Skipped tests and technical debt (old - 2025) |
| [task/selfhost_report.md](task/selfhost_report.md), [task/selfhost_subset.md](task/selfhost_subset.md) | The self-hosting test run (Task 28) |

#### What the language is - reference
| File | What it holds |
|---|---|
| [files/spec/index.md](files/spec/index.md) | The language specification, one topic per file, navigable (Task 51.5) |
| [files/SYNTAX_REFERENCE.md](files/SYNTAX_REFERENCE.md) | What works now, with examples (each becomes a program in [examples/](examples/)) |
| [files/fusion-language-spec.md](files/fusion-language-spec.md) | Moved to [files/spec/](files/spec/index.md) - only "Moved to" notes left (Task 51.5) |
| [files/fusion.ebnf](files/fusion.ebnf) | The grammar |
| [files/Compiler_and_Commands.md](files/Compiler_and_Commands.md) | A draft map: every job of the compiler, the `console` app's commands, the IDE and other apps - from 35 languages' tools (to plan what to add) |
| [files/Symbols.md](files/Symbols.md) | Every symbol (`.` `<>` `=` `==` `:` `;` arrows ...) - its job in Fusion and in other languages, the Rust call-chain example explained, the symbols with more than one job (to review - keep syntax consistent) |
| [files/Builtins.md](files/Builtins.md) | Every built-in function and method (generated) |
| [files/FusionTypes.html](files/FusionTypes.html) | Every type: default, range, size, status (open in a browser) |
| [files/ArrayCube.html](files/ArrayCube.html) | An array of 3 dimensions as a cube: which slots `cube[1]`, `cube[][2][1]`, `foreach` and `expand` reach, the flat block (open in a browser, Task 45.16) |
| [files/fusionSettings.xml](files/fusionSettings.xml) | Every built project setting: values, default (the master template) |
| [files/tutorial/](files/tutorial/) | The tutorial site (w3schools style, started 2026-11-22): `index.html`, `site.css`, `fusion-code.css`, `tutorial.json`; the plan as a text hierarchy in [main.md](files/tutorial/main.md) (FEATURES L15.3) |
| [files/showcase/](files/showcase/) | The whole language as code: `Fusion_showcase.fusion` (every feature, tagged), `Fusion_template.fusion` (each construct's shape), `Ownership.fusion`, `Interfaces.fusion`, `fusion.toml` (every setting, tagged) |
| [files/FusionTemplate.md](files/FusionTemplate.md) | How a .fusion file is laid out |

#### Design documents - one topic each, with truth tables
| File | What it holds |
|---|---|
| [files/Ownership.md](files/Ownership.md) | Moves, borrows, readonly, one writer (Task 48); every rule as code in [files/showcase/Ownership.fusion](files/showcase/Ownership.fusion), for Claude the skill [.claude/skills/fusion-ownership](.claude/skills/fusion-ownership) |
| [files/Object_Lifetime.md](files/Object_Lifetime.md) | When an object is freed; memory strategies; copies |
| [files/Classes.md](files/Classes.md) | Visibility, constructors, static set-up (forms A-C), Default, ToString |
| [files/Nullable_Values.md](files/Nullable_Values.md) | Null: `?.`, `??`, number conditions, `length()` on null |
| [files/Arrays.md](files/Arrays.md) | Arrays, Lists, Maps: what each does, when to use it |
| [files/Service.md](files/Service.md) | The `service` keyword - the reference |
| [files/Concurrency.md](files/Concurrency.md) / [files/Concurrency_Traps.md](files/Concurrency_Traps.md) | Concurrency: the full write-up / the overview tables |
| [files/Research/Services/Service_Resilience_Recommendations.md](files/Research/Services/Service_Resilience_Recommendations.md) | Research for Task 42: service isolation, resilience and failure containment (the Microsoft 365 outage, a CD/DVD hang) - to study in full first (FEATURES "Research" R1) |
| [files/Research/Services/Fusion_Concurrency_Atomicity_and_Group_Services.md](files/Research/Services/Fusion_Concurrency_Atomicity_and_Group_Services.md) | Why the CPU can pause a thread mid-check, a lock against a service's `run`, group services (ChatGPT, corrected to Service.md - Research R3) |
| [files/Research/Services/Service_Review_Notes.md](files/Research/Services/Service_Review_Notes.md) | A second Claude review of Service.md: the gaps to decide (Research R3) |
| [files/Research/Memory/Points.md](files/Research/Memory/Points.md) | Memory: what an arena is and its speed, Goose (ChatGPT's comparison in the same folder), Fil-C, where Rust is not memory safe, Zig's allocators (Research R6) |
| [files/Research/Memory/GooseVsRust.md](files/Research/Memory/GooseVsRust.md) | ChatGPT: Goose against Rust, then the FSMA follow-up - generation handles, named pools, 12 principles (Research R6.2, R11) |
| [files/Research/Memory/FSMA/FSMA.md](files/Research/Memory/FSMA/FSMA.md) | FSMA, the Fusion Structured Memory Architecture: the abstract of every rule and setting, all proposals (Research R11) |
| [files/Research/Memory/FSMA/MemoryAllocation.md](files/Research/Memory/FSMA/MemoryAllocation.md) / [MemoryAllocationNew.md](files/Research/Memory/FSMA/MemoryAllocationNew.md) | A primer on memory models (stack, heap, GC, counting, ownership, arenas, pools) / the first FSMA sketch: Data Stacks A, B, C (Research R11) |
| [files/Research/Memory/FSMA/Gemini_FSMA_Review.md](files/Research/Memory/FSMA/Gemini_FSMA_Review.md) | Gemini's FSMA review: rules R1-R3, service-owned stacks, a C bump allocator - what is taken in FSMA.md section 6 (Research R11) |
| [files/Research/Memory/FSMA/images/](files/Research/Memory/FSMA/images/) | The FSMA images: v1 Simple, v2 Complex (the main one), v3 Complex to fix, Hierarchy (where data lives), Register-Only (devices, HIDL) |
| [files/Research/Services/Gemini_Service_Review.md](files/Research/Services/Gemini_Service_Review.md) | Gemini's service review: call cycles, `run` captures, `[blocking]`, timed-out queued requests, group lifetimes, tiers 0-4 (Research R3) |
| [files/Research/ExecutionModels/fusion_programming_execution_models.md](files/Research/ExecutionModels/fusion_programming_execution_models.md) | Ways code is written and run: AOT, script, VM, REPL, notebook, live programming (ChatGPT - Research R7) |
| [files/Research/Libraries/FusionLibraries.md](files/Research/Libraries/FusionLibraries.md) / [NewLibrarys.md](files/Research/Libraries/NewLibrarys.md) | The 21 planned fusionlib modules in one table / three proposed libraries: SourceControl, WorkTracking, Governance (Research R8) |
| [files/Research/RustZig/Points.md](files/Research/RustZig/Points.md) | Rust and Zig: the points for Fusion, `comptime`, and the pitfalls of a rewrite in Rust (RustPitfalls.md, section 6) - from two YouTube transcripts and a ChatGPT comparison in the same folder (Research R4) |
| [files/Fusion_Multi_Language_Compiler_Architecture.md](files/Fusion_Multi_Language_Compiler_Architecture.md) | `Lang.<language>.Fusion` modules (Task 49) |
| [files/Fusion_Hardware_Interface_Definition_Language_HIDL.md](files/Fusion_Hardware_Interface_Definition_Language_HIDL.md) | HIDL - hardware description (Task 41) |
| [files/Literals.md](files/Literals.md) | Ways to write values directly - a proposal only |

#### Ideas, reviews and background - not decisions
| File | What it holds |
|---|---|
| [files/FutureFeaturesCaution.md](files/FutureFeaturesCaution.md) | Read before picking a future feature |
| [files/future/index.md](files/future/index.md) | Ideas not decided or scheduled yet, one topic per file, navigable (Task 51.5b) |
| [files/FutureFeatures.md](files/FutureFeatures.md) | A table of where each old section went in files/future/ |
| [files/FutureFeatures Add Later.md](<files/FutureFeatures Add Later.md>) | A checklist of what may be missing (ChatGPT) |
| [files/Fusion_Memory_Ownership_and_Services.md](files/Fusion_Memory_Ownership_and_Services.md) | A review of memory, ownership and services (ChatGPT) |
| [files/Programming Languages Pain points.md](<files/Programming Languages Pain points.md>) | Why 30 languages were made; what each domain needs |
| [files/Fusion_domain.md](files/Fusion_domain.md) | A map of Fusion's whole feature domain |
| [files/Fusion Ecosystem Map.md](<files/Fusion Ecosystem Map.md>) | The wider ecosystem (ChatGPT, to review) |
| [files/OtherFusionLanauge.md](files/OtherFusionLanauge.md) | The other language called Fusion (fusion-lang.org) |
| [files/DocumentationSystemProposal.md](files/DocumentationSystemProposal.md) | The documentation system proposal (Task 51) |
| [files/ASTs.md](files/ASTs.md) | What an abstract syntax tree is |
| [files/TestDriven Development and specialised testing.md](<files/TestDriven Development and specialised testing.md>) | TDD and testing one function across implementations |
| [files/dbcontext.md](files/dbcontext.md) | A database of task context for AI agents (future idea) |
| [files/fusion-devcontainer.md](files/fusion-devcontainer.md) | A Docker development environment (future project) |
| [files/notes.md](files/notes.md) | Early notes with IGNORE / PLANNED / DONE sections |
| [files/reviews/](files/reviews/) | Reviews by ChatGPT, Claude, Gemini |

#### Older documents - kept for history, may be out of date
| File | What it holds |
|---|---|
| [files/README.md](files/README.md) | The old documentation index (2025) |
| [files/fusion-strict.md](files/fusion-strict.md) | Strict mode (2025) |
| [files/fusion-threading-concurrency.md](files/fusion-threading-concurrency.md) | Threading (2025) - replaced by [files/Concurrency.md](files/Concurrency.md), [files/Service.md](files/Service.md) |
| [files/fusion_specs.md](files/fusion_specs.md), [files/json/](files/json/) | JSON configurations and templates (2025) |
| [files/fusion-overview.yaml](files/fusion-overview.yaml) | An overview in YAML (2025) |
| [files/fusion-planning.md](files/fusion-planning.md), [files/fusion-summary.md](files/fusion-summary.md) | Historical snapshots of progress |
| [files/archive/](files/archive/) | Merged-away plans and specs |
| [files/reports/verification_report.md](files/reports/verification_report.md) | Written by [tests/verify_examples.py](tests/verify_examples.py) |

#### Code
| Folder | What it holds |
|---|---|
| [src/](src/) | The compiler - [src/CLAUDE.md](src/CLAUDE.md) explains the pipeline; each subfolder's [CLAUDE.md](CLAUDE.md) has one line per file |
| [runtime/](runtime/) | The C run-time (`fusion_runtime.h` is generated) |
| [selfhost/](selfhost/) | The compiler written in Fusion (Task 28, 35) |
| [tests/](tests/) | The test suite; [examples/](examples/) - example programs with expected output, in numbered topic folders (`01_basics` ... `13_projects`) |
| [tools/](tools/) | Helper scripts (`patch.py`, `builtins_doc.py`, `example_files.py` - where the examples live, Windows preview); [tools/editors/](tools/editors/README.md) - syntax highlighting for VS Code and Sublime Text (Task 36), Fusion's colours in `colors.json` - four themes, colour-blind safe ones too (36.8) |
| [debug/](debug/) | Old debug scripts |
| [Notes/](Notes/) | Internal discussion and sources - not in git |
| [files/requirements.txt](files/requirements.txt) | Python packages to install |

[Main](Main.md) | [Spec](files/spec/index.md) | [Decisions >](Decisions.md) <!-- nav -->
