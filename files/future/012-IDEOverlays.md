[< 011 IDEProjects](011-IDEProjects.md) | [Index](index.md) | [013 IDEOverlays2 >](013-IDEOverlays2.md) <!-- nav -->

# 012 IDE Overlays

**Status:** idea - the thread view is FEATURES 36.6; the rest no task

**Contents**

- [IDE Code Quality Overlays & Hints](#ide-code-quality-overlays--hints)
- [Overview](#overview)
- [Feature 1: Inverted If Detection (Reduce Nesting)](#feature-1-inverted-if-detection-reduce-nesting)
- [Feature 2: Thread Visualization (Communication Tracking)](#feature-2-thread-visualization-communication-tracking)
- [Feature 3: Performance Profiling Overlay](#feature-3-performance-profiling-overlay)
- [Feature 4: Duplicate Code Detection](#feature-4-duplicate-code-detection)

## IDE Code Quality Overlays & Hints

**Status:** 📝 Proposed
**Priority:** High (developer experience, code quality)
**Impact:** IDE integration, Language Server Protocol (LSP)
**Depends On:** fusionlib.IDE module, LSP implementation
**Module:** fusionlib.IDE

**Purpose:** Provide real-time code quality analysis, performance insights, and refactoring suggestions directly in the IDE through visual overlays and interactive hints.

---

### Overview

- Modern IDEs provide rich feedback beyond syntax errors.
- This feature adds intelligent overlays and hints that help developers write better, faster, more maintainable code.
- All features are configurable by project managers to match team standards and project requirements.

**Key Principles:**
- Non-intrusive: Hints don't block development
- Configurable: Project leads control thresholds and enabled features
- Actionable: Each hint provides clear next steps
- Context-aware: Suggestions match project patterns

---

### Feature 1: Inverted If Detection (Reduce Nesting)

**Purpose:** Detect deeply nested IF statements and suggest guard clauses/early returns to reduce complexity.

**Problem - Deeply Nested Code:**
```fusion
int function processUser(User user)
    if user != null
        if user.isActive
            if user.hasPermission("admin")
                if user.age >= 18
                    // 4 levels of nesting - hard to read
                    return performAdminAction(user)
                else
                    return ErrorCode.TooYoung
            else
                return ErrorCode.NoPermission
        else
            return ErrorCode.Inactive
    else
        return ErrorCode.NullUser
```

**Solution - Inverted Conditions (Guard Clauses):**
```fusion
int function processUser(User user)
    // Early returns - flat structure
    if user == null
        return ErrorCode.NullUser

    if not user.isActive
        return ErrorCode.Inactive

    if not user.hasPermission("admin")
        return ErrorCode.NoPermission

    if user.age < 18
        return ErrorCode.TooYoung

    // Main logic at top level - easy to read
    return performAdminAction(user)
```

**IDE Visualization:**
- **Overlay:** Colored vertical lines showing nesting depth
- **Warning:** "Consider inverting conditions to reduce nesting"
- **Quick-fix:** "Refactor to guard clauses" (auto-applies transformation)
- **Before/After Preview:** Shows refactored code

**Configuration:**
```json
{
  "codeQuality": {
    "maxNestingDepth": 3,
    "suggestGuardClauses": true,
    "warnAtDepth": 3,
    "errorAtDepth": 5
  }
}
```

**Thresholds:**
- **Depth 1-2:** ✅ Green (good)
- **Depth 3:** ⚠️ Yellow warning (consider refactoring)
- **Depth 4:** 🟠 Orange warning (should refactor)
- **Depth 5+:** 🔴 Red error (must refactor)

---

### Feature 2: Thread Visualization (Communication Tracking)

**Purpose:** Show where threads/goroutines are created and visualize channel communication between concurrent tasks.

**Example Code:**
```fusion
import Fusion.Threading

void function main()
    Channel<int> results = Channel<int>()

    // Create 3 worker threads
    go worker(results, 1)  // Thread 1
    go worker(results, 2)  // Thread 2
    go worker(results, 3)  // Thread 3

    // Collect results
    for i = 0 to 3
        int result = results.receive()
        print("Got result: {result}")

void function worker(Channel<int> ch, int id)
    // Do work
    int result = compute(id)
    ch.send(result)  // Send to channel
```

**IDE Visualization:**

**1. Thread Creation Points:**
- `go worker(...)` highlighted with thread icon 🧵
- Hover tooltip: "Creates new goroutine/thread"
- Click to jump to function definition

**2. Channel Communication:**
- Visual arrows showing data flow:
  ```
  worker(1) -----> [Channel] -----> main()
  worker(2) -----> [Channel] -----> main()
  worker(3) -----> [Channel] -----> main()
  ```

**3. Synchronization Points:**
- Mutex locks highlighted in blue
- Channels highlighted in green
- WaitGroups highlighted in purple

**4. Data Race Detection:**
- Warn if shared variables accessed without locks
- Highlight potential race conditions in red

**IDE Features:**
- **Thread Tree View:** Shows all threads and their parent-child relationships
- **Message Trace:** Shows channel send/receive pairs
- **Deadlock Detection:** Warns about potential deadlocks (circular waits)

**Configuration:**
```json
{
  "threading": {
    "showThreadCreation": true,
    "showChannelFlow": true,
    "showSynchronization": true,
    "warnDataRaces": true,
    "warnDeadlocks": true
  }
}
```

---

### Feature 3: Performance Profiling Overlay

**Purpose:** After running/profiling the app, show inline performance metrics (execution time, memory usage, call frequency) directly in the code editor.

**Example:**
```fusion
void function main()
    processData()  // 85% of total time ⚠️
    saveResults()  // 10% of total time
    cleanup()      // 5% of total time

void function processData()
    // Called: 1 time
    // Time: 850ms (85% of total)
    // Memory: 120MB allocated

    for i = 0 to 1000000  // 60% of function time
        heavyCalculation(i)

    sortResults()  // 25% of function time

void function heavyCalculation(int n)  // Called: 1,000,000 times ⚠️
    // Avg time per call: 0.85μs
    // Total time: 850ms
    // Memory per call: 120 bytes

    // Hot path detected ⚡
    int result = complexMath(n)
    return result
```

**IDE Visualization:**

**1. Inline Metrics (Next to Function):**
```fusion
void function processData()  // 🔥 85% | 850ms | 120MB
```

**2. Heatmap Overlay:**
- Red: Hot code (most time spent)
- Orange: Warm code (moderate time)
- Yellow: Cool code (little time)
- Green: Cold code (negligible time)

**3. Memory Allocation Indicators:**
```fusion
List<int> data = List<int>()  // 💾 5MB allocated
```

**4. Call Frequency:**
```fusion
void function calculate(int x)  // 📞 Called 1,000,000× per run
```

**IDE Features:**
- **Profiler Panel:** Shows flame graph, call tree, memory timeline
- **Comparison Mode:** Compare performance before/after refactoring
- **Export:** Save profile data to file for analysis

**Configuration:**
```json
{
  "profiling": {
    "showInlineMetrics": true,
    "showHeatmap": true,
    "showMemoryAllocation": true,
    "showCallFrequency": true,
    "hotPathThreshold": 10,  // % of total time to mark as "hot"
    "frequentCallThreshold": 1000  // Calls per run to warn
  }
}
```

**Integration:**
```bash
# Run app with profiling enabled
fusion run --profile main.fusion

# IDE automatically loads profile data and shows overlays
```

---

### Feature 4: Duplicate Code Detection

**Purpose:** Highlight duplicated code blocks and suggest extraction to functions/methods to follow DRY principle.

**Example - Duplicated Code:**
```fusion
void function processOrderA(Order order)
    // Duplicate block 1
    if order.total > 100
        order.discount = order.total * 0.1
        order.total = order.total - order.discount

    saveOrder(order)

void function processOrderB(Order order)
    // Duplicate block 2 (87% similar)
    if order.total > 100
        order.discount = order.total * 0.1
        order.total = order.total - order.discount

    emailCustomer(order)
```

**IDE Visualization:**

**1. Highlight Duplicates:**
- Both duplicate blocks highlighted in yellow
- Link icon showing relationship
- Hover tooltip: "87% similar to code at line 15"

**2. Similarity Percentage:**
```
🔗 Duplicate detected (87% similar)
Found in: processOrderB() at line 15
```

**3. Quick-fix Suggestion:**
```
💡 Extract to function: "applyDiscount(Order)"
```

**Refactored Code:**
```fusion
void function applyDiscount(Order order)
    if order.total > 100
        order.discount = order.total * 0.1
        order.total = order.total - order.discount

void function processOrderA(Order order)
    applyDiscount(order)
    saveOrder(order)

void function processOrderB(Order order)
    applyDiscount(order)
    emailCustomer(order)
```

**IDE Features:**
- **Duplicate Panel:** Lists all duplicates in project
- **Auto-refactor:** One-click extraction to function
- **Ignore List:** Mark intentional duplicates (e.g., templates)

**Configuration:**
```json
{
  "duplicateDetection": {
    "enabled": true,
    "minSimilarity": 70,  // % similarity to flag as duplicate
    "minLines": 5,        // Minimum lines to consider
    "ignoreComments": true,
    "ignoreWhitespace": true,
    "suggestExtraction": true
  }
}
```

[< 011 IDEProjects](011-IDEProjects.md) | [Index](index.md) | [013 IDEOverlays2 >](013-IDEOverlays2.md) <!-- nav -->
