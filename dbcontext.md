# 🗄️ Database Context Management System for AI Agents

**Purpose:** Store granular task context, progress, and code snippets in SQLite to enable specialized AI agents to work independently with minimal token usage and zero hallucination/drift.

**Status:** 🔮 Future enhancement (post-MVP compiler)

---

## Inspiration: Real-World Problem

**Source:** [Reddit - r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/comments/1p3io5m/i_built_a_task_system_that_survives_claude/)

**The Problem Solved:**
- ❌ Context loss between Claude sessions and machines
- ❌ Rule adherence drift and hallucinations
- ❌ Claude forgets to update task.md files after completing work
- ❌ Task files drift out of sync (falsely marked done, changed instead of followed)
- ❌ Manual git commit/push/pull just to sync task progress
- ❌ Git conflicts when switching devices
- ❌ Too many task markdowns become difficult to track

**Real-World Solution (Taskr - taskr.one):**
- ✅ **Database-first task management** - Tasks have real status (open/wip/done), enforced workflow
- ✅ **Embedded guidance in MCP tools** - Guidance built into tool responses, not separate files
- ✅ **Full task hierarchy** - Parent/child relationships, AI sees entire cause-effect chain
- ✅ **Context through notes** - Notes attach to tasks (FILE_LIST, PROGRESS, CONTEXT, FINDING)
- ✅ **AI-powered task generation** - Upload PRD, AI breaks it into task hierarchy
- ✅ **Instant sync across devices** - No git commits needed, no conflicts, no drift

**Key Insight:** *"Instead of hoping Claude reads your CLAUDE.md file, the guidance is built directly into the MCP tool input and responses."*

This document adapts these proven concepts for the Fusion compiler development workflow.

---

## Core Concept

Instead of passing massive markdown files to AI agents, store structured context in a database where:
- Each task has **only the context it needs** (code snippets, dependencies, constraints)
- AI agents query the database for their specific task context
- Progress/results are written back to the database
- Session continuity survives token limits and interruptions

---

## SQLite Schema

```sql
-- Core task tracking
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,              -- e.g., "2.3", "2.3.1"
    phase INT NOT NULL,               -- 1 (Lexer), 2 (Parser), 3 (Semantic), etc.
    parent_id TEXT,                   -- NULL for top-level, "2.3" for subtasks
    title TEXT NOT NULL,              -- "Statement Parsing"
    description TEXT,                 -- Detailed task description
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'in_progress', 'completed', 'blocked'
    progress INT DEFAULT 0,           -- 0-100%
    estimated_tests INT,              -- Expected number of tests
    actual_tests INT DEFAULT 0,       -- Actual tests written
    priority INT DEFAULT 0,           -- Higher = more urgent
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (parent_id) REFERENCES tasks(id)
);

-- Context snippets (code, specifications, constraints)
CREATE TABLE task_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    context_type TEXT NOT NULL,       -- 'code_snippet', 'spec', 'constraint', 'dependency', 'example'
    content TEXT NOT NULL,            -- The actual context data
    file_path TEXT,                   -- If code snippet, where it came from
    line_start INT,                   -- Starting line number
    line_end INT,                     -- Ending line number
    relevance INT DEFAULT 5,          -- 1-10, how critical is this context?
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- Dependencies between tasks
CREATE TABLE task_dependencies (
    task_id TEXT NOT NULL,
    depends_on_task_id TEXT NOT NULL,
    dependency_type TEXT DEFAULT 'blocks',  -- 'blocks', 'requires', 'references'
    notes TEXT,
    PRIMARY KEY (task_id, depends_on_task_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (depends_on_task_id) REFERENCES tasks(id)
);

-- Session tracking (for continuity across Claude sessions)
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    agent_type TEXT,                  -- 'general', 'lexer_specialist', 'parser_specialist', etc.
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    actions_taken TEXT,               -- Summary of what was done
    files_modified TEXT,              -- JSON array of file paths
    tests_added INT DEFAULT 0,
    token_usage INT,                  -- Approximate token count
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- Test results (track test suite growth)
CREATE TABLE test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    test_file TEXT NOT NULL,
    test_name TEXT NOT NULL,
    status TEXT NOT NULL,             -- 'pass', 'fail', 'skip'
    execution_time REAL,              -- Seconds
    error_message TEXT,
    run_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- Code artifacts (generated/modified code)
CREATE TABLE code_artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    artifact_type TEXT NOT NULL,      -- 'function', 'class', 'test', 'module'
    name TEXT NOT NULL,               -- Function/class/test name
    code TEXT NOT NULL,               -- The actual code
    line_start INT,
    line_end INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- Agent memory (decisions, rationale, learned patterns)
CREATE TABLE agent_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,                     -- NULL if global memory
    memory_type TEXT NOT NULL,        -- 'decision', 'pattern', 'pitfall', 'optimization'
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    relevance_score INT DEFAULT 5,    -- 1-10
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- Indexes for fast queries
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_phase ON tasks(phase);
CREATE INDEX idx_task_context_task_id ON task_context(task_id);
CREATE INDEX idx_task_context_type ON task_context(context_type);
CREATE INDEX idx_sessions_task_id ON sessions(task_id);
CREATE INDEX idx_test_results_task_id ON test_results(task_id);
CREATE INDEX idx_code_artifacts_task_id ON code_artifacts(task_id);
```

