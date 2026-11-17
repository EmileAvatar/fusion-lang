# Fusion `service` review notes (2026-11-17)

**For:** Claude Code (handoff from a chat session). Everything needed is in this file.

**Files involved:**
- `Service.md`: the spec (source of truth). Do not change it unless the owner approves a decision below.
- `Fusion_Concurrency_Atomicity_and_Group_Services.md`: an explanatory companion note that needs the corrections in Part 1.

---

## Part 1: Corrections to the companion note (do these)

1. **Syntax.** `Service.md` only documents `service(x).run { ... }`. The companion note uses `balance.run { ... }` and `accountService.run { ... }`. Change them to:
   - `service(balance).run { ... }`
   - `service(accountService).run { ... }`
   - In section 4, drop the "user's shorthand" paragraph, or say it is not in the spec.
2. **Group example (section 5).** Use the spec's group syntax: `service(account, ledger) accountService`. Keep the `run` block example but with the corrected `service(accountService).run` form.
3. **Section 7 (key rules).** Add: *A service is not re-entrant. It finishes one request before starting the next (Service.md rule 3), so a request that waits on its own service deadlocks.*
4. **Section 5.** Add that nesting is allowed (group rule 5) and that a second owner for a variable is a compile error (group rule 4).
5. Keep the note short and consistent with `Service.md`. No new design claims.

---

## Part 2: Gaps found in the design (for the owner to decide, do not edit `Service.md`)

Already covered by the spec, so not gaps: parallel reads (S4, `Snapshot`, `MaxParallelReads`), queue limits and timeouts (`Mailbox`, `WhenFull`, `Timeout`, `Budget`), no re-entrancy (rule 3, S7), one owner per variable (group rule 4), nesting (group rule 5), partial rollback (group rule 7, already listed under "Not decided yet").

### Open items

| # | Gap | Suggestion |
|---|---|---|
| 1 | **Rollback by "opposite operation" is fragile.** `balance + 1` has an inverse, but `x = x * 2` or a plain assignment does not. | Since the group is the only writer, snapshot the touched members at the start of `run` and restore them on failure. Exact for in-memory state. Keep the opposite-operation idea only for things that have left the program (and say they cannot be undone). |
| 2 | **Timeout vs rollback.** Rule 5 says a timed-out request may still execute, so a caller cannot know whether a withdrawal happened. | Add a request id or idempotency key, or a way to query a request's final state (completed / failed / timed out / cancelled). |
| 3 | **Group release while children still use it.** When the group leaves scope, members are released, but child threads may still hold handles. | Guarantee children finish before the creating scope ends (structured concurrency), or make release wait for the queue to drain. |
| 4 | **Self-deadlock.** Not re-entrant means a method calling `service(this).run`, or a member calling back into its group, blocks forever. The same applies to a service sending to itself with `WhenFull = WAIT` and a full mailbox. | Compile-time check for same-service calls, and a rule for self-sends. |
| 5 | **Compiler-made groups (S7) vs developer groups (rule 4).** What if the compiler wants to group a variable already in a developer-written group? | Compile error telling the developer to extend their group. |
| 6 | **Hidden cost of auto-routing (group rule 2).** `person.name` silently becomes a queued request that can block. | Warning, or a visible marker in tooling/IDE. |
| 7 | **Overlapping ordering knobs.** `Scheduler`, `Priority`, `Rule` all affect ordering. It is unclear what `Rule` does when a queue already serializes requests. | Add a worked example to the spec. |

### Smaller inconsistencies in `Service.md`

- `Readers = PARALLEL | SERIAL` appears only in S4, not in the settings tables.
- Default `Timeout` is "per kind of resource", but `[concurrency.traps] missingTimeout = "error"`. What default does a plain (non-resource) service get?
- `WorkerThreadType.AUTO` switching `SHARED` to `SINGLE` at runtime implies migrating live state. A rule is needed.
- Naming: the spec uses `max_unit_warn` / `max_unit` in prose but `maxUnitWarn` / `maxUnit` in `fusion.toml`; `file_lock` in prose vs `fileLock` in toml. Pick one style.

---

## Suggested order of work

1. Apply Part 1 to the companion note.
2. Put Part 2 into the design log or `files/FEATURES.md` Task 42 as open questions, once the owner has decided which to take.
3. Items 1, 2, 3 and 4 are the ones most likely to hurt in practice (data correctness and deadlocks). Settle those before building.
