# HIDL Compiler Architecture: AST, LLVM-Style IR, ABI & x86-64 Assembly

This specification defines the core **interfaces, classes, and enums** for compiling a **Hardware Interface Definition Language (HIDL)** specification down to optimized **x86-64 assembly** with a first-class **ABI** layer.

It is written in strongly typed TypeScript-style OOP syntax so it can be translated directly into **Fusion**, **C#**, **Rust** (traits/structs), or **TypeScript** with Claude Code.

---

## Architecture Overview

```text
.hidl Spec
    │
    ▼
[1. HIDL AST]          ──► DeviceNode, RegisterNode, BitFieldNode, CommandNode
    │
    ▼
[2. LLVM-Style IR]     ──► IRModule, IRFunction, VolatileLoad/Store, Fence, BitOps
    │
    ▼
[3. ABI Layer]         ──► IABI (SystemV_AMD64_ABI: Regs, Stack, MMIO, Alignment, ISR)
    │
    ▼
[4. x86-64 Backend]    ──► X64CodeGenerator + Peephole Optimizer ──► Optimized .s
```

---

## 1. Abstract Syntax Tree (HIDL AST)

The AST represents the **hardware truth** parsed from a `.hidl` file—registers, access rules, bitfields, multi-register values, commands, state constraints, and timing requirements.

```typescript
// ============================================================================
// 1. HIDL ABSTRACT SYNTAX TREE (AST)
// ============================================================================

export enum RegisterAccess {
    READ_ONLY           = "READ_ONLY",
    WRITE_ONLY          = "WRITE_ONLY",
    READ_WRITE          = "READ_WRITE",
    CLEAR_ON_READ       = "CLEAR_ON_READ",
    WRITE_ONE_TO_CLEAR  = "WRITE_ONE_TO_CLEAR",
    WRITE_ONE_TO_SET    = "WRITE_ONE_TO_SET",
    COMMAND             = "COMMAND",
}

export enum PhysicalDirection {
    INPUT               = "INPUT",
    OUTPUT              = "OUTPUT",
    BIDIRECTIONAL       = "BIDIRECTIONAL",
}

export enum ByteOrder {
    LITTLE_ENDIAN       = "LITTLE_ENDIAN",
    BIG_ENDIAN          = "BIG_ENDIAN",
}

export enum HardwarePrimitive {
    UINT8  = 8,
    UINT16 = 16,
    UINT32 = 32,
    UINT64 = 64,
    BOOL   = 1,
}

export interface SourceSpan {
    readonly file: string;
    readonly line: number;
    readonly column: number;
}

/** Base contract for every node in the HIDL AST */
export interface IHidlAstNode {
    readonly kind: string;
    readonly span: SourceSpan;
    accept<T>(visitor: IHidlAstVisitor<T>): T;
}

export interface IHidlAstVisitor<T> {
    visitDevice(node: DeviceNode): T;
    visitRegister(node: RegisterNode): T;
    visitBitField(node: BitFieldNode): T;
    visitCommand(node: CommandNode): T;
    visitConstraint(node: ConstraintNode): T;
}

/** Represents a bit or slice of bits inside a register (HIDL Sec. 9) */
export class BitFieldNode implements IHidlAstNode {
    readonly kind = "BitField";
    constructor(
        public readonly name: string,
        public readonly bitOffset: number,      // e.g., 4
        public readonly bitWidth: number,       // e.g., 2 (bits 4-5)
        public readonly access: RegisterAccess,
        public readonly enumValues: ReadonlyMap<string, number>,
        public readonly span: SourceSpan,
    ) {}

    /** Bitmask shifted into position, e.g., offset=4, width=2 => 0b00110000 */
    get mask(): bigint {
        return ((1n << BigInt(this.bitWidth)) - 1n) << BigInt(this.bitOffset);
    }

    accept<T>(visitor: IHidlAstVisitor<T>): T {
        return visitor.visitBitField(this);
    }
}

/** Represents a hardware register (HIDL Sec. 7-11) */
export class RegisterNode implements IHidlAstNode {
    readonly kind = "Register";
    constructor(
        public readonly name: string,
        public readonly offsetAddress: bigint,  // Offset from device MMIO base (e.g., 0x02n)
        public readonly bitSize: HardwarePrimitive,
        public readonly access: RegisterAccess,
        public readonly direction: PhysicalDirection,
        public readonly resetValue: bigint,
        public readonly fields: readonly BitFieldNode[],
        public readonly minRange: number | null,
        public readonly maxRange: number | null,
        public readonly unit: string | null,
        public readonly span: SourceSpan,
    ) {}

    accept<T>(visitor: IHidlAstVisitor<T>): T {
        return visitor.visitRegister(this);
    }
}

/** Represents a hardware precondition / state dependency (HIDL Sec. 13) */
export class ConstraintNode implements IHidlAstNode {
    readonly kind = "Constraint";
    constructor(
        public readonly targetRegister: string,
        public readonly operator: "==" | "!=" | ">" | "<" | ">=" | "<=",
        public readonly expectedValue: number,
        public readonly span: SourceSpan,
    ) {}

    accept<T>(visitor: IHidlAstVisitor<T>): T {
        return visitor.visitConstraint(this);
    }
}

/** Represents a timing requirement (HIDL Sec. 14) */
export class TimingSpec {
    constructor(
        public readonly delayBeforeNs: number = 0,
        public readonly delayAfterNs: number = 0,
        public readonly minIntervalNs: number = 0,
    ) {}
}

/** Represents a write-triggered hardware command (HIDL Sec. 12) */
export class CommandNode implements IHidlAstNode {
    readonly kind = "Command";
    constructor(
        public readonly name: string,
        public readonly targetRegisterOffset: bigint,
        public readonly opcodeValue: bigint,
        public readonly requires: readonly ConstraintNode[],
        public readonly timing: TimingSpec,
        public readonly span: SourceSpan,
    ) {}

    accept<T>(visitor: IHidlAstVisitor<T>): T {
        return visitor.visitCommand(this);
    }
}

/** Root AST Node for a HIDL hardware device (HIDL Sec. 4, 22) */
export class DeviceNode implements IHidlAstNode {
    readonly kind = "Device";
    constructor(
        public readonly name: string,
        public readonly hardwareVersion: string, // e.g., "1.0"
        public readonly byteOrder: ByteOrder,
        public readonly baseAddressAlignment: number,
        public readonly registers: readonly RegisterNode[],
        public readonly commands: readonly CommandNode[],
        public readonly span: SourceSpan,
    ) {}

    accept<T>(visitor: IHidlAstVisitor<T>): T {
        return visitor.visitDevice(this);
    }
}
```