---

## Python Helper Script (`db_manager.py`)

```python
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class TaskContextDB:
    def __init__(self, db_path: str = "tasks.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def get_task_context(self, task_id: str) -> Dict:
        """Get all context needed for a specific task (minimal token usage)"""
        # Get task details
        task = self.cursor.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

        if not task:
            return {"error": f"Task {task_id} not found"}

        # Get relevant context snippets (sorted by relevance)
        context = self.cursor.execute(
            """SELECT context_type, content, file_path, line_start, line_end, relevance
               FROM task_context
               WHERE task_id = ?
               ORDER BY relevance DESC, created_at ASC""",
            (task_id,)
        ).fetchall()

        # Get dependencies
        dependencies = self.cursor.execute(
            """SELECT d.depends_on_task_id, t.title, t.status, d.dependency_type
               FROM task_dependencies d
               JOIN tasks t ON d.depends_on_task_id = t.id
               WHERE d.task_id = ?""",
            (task_id,)
        ).fetchall()

        # Get previous session notes
        sessions = self.cursor.execute(
            """SELECT actions_taken, files_modified, error_message
               FROM sessions
               WHERE task_id = ?
               ORDER BY start_time DESC
               LIMIT 3""",
            (task_id,)
        ).fetchall()

        return {
            "task": dict(task),
            "context": [dict(c) for c in context],
            "dependencies": [dict(d) for d in dependencies],
            "recent_sessions": [dict(s) for s in sessions]
        }

    def update_task_progress(self, task_id: str, progress: int, status: str = None):
        """Update task progress and status"""
        updates = ["progress = ?", "updated_at = ?"]
        params = [progress, datetime.now()]

        if status:
            updates.append("status = ?")
            params.append(status)
            if status == "completed":
                updates.append("completed_at = ?")
                params.append(datetime.now())

        params.append(task_id)
        self.cursor.execute(
            f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?",
            params
        )
        self.conn.commit()

    def add_context_snippet(self, task_id: str, context_type: str,
                           content: str, file_path: str = None,
                           line_start: int = None, line_end: int = None,
                           relevance: int = 5):
        """Add a context snippet for a task"""
        self.cursor.execute(
            """INSERT INTO task_context
               (task_id, context_type, content, file_path, line_start, line_end, relevance)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (task_id, context_type, content, file_path, line_start, line_end, relevance)
        )
        self.conn.commit()

    def log_session(self, task_id: str, agent_type: str, actions: str,
                    files_modified: List[str], tests_added: int = 0,
                    success: bool = True, error_message: str = None):
        """Log an agent session"""
        self.cursor.execute(
            """INSERT INTO sessions
               (task_id, agent_type, actions_taken, files_modified,
                tests_added, end_time, success, error_message)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (task_id, agent_type, actions, json.dumps(files_modified),
             tests_added, datetime.now(), success, error_message)
        )
        self.conn.commit()

    def get_next_task(self, phase: int = None) -> Optional[Dict]:
        """Get the next pending/in_progress task (highest priority)"""
        query = """
            SELECT t.*
            FROM tasks t
            LEFT JOIN task_dependencies d ON t.id = d.task_id
            LEFT JOIN tasks dep ON d.depends_on_task_id = dep.id
            WHERE t.status IN ('pending', 'in_progress')
            AND (dep.status = 'completed' OR dep.id IS NULL)
        """
        params = []

        if phase:
            query += " AND t.phase = ?"
            params.append(phase)

        query += " ORDER BY t.priority DESC, t.created_at ASC LIMIT 1"

        task = self.cursor.execute(query, params).fetchone()
        return dict(task) if task else None

    def add_agent_memory(self, memory_type: str, title: str, content: str,
                        task_id: str = None, relevance: int = 5):
        """Store agent learning/decision for future reference"""
        self.cursor.execute(
            """INSERT INTO agent_memory
               (task_id, memory_type, title, content, relevance_score)
               VALUES (?, ?, ?, ?, ?)""",
            (task_id, memory_type, title, content, relevance)
        )
        self.conn.commit()

    def search_memory(self, query: str, limit: int = 5) -> List[Dict]:
        """Search agent memory for relevant patterns/decisions"""
        results = self.cursor.execute(
            """SELECT * FROM agent_memory
               WHERE title LIKE ? OR content LIKE ?
               ORDER BY relevance_score DESC, created_at DESC
               LIMIT ?""",
            (f"%{query}%", f"%{query}%", limit)
        ).fetchall()
        return [dict(r) for r in results]

    def export_task_summary_markdown(self, output_file: str = "taskSummary.md"):
        """Export current state to markdown for human review"""
        tasks = self.cursor.execute(
            "SELECT * FROM tasks ORDER BY phase, id"
        ).fetchall()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Task Summary (Auto-generated from Database)\n\n")

            current_phase = None
            for task in tasks:
                if task['phase'] != current_phase:
                    current_phase = task['phase']
                    f.write(f"\n## Phase {current_phase}\n\n")

                status_emoji = {
                    'completed': '✅',
                    'in_progress': '🔵',
                    'pending': '⏳',
                    'blocked': '🔴'
                }.get(task['status'], '⚪')

                f.write(f"### {status_emoji} Task {task['id']}: {task['title']} ({task['progress']}%)\n")
                if task['description']:
                    f.write(f"{task['description']}\n\n")

    def close(self):
        self.conn.close()

# Example usage
if __name__ == "__main__":
    db = TaskContextDB()

    # Get context for task 2.3
    context = db.get_task_context("2.3")
    print(json.dumps(context, indent=2))

    # Update progress
    db.update_task_progress("2.3", 50, "in_progress")

    # Log a session
    db.log_session(
        task_id="2.3",
        agent_type="parser_specialist",
        actions="Implemented if/while statement parsing, added 15 tests",
        files_modified=["src/parser/statement_parser.py", "tests/test_statements.py"],
        tests_added=15
    )

    db.close()
```

