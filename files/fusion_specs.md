# Fusion Specifications, Templates, and Configurations

Description: Complete reference for JSON configurations, language templates, and project settings.

---

## Table of Contents

* JSON Configuration Specifications
* Language Templates
* Configuration Reference
* Safety Modes and Annotations
* Environment Variables
* CLI Commands

---

## JSON Configuration Specifications

Description: All configuration file formats and structures.

---

### fusion.project.json

Description: Project-wide settings (required for all projects).

```json
{
  "project": {
    "name": "MyFusionProject",
    "version": "1.0.0",
    "description": "A Fusion language project",
    "author": "Your Name",
    "license": "MIT",
    "fusionVersion": "1.0.0",
    "projectType": "application"
  },
  
  "build": {
    "outputDirectory": "./build",
    "targetPlatform": "windows-x64",
    "buildType": "release",
    "optimization": "speed"
  },
  
  "compiler": {
    "strictMode": true,
    "unsafeMode": false,
    "warningsAsErrors": false,
    "optimizationLevel": 2,
    "parallelCompilation": true
  },
  
  "language": {
    "allowWeakPointers": false,
    "allowGoto": false,
    "enforceNullChecks": true,
    "requireExplicitTypes": false,
    "enforceCodingStandards": true
  },
  
  "loop": {
    "autoProtection": true,
    "defaultMaxIterations": 1000000,
    "enableThreadInterrupts": true,
    "adaptToSystemResources": true
  },
  
  "memory": {
    "defaultMode": "gc",
    "enableSmartPointers": true,
    "enableRawPointers": false,
    "gcMaxHeapSize": "512MB"
  },
  
  "threading": {
    "enableChannels": true,
    "enableSharedMemory": true,
    "enableAutoLocking": true,
    "maxThreads": 8,
    "enableRaceDetection": true
  },
  
  "standardLibrary": {
    "includeAll": true,
    "fileFormats": { "json": true, "xml": true, "csv": true },
    "networking": true,
    "graphics": true,
    "audio": true
  },
  
  "syntax": {
    "commentStyle": "doubleSlash",
    "enumStyle": "auto",
    "allowSpreadOperator": true,
    "comparisonOperator": "both"
  },
  
  "testing": {
    "testDirectory": "./tests",
    "enableUnitTests": true,
    "coverageThreshold": 80
  }
}
```

---

### fusion.users.json

Description: User roles and permissions for multi-user projects.

```json
{
  "users": {
    "version": "1.0.0",
    "defaultRole": "developer"
  },
  
  "roles": {
    "owner": {
      "permissions": {
        "read": ["*"], "write": ["*"], "delete": ["*"],
        "build": true, "deploy": true, "manageUsers": true
      }
    },
    "admin": {
      "permissions": {
        "read": ["*"], "write": ["*"], "delete": ["*"],
        "build": true, "deploy": true, "manageUsers": true
      },
      "restrictions": { "cannotModify": ["fusion.project.json"] }
    },
    "developer": {
      "permissions": {
        "read": ["./src/**", "./tests/**"],
        "write": ["./src/**", "./tests/**"],
        "build": true, "deploy": false
      },
      "restrictions": {
        "requiresReview": ["./src/core/**"]
      }
    },
    "reviewer": {
      "permissions": {
        "read": ["*"], "write": [], "build": true
      },
      "canReview": true
    },
    "viewer": {
      "permissions": {
        "read": ["./src/**", "./docs/**"],
        "write": [], "build": false
      }
    }
  },
  
  "userList": [
    {
      "id": "user-001",
      "username": "owner",
      "role": "owner",
      "active": true
    }
  ]
}
```

---

### fusion.user.json

Description: Individual user preferences and IDE settings.