---

## 2. Intermediate Representation (LLVM-Style Hardware IR)

Before targeting any CPU, HIDL operations are lowered into an **SSA (Static Single Assignment) LLVM-style IR**. Unlike generic software IR, hardware IR explicitly models **`volatile` MMIO access**, **memory ordering fences**, **bitfield extraction/insertion**, and **timing intrinsics**.

```typescript
// ============================================================================
// 2. INTERMEDIATE REPRESENTATION (LLVM-STYLE HARDWARE IR)
// ============================================================================

export enum IRTypeKind {
    VOID = "void",
    I1   = "i1",
    I8   = "i8",
    I16  = "i16",
    I32  = "i32",
    I64  = "i64",
    PTR  = "ptr", // Opaque MMIO base pointer (LLVM 15+ style)
}

export enum MemoryOrdering {
    UNORDERED = "unordered",
    MONOTONIC = "monotonic",
    ACQUIRE   = "acquire",
    RELEASE   = "release",
    ACQ_REL   = "acq_rel",
    SEQ_CST   = "seq_cst",
}

export interface IIRValue {
    readonly name: string;      // e.g., "%0", "%base", "80"
    readonly type: IRTypeKind;
    readonly isConstant: boolean;
    readonly constantValue?: bigint;
}

export class IRVirtualReg implements IIRValue {
    readonly isConstant = false;
    constructor(
        public readonly name: string,
        public readonly type: IRTypeKind,
    ) {}
}

export class IRConstant implements IIRValue {
    readonly isConstant = true;
    readonly name: string;
    constructor(
        public readonly type: IRTypeKind,
        public readonly constantValue: bigint,
    ) {
        this.name = constantValue.toString();
    }
}

/** Base interface for every SSA instruction in a basic block */
export interface IIRInstruction {
    readonly opcode: string;
    readonly result: IRVirtualReg | null;
    toLLVMText(): string;
}

/** Pointer arithmetic: %reg_ptr = getelementptr i8, ptr %base, i64 <offset> */
export class IRGetElementPtr implements IIRInstruction {
    readonly opcode = "getelementptr";
    constructor(
        public readonly result: IRVirtualReg,
        public readonly basePtr: IIRValue,
        public readonly byteOffset: bigint,
    ) {}

    toLLVMText(): string {
        return `  ${this.result.name} = getelementptr i8, ptr ${this.basePtr.name}, i64 ${this.byteOffset}`;
    }
}

/** Hardware MMIO Read: %val = load volatile i8, ptr %reg_ptr, align 1 */
export class IRVolatileLoad implements IIRInstruction {
    readonly opcode = "load_volatile";
    constructor(
        public readonly result: IRVirtualReg,
        public readonly address: IIRValue,
        public readonly alignment: number,
        public readonly ordering: MemoryOrdering = MemoryOrdering.ACQUIRE,
    ) {}

    toLLVMText(): string {
        return `  ${this.result.name} = load volatile ${this.result.type}, ptr ${this.address.name}, align ${this.alignment}`;
    }
}

/** Hardware MMIO Write: store volatile i8 %val, ptr %reg_ptr, align 1 */
export class IRVolatileStore implements IIRInstruction {
    readonly opcode = "store_volatile";
    readonly result = null;
    constructor(
        public readonly value: IIRValue,
        public readonly address: IIRValue,
        public readonly alignment: number,
        public readonly ordering: MemoryOrdering = MemoryOrdering.RELEASE,
    ) {}

    toLLVMText(): string {
        return `  store volatile ${this.value.type} ${this.value.name}, ptr ${this.address.name}, align ${this.alignment}`;
    }
}

/** Hardware memory barrier: fence seq_cst */
export class IRMemoryFence implements IIRInstruction {
    readonly opcode = "fence";
    readonly result = null;
    constructor(public readonly ordering: MemoryOrdering) {}

    toLLVMText(): string {
        return `  fence ${this.ordering}`;
    }
}

/** Binary ALU / Bitwise op: add, mul, and, or, shl, lshr */
export class IRBinaryOp implements IIRInstruction {
    constructor(
        public readonly opcode: "add" | "sub" | "mul" | "and" | "or" | "xor" | "shl" | "lshr",
        public readonly result: IRVirtualReg,
        public readonly lhs: IIRValue,
        public readonly rhs: IIRValue,
    ) {}

    toLLVMText(): string {
        return `  ${this.result.name} = ${this.opcode} ${this.result.type} ${this.lhs.name}, ${this.rhs.name}`;
    }
}

/** Function return */
export class IRRet implements IIRInstruction {
    readonly opcode = "ret";
    readonly result = null;
    constructor(public readonly value: IIRValue | null) {}

    toLLVMText(): string {
        return this.value
            ? `  ret ${this.value.type} ${this.value.name}`
            : `  ret void`;
    }
}

export class IRBasicBlock {
    public readonly instructions: IIRInstruction[] = [];
    constructor(public readonly label: string) {}

    emit(instr: IIRInstruction): void {
        this.instructions.push(instr);
    }
}

export class IRFunction {
    public readonly blocks: IRBasicBlock[] = [];
    constructor(
        public readonly name: string,
        public readonly returnType: IRTypeKind,
        public readonly parameters: readonly IRVirtualReg[],
        public readonly isLeaf: boolean = true,
        public readonly isInterruptHandler: boolean = false,
    ) {}

    toLLVMText(): string {
        const params = this.parameters.map(p => `${p.type} ${p.name}`).join(", ");
        const body = this.blocks
            .map(b => `${b.label}:\n` + b.instructions.map(i => i.toLLVMText()).join("\n"))
            .join("\n");
        return `define ${this.returnType} @${this.name}(${params}) {\n${body}\n}`;
    }
}

export class IRModule {
    public readonly functions: IRFunction[] = [];
    constructor(
        public readonly moduleName: string,
        public readonly targetTriple: string, // e.g., "x86_64-unknown-linux-gnu"
    ) {}
}
```