---

## Specialized AI Agent Types

### 1. **Task Orchestrator Agent** (`orchestrator`)
**Purpose:** Manages task queue, assigns work to specialized agents, tracks overall progress

**Query Pattern:**
```python
# Get next available task
next_task = db.get_next_task(phase=2)

# Get task dependencies
dependencies = db.get_task_dependencies(next_task['id'])

# Assign to specialist agent based on task type
agent_type = determine_agent_type(next_task)
```

**Responsibilities:**
- ✅ Reads current project state from database
- ✅ Determines next task based on dependencies + priority
- ✅ Spawns specialist agent with minimal context
- ✅ Monitors agent progress
- ✅ Updates task status/progress in database

---

### 2. **Lexer Specialist Agent** (`lexer_specialist`)
**Purpose:** Implements lexer tasks (Phase 1)

**Context Query:**
```python
context = db.get_task_context("1.5")  # Operator tokenization
# Returns: Token.py excerpt, EBNF operators, test examples, prior session notes
```

**Responsibilities:**
- ✅ Reads only lexer-related context
- ✅ Implements token recognition logic
- ✅ Writes unit tests
- ✅ Logs progress back to database
- ✅ Stores code artifacts (functions written)

---

### 3. **Parser Specialist Agent** (`parser_specialist`)
**Purpose:** Implements parser tasks (Phase 2)

