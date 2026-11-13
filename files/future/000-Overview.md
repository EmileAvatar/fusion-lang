[Index](index.md) | [010 IDEModule >](010-IDEModule.md) <!-- nav -->

# 000 Overview

**Status:** historic - the planning notes of 2026-09 / 10; the plan today: files/FEATURES.md

## Overview

- This document tracks features that are **not part of the MVP (Minimum Viable Product)** but are planned for future versions of Fusion.
- These features have been discussed and documented here to ensure they're not forgotten during development.

**Current MVP Status (updated 2026-09-13, Task 12.8):** MVP compiler complete (Lexer → Parser → Semantic → CodeGen, all four phases). Post-MVP work has also shipped: Tasks 5-9 (cleanup, verification, git, `const`, fixed-size arrays) and Task 12's Core Typed AST. See `../CLAUDE.md` and `../taskSummary2.md` for current status - the feature proposals below remain accurate as forward-looking plans, only this status line was stale.

---


## Implementation Priority

### Phase 1: Basic Compiler (Current - MVP)
- ✅ Lexer
- ✅ Parser
- ✅ Semantic Analyzer
- ✅ Code Generator (C output)

### Phase 2: Core Enhancements (Post-MVP)
- Design fusionlib.IDE module architecture
- Define project.json schema
- Plan Language Server Protocol implementation

### Phase 3: IDE Integration (High Priority)
- Build fusionlib.IDE module
- Implement Language Server Protocol
- Create VS Code extension (highest priority)
- Generate syntax highlighting files

### Phase 4: Additional IDE Support
- IntelliJ IDEA plugin
- Sublime Text package
- Vim plugin
- Code formatter tool

---


## Related Files

When implementing these features, update:
1. **fusion-language-spec.md** - Add fusionlib.IDE module documentation
2. **fusion-summary.md** - Update module count to 22
3. **CLAUDE.md** - Update standard library table
4. **fusion_specs.md** - Add API specifications for new features
5. **README.md** - Mention IDE integration support

---


## Implementation Checklist

### fusionlib.IDE Module
- [ ] Design module architecture (all components)
- [ ] Implement CompilerSettings API
- [ ] Implement BuildConfig API
- [ ] Implement ProjectConfig API (read project.json)
- [ ] Implement UserPreferences API
- [ ] Design Language Server Protocol implementation
- [ ] Create VS Code extension skeleton
- [ ] Implement syntax highlighter generators
- [ ] Build code formatter (indentation ↔ braces ↔ End)
- [ ] Define project.json schema
- [ ] Define preferences.json schema
- [ ] Update compiler to use IDE module for settings
- [ ] Write comprehensive tests
- [ ] Document all APIs

### Documentation
- [ ] Update fusion-language-spec.md (add IDE module)
- [ ] Update fusion-summary.md (22 modules)
- [ ] Update CLAUDE.md (library table)
- [ ] Update fusion_specs.md (new APIs)
- [ ] Create IDE integration guide
- [ ] Write user preference documentation

---


## Timeline Estimate

| Feature | Estimated Effort | Depends On |
|---------|------------------|------------|
| Config API (Core) | 1 week | Basic compiler complete |
| CompilerSettings (System) | 1 week | Config API |
| Language Server Protocol | 3-4 weeks | Basic compiler complete |
| VS Code Extension | 2-3 weeks | LSP complete |
| Syntax Highlighters | 1 week | LSP complete |
| Code Formatter | 2 weeks | Parser complete |
| User Preferences | 1 week | Config API |
| IntelliJ Plugin | 3-4 weeks | LSP complete |
| **Total** | **14-17 weeks** | Parallel work possible |

---


## Success Criteria

### fusionlib.IDE Module Complete When:
- [ ] VS Code extension works (syntax highlighting, LSP)
- [ ] Can convert code between all 3 block styles
- [ ] Language Server provides auto-completion
- [ ] User preferences saved and loaded correctly
- [ ] Syntax highlighting available for 5+ editors
- [ ] Documentation complete
- [ ] All tests pass

### Settings System Complete When:
- [ ] project.json fully supported
- [ ] CompilerSettings API available at runtime
- [ ] User apps can read config files (JSON, INI, YAML)
- [ ] IDE can save/load user preferences
- [ ] All build targets work (native, script, bytecode)
- [ ] Documentation complete
- [ ] All tests pass

---


## Discussion Points

**To discuss later:**
1. Should fusionlib.IDE be included in compiled executables? (Probably not - dev-only)
2. Should Config API support custom formats? (Extensibility?)
3. Priority order: VS Code first or IntelliJ first? (VS Code more popular)
4. Should formatter be a CLI tool or library or both? (Both!)
5. LSP port number: 9257 or configurable? (Configurable with default)
6. Block style conversion: preserve comments? (Yes!)

[Index](index.md) | [010 IDEModule >](010-IDEModule.md) <!-- nav -->
