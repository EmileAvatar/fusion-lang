# Fusion Project Configuration Specification

Description: Complete configuration file format for Fusion projects including project settings, file configurations, user roles, and preferences.

---

## Configuration Files Overview

Description: Fusion uses multiple configuration files for different scopes.

**File Structure**:
* `fusion.project.json` - Project-wide settings (required)
* `fusion.file.json` - File-specific overrides (optional, per-file)
* `fusion.users.json` - User roles and permissions (multi-user projects)
* `fusion.user.json` - Individual user preferences (per-user)

**File Locations**:
* Project config: `./fusion.project.json` (project root)
* File config: Same directory as source file
* Users config: `./fusion.users.json` (project root)
* User preferences: `~/.fusion/fusion.user.json` (user home)

---

## 1. fusion.project.json

Description: Project-wide configuration file (required for all Fusion projects).

```json
{
  "project": {
    "name": "MyFusionProject",
    "version": "1.0.0",
    "description": "My Fusion project description",
    "author": "Developer Name",
    "license": "MIT",
    "fusionVersion": "1.0.0",
    "projectType": "application",
    "createdDate": "2025-01-15T10:00:00Z",
    "modifiedDate": "2025-01-15T10:00:00Z"
  },
  
  "build": {
    "outputDirectory": "./build",
    "targetPlatform": "windows-x64",
    "buildType": "release",
    "optimization": "speed",
    "enableDebugSymbols": false,
    "generateDocumentation": true,
    "compressionLevel": "medium"
  },
  
  "compiler": {
    "strictMode": true,
    "unsafeMode": false,
    "warningsAsErrors": false,
    "maxWarnings": 100,
    "optimizationLevel": 2,
    "parallelCompilation": true,
    "maxParallelJobs": 4
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
    "enableResourceMonitoring": true,
    "adaptToSystemResources": true
  },
  
  "memory": {
    "defaultMode": "gc",
    "enableSmartPointers": true,
    "enableRawPointers": false,
    "gcMaxHeapSize": "512MB",
    "gcThreads": 2
  },
  
  "threading": {
    "enableChannels": true,
    "enableSharedMemory": true,
    "enableAutoLocking": true,
    "maxThreads": 8,
    "threadPoolSize": 4,
    "enableRaceDetection": true,
    "enableDeadlockDetection": true
  },
  
  "modules": {
    "searchPaths": [
      "./modules",
      "./lib",
      "${FUSION_HOME}/stdlib"
    ],
    "autoImport": [
      "Fusion.Core",
      "Fusion.Collections"
    ]
  },
  
  "standardLibrary": {
    "includeAll": true,
    "fileFormats": {
      "json": true,
      "xml": true,
      "csv": true,
      "yaml": true,
      "ini": true,
      "md": true
    },
    "imageFormats": {
      "png": true,
      "jpeg": true,
      "bmp": true,
      "gif": true
    },
    "languages": {
      "fusion": true,
      "java": false,
      "cpp": false
    },
    "networking": true,
    "graphics": true,
    "audio": true
  },
  
  "codegen": {
    "indentStyle": "spaces",
    "indentSize": 4,
    "lineEndings": "lf",
    "maxLineLength": 120,
    "preferredBraceStyle": "indentation"
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
    "coverageThreshold": 80,
    "parallelTests": true
  },
  
  "dependencies": {
    "packages": {
      "FusionMath": "^2.0.0",
      "FusionGraphics": "^1.5.0"
    }
  }
}
```

---

## 2. fusion.file.json

Description: File-specific overrides (optional, placed in same directory as source file).

```json
{
  "file": {
    "path": "./src/Spaceship.fusion",
    "encoding": "utf-8",
    "generated": false,
    "readOnly": false
  },
  
  "overrides": {
    "compiler": {
      "strictMode": false,
      "optimizationLevel": 3
    },
    "language": {
      "allowWeakPointers": true
    },
    "loop": {
      "defaultMaxIterations": 10000000
    }
  },
  
  "metadata": {
    "author": "John Doe",
    "createdDate": "2025-01-10",
    "tags": ["core", "game", "physics"],
    "category": "gameplay"
  }
}
```

---

## 3. fusion.users.json

Description: User roles and permissions for multi-user projects.