**Context Query:**
```python
context = db.get_task_context("2.3")  # Statement parsing
# Returns: AST node definitions, EBNF grammar for statements, lexer token types, examples
```

**Responsibilities:**
- ✅ Reads parser-specific context (AST nodes, grammar)
- ✅ Implements parsing logic (recursive descent, precedence climbing)
- ✅ Writes parser tests
- ✅ Updates task progress after each statement type

---

### 4. **Test Writer Agent** (`test_writer`)
**Purpose:** Generates comprehensive test cases for completed features

**Context Query:**
```python
# Get code artifacts for task
artifacts = db.get_code_artifacts("2.2")
# Get test coverage gaps
coverage = db.get_test_coverage("2.2")
```

**Responsibilities:**
- ✅ Reads function/class definitions
- ✅ Generates edge case tests
- ✅ Ensures test coverage targets met
- ✅ Logs test results to database

---

### 5. **Documentation Agent** (`doc_writer`)
**Purpose:** Generates/updates documentation from code + task context

**Context Query:**
```python
# Get all completed tasks in phase
completed = db.get_tasks_by_status("completed", phase=2)
# Get code artifacts
artifacts = db.get_all_code_artifacts(phase=2)
```

**Responsibilities:**
- ✅ Generates API documentation
- ✅ Updates CLAUDE.md with progress
- ✅ Creates usage examples
- ✅ Exports markdown summaries

---

### 6. **Debugger Agent** (`debugger`)
**Purpose:** Investigates test failures, fixes bugs

**Context Query:**
```python
# Get failed tests
failures = db.get_failed_tests("2.3")
# Get related code artifacts
code = db.get_code_artifacts("2.3")
# Get agent memory (known pitfalls)
pitfalls = db.search_memory("common parser errors")
```

**Responsibilities:**
- ✅ Reads test failure logs
- ✅ Analyzes code for bugs
- ✅ Fixes errors
- ✅ Logs bug patterns to agent memory

---

### 7. **Refactor Agent** (`refactor_specialist`)
**Purpose:** Improves code quality, removes duplication

**Context Query:**
```python
# Get code artifacts with low quality score
code = db.get_code_artifacts_needing_refactor()
# Get agent memory (best practices)
patterns = db.search_memory("design patterns")
```

**Responsibilities:**
- ✅ Identifies code smells
- ✅ Refactors without breaking tests
- ✅ Logs refactoring decisions to memory

---

### 8. **Integration Agent** (`integrator`)
**Purpose:** Combines completed tasks into cohesive system

**Context Query:**
```python
# Get all completed phase 2 tasks
tasks = db.get_tasks_by_status("completed", phase=2)
# Get integration tests
tests = db.get_integration_tests(phase=2)
```

**Responsibilities:**
- ✅ Combines lexer + parser modules
- ✅ Writes integration tests
- ✅ Ensures end-to-end functionality

---

### 9. **Performance Agent** (`perf_optimizer`)
**Purpose:** Profiles code, optimizes bottlenecks

**Context Query:**
```python
# Get code artifacts with high execution time
slow_code = db.get_slow_functions()
# Get agent memory (optimization patterns)
opts = db.search_memory("performance optimization")
```

**Responsibilities:**
- ✅ Profiles code execution
- ✅ Identifies bottlenecks
- ✅ Implements optimizations
- ✅ Logs optimization decisions

---

## Agent Workflow Example

### Scenario: Implement Task 2.3 (Statement Parsing)