```json
{
  "user": {
    "id": "user-001",
    "username": "developer",
    "displayName": "Developer Name"
  },
  
  "editor": {
    "theme": "dark",
    "fontSize": 14,
    "fontFamily": "Fira Code",
    "tabSize": 4,
    "insertSpaces": true,
    "wordWrap": "on",
    "lineNumbers": true
  },
  
  "syntax": {
    "preferredCommentStyle": "doubleSlash",
    "preferredEnumStyle": "indentation",
    "useBraces": false
  },
  
  "formatting": {
    "formatOnSave": true,
    "trimTrailingWhitespace": true,
    "insertFinalNewline": true
  },
  
  "intellisense": {
    "enabled": true,
    "autoComplete": true,
    "showSnippets": true
  },
  
  "keyboard": {
    "shortcuts": {
      "build": "Ctrl+Shift+B",
      "run": "F5",
      "format": "Shift+Alt+F"
    }
  }
}
```

---

### fusion.file.json

Description: File-specific overrides (optional).

```json
{
  "file": {
    "path": "./src/Example.fusion",
    "encoding": "utf-8"
  },
  
  "overrides": {
    "compiler": {
      "strictMode": false,
      "optimizationLevel": 3
    },
    "loop": {
      "defaultMaxIterations": 10000000
    }
  },
  
  "metadata": {
    "author": "John Doe",
    "tags": ["core", "performance"],
    "category": "gameplay"
  }
}
```

---

## Language Templates

Description: Syntax templates for all Fusion constructs.

**Notation**:
* `<type>` - Type placeholder (int, string, etc.)
* `<name>` - Identifier placeholder
* `{}` - Optional element
* `...` - Repetition/variadic
* **Note**: In syntax examples, `{= defaultValue}` indicates optional default values. The curly braces are notation only, not actual syntax.

---

### Variable Templates

```fusion
// Basic declaration
<type> <name> = <value>

// Type inference
var <name> = <value>

// Constant
const <type> <name> = <value>
```

---

### Function Templates

```fusion
// Basic function
<returnType> function <name>(<type> <param> {= <default>})
    <body>

// Variadic function
<returnType> function <name>(<type>... <params>)
    <body>

// Main function (application entry point)
void function main(string... args)
    <body>

// Function with error return (multiple returns)
<returnType>, Error function <name>(<type> <param>)
    if <errorCondition>
        return <defaultValue>, Error("<message>")
    return <result>, null
```

---

### Lambda Templates

```fusion
// Single-line lambda (variable holds function)
<returnType> <variableName>(<type> <param> {= <default>}) : <expression>

// Multi-line lambda (indentation)
<returnType> <variableName>(<type> <param>) :
    <statement>
    <statement>
    return <value>

// Multi-line lambda (braces)
<returnType> <variableName>(<type> <param>) : {
    <statement>
    return <value>
}

// With func keyword (optional)
<returnType> <variableName> = func(<type> <param>) : <expression>

// With function keyword (optional)
<returnType> <variableName> = function(<type> <param>) : <expression>

// Function type annotation (for parameters)
(<type>, <type>) : <returnType>           // Default syntax
(<type>, <type>) -> <returnType>          // Alternative syntax (both work)
```

---

### Enum Templates

```fusion
// Braces style
Enum <name> {
    <VALUE1>,
    <VALUE2>
}

// Indentation style
Enum <name>
    <VALUE1>
    <VALUE2>

// Single-line style
Enum <name>: <VALUE1>, <VALUE2>, <VALUE3>
```

---

### Class Templates

```fusion
// Basic class
class <name>
    <type> <field>
    
    constructor(<params>)
        <initialization>
    
    <returnType> function <methodName>(<params>)
        <body>

// Static method
public static <returnType> function <name>(<params>)
    <body>

// Constant (automatically static)
public const <type> <NAME> = <value>
```

---

### Control Flow Templates

```fusion
// If statement
if <condition>
    <body>
elif <condition>
    <body>
else
    <body>

// For loop with range
for <var> in <start>...<end>
    <body>
end loop

// While loop
while <condition>
    <body>
end loop

// Match statement
match <value>
    case <pattern>:
        <body>
    else:
        <body>
```

---

### Comment Templates