```json
{
  "users": {
    "version": "1.0.0",
    "lastUpdated": "2025-01-15T10:00:00Z",
    "defaultRole": "developer"
  },
  
  "roles": {
    "owner": {
      "name": "Project Owner",
      "permissions": {
        "read": ["*"],
        "write": ["*"],
        "delete": ["*"],
        "build": true,
        "deploy": true,
        "manageUsers": true,
        "manageSettings": true,
        "accessUnsafe": true
      }
    },
    
    "admin": {
      "name": "Administrator",
      "permissions": {
        "read": ["*"],
        "write": ["*"],
        "delete": ["*"],
        "build": true,
        "deploy": true,
        "manageUsers": true,
        "manageSettings": true,
        "accessUnsafe": true
      },
      "restrictions": {
        "cannotModify": ["fusion.project.json"]
      }
    },
    
    "developer": {
      "name": "Developer",
      "permissions": {
        "read": ["./src/**", "./tests/**", "./docs/**"],
        "write": ["./src/**", "./tests/**"],
        "delete": ["./src/**/*.temp"],
        "build": true,
        "deploy": false,
        "manageUsers": false,
        "accessUnsafe": false
      },
      "restrictions": {
        "cannotModify": [
          "fusion.project.json",
          "./src/core/Critical*.fusion"
        ],
        "requiresReview": ["./src/core/**"]
      }
    },
    
    "reviewer": {
      "name": "Code Reviewer",
      "permissions": {
        "read": ["*"],
        "write": [],
        "delete": [],
        "build": true,
        "deploy": false
      },
      "canReview": true,
      "canApprove": true
    },
    
    "viewer": {
      "name": "Read-Only Viewer",
      "permissions": {
        "read": ["./src/**", "./docs/**"],
        "write": [],
        "delete": [],
        "build": false
      }
    },
    
    "contributor": {
      "name": "External Contributor",
      "permissions": {
        "read": ["./src/public/**", "./docs/**"],
        "write": ["./src/public/**"],
        "delete": [],
        "build": true
      },
      "restrictions": {
        "requiresReview": ["./src/public/**"]
      }
    }
  },
  
  "userList": [
    {
      "id": "user-001",
      "username": "john.doe",
      "email": "john.doe@example.com",
      "displayName": "John Doe",
      "role": "owner",
      "active": true,
      "joinedDate": "2025-01-01",
      "lastActive": "2025-01-15"
    },
    {
      "id": "user-002",
      "username": "jane.smith",
      "email": "jane.smith@example.com",
      "displayName": "Jane Smith",
      "role": "admin",
      "active": true,
      "joinedDate": "2025-01-02",
      "customPermissions": {}
    }
  ],
  
  "teams": [
    {
      "id": "team-001",
      "name": "Core Team",
      "description": "Core development team",
      "members": ["user-001", "user-002"],
      "permissions": {
        "read": ["./src/core/**"],
        "write": ["./src/core/**"]
      }
    }
  ]
}
```

---

## 4. fusion.user.json

Description: Individual user preferences (stored per-user).

```json
{
  "user": {
    "id": "user-001",
    "username": "john.doe",
    "displayName": "John Doe",
    "email": "john.doe@example.com"
  },
  
  "editor": {
    "theme": "dark",
    "fontSize": 14,
    "fontFamily": "Fira Code",
    "tabSize": 4,
    "insertSpaces": true,
    "wordWrap": "on",
    "lineNumbers": true,
    "minimap": true
  },
  
  "syntax": {
    "preferredCommentStyle": "doubleSlash",
    "preferredEnumStyle": "indentation",
    "preferredBlockStyle": "indentation",
    "useBraces": false,
    "preferredComparisonOperator": "notEqual"
  },
  
  "formatting": {
    "formatOnSave": true,
    "formatOnPaste": true,
    "insertSpaces": true,
    "tabSize": 4,
    "trimTrailingWhitespace": true,
    "insertFinalNewline": true,
    "maxLineLength": 120
  },
  
  "codeStyle": {
    "namingConvention": {
      "classes": "PascalCase",
      "functions": "camelCase",
      "variables": "camelCase",
      "constants": "UPPER_SNAKE_CASE"
    }
  },
  
  "intellisense": {
    "enabled": true,
    "autoComplete": true,
    "suggestionDelay": 300,
    "showSnippets": true,
    "showParameters": true,
    "showDocumentation": true
  },
  
  "diagnostics": {
    "enableLinting": true,
    "lintOnSave": true,
    "showErrors": true,
    "showWarnings": true,
    "showHints": true
  },
  
  "debug": {
    "showDebugConsole": true,
    "verboseOutput": false,
    "breakOnException": true,
    "enableHotReload": true
  },
  
  "build": {
    "autoSaveBeforeBuild": true,
    "clearConsoleBeforeBuild": true,
    "defaultBuildType": "debug",
    "parallelBuild": true
  },
  
  "git": {
    "enableGit": true,
    "autoFetch": true,
    "confirmSync": true,
    "showInlineBlame": true
  },
  
  "ui": {
    "showWelcomeScreen": true,
    "compactFolders": true,
    "showFileIcons": true,
    "sidebarPosition": "left"
  },
  
  "keyboard": {
    "shortcuts": {
      "build": "Ctrl+Shift+B",
      "run": "F5",
      "format": "Shift+Alt+F",
      "save": "Ctrl+S",
      "find": "Ctrl+F",
      "comment": "Ctrl+/"
    }
  },
  
  "recentProjects": [
    {
      "path": "/projects/spaceship-game",
      "name": "Spaceship Game",
      "lastOpened": "2025-01-15"
    }
  ]
}
```

---

## Configuration Sections Reference

Description: Detailed explanation of all configuration options.

---

### Project Section

