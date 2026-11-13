[< 034 DataFormats](034-DataFormats.md) | [Index](index.md) | [040 CrossLanguage >](040-CrossLanguage.md) <!-- nav -->

# 035 HIDL

**Status:** planned - HIDL is FEATURES Task 41; these ideas 41.10 (MOD.010)

## HIDL Library: Hardware Testing Ideas from Maia

**Status:** Idea (user, 2026-11-01). **Not in the core:** it belongs in the HIDL library,
made for hardware (files/FEATURES.md Task 41, 41.10). Source: https://maia-eda.net/ (read
2026-11-01: its main page and its "DUT testing" page).

**What Maia is:** a small C-like language for writing **self-checking testbenches** for
hardware designs in Verilog or VHDL. Its compiler (`mtv`) turns a Maia program into a
Verilog testbench that runs in an ordinary simulator, and `rtv` runs batches and
regressions. You don't need to know Verilog to use it. Its compilers are free downloads,
but the site says "All Rights Reserved" and names no open-source licence: take ideas from
it, not code.

| Maia idea | What it is | Value for Fusion's HIDL library |
|---|---|---|
| **A `DUT` block** | Declares the device under test: its ports, directions, bit widths and clock | A natural form for HIDL's hardware description. One declaration could serve both for driving the device and for testing it |
| **Drive / expect vectors** | Declare the format with `[CLK, RST] -> [Q]`, then each line is a test, e.g. `[.C, 1] -> [0]` (clock pulse, RST high, expect Q = 0) | Very short test lines (concise syntax). A failure reports the line, the time, and the expected and actual values (clear errors) |
| **Pipeline depth `->n`** | The expected output arrives n clocks later, and n can be computed while running | Hardware timing stated in the test itself, not hand-counted |
| **Clocks and timing** | `create_clock`, periods and waveforms, in a syntax compatible with SDC (the standard file format for chip timing constraints) | Reusing an industry format instead of inventing one |
| **`trigger f() when cond`** | Runs a function when a condition becomes true; `when all` runs it again each time | Fits embedded interrupts; might also fit services reacting to events |
| **Bits as types** | Any bit width, 2-state and 4-state values (0 / 1 / X / Z) and bit slices | HIDL needs these for registers. A bit slice like `reg[7:4]` could also be useful in ordinary Fusion for flags and protocols (a separate decision) |
| **Self-checking by design** | A test reports its own pass count and every failure | The same idea could serve testing in Fusion generally |

**Not to take:** its full C preprocessor (Fusion's design avoids one) and its Verilog-only
output - HIDL is meant to generate Fusion code.

**Not read yet:** Maia's pages on 4-state values, K-maps, streams and its type system. Read
them when Task 41 starts.

[< 034 DataFormats](034-DataFormats.md) | [Index](index.md) | [040 CrossLanguage >](040-CrossLanguage.md) <!-- nav -->