---

## 3. The ABI Layer (First-Class Contract)

The **ABI (Application Binary Interface)** is the bridge between hardware-agnostic IR and concrete machine code. For HIDL, the ABI must govern **four** distinct domains:
1. **Calling Convention** (how arguments/returns pass in registers vs. stack).
2. **Data & MMIO Layout** (endianness, alignment, volatile access widths, memory fences).
3. **Interrupt / ISR ABI** (how hardware interrupts save/restore CPU state).
4. **ABI Compatibility & Versioning** (verifying whether HIDL v1 and v2 are binary-compatible).

```typescript
// ============================================================================
// 3. APPLICATION BINARY INTERFACE (ABI) — CORE CONTRACTS & SYSTEM V AMD64
// ============================================================================

export enum RegisterClass {
    INTEGER_GP  = "INTEGER_GP",
    FLOAT_SIMD  = "FLOAT_SIMD",
    FLAGS       = "FLAGS",
    STACK_PTR   = "STACK_PTR",
}

export enum RegisterPreservation {
    CALLER_SAVED = "CALLER_SAVED", // Volatile across calls (scratch)
    CALLEE_SAVED = "CALLEE_SAVED", // Must be preserved by called function
    RESERVED     = "RESERVED",     // e.g., RSP
}

/** Describes a physical CPU register and its sub-register aliases */
export interface IPhysicalRegister {
    readonly id: string;           // Canonical name, e.g., "rdi"
    readonly regClass: RegisterClass;
    readonly preservation: RegisterPreservation;
    readonly bitWidth: 64 | 32 | 16 | 8;
    aliasForWidth(bits: 64 | 32 | 16 | 8): string; // e.g., rdi -> edi -> di -> dil
}

/** Calling Convention Contract (How functions receive args & return values) */
export interface ICallingConvention {
    readonly name: string;
    readonly intArgRegisters: readonly IPhysicalRegister[];
    readonly floatArgRegisters: readonly IPhysicalRegister[];
    readonly intReturnRegisters: readonly IPhysicalRegister[];
    readonly calleeSavedRegisters: readonly IPhysicalRegister[];
    readonly callerSavedRegisters: readonly IPhysicalRegister[];
    readonly stackPointer: IPhysicalRegister;
    readonly framePointer: IPhysicalRegister;

    readonly stackAlignmentBytes: number;   // 16 on System V AMD64
    readonly redZoneBytes: number;          // 128 on System V AMD64, 0 on Windows x64 / Kernel
    readonly shadowSpaceBytes: number;      // 0 on System V AMD64, 32 on Windows x64

    /** Determines where argument #index of a given IR type lives */
    locateArgument(index: number, type: IRTypeKind): ArgumentLocation;
    /** Determines if a leaf function can omit push rbp / mov rbp, rsp */
    canOmitFramePointer(fn: IRFunction): boolean;
}

export type ArgumentLocation =
    | { kind: "register"; register: IPhysicalRegister; subRegName: string }
    | { kind: "stack"; offsetFromRsp: number };

/** MMIO & Hardware Memory Layout Contract (Crucial for HIDL!) */
export interface IMemoryLayoutABI {
    readonly endianness: ByteOrder;
    readonly pointerSizeBytes: 4 | 8;
    readonly supportsUnalignedMMIO: boolean;
    readonly maxAtomicBusWidthBits: 32 | 64;

    /** Returns the required alignment in bytes for an IR type */
    alignmentOf(type: IRTypeKind): number;
    /** Maps an IR MemoryOrdering to the target CPU's barrier instruction(s) */
    fenceInstructionFor(ordering: MemoryOrdering): string | null;
}

/** Interrupt Service Routine (ISR) Contract (HIDL Sec. 28) */
export interface IInterruptABI {
    readonly returnInstruction: string;         // e.g., "iretq" on x86-64
    readonly mustPreserveAllRegisters: boolean; // ISRs cannot clobber caller-saved regs
    readonly disablesRedZone: boolean;          // Must be true for kernel/ISR code
}

/** ABI Compatibility Report (HIDL Sec. 22-23) */
export enum CompatibilityLevel {
    FULLY_COMPATIBLE    = "FULLY_COMPATIBLE",
    API_COMPATIBLE_ONLY = "API_COMPATIBLE_ONLY", // Recompile required (offsets/ABI changed)
    REGISTER_COMPATIBLE = "REGISTER_COMPATIBLE",
    INCOMPATIBLE        = "INCOMPATIBLE",
}

export interface IABICompatibilityChecker {
    compareDevices(oldDev: DeviceNode, newDev: DeviceNode, abi: IABI): CompatibilityLevel;
}

/** Master ABI Interface passed into Code Generators & Linkers */
export interface IABI {
    readonly targetTriple: string;
    readonly callingConvention: ICallingConvention;
    readonly memoryLayout: IMemoryLayoutABI;
    readonly interruptABI: IInterruptABI;
    readonly compatibilityChecker: IABICompatibilityChecker;
}
```

