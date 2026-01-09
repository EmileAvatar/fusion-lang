Notes 
Sectsion below can be set to IGNORE, PLANNED, PARTIAL, DONE
IGNORE - ignore for now
PLANNED - added to FutureFeatures.md
PARTIAL - partially planned/ignored
DONE - done already

---
DONE

this one done already
the icon 🏗️ will be fusion offical icon.
sub folders "icons and images" contain "icons" folder and "images" folder contains varrious icons and images variants. 

![alt text](<icons and Images/icons/building_construction_3d.png>)

also another icon
![alt text](<icons and Images/images/1f3d7.png>)

---
DONE
have a lib that handles IDE syntax checking. 
that handles the various sysntex indenting, {}, keywords

---
PLANNED
regex as code .functionName chaining


Ah! Got it — you want a **more human-readable, fluent API version** of regex, where the **method name reflects the purpose**, not the raw regex symbol. Also, you want an extra column explaining clearly what the pattern does. Here’s a revised table in that style:

| Pattern | Meaning                             | Explanation / What it Does                                  | Example Function / Parameter                          |
| ------- | ----------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------- |
| `.`     | Any single character                | Matches **any one character** except newline                | `.regexAnyChar()`                                     |
| `\d`    | Digit (0–9)                         | Matches **any single digit**                                | `.regexFilterNumbers()` or `.regexFilterNumbers(0,9)` |
| `\w`    | Word character (letters, digits, _) | Matches **letters, numbers, or underscore**                 | `.regexWord()`                                        |
| `\s`    | Whitespace                          | Matches **spaces, tabs, newlines**                          | `.regexRemoveWhiteSpaces()`                           |
| `^`     | Start of string                     | Ensures the match **starts at the beginning of the string** | `.regexStartWith('pattern')`                          |
| `$`     | End of string                       | Ensures the match **ends at the end of the string**         | `.regexEndWith('pattern')`                            |
| `+`     | One or more of preceding element    | Repeats **the previous element one or more times**          | `.regexRepeat(1, None)`                               |
| `*`     | Zero or more of preceding element   | Repeats **the previous element zero or more times**         | `.regexRepeat(0, None)`                               |
| `?`     | Zero or one of preceding element    | Makes **the previous element optional**                     | `.regexOptional()`                                    |
| `[...]` | Character set                       | Matches **any one character in the brackets**               | `.regexFilterCharacters('abc123')`                    |
| `( )`   | Capture group                       | Groups part of a pattern to **extract or reuse**            | `.regexExtractGroup('pattern')`                       |



### ✅ Notes:

1. The **Explanation** column avoids regex jargon — it describes behavior in simple words.
2. The **Function / Parameter** column shows a **human-readable, chainable function name** like you requested.
3. Digits, word characters, and whitespace no longer require `\d`, `\w`, or `\s` — instead, the function name communicates intent.



If you want, I can **expand this table to 20–30 of the most common regex concepts** and map them all to **friendly `.regex...()` functions** so you can basically **replace regex symbols with human-readable methods in your class**.

Do you want me to do that?

---
IGNORE

various arrays/data structures

Notes / Key Points

Fixed-size arrays: Compile-time fixed size, static memory.

Dynamic arrays / List / Vector: Resizable, auto-managed memory.

Slices / Subarrays: Lightweight view into array (no copy in Go/Rust, shallow copy in Python/JS).

Linked list / Deque / Queue / Stack: Classic data structures, often library-provided.

Circular buffer / Ring buffer: Used in embedded systems and high-performance queues.

Strings: Often implemented as arrays of characters internally; some languages have immutable strings.

Tuples / structs / records: Used for grouping multiple values; may be fixed-size or immutable.


return type in two places only one is needed but cant do both

//to have support similar funtionality like in go.
func/function returntype FunctionName(param1 type, param2 type) (named returntype,named returntype) {
  // code to be executed
  return output, Error()
}

functions don't need return statement

---
IGNORE

Var variable decleration. 
eg
int age = 5
age int = 3 //like go don't know why they did this but should be able to support
var int age = 1

can use the following to specific declar variable: val, var, let, dim
fusion you only need the data type and the name

[] for array decleriation
int[] ages = []
int ages[] = []

() for array decleriation read only
int() ages = ()
int ages() = ()



---
PLANNED

based this on the Wiki.js wiki container app.