```python
# 1. Orchestrator spawns parser specialist
orchestrator = TaskOrchestratorAgent(db)
next_task = orchestrator.get_next_task()  # Returns task 2.3

# 2. Parser specialist gets minimal context
parser = ParserSpecialistAgent(db)
context = parser.get_context("2.3")
"""
Context returned (500 tokens instead of 5000):
- Task: "Implement if/while/for statement parsing"
- Code snippet: ASTNode definitions (50 lines)
- Code snippet: Lexer token types (30 lines)
- EBNF grammar: Statement production rules (20 lines)
- Example: if statement AST structure
- Dependency: Task 2.1 completed (AST nodes available)
- Previous session: "Attempted if parsing, got indent error"
"""

# 3. Parser specialist works on task
parser.implement_statement_parsing()
parser.write_tests()
parser.log_session(
    actions="Implemented if/while/for parsing, added 18 tests",
    files_modified=["src/parser/statement_parser.py", "tests/test_statements.py"],
    tests_added=18
)
parser.update_progress("2.3", 100, "completed")

# 4. Test writer validates
test_writer = TestWriterAgent(db)
test_writer.verify_coverage("2.3")  # Ensures 18 tests cover edge cases

# 5. Documentation agent updates
doc_writer = DocumentationAgent(db)
doc_writer.update_task_summary()  # Exports taskSummary.md from DB
```

---

## Benefits Over Pure Markdown

