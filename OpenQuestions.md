[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->

# Fusion - Open Questions

Questions not decided yet. Next to `Decisions.md`: when the user answers one, the answer goes
into `Decisions.md` (and the design document named) and the question is removed here. A new
question gets the next number (never reused). Claude adds a question here instead of guessing
(CLAUDE.md Rule 3b).

**How a question is written (user, 2026-11-07):**
- A heading `#### Q.NNN` with a short title and where it belongs (task, document)
- One or two lines: the question
- **An example code block** wherever code can show it - Claude's understanding of today's
  rule and the options, marked `A:` / `B:` / `C:`, so the user can see it and answer by letter.
  Only a question code can't show (a review, a name) goes without one
- Claude's suggestion, if it has one, marked "suggested"
- Once the user answers: **Answer** (the user's words, short), **Understood as** (a code block
  of the rule as Claude now reads it) and **To confirm** (anything still unclear). After the
  user confirms, it moves to `Decisions.md`

Ideas not scheduled yet keep their own open questions in `files/FutureFeatures.md`
("Open Questions" sections) until they become a task.

---

## Open

#### Q.020 Buffers for large arrays (Task 45.13 now, built in L16 after self-hosting)
**Answer** (user, 2026-11-14): `stackLimit` goes with the buffers - a large array is worked through a
small buffer on the stack, so the limit is never hit. Settings for the buffer size (e.g. 2KB small,
8KB large); per array `setBufferType` and `setSize`; the compiler may pick RING as a safeguard so the
PC's memory is never used up. SINGLE is the simplest - how arrays work today.

**Understood as:**
```fusion
int[100000] samples          // 400 KB - above stackLimit
samples.setBufferType(TWO)   // SINGLE (default), TWO, THREE, RING
samples.setSize(1024)        // the buffer: 1024 bytes - with TWO, 512 + 512
// SINGLE - the whole array in one place (today's arrays)
// TWO    - one buffer worked on by the CPU while the other loads the next part from the heap; then swap
// THREE  - the same with three (one working, two loading)
// RING   - one part read while the next is written - the stack never grows
```
```toml
[arrays]
bufferSmall = "2KB"     # the buffer for a small array (names open)
bufferLarge = "8KB"     # the buffer for a large array
bufferType  = "single"  # the project's default
```
- The array itself lives on the heap; only its buffer is on the stack

**To confirm:**
1. `THIRD` written as `THREE` (like `TWO`)? Suggested: THREE
2. `setSize` in bytes (like the stack limits)? Suggested: bytes
3. Small or large: an array up to `stackWarn` (16KB) is small, above it large?
4. Above `stackLimit`: once the buffers are built (L16), the compiler picks RING itself (a note, no error);
   until then the compile error of D.145 stays. Suggested: yes - so Task 45 builds only SINGLE and the
   limits, and records the rest; TWO / THREE / RING and the settings are built in L16 (no pre-optimising -
   profiled first, user 2026-11-14)
5. `setBufferType` / `setSize` written before L16: an error "not built yet - L16"? Suggested: yes

Earlier: Q.013 (modules and namespaces) answered 2026-11-12: Decisions.md D.136, FEATURES
Task 57. Q.014 (a may-be-null parameter mark) answered 2026-11-14: no mark - every object may be
null (D.138, D.117). Q.001-Q.012 answered 2026-11-07: Decisions.md D.103, D.113-D.124, the Decisions.md status
PARTIAL; FEATURES 48.10-48.12, 50.4, 51.5, 52.6-52.7, 42.29, Task 53 (the Core language and the
name). Q.015-Q.019 (arrays) answered 2026-11-14: D.141-D.145. Next question: Q.021.

[< Decisions](Decisions.md) | [Main](Main.md) | [Spec](files/spec/index.md) | [README >](README.md) <!-- nav -->