Docker container random notes
run code within docker container which has all the code installed. 
authentication for what developers can and cant do.
the docker can then able to git push/pull the specific project.
the specific docker container has all the needed
  - so devs can say it works on my pc eg when it build fails they cant use the excuse. 
  - project manager can manage the containers remotely
    - install patchs
    - install new apps/libraries inside docker
  - Progress reporting
    - proper unit tests are automatically done and reported.
    - the code automatically reported if failing/comile errors
    - added to project status and git automatically on the progress
  - the docker container input the dev specific preference (eg indention, {}, keyword)

# Docker Container
Self contained Docker container for the project. Contains all the info ready to use.
Auto updates the code to GIT and has all the apps ready installed needed for the app.

## Setup
  - Init: dev pulls the docker container (auth).
  - Pulls the container down ready to use
  - All settings are already preset

## Container
  - Contains the build environment
  - Contains authentication needed to use the container
  - Contains all installed needed apps.
    - Libraries: fusion, python, java, vb.net etc
    - IDE: VS Code, Netbeans, Idle, etc
  - Test Suite
    - Unit tests

## Remote
  - Project Admin can update primary container
    - Then the Dev container can get the patchs

## Input
  - Dev Code Preference
  - Dev Codeing the specific files
  - App fetches project: eg tickets/projects on what to fix and time period
    - eg project management app: teams, monday.com, jira etc
    - Ticketing Management app: zendesk etc
  - Git Fetch to automatically stay updated <AUTO>

## Output
  - Git Push code to repo with the updated code <MANUAL>
    - Dev eg only allowed to save to his branch and auto updates <AUTO>
  - Progress reporting
    - Update project management app:
    - Update Ticketing management app:

## Use
  - Dev logs into Container to run the IDE <default>
  - Dev could have His IDE mount the Container to access the code within <is this possible to check>

---
PLANNED

# Standards

## Program Parigem
  - dev uses his own programming styles: indention, {}, keywords
  - docker container for more complex handling
    - All is self contained so the dev doesn't need to install or set
  - documentaions from beginning: 
    - Into to project: onboarding new devs
      - can have specific topics: eg Threading, IO on how to use the code/library
    - Code wiki: full api spec
    - Tutorials: Tutorials on varias aspecs of the code. <normal apps don't use this its for the fusion/go/java language >
    - example projects: example pojects <normal apps don't use this its for the fusion/go/java language >

---
PLANNED

Got it — I’ll make sure to search your uploaded Fusion project files if I need details to answer future questions.

To confirm: you want me to **add a note/reminder for Claude** about a new feature — specifically support for:

1. **Multiple import blocks** (Go-style):

   ```go
   import (
       "bufio"
       "fmt"
       "log"
       "os"
   )
   ```

2. **Function parameter lists with annotated comments showing type hints** (both `String` and `string` valid, same for `Date` etc.):

   ```c
   int function name(String name,   // String or string for name
                     String surname, // string or String for surname
                     int age,        // age
                     Date date)      // Date object
   ```

I’ll phrase it as a task entry for Claude like this:

---
PLANNED

### 🆕 Feature Reminder (to add for Claude session)

**Title:** Multi-import & Parameter Comment Feature
**Description:**
Add syntax handling for:

1. **Grouped imports** (Go-style multi-line `import (...)` block).
2. **Function parameters with inline type comments** that allow flexible casing (`String` or `string`, `Date` or `date`) and optional trailing comments for IDE hints.

**Example:**

```fusion
import (
    "fmt"
    "log"
    "os"
)

//parameters inline or steped()
//inline default for fusion
int function createUser(String name, String Surname)


//steped??
int function createUser(String name, // first name
                        String surname, // last name
                        int age, // age
                        Date date) // birth date
```


---
PLANNED

some Golang notes
- some have the go test, doc, build, run commands that might be usefull


🧰 1. Go shipped with go fmt, go test, go doc, etc. — standard, consistent tools

Meaning:
Go includes built-in command-line tools that handle common developer tasks — no need for external frameworks or inconsistent setups.

Main tools and what they do:

go fmt – auto-formats code according to the Go style guide.

Removes arguments over formatting (spaces, tabs, braces).

Every Go project looks the same everywhere.

go test – built-in test runner.

Lets you write _test.go files and run tests without extra setup.

Unified testing across all Go projects.

go doc – documentation generator and viewer.

Reads code comments and shows them as structured docs.

Example: go doc fmt.Println shows docs for that function.

go build – compiles your program.

Handles dependencies automatically.

go run – compiles and runs a Go file in one step (useful for quick testing).

Why it matters:

Every Go developer uses the same tools.

No configuration wars like in C++ or Java (different IDEs, build systems).

Encourages clean, standardized development practices.

---










