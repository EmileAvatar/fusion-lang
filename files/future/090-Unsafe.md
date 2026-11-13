[< 081 Strings](081-Strings.md) | [Index](index.md) | [100 CLI >](100-CLI.md) <!-- nav -->

# 090 Unsafe

**Status:** design - `unsafe` blocks and functions (MEM.006, D.030, D.031); memory freed at the end of its scope (D.134); bounds checks stay even in unsafe (COL.010)

Contents: [Unsafe Mode Enhancements](#unsafe-mode-enhancements) | [Implementation Strategy Tiers & the Configurable-Strategy Philosophy](#implementation-strategy-tiers--the-configurable-strategy-philosophy) | [Bit Type & Assembly Support](#bit-type--assembly-support)

## Unsafe Mode Enhancements

### Implementation Strategy Tiers & the Configurable-Strategy Philosophy

**Status:** 📝 Proposed (vision/framing, not a scoped feature)
**Source:** User-provided notes (`Notes/03/Fusion_C_Rust_and_Implementation_Strategies.md`,
reviewed 2026-09-27) - written with limited knowledge of Fusion's current implementation,
so treat this as philosophy/direction, not an accurate description of what exists today.

**The central idea, stated more sharply than Fusion's philosophy is currently written down
anywhere else:**

> Don't make the *meaning* of Fusion configurable. Make the *implementation strategy*
> configurable.

- A program's semantics stay stable; what changes per project is *how* that meaning gets realized - memory strategy, safety level, compilation target, runtime footprint.
- This is the same idea CLAUDE.md's "Core Concept" and this document's various per-project knobs (`fusion.toml`'s `[safety]`/`[backend]`, the decimal/Currency precision config, the Feature Registry concept explored in conversation) already point at individually - this framing is worth adopting as the one sentence that explains *why* all of those exist, rather than each looking like an unrelated configuration knob.

**Proposed escalation tiers** - not separate languages, one Fusion, with progressively lower
guardrails available when a project genuinely needs them:

```text
Application Fusion  - the default: safe memory, automatic resource management, high-level
                       collections, concurrency safety, productive defaults. Aimed at
                       covering roughly 70-90% of ordinary development, with 95% as a
                       long-term aspiration - the "everyday" tier most projects never leave.
        |
Systems Fusion       - explicit allocation, deterministic destruction, manual memory where
                       required, direct OS interaction. For OS components, high-performance
                       services, storage/networking systems, game engines.
        |
Embedded Fusion      - no GC, no runtime, fixed memory, predictable execution, direct
                       peripheral access. For devices with no OS, fixed memory budgets, and
                       hard determinism requirements.
        |
Kernel Fusion        - explicit hardware access, controlled unsafe operations, strict
                       compiler checks, direct memory manipulation, interrupt/device
                       interaction.
        |
Assembly / Hardware  - inline/integrated assembly as the final escape hatch when even
                       Kernel Fusion's control isn't enough (CPU-specific instructions, boot
                       code, SIMD, cryptographic primitives) - see "Bit Type & Assembly
                       Support" below, which already covers this tier concretely.
```

The stated principle: **"easy by default, but never a dead end"** - a developer starts in
Application Fusion and only descends a tier when the project actually demands it, without
switching languages or relearning semantics to do so.

**A distinctive idea worth keeping even if the tier model above changes:** tagging `unsafe`
blocks with a numbered design-rule reference connecting the code to *why* it's unsafe, not
just what it does:

```fusion
###<1042> Hardware buffer must remain valid
###<1043> DMA operation requires exclusive ownership

unsafe
{
    pointer = address(...)
    memory.write(pointer, value)
}
```

- The idea is that `###<NNNN>` numbers key into a project's design/engineering-rule documentation, so a reviewer (or a future maintainer) can trace an unsafe block back to the actual constraint that justified it, not just trust a comment.
- Needs real design before it's buildable (where does the rule registry live, is the numbering compiler-checked or purely conventional) but it's a genuinely useful angle on "unsafe should be explicit and
*explained*, not just contained."

**Why this stays in "Unsafe Mode Enhancements" specifically:** everything below Application
Fusion in the tier list is, functionally, a larger version of what this section's "Bit Type
& Assembly Support" already proposes - this framing gives that existing content a home in a
bigger picture rather than treating hardware/assembly access as an isolated feature.

---

### Bit Type & Assembly Support

**Status:** 📝 Proposed
**Purpose:** Enable absolute hardware control for low-level programming

**What:** Support for bit-level operations and inline assembly code for scenarios requiring maximum control and performance.

#### Use Cases

- **Direct hardware control** (PC, embedded systems, IoT, robotics)
- **Banking security systems** (hardware encryption modules)
- **Operating system development** (kernel, drivers)
- **Real-time systems** (fighter jets, spacecraft, medical devices)
- **Performance-critical code** (game engines, cryptography)

#### Bit Type

**Definition:** A primitive type representing a single bit (0 or 1)

🧩 **Example:**
```fusion
// Bit type declaration (unsafe mode only)
bit flag = 1
bit isEnabled = 0

// Bit manipulation
bit result = flag & isEnabled  // AND
bit result2 = flag | isEnabled // OR
bit result3 = flag ^ isEnabled // XOR
bit result4 = ~flag            // NOT

// Hardware register access
bit[8] statusRegister = readHardwareRegister(0x3F8)
statusRegister[3] = 1  // Set bit 3
writeHardwareRegister(0x3F8, statusRegister)
```

#### Bit Arrays

```fusion
// 8-bit register
bit[8] register = [0, 1, 0, 1, 1, 0, 1, 0]

// 32-bit integer as bit array
bit[32] flags = int32.toBits(0xDEADBEEF)

// Access individual bits
bit highBit = flags[31]
flags[0] = 1  // Set LSB
```

#### Assembly Code Support

**Inline Assembly:** Embed assembly directly in Fusion code

🧩 **Example:**
```fusion
// x86_64 assembly example
void function enableInterrupts()
    asm
        sti  // Set interrupt flag
    end asm

// ARM assembly example
int function addWithCarry(int a, int b)
    int result
    asm
        adds r0, r0, r1  // Add with status update
        mov result, r0
    end asm
    return result
```

#### Hardware Interface Classes

**Concept:** Encapsulate hardware-specific code in classes/interfaces

🧩 **Example:**
```fusion
// Abstract hardware interface
interface IHardwareController
    void function initialize()
    void function writeRegister(int address, byte value)
    byte function readRegister(int address)
    void function shutdown()

// PC serial port implementation
class SerialPortController implements IHardwareController
    private int baseAddress = 0x3F8

    public void function initialize()
        // Configure baud rate, parity, etc.
        writeRegister(baseAddress + 1, 0x00)  // Disable interrupts
        writeRegister(baseAddress + 3, 0x80)  // Enable DLAB
        writeRegister(baseAddress + 0, 0x03)  // Set divisor (low byte)
        writeRegister(baseAddress + 1, 0x00)  // Set divisor (high byte)
        writeRegister(baseAddress + 3, 0x03)  // 8N1 mode

    public void function writeRegister(int address, byte value)
        asm
            mov dx, address
            mov al, value
            out dx, al
        end asm

// Spacecraft thruster controller
class ThrusterController implements IHardwareController
    private int thrusterPort = 0x400

    public void function fireThruster(int thrusterId, int duration)
        // Safety checks
        if thrusterId < 0 or thrusterId > 15
            throw Error("Invalid thruster ID")

        // Set thruster bit
        bit[16] thrusterMask = 0
        thrusterMask[thrusterId] = 1
        writeRegister(thrusterPort, thrusterMask.toInt16())

        // Wait for duration (microseconds)
        sleep(duration)

        // Disable thruster
        writeRegister(thrusterPort, 0x0000)
```

#### Safety Considerations

**Unsafe mode required:**
```fusion
// Must be in unsafe block or unsafe file
unsafe
    bit[8] register = readPort(0x3F8)
    asm
        cli  // Disable interrupts (dangerous!)
    end asm
end unsafe
```

**Warning system:**
```
⚠️  Warning: Bit type used outside unsafe context
⚠️  Warning: Inline assembly may cause undefined behavior
⚠️  Warning: Direct hardware access requires elevated privileges
```

[< 081 Strings](081-Strings.md) | [Index](index.md) | [100 CLI >](100-CLI.md) <!-- nav -->