### Concrete Implementation: `SystemV_AMD64_ABI`

```typescript
// ============================================================================
// CONCRETE IMPLEMENTATION: SYSTEM V AMD64 ABI (Linux / macOS / BSD x86-64)
// ============================================================================

export class X64PhysicalRegister implements IPhysicalRegister {
    readonly bitWidth = 64 as const;
    constructor(
        public readonly id: string,
        private readonly name32: string,
        private readonly name16: string,
        private readonly name8: string,
        public readonly regClass: RegisterClass,
        public readonly preservation: RegisterPreservation,
    ) {}

    aliasForWidth(bits: 64 | 32 | 16 | 8): string {
        switch (bits) {
            case 64: return this.id;
            case 32: return this.name32;
            case 16: return this.name16;
            case 8:  return this.name8;
        }
    }
}

export const X64Regs = {
    RAX: new X64PhysicalRegister("rax", "eax", "ax",  "al",  RegisterClass.INTEGER_GP, RegisterPreservation.CALLER_SAVED),
    RBX: new X64PhysicalRegister("rbx", "ebx", "bx",  "bl",  RegisterClass.INTEGER_GP, RegisterPreservation.CALLEE_SAVED),
    RCX: new X64PhysicalRegister("rcx", "ecx", "cx",  "cl",  RegisterClass.INTEGER_GP, RegisterPreservation.CALLER_SAVED),
    RDX: new X64PhysicalRegister("rdx", "edx", "dx",  "dl",  RegisterClass.INTEGER_GP, RegisterPreservation.CALLER_SAVED),
    RSI: new X64PhysicalRegister("rsi", "esi", "si",  "sil", RegisterClass.INTEGER_GP, RegisterPreservation.CALLER_SAVED),
    RDI: new X64PhysicalRegister("rdi", "edi", "di",  "dil", RegisterClass.INTEGER_GP, RegisterPreservation.CALLER_SAVED),
    R8:  new X64PhysicalRegister("r8",  "r8d", "r8w", "r8b", RegisterClass.INTEGER_GP, RegisterPreservation.CALLER_SAVED),
    R9:  new X64PhysicalRegister("r9",  "r9d", "r9w", "r9b", RegisterClass.INTEGER_GP, RegisterPreservation.CALLER_SAVED),
    RBP: new X64PhysicalRegister("rbp", "ebp", "bp",  "bpl", RegisterClass.STACK_PTR,  RegisterPreservation.CALLEE_SAVED),
    RSP: new X64PhysicalRegister("rsp", "esp", "sp",  "spl", RegisterClass.STACK_PTR,  RegisterPreservation.RESERVED),
} as const;

export class SystemVCallingConvention implements ICallingConvention {
    readonly name = "System V AMD64";
    readonly intArgRegisters    = [X64Regs.RDI, X64Regs.RSI, X64Regs.RDX, X64Regs.RCX, X64Regs.R8, X64Regs.R9];
    readonly floatArgRegisters  = []; // XMM0..XMM7 omitted for brevity
    readonly intReturnRegisters = [X64Regs.RAX, X64Regs.RDX];
    readonly calleeSavedRegisters = [X64Regs.RBX, X64Regs.RBP]; // + R12..R15
    readonly callerSavedRegisters = [X64Regs.RAX, X64Regs.RCX, X64Regs.RDX, X64Regs.RSI, X64Regs.RDI, X64Regs.R8, X64Regs.R9];
    readonly stackPointer = X64Regs.RSP;
    readonly framePointer = X64Regs.RBP;

    readonly stackAlignmentBytes = 16;
    readonly redZoneBytes = 128;
    readonly shadowSpaceBytes = 0;

    locateArgument(index: number, type: IRTypeKind): ArgumentLocation {
        const bitWidth = this.bitsForIRType(type);
        if (index < this.intArgRegisters.length) {
            const reg = this.intArgRegisters[index];
            return { kind: "register", register: reg, subRegName: reg.aliasForWidth(bitWidth) };
        }
        // Spill overflow arguments to stack (8-byte slots above return address)
        const stackSlot = index - this.intArgRegisters.length;
        return { kind: "stack", offsetFromRsp: 8 + stackSlot * 8 };
    }

    canOmitFramePointer(fn: IRFunction): boolean {
        return fn.isLeaf && !fn.isInterruptHandler;
    }

    private bitsForIRType(type: IRTypeKind): 64 | 32 | 16 | 8 {
        switch (type) {
            case IRTypeKind.I1:
            case IRTypeKind.I8:  return 8;
            case IRTypeKind.I16: return 16;
            case IRTypeKind.I32: return 32;
            default:             return 64;
        }
    }
}

export class X64MemoryLayoutABI implements IMemoryLayoutABI {
    readonly endianness = ByteOrder.LITTLE_ENDIAN;
    readonly pointerSizeBytes = 8 as const;
    readonly supportsUnalignedMMIO = false; // Hardware MMIO generally requires natural alignment
    readonly maxAtomicBusWidthBits = 64 as const;

    alignmentOf(type: IRTypeKind): number {
        switch (type) {
            case IRTypeKind.I1:
            case IRTypeKind.I8:  return 1;
            case IRTypeKind.I16: return 2;
            case IRTypeKind.I32: return 4;
            default:             return 8;
        }
    }

    fenceInstructionFor(ordering: MemoryOrdering): string | null {
        // x86-64 TSO (Total Store Order) guarantees Acquire/Release in hardware;
        // explicit MFENCE is needed for SEQ_CST or strict MMIO write-to-read ordering.
        switch (ordering) {
            case MemoryOrdering.SEQ_CST: return "mfence";
            case MemoryOrdering.RELEASE: return "sfence";
            case MemoryOrdering.ACQUIRE: return "lfence";
            default:                     return null;
        }
    }
}

export class SystemV_AMD64_ABI implements IABI {
    readonly targetTriple = "x86_64-unknown-linux-gnu";
    readonly callingConvention = new SystemVCallingConvention();
    readonly memoryLayout = new X64MemoryLayoutABI();
    readonly interruptABI: IInterruptABI = {
        returnInstruction: "iretq",
        mustPreserveAllRegisters: true,
        disablesRedZone: true,
    };
    readonly compatibilityChecker: IABICompatibilityChecker = {
        compareDevices(oldDev, newDev): CompatibilityLevel {
            if (oldDev.byteOrder !== newDev.byteOrder) return CompatibilityLevel.INCOMPATIBLE;
            for (const oldReg of oldDev.registers) {
                const match = newDev.registers.find(r => r.name === oldReg.name);
                if (!match) return CompatibilityLevel.INCOMPATIBLE;
                if (match.offsetAddress !== oldReg.offsetAddress || match.bitSize !== oldReg.bitSize) {
                    return CompatibilityLevel.API_COMPATIBLE_ONLY;
                }
            }
            return CompatibilityLevel.FULLY_COMPATIBLE;
        },
    };
}
```

