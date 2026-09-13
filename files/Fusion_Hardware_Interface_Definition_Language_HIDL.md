# Hardware Interface Definition Language (HIDL)

> **Scope note (added 2026-09-13):** HIDL is a standalone, language-agnostic hardware
> description framework - it is not Fusion-specific and does not depend on Fusion existing.
> A hardware supplier's `.hidl` spec can already be consumed to generate C, C++, Rust, C#,
> Java, etc. bindings (see Section 19). Fusion's role is to eventually add a **HIDL module** -
> a consumer/generator that reads a HIDL spec and produces typed Fusion bindings - alongside
> whatever other languages also choose to consume the same spec. Earlier drafts of this
> document (including the title and Section 1 below) described HIDL as being "for Fusion";
> that framing is superseded by this note. Tracked as Task 13 in `taskSummary2.md` (blocked,
> future work).

## 1. Overview

HIDL is a proposed machine-readable **Hardware Interface Definition Language** - a standalone
framework for describing hardware devices, independent of any one programming language. It is
of interest to Fusion because Fusion could eventually consume HIDL specs via a dedicated module,
the same way any other language's toolchain could.

The core idea is:

> **A hardware supplier describes a device once in a formal specification. Development tools consume that specification and automatically generate a safe, friendly programming interface.**

Instead of every programmer manually translating a hardware manual into registers, constants, structs, functions, classes, validation rules, and driver code, the hardware definition becomes the authoritative source from which these artifacts are generated.

```text
Hardware Designer
       |
       v
Hardware design / register-definition tool
       |
       v
HIDL hardware specification
       |
       +--------------------+--------------------+
       |                    |                    |
       v                    v                    v
   Fusion API            C API              C#/Java/Rust/etc.
       |                    |                    |
       +--------------------+--------------------+
                            |
                            v
                       Application
                            |
                            v
                     Hardware driver
                            |
                            v
                       Machine code
                            |
                            v
                         Hardware
```

## 2. The Problem HIDL Solves

Custom hardware frequently exposes a low-level programming model consisting of:

- Memory-mapped registers
- I/O ports
- Control bits
- Status bits
- Input/output pins
- Commands
- Timers
- Interrupts
- Multiple registers that form larger values
- Required register access ordering
- Hardware states
- Timing requirements
- Validation constraints
- Device-specific behavior

A traditional programmer may receive a hardware manual and manually create:

```text
register addresses
constants
bit masks
enums
structs
classes
functions
validation
driver code
documentation
```

This creates:

- Repetition
- Human error
- Inconsistent implementations
- Poor type safety
- Difficult hardware-version management
- Duplicate documentation
- Different APIs for different languages
- Poor IDE integration
- Difficult simulation/testing
- Hardware knowledge becoming buried inside source code

HIDL addresses this by making the hardware description itself a formal artifact.

## 3. HIDL Is Not Necessarily the Hardware Driver

An important distinction:

```text
HIDL
  =
description of what the hardware exposes
```

It does not necessarily contain the entire implementation of the driver.

For example:

```text
HIDL
  |
  +-- Register 0x20
  +-- Bit 0 = START
  +-- Bit 1 = STOP
  +-- Register 0x21 = POWER
  +-- Register 0x22 = TIMER
```

The generated API might provide:

```text
microwave.Power = 800
microwave.Timer = 90
microwave.Start()
```

The underlying driver/runtime is responsible for actually performing the hardware access.

This separation allows the same hardware definition to be used by multiple languages and environments.

## 4. HIDL as the Hardware Contract

The supplier effectively provides a formal contract:

"This is what this hardware exposes, how it is accessed, what values are valid, and what relationships exist between its components."

The specification should describe:

```text
Device identity
Hardware version
Architecture
Memory map
Registers
Bits
Fields
Commands
Inputs
Outputs
Data types
Units
Ranges
Relationships
Dependencies
Timing
State requirements
Side effects
Interrupts
DMA
Reset values
Reserved areas
```

The hardware definition should be versioned.

Example:

```text
MicrowaveController
    v1.0
    v1.1
    v2.0
```

A compiler or development environment can then determine which hardware version the program targets.