```fusion
// Single-line comment (double slash)
// <comment>

' Single-line comment (single quote)
' <comment>

/* Multi-line comment */
/* <comment>
   <comment> */

// Region
#Region <description>
<code>
#End Region
```

---

## Configuration Reference

Description: Detailed settings explanation.

---

### Compiler Settings

Setting | Type | Default | Description
---|---|---|---
strictMode | bool | true | Maximum safety enforcement
unsafeMode | bool | false | Allow unsafe operations
warningsAsErrors | bool | false | Treat warnings as errors
optimizationLevel | 0-3 | 2 | 0=none, 3=aggressive
parallelCompilation | bool | true | Compile files in parallel

---

### Language Settings

Setting | Type | Default | Description
---|---|---|---
allowWeakPointers | bool | false | Allow Weak<T> pointers
allowGoto | bool | false | Allow goto statements
enforceNullChecks | bool | true | Require null checks
requireExplicitTypes | bool | false | Disable type inference
enforceCodingStandards | bool | true | Enforce naming conventions

---

### Loop Settings

Setting | Type | Default | Description
---|---|---|---
autoProtection | bool | true | Automatic loop safety
defaultMaxIterations | int | 1000000 | Default iteration limit
enableThreadInterrupts | bool | true | Check for interrupts
adaptToSystemResources | bool | true | Adjust based on RAM/CPU

---

### Memory Settings

Setting | Type | Default | Description
---|---|---|---
defaultMode | enum | gc | gc, smart-pointers, raw-pointers
enableSmartPointers | bool | true | Allow Unique/Shared pointers
enableRawPointers | bool | false | Allow raw pointers (unsafe)
gcMaxHeapSize | string | 512MB | Maximum garbage collector heap

---

### Threading Settings

Setting | Type | Default | Description
---|---|---|---
enableChannels | bool | true | Enable Go-style channels
enableSharedMemory | bool | true | Allow shared memory with locks
enableAutoLocking | bool | true | Compiler inserts locks automatically
maxThreads | int | 8 | Maximum concurrent threads
enableRaceDetection | bool | true | Detect race conditions

---

## Safety Modes

Description: Three compilation modes with different safety levels.

---

### Standard Mode (Default)

**Features**:
* Balanced safety and flexibility
* Warnings for potential issues
* Type inference allowed
* Weak pointers with warning
* Automatic loop protection

**Configuration**:
```json
{
  "compiler": { "strictMode": false, "unsafeMode": false }
}
```

---

### Strict Mode

**Features**:
* Maximum safety enforcement
* All warnings become errors
* No weak pointers (compilation error)
* No type inference (explicit types required)
* Required null checks before use
* No callbacks when performance is more important (compilation error)

**Configuration**:
```json
{
  "compiler": { "strictMode": true, "warningsAsErrors": true },
  "language": {
    "allowWeakPointers": false,
    "requireExplicitTypes": true,
    "enforceNullChecks": true
  }
}
```

**Best For**: Production code, enterprise applications

---

### Unsafe Mode

**Features**:
* Minimal restrictions
* Raw pointers allowed
* Manual memory management
* goto statements enabled
* No automatic protections

**Configuration**:
```json
{
  "compiler": { "unsafeMode": true },
  "memory": { "enableRawPointers": true },
  "loop": { "autoProtection": false }
}
```

**Best For**: Embedded systems, performance-critical code

---

## Annotations

Description: Code-level metadata and compiler directives.

---

### Built-in Annotations

**@Performance** - Mark performance-critical code
```fusion
@Performance
class GameEngine
    @Performance
    void function update(float dt)
        // Optimized by compiler
```

**@Deprecated** - Mark old code
```fusion
@Deprecated("Use NewClass instead", version = "2.0.0")
class OldClass
```

**@Unsafe** - Explicit unsafe marking
```fusion
@Unsafe
void function directMemoryAccess()
    unsafe
        // Unsafe operations
```

**@NoOptimize** - Prevent optimization
```fusion
@NoOptimize
void function debugCode()
    // Keep as-is for debugging
```