---

## 4. Generated x86-64 Assembly (Optimized, System V ABI)

The backend consumes an `IRModule` and an `IABI`, performs instruction selection, applies peephole optimizations (such as folding `getelementptr` offsets directly into `[rdi + 0x02]` addressing and omitting stack frames on leaf functions), and emits `.s` assembly.

```typescript
// ============================================================================
// 4. X86-64 ASSEMBLY MODEL, OPTIMIZER & CODE GENERATOR
// ============================================================================

export interface IAsmOperand {
    formatIntel(): string;
}

export class RegOperand implements IAsmOperand {
    constructor(public readonly regName: string) {}
    formatIntel(): string { return this.regName; }
}

export class ImmOperand implements IAsmOperand {
    constructor(public readonly value: bigint) {}
    formatIntel(): string { return `0x${this.value.toString(16)}`; }
}

/** Represents x86-64 memory addressing: size ptr [base + index*scale + disp] */
export class MemOperand implements IAsmOperand {
    constructor(
        public readonly sizeQualifier: "byte ptr" | "word ptr" | "dword ptr" | "qword ptr",
        public readonly baseReg: string,
        public readonly displacement: bigint = 0n,
        public readonly indexReg: string | null = null,
        public readonly scale: 1 | 2 | 4 | 8 = 1,
    ) {}

    formatIntel(): string {
        let expr = this.baseReg;
        if (this.indexReg) {
            expr += this.scale > 1 ? ` + ${this.indexReg}*${this.scale}` : ` + ${this.indexReg}`;
        }
        if (this.displacement !== 0n) {
            const sign = this.displacement > 0n ? "+" : "-";
            const abs = this.displacement > 0n ? this.displacement : -this.displacement;
            expr += ` ${sign} 0x${abs.toString(16)}`;
        }
        return `${this.sizeQualifier} [${expr}]`;
    }
}

export class X64Instruction {
    constructor(
        public readonly mnemonic: string,
        public readonly operands: readonly IAsmOperand[] = [],
        public readonly comment: string | null = null,
    ) {}

    formatIntel(): string {
        const ops = this.operands.map(o => o.formatIntel()).join(", ");
        const base = ops ? `    ${this.mnemonic} ${ops}` : `    ${this.mnemonic}`;
        return this.comment ? `${base.padEnd(36)} ; ${this.comment}` : base;
    }
}

export class X64FunctionAsm {
    public readonly instructions: X64Instruction[] = [];
    constructor(public readonly label: string) {}

    emit(mnemonic: string, operands: IAsmOperand[] = [], comment: string | null = null): void {
        this.instructions.push(new X64Instruction(mnemonic, operands, comment));
    }

    formatIntel(): string {
        return [
            `.global ${this.label}`,
            `${this.label}:`,
            ...this.instructions.map(i => i.formatIntel()),
        ].join("\n");
    }
}

export interface ICodeGenerator {
    generate(module: IRModule, abi: IABI): string;
}

/** Generates Optimized x86-64 Assembly obeying the supplied IABI */
export class X64CodeGenerator implements ICodeGenerator {
    generate(module: IRModule, abi: IABI): string {
        const lines: string[] = [
            `.intel_syntax noprefix`,
            `; Target ABI: ${abi.callingConvention.name} (${abi.targetTriple})`,
            `.text`,
            ``,
        ];

        for (const fn of module.functions) {
            const asmFn = this.compileFunction(fn, abi);
            lines.push(asmFn.formatIntel(), "");
        }
        return lines.join("\n");
    }

    private compileFunction(fn: IRFunction, abi: IABI): X64FunctionAsm {
        const out = new X64FunctionAsm(fn.name);
        const cc = abi.callingConvention;

        // 1. ABI Prologue (omitted for optimized leaf functions!)
        const omitFrame = cc.canOmitFramePointer(fn);
        if (!omitFrame) {
            out.emit("push", [new RegOperand(cc.framePointer.id)], "ABI prologue");
            out.emit("mov",  [new RegOperand(cc.framePointer.id), new RegOperand(cc.stackPointer.id)]);
        }

        // Map incoming IR parameters to their ABI-mandated physical registers
        const vregToPhys = new Map<string, string>();
        fn.parameters.forEach((param, idx) => {
            const loc = cc.locateArgument(idx, param.type);
            if (loc.kind === "register") {
                vregToPhys.set(param.name, loc.subRegName);
            }
        });

        // Track GEP offsets so we can fold [base + offset] directly into MOV instructions
        const gepOffsets = new Map<string, { baseReg: string; offset: bigint }>();

        // 2. Instruction Selection + Address Folding Optimization
        for (const block of fn.blocks) {
            for (const instr of block.instructions) {
                if (instr instanceof IRGetElementPtr) {
                    const baseReg = vregToPhys.get(instr.basePtr.name) ?? "rdi";
                    gepOffsets.set(instr.result.name, { baseReg, offset: instr.byteOffset });
                } else if (instr instanceof IRVolatileStore) {
                    const mem = this.resolveMemoryOperand(instr.address.name, instr.value.type, gepOffsets, vregToPhys);
                    const valOp = instr.value.isConstant
                        ? new ImmOperand(instr.value.constantValue!)
                        : new RegOperand(vregToPhys.get(instr.value.name)!);
                    out.emit("mov", [mem, valOp], "Volatile MMIO store");
                } else if (instr instanceof IRVolatileLoad) {
                    const mem = this.resolveMemoryOperand(instr.address.name, instr.result.type, gepOffsets, vregToPhys);
                    const retReg = cc.intReturnRegisters[0];
                    const dst = instr.result.type === IRTypeKind.I8 ? retReg.aliasForWidth(32) : retReg.aliasForWidth(64);
                    const mnemonic = instr.result.type === IRTypeKind.I8 ? "movzx" : "mov";
                    out.emit(mnemonic, [new RegOperand(dst), mem], "Volatile MMIO load (zero-extended)");
                    vregToPhys.set(instr.result.name, dst);
                } else if (instr instanceof IRMemoryFence) {
                    const fenceMnemonic = abi.memoryLayout.fenceInstructionFor(instr.ordering);
                    if (fenceMnemonic) {
                        out.emit(fenceMnemonic, [], `ABI memory barrier (${instr.ordering})`);
                    }
                } else if (instr instanceof IRRet) {
                    if (!omitFrame) {
                        out.emit("pop", [new RegOperand(cc.framePointer.id)], "ABI epilogue");
                    }
                    out.emit(fn.isInterruptHandler ? abi.interruptABI.returnInstruction : "ret");
                }
            }
        }

        return out;
    }

    private resolveMemoryOperand(
        ptrName: string,
        valueType: IRTypeKind,
        gepOffsets: Map<string, { baseReg: string; offset: bigint }>,
        vregToPhys: Map<string, string>,
    ): MemOperand {
        const qual = valueType === IRTypeKind.I8 ? "byte ptr"
                   : valueType === IRTypeKind.I16 ? "word ptr"
                   : valueType === IRTypeKind.I32 ? "dword ptr"
                   : "qword ptr";
        const gep = gepOffsets.get(ptrName);
        if (gep) {
            return new MemOperand(qual, gep.baseReg, gep.offset);
        }
        return new MemOperand(qual, vregToPhys.get(ptrName) ?? "rdi", 0n);
    }
}
```