Setting | Type | Default | Description
---|---|---|---
name | string | required | Project name
version | string | "1.0.0" | Project version (semantic versioning)
description | string | "" | Project description
author | string | "" | Project author
license | string | "MIT" | Project license
fusionVersion | string | required | Required Fusion language version
projectType | enum | "application" | application, library, game, embedded

---

### Compiler Section

Setting | Type | Default | Description
---|---|---|---
strictMode | boolean | true | Enable strict type checking and null safety
unsafeMode | boolean | false | Allow unsafe code blocks and raw pointers
warningsAsErrors | boolean | false | Treat warnings as compilation errors
optimizationLevel | int (0-3) | 2 | 0=none, 1=basic, 2=full, 3=aggressive
parallelCompilation | boolean | true | Compile multiple files in parallel

---

### Language Section

Setting | Type | Default | Description
---|---|---|---
allowWeakPointers | boolean | false | Allow Weak<T> pointers (discouraged)
allowGoto | boolean | false | Allow goto statements (unsafe mode only)
enforceNullChecks | boolean | true | Force null checks before object use
requireExplicitTypes | boolean | false | Require explicit types (no var)
enforceCodingStandards | boolean | true | Enforce naming and style conventions

---

### Loop Section

Setting | Type | Default | Description
---|---|---|---
autoProtection | boolean | true | Compiler adds loop safety checks
defaultMaxIterations | int | 1000000 | Default iteration limit
enableThreadInterrupts | boolean | true | Check for thread interrupts
enableResourceMonitoring | boolean | true | Monitor RAM/CPU usage
adaptToSystemResources | boolean | true | Adjust limits based on system

---

### Memory Section

Setting | Type | Default | Description
---|---|---|---
defaultMode | enum | "gc" | gc, smart-pointers, raw-pointers
enableSmartPointers | boolean | true | Allow Unique/Shared pointers
enableRawPointers | boolean | false | Allow raw pointers (unsafe mode)
gcMaxHeapSize | string | "512MB" | Maximum heap size for GC
gcThreads | int | 2 | Number of GC threads

---

### Threading Section

Setting | Type | Default | Description
---|---|---|---
enableChannels | boolean | true | Enable Go-style channels
enableSharedMemory | boolean | true | Allow shared memory with locks
enableAutoLocking | boolean | true | Compiler inserts locks automatically
maxThreads | int | 8 | Maximum concurrent threads
enableRaceDetection | boolean | true | Detect race conditions at runtime
enableDeadlockDetection | boolean | true | Detect potential deadlocks

---

### Syntax Section

Setting | Type | Default | Description
---|---|---|---
commentStyle | enum | "doubleSlash" | doubleSlash (//) or singleQuote (')
enumStyle | enum | "auto" | auto, braces, indentation, singleLine
allowSpreadOperator | boolean | true | Enable ... operator
comparisonOperator | enum | "both" | both, notEqual (!=), notEqualAngle (<>)

---

## Role Permissions Reference

Description: Available permissions for user roles.

**Read Permissions**:
* Paths to files/directories user can view
* Wildcards supported: `["./src/**", "./docs/**"]`
* `["*"]` = read everything

**Write Permissions**:
* Paths to files/directories user can edit
* More restrictive than read
* `[]` = no write access

**Delete Permissions**:
* Paths to files user can delete
* Usually most restrictive
* `[]` = no delete access

**Special Permissions**:
* `build` - Can compile project
* `deploy` - Can deploy to production
* `manageUsers` - Can add/remove users
* `manageSettings` - Can edit fusion.project.json
* `accessUnsafe` - Can use unsafe code blocks

---

## Example Configurations

---

### Game Development (Performance Focus)

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
  },
  "standardLibrary": {
    "graphics": true,
    "audio": true
  }
}
```

---

### Enterprise Application (Strict Safety)

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

### Embedded System (Minimal Overhead)

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
  },
  "threading": {
    "maxThreads": 1
  }
}
```

---

## Configuration Validation

**CLI Commands**:
```bash
# Validate project config
fusion validate

# Validate specific file
fusion validate fusion.users.json

# Show current configuration
fusion config show

# Set configuration value
fusion config set compiler.strictMode true

# Reset to defaults
fusion config reset
```

**IDE Integration**:
* Real-time validation
* Auto-complete for settings
* Hover tooltips for descriptions
* Error highlighting

---

## Environment Variables

```bash
FUSION_HOME=/usr/local/fusion
FUSION_USER_CONFIG=~/.fusion
FUSION_PROJECT_CONFIG=./custom.json
FUSION_STRICT_MODE=true
FUSION_MAX_HEAP=1024MB
```

---

## Configuration Best Practices

**Project Configuration**:
* Version control fusion.project.json
* Use comments (JSON with comments supported)
* Document custom settings
* Keep defaults when possible

**User Roles**:
* Use principle of least privilege
* Require code review for critical files
* Regularly audit permissions
* Use teams for group permissions

**User Preferences**:
* Don't version control user.json
* Sync across machines if desired
* Backup custom settings
* Use workspace-specific overrides