**@Inline** - Suggest inlining
```fusion
@Inline
int function add(int a, int b)
    return a + b
```

**@ThreadSafe** - Thread safety documentation
```fusion
@ThreadSafe
class Counter
    // Thread-safe implementation
```

**@Test** - Test function marker
```fusion
@Test
void function testAddition()
    assert(add(2, 2) == 4)
```

**@NoLoopProtection** - Disable loop safety
```fusion
@NoLoopProtection
void function infiniteLoop()
    while true
        processRequest()
```

**@MaxIterations** - Custom iteration limit
```fusion
@MaxIterations(10000000)
void function heavyComputation()
    for i in 1...50000000
        process(i)
    end loop
```

---

### Custom Annotations

**Definition** (in fusion.project.json):
```json
{
  "annotations": {
    "customAnnotations": {
      "@GameLogic": {
        "enabled": true,
        "description": "Game-specific logic",
        "parameters": {
          "module": "string",
          "priority": "int"
        }
      }
    }
  }
}
```

**Usage**:
```fusion
@GameLogic(module = "combat", priority = 1)
class CombatSystem
```

---

## Environment Variables

Description: System environment variables affecting Fusion.

```bash
# Installation directory
FUSION_HOME=/usr/local/fusion

# User configuration
FUSION_USER_CONFIG=~/.fusion

# Build settings
FUSION_BUILD_TYPE=release
FUSION_TARGET_PLATFORM=linux-x64

# Compiler flags
FUSION_STRICT_MODE=true
FUSION_UNSAFE_MODE=false

# Memory settings
FUSION_MAX_HEAP=1024MB
FUSION_GC_THREADS=4

# Thread settings
FUSION_MAX_THREADS=8
```

---

## CLI Commands

Description: Command-line interface commands.

---

### Build Commands

```bash
# Standard build
fusion build

# Strict mode
fusion build --strict

# Unsafe mode
fusion build --unsafe

# Specific target
fusion build --target=linux-x64

# Release build
fusion build --release
```

---

### Configuration Commands

```bash
# Show current config
fusion config show

# Set value
fusion config set compiler.strictMode true

# Validate configs
fusion validate

# Reset to defaults
fusion config reset
```

---

### Project Commands

```bash
# Create new project
fusion new MyProject

# Initialize in current directory
fusion init

# Add dependency
fusion add FusionMath@2.0.0

# Run tests
fusion test

# Generate documentation
fusion doc
```

---

### User Management Commands

```bash
# List users
fusion users list

# Add user
fusion users add USERNAME ROLE

# Remove user
fusion users remove USERNAME

# Show permissions
fusion users permissions USERNAME
```

---

## Configuration Examples

---

### Game Development

```json
{
  "compiler": {
    "strictMode": false,
    "optimizationLevel": 3
  },
  "memory": {
    "defaultMode": "smart-pointers",
    "gcMaxHeapSize": "2GB"
  },
  "loop": {
    "defaultMaxIterations": 100000000
  }
}
```

---

### Enterprise Application

```json
{
  "compiler": {
    "strictMode": true,
    "warningsAsErrors": true
  },
  "language": {
    "allowWeakPointers": false,
    "enforceNullChecks": true,
    "requireExplicitTypes": true
  },
  "testing": {
    "coverageThreshold": 90
  }
}
```

---

### Embedded System

```json
{
  "compiler": {
    "unsafeMode": true,
    "optimizationLevel": 3
  },
  "memory": {
    "defaultMode": "raw-pointers",
    "gcMaxHeapSize": "64MB"
  },
  "loop": {
    "autoProtection": false
  }
}
```

---

## Best Practices

**Project Configuration**:
* Version control fusion.project.json
* Document custom settings
* Use environment variables for secrets
* Keep user preferences out of version control

**Safety Modes**:
* Start with standard mode
* Use strict for production
* Limit unsafe to specific files
* Document all mode changes

**Annotations**:
* Use built-in annotations first
* Don't over-annotate
* Review @Unsafe code thoroughly
* Profile @Performance impact