## 5. Example Hardware

Consider a deliberately simple custom microwave controller.

The physical device contains:

- Door sensor
- Temperature sensor
- Turntable motor
- Magnetron
- Power control
- Timer
- Display
- Buzzer

The hardware might expose:

```text
0x00  STATUS
0x01  COMMAND
0x02  POWER
0x03  TIMER
0x04  DOOR
0x05  MOTOR
0x06  MAGNETRON
0x07  BUZZER
```

A traditional low-level program would need to know these addresses.

HIDL allows the supplier to encode them once.

## 6. Conceptual HIDL Example

A possible XML representation:

```xml
<device name="MicrowaveController" version="1.0">

    <register name="STATUS"
              address="0x00"
              size="8"
              access="read">

        <bit name="RUNNING" position="0"/>
        <bit name="DOOR_OPEN" position="1"/>
        <bit name="ERROR" position="2"/>
        <bit name="COMPLETE" position="3"/>

    </register>

    <register name="POWER"
              address="0x02"
              size="8"
              access="readwrite"
              type="uint8">

        <range min="0" max="100"/>
        <unit>percent</unit>

    </register>

    <register name="TIMER"
              address="0x03"
              size="16"
              access="readwrite"
              type="uint16">

        <unit>seconds</unit>

    </register>

    <register name="DOOR"
              address="0x04"
              size="8"
              access="read">

        <value name="OPEN" value="0"/>
        <value name="CLOSED" value="1"/>

    </register>

    <command name="START"
             register="0x01"
             value="0x01"/>

    <command name="STOP"
             register="0x01"
             value="0x02"/>

</device>
```

The exact syntax is illustrative. The important part is the information model.

## 7. Registers

A register definition should contain at least:

```text
Name
Address
Size
Access
Data type
Reset value
Description
```

Example:

```text
Register: POWER
Address: 0x02
Size: 8 bits
Access: Read/Write
Type: uint8
Range: 0–100
Unit: percent
Description: Magnetron power level
```

This information can generate both code and documentation.

## 8. Register Access

HIDL should distinguish:

```text
READ
WRITE
READ_WRITE
WRITE_ONLY
READ_ONLY
```

Potentially also:

```text
CLEAR_ON_READ
WRITE_ONE_TO_CLEAR
WRITE_ONE_TO_SET
TOGGLE
COMMAND
LATCHED
```

These distinctions matter because a hardware register is not necessarily ordinary memory.

For example:

```text
WRITE_ONE_TO_CLEAR
```

means writing 1 to a bit may clear it rather than store the value 1.

## 9. Bit Fields

Registers frequently contain multiple independent fields.

Example:

```text
CONTROL
Address: 0x10

Bit 0       START
Bit 1       STOP
Bit 2       PAUSE
Bit 3       LIGHT
Bits 4-5    POWER_MODE
Bits 6-7    RESERVED
```

HIDL should represent fields separately.

This allows generated Fusion code such as:

```text
controller.Control.Start = true
controller.Control.Light = true
controller.Control.PowerMode = PowerMode.High
```

instead of requiring:

```text
controller.WriteRegister(0x10, 0b00101101)
```

The low-level representation can still be generated underneath.

## 10. Multiple Registers Acting as One Value

Some hardware values span multiple registers.

Example:

```text
TIMER_0
TIMER_1
TIMER_2
TIMER_3
```

Together they form:

```text
uint32 TIMER
```

HIDL should be able to express:

```text
TIMER
    size = 32
    registers =
        TIMER_0
        TIMER_1
        TIMER_2
        TIMER_3

    byte_order = little
```

It should also describe access requirements:

```text
write_order =
    TIMER_3
    TIMER_2
    TIMER_1
    TIMER_0
```

This prevents programmers from having to manually understand hardware-specific register assembly.

## 11. Inputs and Outputs

HIDL should distinguish two concepts.

Register access

```text
READ
WRITE
READ_WRITE
```

Physical direction

```text
INPUT
OUTPUT
BIDIRECTIONAL
```

For example:

```text
DOOR_SENSOR

Register access: READ
Physical direction: INPUT
```

and:

```text
MAGNETRON_CONTROL

Register access: READ_WRITE
Physical direction: OUTPUT
```

Keeping these separate makes the model more accurate.

## 12. Commands

Some registers aren't really storage. They represent commands.

Example:

```text
COMMAND

0x01 = START
0x02 = STOP
0x03 = RESET
0x04 = PAUSE
```

The generated Fusion API could become:

```text
microwave.Start()
microwave.Stop()
microwave.Reset()
microwave.Pause()
```

rather than:

```text
WriteRegister(0x01, 0x01)
```

The low-level operation remains encoded in the generated implementation.

## 13. State and Dependencies

A rich HIDL can describe hardware rules.

For example:

```text
START

Requires:
    DOOR == CLOSED
    POWER > 0
    ERROR == false
```

Or:

```text
MAGNETRON

Requires:
    MOTOR == ON
    DOOR == CLOSED
    CONTROLLER == RUNNING
```

The generated API can potentially enforce these rules.

The HIDL therefore becomes more than a register map. It becomes a formal description of the hardware interface and its constraints.

## 14. Timing Requirements

Hardware frequently has timing requirements.

For example:

```text
After RESET:

wait 10 microseconds

before accessing STATUS.
```

Or:

```text
COMMAND.START

minimum interval = 5 ms
```

HIDL should be capable of expressing such requirements.

Example:

```text
operation START
    requires controller.ready
    delay_before = 10us
    delay_after = 5ms
```

This information can be used by:

- Generated drivers
- Runtime libraries
- Static analysis
- Testing tools
- Simulators

## 15. Side Effects

Hardware operations often have side effects.

Example:

```text
Writing START:

- Clears COMPLETE
- Sets RUNNING
- Starts TIMER
- Enables MOTOR
- Enables MAGNETRON
```

The specification should record this.

This makes hardware behavior discoverable to both humans and tools.

## 16. Generated Fusion API

Given the HIDL definition, Fusion could generate something conceptually like:

```text
hardware MicrowaveController

property Power : UInt8
property Timer : UInt16

readonly property Door : DoorState

property Status : MicrowaveStatus

function Start()
function Stop()
function Pause()
function Reset()
```

The programmer sees a normal Fusion API.

The compiler/toolchain knows that:

```text
microwave.Power = 80
```

ultimately maps to a specific hardware register.

## 17. Generated Types

HIDL can automatically generate types.

For example:

```text
DoorState
    Open
    Closed

PowerMode
    Low
    Medium
    High

MicrowaveStatus
    Running
    Complete
    Error
```

Fusion could then provide type-safe code:

```text
if microwave.Door == DoorState.Closed
    microwave.Start()
```

This is much better than manipulating raw numeric values.

## 18. Generated Constants

The compiler can still expose low-level information when required.

For example:

```text
MicrowaveController.Registers.Status
MicrowaveController.Registers.Command
MicrowaveController.Registers.Power
```

Advanced developers could deliberately access the hardware at a lower level.

This creates multiple abstraction levels:

```text
Friendly API
     |
Typed hardware API
     |
Register API
     |
Raw memory/I/O API
     |
Machine instructions
```

Fusion should ideally allow the programmer to choose the appropriate level.

## 19. Code Generation

The same HIDL specification could generate:

```text
Fusion
C
C++
Rust
C#
Java
VB.NET
Python
Assembly definitions
```

For example:

```text
Hardware.hidl
      |
      +--> Microwave.fusion
      +--> Microwave.h
      +--> Microwave.hpp
      +--> Microwave.rs
      +--> Microwave.cs
      +--> Microwave.java
```

The generated APIs are language-specific but semantically derived from the same hardware definition.

## 20. IDE Integration

A Fusion IDE could consume HIDL directly.

The IDE could provide:

- Autocomplete
- Register browser
- Bit-field editor
- Hardware documentation
- Register inspection
- Warnings
- Validation
- Hardware simulator
- Debugger integration

Typing:

```text
microwave.
```

could show:

```text
Power
Timer
Door
Status
Start()
Stop()
Pause()
Reset()
```

The IDE knows these exist because they were generated from the hardware definition.

## 21. Hardware-Aware Compiler