---

## 5. End-to-End Example: `MicrowaveController` (HIDL $\rightarrow$ IR $\rightarrow$ x86-64)

Using the `MicrowaveController` from your HIDL document (`POWER` at `0x02`, `COMMAND` at `0x01`, `START = 0x01`):

### Stage A: Lowered LLVM-Style IR (Generated from `DeviceNode`)

```llvm
; microwave.Power = value   (ptr %base -> rdi, i8 %value -> sil)
define void @MicrowaveController_set_Power(ptr %base, i8 %value) {
entry:
  %power_ptr = getelementptr i8, ptr %base, i64 2
  store volatile i8 %value, ptr %power_ptr, align 1
  fence release
  ret void
}

; microwave.Start()         (ptr %base -> rdi)
define void @MicrowaveController_Start(ptr %base) {
entry:
  %cmd_ptr = getelementptr i8, ptr %base, i64 1
  store volatile i8 1, ptr %cmd_ptr, align 1
  fence seq_cst
  ret void
}
```

### Stage B: Optimized x86-64 Assembly (Emitted via `SystemV_AMD64_ABI`)

Because `SystemVCallingConvention.canOmitFramePointer()` returns `true` for leaf functions, and `X64CodeGenerator` folds `getelementptr` into `[rdi + offset]`, the compiler produces zero-overhead hardware access:

```asm
.intel_syntax noprefix
; Target ABI: System V AMD64 (x86_64-unknown-linux-gnu)
.text

.global MicrowaveController_set_Power
MicrowaveController_set_Power:
    mov byte ptr [rdi + 0x2], sil    ; Volatile MMIO store (rdi = base, sil = power)
    sfence                           ; ABI memory barrier (release)
    ret

.global MicrowaveController_Start
MicrowaveController_Start:
    mov byte ptr [rdi + 0x1], 0x1    ; Volatile MMIO store (START opcode = 0x01)
    mfence                           ; ABI memory barrier (seq_cst)
    ret
```

---

## 6. How This Fits Into Fusion & Claude Code

* **Swap ABIs without changing HIDL or IR:** Implementing `Microsoft_x64_ABI` (`RCX`, `RDX`, `R8`, `R9`, 32-byte shadow space) or `ARM64_AAPCS_ABI` (`X0`–`X7`, `DMB SY`) simply plugs into `X64CodeGenerator` / `ARM64CodeGenerator`.
* **Maps directly to Fusion's core triad:**
  * **HIDL AST (`DeviceNode`)** $\rightarrow$ Hardware truth.
  * **Interfaces (`IABI`, `ICallingConvention`, `IMemoryLayoutABI`)** $\rightarrow$ Contracts/promises.
  * **Classes (`SystemV_AMD64_ABI`, `X64CodeGenerator`)** $\rightarrow$ Concrete implementations.