| Feature | Markdown Files | Database System |
|---------|---------------|-----------------|
| **Context Size** | 5000+ tokens per task | 200-500 tokens (query only what's needed) |
| **Agent Specialization** | Agent reads entire spec | Agent gets task-specific context only |
| **Progress Tracking** | Manual updates, inconsistent | Automatic, queryable, time-stamped |
| **Session Continuity** | "Read taskSummary.md every session" | Query: `get_incomplete_tasks()` |
| **Dependency Management** | Manual tracking in markdown | SQL relationships, auto-validation |
| **Test Coverage** | Count manually in markdown | Query: `get_test_count_by_task()` |
| **Agent Memory** | Lost between sessions | Persistent in `agent_memory` table |
| **Search** | Grep/manual reading | SQL queries, indexed |
| **Hallucination Risk** | High (too much context) | Low (minimal, focused context) |
| **Token Usage** | 5-10K tokens per task | 500-1K tokens per task |

---

## Migration from Markdown to Database

```python
def migrate_from_markdown(md_file: str, db_path: str):
    """Parse taskSummary.md and populate database"""
    db = TaskContextDB(db_path)

    # Parse markdown (custom parser based on task format)
    tasks = parse_task_markdown(md_file)

    for task in tasks:
        db.cursor.execute(
            """INSERT INTO tasks
               (id, phase, title, description, status, progress, estimated_tests)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (task['id'], task['phase'], task['title'], task['description'],
             task['status'], task['progress'], task['estimated_tests'])
        )

    db.conn.commit()
    print(f"Migrated {len(tasks)} tasks to database")
```

---

## MCP (Model Context Protocol) Integration

**Why MCP?** Following Taskr's proven approach, embed guidance directly into tool responses instead of separate CLAUDE.md files.

### MCP Server Implementation

```typescript
// fusion-task-server/src/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import sqlite3 from "sqlite3";

const server = new Server(
  {
    name: "fusion-task-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Tool: Get next task with embedded guidance
server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "get_next_task",
      description: "Get next available task with embedded context and guidance",
      inputSchema: {
        type: "object",
        properties: {
          phase: { type: "number", description: "Compiler phase (1=Lexer, 2=Parser, etc.)" },
          agent_type: { type: "string", description: "Agent type requesting task" }
        }
      }
    },
    {
      name: "update_task_progress",
      description: "Update task progress and status",
      inputSchema: {
        type: "object",
        properties: {
          task_id: { type: "string" },
          progress: { type: "number", minimum: 0, maximum: 100 },
          status: { type: "string", enum: ["pending", "in_progress", "completed", "blocked"] }
        },
        required: ["task_id", "progress"]
      }
    },
    {
      name: "log_session",
      description: "Log completed work session",
      inputSchema: {
        type: "object",
        properties: {
          task_id: { type: "string" },
          actions: { type: "string" },
          files_modified: { type: "array", items: { type: "string" } },
          tests_added: { type: "number" }
        },
        required: ["task_id", "actions", "files_modified"]
      }
    }
  ]
}));

// Tool implementation with embedded guidance
server.setRequestHandler("tools/call", async (request) => {
  if (request.params.name === "get_next_task") {
    const { phase, agent_type } = request.params.arguments;
    const task = await getNextTask(phase);

    if (!task) {
      return { content: [{ type: "text", text: "No tasks available" }] };
    }

    // Get context snippets
    const context = await getTaskContext(task.id);

    // Build response with embedded guidance
    const guidance = buildGuidanceForTask(task, agent_type);

    return {
      content: [{
        type: "text",
        text: `
## Task ${task.id}: ${task.title}

**Status:** ${task.status} (${task.progress}%)
**Phase:** ${task.phase}
**Estimated Tests:** ${task.estimated_tests}

### Description
${task.description}

### Context
${context.map(c => `**${c.context_type}:** ${c.file_path || ''}
\`\`\`
${c.content}
\`\`\`
`).join('\n')}

### Guidance for ${agent_type}
${guidance}

### Dependencies
${await getDependencyInfo(task.id)}

### Previous Sessions
${await getRecentSessions(task.id)}

**IMPORTANT:**
- Update progress using update_task_progress after each milestone
- Log your session using log_session when complete
- Add code artifacts and test results as you work
        `
      }]
    };
  }

  // Handle other tools...
});

function buildGuidanceForTask(task, agent_type) {
  const baseGuidance = `
1. Read all context snippets before starting
2. Follow existing code patterns (check context_type='pattern')
3. Write tests FIRST if this is a new feature
4. Update progress every 25% (0% -> 25% -> 50% -> 75% -> 100%)
5. Log session details when complete
  `;

  const agentGuidance = {
    "parser_specialist": `
**Parser-Specific Rules:**
- Use recursive descent parsing for statements
- Use precedence climbing for expressions (already implemented in task 2.2)
- Every parsing function should return an AST node (defined in task 2.1)
- Handle all three block styles: indentation, braces, End keywords
- Add error recovery (don't crash on invalid syntax)
- Write at least 3 tests per statement type: valid case, edge case, error case
    `,
    "lexer_specialist": `
**Lexer-Specific Rules:**
- Token definitions are in src/lexer/Token.py (frozen dataclass)
- Track SourceLocation for error messages
- Handle whitespace and indentation (see task 1.2)
- Respect block style detection (see task 1.3)
- Add tests for: valid input, edge cases, error conditions
    `,
    "test_writer": `
**Test Writing Rules:**
- Use pytest framework
- Each test should be self-contained
- Test naming: test_<feature>_<condition>_<expected>
- Cover: happy path, edge cases, error conditions
- Minimum 80% code coverage for the module
    `
  };

  return baseGuidance + (agentGuidance[agent_type] || "");
}
```

### Claude Code Configuration

Add to `.claude/mcp.json`:
```json
{
  "mcpServers": {
    "fusion-tasks": {
      "command": "node",
      "args": ["d:/Dropbox/Fusion/mcp-server/build/index.js"],
      "env": {
        "FUSION_DB_PATH": "d:/Dropbox/Fusion/tasks.db"
      }
    }
  }
}
```

### Usage in Claude Code

```
# Claude automatically sees MCP tools
User: "Continue working on the compiler"

Claude: Let me check what task is next...
[Calls mcp__fusion-tasks__get_next_task with phase=2, agent_type="parser_specialist"]

[MCP returns task 2.3 with full context + embedded guidance]

Claude: I see task 2.3 (Statement Parsing) is next. The embedded context shows:
- AST node definitions from task 2.1 (53 lines)
- Lexer tokens available (30 lines)
- EBNF grammar for statements (20 lines)
- Parser guidance: Use recursive descent, handle 3 block styles

Let me start implementing if statement parsing...
[Works on task]
[Calls mcp__fusion-tasks__update_task_progress: task_id="2.3", progress=50]
[Calls mcp__fusion-tasks__log_session when complete]
```

### Benefits of MCP Approach

| Feature | CLAUDE.md Approach | MCP Tool Approach |
|---------|-------------------|-------------------|
| **Guidance Delivery** | Hope Claude reads file | Embedded in every tool response |
| **Context Freshness** | Manual updates to .md | Live query from database |
| **Rule Enforcement** | Suggestions only | Can validate before returning |
| **Cross-Device Sync** | Git commit required | Automatic (database) |
| **Agent Specialization** | Generic instructions | Task-type-specific guidance |
| **Progress Tracking** | Manual updates | Forced via tool schema |
| **Drift Prevention** | Relies on Claude memory | Database enforces state |

---

## Future Enhancements

1. **Web Dashboard** - Flask app to visualize task progress, agent sessions
2. **Agent Collaboration** - Multiple agents work on different tasks simultaneously (via MCP server)
3. **Context Embeddings** - Use vector similarity to find relevant context automatically
4. **Auto-Repair** - If test fails, debugger agent spawns automatically (triggered by MCP)
5. **Rollback System** - Version control for code artifacts in database
6. **Cost Tracking** - Track API token usage per agent/task
7. **MCP Tool Chaining** - One MCP tool can call another (e.g., get_task → add_context → update_progress)
8. **Real-time Collaboration** - Multiple Claude instances work on different tasks via shared MCP server

---

## Usage in Fusion Project

**When to implement:** After MVP compiler is complete (Phase 5+)

**Migration steps:**
1. Create `tasks.db` from current `taskSummary.md`
2. Run `db_manager.py` to populate context snippets from code
3. Update CLAUDE.md to reference database instead of markdown
4. Train orchestrator agent to manage task queue
5. Deploy specialist agents for maintenance/enhancements

**Benefit:** Self-sustaining compiler development with minimal human intervention

---

## Comparison: Taskr vs. Fusion Task System

| Feature | Taskr (General SaaS) | Fusion Task System (Compiler-Specific) |
|---------|---------------------|----------------------------------------|
| **Target Use Case** | Any software project | Compiler development (Fusion) |
| **Task Types** | Setup/Analysis/Implementation/Validation/Testing | Phase-specific (Lexer/Parser/Semantic/Codegen) |
| **Context Storage** | Notes (FILE_LIST, PROGRESS, CONTEXT, FINDING) | Code snippets with line numbers, EBNF grammar, test patterns |
| **Agent Types** | Generic AI agents | Specialized (Lexer/Parser/Test/Debug/Refactor) |
| **Database** | Cloud-hosted (sync across devices) | Local SQLite (version controlled with code) |
| **MCP Integration** | Built-in MCP server | Custom MCP server (fusion-task-server) |
| **PRD Parsing** | AI-powered task generation from PRD | Manual task breakdown (compiler phases predefined) |
| **Test Tracking** | Generic test status | Test count per task, pytest integration, coverage tracking |
| **Code Artifacts** | File tracking only | Function/class/test storage with line ranges |
| **Agent Memory** | Session notes | Pattern/pitfall/optimization learning across phases |
| **Cost** | Paid SaaS (beta free) | Free (local, open-source) |

**When to use Taskr:**
- ✅ Multi-developer team needing cloud sync
- ✅ General web/mobile app development
- ✅ Want PRD → task hierarchy automation
- ✅ Need web dashboard out-of-the-box

**When to use Fusion Task System:**
- ✅ Solo compiler developer (or small team with git)
- ✅ Need compiler-specific context (EBNF, AST, tokens)
- ✅ Want local control over database schema
- ✅ Building specialized AI agents for compiler phases
- ✅ Want to learn MCP server development

**Hybrid Approach:** Use Taskr for general project management + Fusion Task System for detailed compiler context

---

## See Also

### Internal Documentation
- [taskSummary.md](taskSummary.md) - Current markdown-based task tracking
- [CLAUDE.md](CLAUDE.md) - Current session instructions for Claude
- [FutureFeatures.md](FutureFeatures.md) - Post-MVP enhancements
- [fusion.ebnf](files/fusion.ebnf) - Grammar specification (used in task context)
- [fusion-language-spec.md](files/fusion-language-spec.md) - Language reference

### External Resources
- [Taskr.one](https://taskr.one) - Production task management system (inspiration)
- [Reddit Discussion](https://www.reddit.com/r/ClaudeAI/comments/1p3io5m/i_built_a_task_system_that_survives_claude/) - Real-world problem validation
- [MCP Specification](https://modelcontextprotocol.io) - Model Context Protocol docs
- [Claude Code MCP Guide](https://docs.anthropic.com/claude-code/mcp) - MCP integration guide

---

**Created:** 2025-11-25
**Status:** 🔮 Proposal (not yet implemented)
**Estimated Implementation Time:** 20-30 hours (after MVP compiler complete)
**Estimated ROI:** 10x reduction in context token usage, 5x faster task context switching