Fusion could potentially integrate HIDL into the language/toolchain.

Example:

```text
import hardware "MicrowaveController.hidl"
```

Then:

```text
let microwave = MicrowaveController.connect()

microwave.Power = 80
microwave.Timer = 90
microwave.Start()
```

The compiler understands that `MicrowaveController` is a hardware-defined entity.

For example, if HIDL specifies:

```text
Power: 0–100
```

then:

```text
microwave.Power = 500
```

could produce a compile-time error:

```text
Power value 500 is outside hardware range 0–100.
```

That is better than discovering the problem at runtime.

## 22. Hardware Versioning

HIDL should be strongly versioned.

Example:

```text
MicrowaveController
    hardware version: 2.1
    specification version: 1.4
```

A program could target:

```text
requires MicrowaveController >= 2.0
```

The compiler can detect incompatible hardware.

This is particularly valuable when hardware revisions change register addresses or behavior.

## 23. Compatibility

A supplier could publish:

```text
MicrowaveController-v1.hidl
MicrowaveController-v2.hidl
MicrowaveController-v3.hidl
```

Fusion tooling could determine:

- API compatible
- Binary compatible
- Register compatible
- Partially compatible
- Incompatible

This can prevent software being deployed to the wrong hardware revision.

## 24. Simulator Generation

One of the strongest features would be automatic simulation.

The HIDL specification already describes:

```text
Registers
States
Inputs
Outputs
Commands
Constraints
```

Therefore a tool could generate a simulated device.

```text
Fusion application
       |
       v
Generated hardware API
       |
       v
HIDL simulator
       |
       +-- Status
       +-- Door
       +-- Timer
       +-- Power
       +-- Motor
       +-- Magnetron
```

Developers could test software without having the physical hardware connected.

## 25. Automatic Documentation

The same specification can generate documentation.

For example:

```text
MicrowaveController
────────────────────────────

Power
    Type: UInt8
    Range: 0–100
    Unit: percent
    Read/Write

Timer
    Type: UInt16
    Unit: seconds
    Read/Write

Door
    Type: DoorState
    Read only

Start()
    Requires:
        Door closed
        No error
        Power > 0
```

The supplier maintains one authoritative source instead of separately maintaining:

```text
PDF manual
C header
C# SDK
Java SDK
Rust crate
IDE definitions
Simulator
```

## 26. Validation

HIDL tooling can validate the hardware definition itself.

Examples:

```text
Register addresses overlap
Invalid bit ranges
Field exceeds register size
Read-only register marked writable
Duplicate command values
Invalid reset value
Missing hardware version
Invalid register dependency
```

The supplier's hardware-definition tool can catch these problems before the specification is released.

## 27. Security

For real hardware, HIDL could describe permissions.

Example:

```text
USER
    can read STATUS
    can read POWER

SERVICE
    can write POWER
    can write TIMER

FACTORY
    can CALIBRATE
    can RESET
```

Hardware may also have:

```text
secure registers
unlock sequences
authentication requirements
protected commands
privileged operations
```

These should be representable where appropriate.

## 28. Interrupts and Events

HIDL should eventually describe asynchronous hardware behavior.

Example:

```text
EVENT TIMER_COMPLETE
EVENT DOOR_CHANGED
EVENT OVERHEAT
EVENT ERROR
```

Fusion could potentially expose:

```text
microwave.OnTimerComplete += handleComplete
microwave.OnDoorChanged += handleDoor
```

The generated implementation connects those events to the hardware's interrupt/event mechanism.

## 29. DMA, Buffers and Memory Regions

For advanced hardware, the specification could describe:

```text
DMA channels
Memory regions
Buffers
FIFO queues
Peripheral memory
Interrupt vectors
Descriptors
Alignment requirements
Cache requirements
```

For example:

```text
DMA_BUFFER
    address alignment: 64 bytes
    size: 4096 bytes
    readable by device: true
    writable by device: true
```

This lets Fusion's compiler/runtime potentially provide safer abstractions around low-level hardware operations.

## 30. Hardware as a Typed Object

This leads to a useful Fusion philosophy:

```text
Raw hardware
      ↓
Typed hardware description
      ↓
Typed hardware object
      ↓
Application
```

Instead of:

```text
hardware = random memory addresses
```

Fusion can treat:

```text
hardware = strongly typed resource
```

For example:

```text
MicrowaveController
    .Power : Percent
    .Timer : Seconds
    .Door : DoorState
    .Status : MicrowaveStatus

    .Start()
    .Stop()
```

The compiler knows what these things mean.

## 31. Traits and Interfaces

This fits naturally with Fusion's trait/interface model.

A useful conceptual distinction is:

- Trait = provides behaviour.
- Interface = provides a promise/contract.

An interface describes what an object promises to support.

Example:

```text
interface Startable
    function Start()

interface Stoppable
    function Stop()
```

A type implementing the interface promises:

- "I provide Start()."
- "I provide Stop()."

A trait can provide reusable behavior:

```text
trait SafeStart
    function SafeStart()
        if CanStart()
            Start()
```

So:

```text
Interface
    = What must exist

Trait
    = Behaviour that can be provided/reused
```

## 32. HIDL + Fusion Interfaces

HIDL might generate:

```text
interface MicrowaveController
    property Power
    property Timer

    function Start()
    function Stop()
```

The hardware implementation then promises to satisfy that interface.

Conceptually:

```text
                    Interface
                 MicrowaveController
                         ▲
                         |
                  promises to provide
                         |
                 Hardware implementation
                         |
                         ▼
                       HIDL
                         |
                         ▼
                    Real hardware
```

Application code can therefore depend on the interface rather than directly depending on the physical device.

## 33. HIDL + Fusion Traits

Traits can provide behavior above the hardware definition.

For example:

```text
trait TimedDevice
    function RunFor(seconds)
        Timer = seconds
        Start()
```

A microwave could gain:

```text
microwave.RunFor(90)
```

without the hardware supplier needing to explicitly implement `RunFor()`.

The distinction becomes:

```text
HIDL
    describes hardware capabilities

Interface
    defines the promised programming contract

Trait
    provides reusable behavior

Class/object
    represents the usable thing

Compiler
    connects everything together
```

## 34. The Full Fusion Concept

```text
                    HARDWARE SUPPLIER
                           |
                           v
                    Hardware Designer
                           |
                           v
                     HIDL Definition
                           |
                           v
                  Fusion Hardware Model
                           |
              +------------+-------------+
              |                          |
              v                          v
        Generated Interface       Generated Types
              |                          |
              +------------+-------------+
                           |
                           v
                         Traits
                           |
                           v
                        Classes
                           |
                           v
                     Application Code
                           |
                           v
                     Fusion Compiler
                           |
                           v
                    Hardware Driver
                           |
                           v
                    Machine Code
                           |
                           v
                       Hardware
```

This gives Fusion a clean separation of responsibilities.

## 35. HIDL Should Describe What the Hardware Is

HIDL should describe what the hardware provides, not prescribe exactly how every programming language must represent it.

For example:

```text
HIDL:
    POWER
    8-bit
    read/write
    range 0–100
    percent
```

Fusion might generate:

```text
property Power : Percent
```

C# might generate:

```text
byte Power { get; set; }
```

Rust might generate:

```text
Power(u8)
```

C might generate:

```text
uint8_t power;
```

The semantics remain the same.

The language-specific generator decides how best to express them.

## 36. Recommended HIDL Layers

A robust HIDL design could have several layers.

```text
Layer 1 — Physical
    pins
    buses
    electrical direction

Layer 2 — Hardware
    registers
    memory
    bits
    interrupts

Layer 3 — Semantic
    commands
    states
    enums
    relationships
    constraints

Layer 4 — Behavioral
    timing
    dependencies
    side effects
    state transitions

Layer 5 — API
    operations
    properties
    events
    interfaces

Layer 6 — Tooling
    debugger
    simulator
    documentation
    code generation
```

This prevents HIDL from becoming merely a fancy register-list format.

## 37. Recommended Source-of-Truth Model

The strongest architecture is:

```text
             ONE SOURCE OF TRUTH

                    HIDL
                     |
       +-------------+-------------+
       |             |             |
       v             v             v
   C generator   Fusion generator  Rust generator
       |             |             |
       v             v             v
      API           API            API

                     +
                     |
                     +--> IDE
                     |
                     +--> Debugger
                     |
                     +--> Simulator
                     |
                     +--> Documentation
                     |
                     +--> Tests
```

The HIDL file should be treated as the canonical hardware interface.

Generated files should normally not be edited manually.

## 38. Suggested Fusion Project Structure

```text
Project/
│
├── hardware/
│   └── MicrowaveController.hidl
│
├── source/
│   ├── MicrowaveApp.fusion
│   └── Cooking.fusion
│
└── generated/
    └── MicrowaveController.generated.fusion
```

The developer normally works with the generated API rather than editing generated files.

## 39. Ideal Developer Experience

```text
1. Supplier provides:
       MicrowaveController.hidl

2. Developer adds it to Fusion project.

3. Fusion IDE reads HIDL.

4. Fusion generates:
       types
       interfaces
       hardware bindings
       constants
       validation
       documentation

5. IDE provides autocomplete.

6. Compiler checks hardware constraints.

7. Developer writes:

       microwave.Power = 80
       microwave.Timer = 90
       microwave.Start()

8. Compiler generates appropriate low-level operations.

9. Program runs on the hardware.
```

The developer never manually copies raw addresses from a PDF into application source code.

## 40. Recommended Core HIDL Model

A useful conceptual model for Fusion would be:

```text
DEVICE
 ├── metadata
 ├── memory regions
 ├── registers
 │    ├── fields
 │    └── access rules
 ├── types
 ├── enums
 ├── commands
 ├── properties
 ├── events
 ├── states
 ├── transitions
 ├── dependencies
 ├── constraints
 ├── timing
 ├── side effects
 ├── interrupts
 ├── DMA
 └── capabilities
```

This gives the language/toolchain enough information to generate a genuinely useful hardware API.

## 41. Potential Fusion Compiler Pipeline

A future Fusion compiler could conceptually process hardware like this:

```text
HIDL
  |
  v
Parse
  |
  v
Validate HIDL
  |
  v
Build Hardware Model
  |
  v
Generate/Load Fusion Types
  |
  v
Generate Interfaces
  |
  v
Apply Traits
  |
  v
Type Check
  |
  v
Hardware Safety Analysis
  |
  v
Optimize
  |
  v
Generate Driver Operations
  |
  v
Generate Machine Code
```

This means HIDL isn't necessarily just a code-generation utility. It could become part of the compiler's semantic model.

## 42. Key Design Principle

The most important design rule is:

> Don't make the programmer learn the hardware representation unless they actually need it.

Normal code:

```text
microwave.Start()
```

Advanced code:

```text
microwave.Registers.Command.write(Command.Start)
```

Expert/low-level code:

```text
hardware.write(0x40001000, 0x01)
```

All three can ultimately reach the same hardware.

Abstraction should reduce complexity, not remove control.

## 43. Final Concept

The complete idea can be summarized as:

> HIDL is a machine-readable contract describing a hardware device's programming interface, capabilities, registers, data structures, commands, constraints, states, timing, and behavior.

The supplier creates the definition once.

The development environment consumes it.

The compiler/toolchain generates the appropriate language-level API.

The programmer works with strongly typed objects and functions rather than raw hardware addresses.

Fusion can take this further by combining:

```text
HIDL
    ↓
Hardware truth/capabilities

Interfaces
    ↓
Promises/contracts

Traits
    ↓
Reusable behavior

Classes/objects
    ↓
Usable abstractions

Compiler
    ↓
Enforcement + optimization + code generation

Machine code
    ↓
Actual hardware
```

### The Three Core Fusion Concepts

**HIDL** — "What does the hardware provide?"
Defines the physical and logical hardware interface.

**Interface** — "What do I promise to provide?"
Defines a contract that an implementation must satisfy.

**Trait** — "What behavior do I provide?"
Provides reusable implementation/behavior that can be composed into types.

Therefore:

```text
HIDL = hardware truth
Interface = promise
Trait = behavior
```

This creates a clean conceptual boundary between hardware, software contracts, reusable behavior, and implementation.
