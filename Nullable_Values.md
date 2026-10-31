# Nullable values in Fusion

How Fusion handles "nothing here": which values can be null, the `?.` guard, `??`, number
conditions, and when (not) to use them. A design document for Task 30, kept in step with
`FEATURES.md` Task 30 and the plan in `taskSummary2.md`. Status: **being designed**
(user decisions 2026-10-27) - nothing here is built yet.

---

## 1. The problem we are solving

Tony Hoare called the null reference his "billion-dollar mistake". In many languages any
object can be null, and using it crashes the program:

| Language | Using null | What you see |
|---|---|---|
| Java | `person.getAge()` on null | NullPointerException - the program stops |
| C# | the same | NullReferenceException |
| C / C++ | `p->age` on NULL | a crash (segmentation fault), sometimes silent memory damage |
| JavaScript | `person.age` on undefined | TypeError: cannot read properties of undefined |
| Python | `person.age` on None | AttributeError |

The problems:
- **Any value might be missing**, and nothing in the code says which ones
- **The crash comes far from the cause**: the value was left unset somewhere else
- **Checking everywhere is noisy**: `if person != null and person.address != null and ...`
- **Data from outside can always be missing**: a JSON object whose field is `null`, a
  database row with an empty column, a value the user never entered, a file that wasn't
  there. The program can't promise these values exist - it can only handle them safely
- **"Missing" is often faked with magic values** (-1, "", 0), and one gets mistaken for a
  real value

Newer languages (Swift, Kotlin, C# 8+, TypeScript, Dart) fixed this. Values are not null
unless the code allows it, and `?.` reads through a possibly-missing value safely.

**Fusion's aim:**
- No value is null unless it can be
- A missing object never crashes the program by surprise
- Reading through a possibly-missing object takes one character (`?.`)
- Nothing changes silently: a default is always one you wrote (`??`)

---

## 2. Which values can be null

| Type | Can be null? | Default with no value | Why |
|---|---|---|---|
| int, float, bool, char, byte | No | 0 / false / '\0' | values |
| struct | No | every field's default | a value type (user, 2026-10-24) |
| **string** | **No** - unless the project allows it | `""` | a value with methods; a setting can allow null (below) |
| **array, List, Map** | **No** - unless the project allows it | empty (`[]`, no keys) | like strings (user, 2026-10-27); see `Arrays.md` |
| class object (Task 32) | **Yes** | null | objects are references |
| **enum** | **Yes** | null - **not** the first value (user, 2026-10-27) | treated as a reference type, like a class: an unset `Status s` must not silently mean `OK` |

**Strings, arrays, lists and maps** (user, 2026-10-27) are values: never null, and empty
when not set. Empty is a real value with a real length: `"".length()` is 0 (no
characters), `[].length()` is 0 (no items). A project that needs "not set yet" to differ
from "set to empty" can allow null, type by type:

```toml
[strings]
nullable = false     # default - never null; true: an unset string is null
[arrays]
nullable = false     # the same for arrays
[lists]
nullable = false     # List<T>
[maps]
nullable = false     # Map<K, V>
```

(Section names follow the existing `[strings]` / `[structs]` style; final names are fixed
when Task 30 is built.)

---

## 3. Three ways to handle a value that might be null

```fusion
Person p = new Person("Jake")
Person pep                      // never set: null
```

| Way | Code | When pep is null | Use it when |
|---|---|---|---|
| 1. Check first | `if pep == null` / `pep is null` / `pep?.null` | you decide what happens | missing means a different path, e.g. "please log in" |
| 2. Guard with `?.` (and `??`) | `pep?.getAge()`, `pep?.getAge() ?? -1` | the call is skipped; the result is null; in an `if` the condition is false | missing simply means "no" or "use a default" |
| 3. Plain `.` (and `catch`) | `pep.getAge()` | a NullError, which only a `catch` handles | it must never be missing - a bug if it is |

- **Checks:** `==`, `===`, `is null`. `x?.null` is quick typing for "x is null", and
  `!x?.null` is quick typing for "x is not null"
- **`?.` is a guard:** on a null object the method is not run, and nothing errors. A
  comparison with a guarded null is false, so `!(pep?.getAge() >= 18)` is true
- **`??` gives a default** when a value is expected and none is there:
  `someObject?.someMethod() ?? value`. Use it only where a null can actually arrive
- **The conditional operator** works on one line and gives a value:
  `int age = (person?.getAge()) ? person.getAge() : -1`
- **Length on a null:** `string?.length()` and `array?.length` give -1 when the string or
  array is null (only when nullable strings or arrays are switched on). An empty one gives
  0. Every other member or method gives null

---

## 4. Numbers as conditions (a setting)

Should `if count` work when `count` is a number? Languages disagree:

| Languages | 0 | Negative | Positive |
|---|---|---|---|
| C, C++, Python, JavaScript, Perl | false | true | true |
| Ruby, Lua | true | true | true |
| Java, C#, Go, Rust, Swift, Kotlin | not allowed: a condition must be a bool | | |

Fusion makes it a setting (user, 2026-10-27) - **built (Task 30.9)**:

```toml
[conditions]
numbers = "positive"   # default: positive is true; zero and negatives are false
                       # "nonzero": 0 is false, any other number is true (C, Python, JS)
                       # "off": a condition must be a bool (Java, C#, Go, Rust, Swift)
```

**Where numbers count as true / false (user, 2026-10-27) - only when the setting is not "off"**:
- in an `if` or `while` condition, including `and` / `or` / `not` inside it:
  `if count and ready`, `if not errors`
- `count == true` / `count == false` compares by the same rule (0 false; 1, 2, 1000 true)
- `count === true` is always false - a number is not a bool (the compiler already warns that
  `===` on two different types is always false)
- `bool b = count` is always an error, whatever the setting - write `bool b = count > 0`
- `and` / `or` always give a bool

- **Why `"positive"`:** -1 is the usual "not found / not set" value (`indexOf`, `?.length()`),
  so with this default `if s?.length()` and `if p?.getAge()` are false for "missing",
  "empty" and "not born yet" alike
- **Watch out for:** developers from C, Python or JavaScript expect -1 to be true. The
  editor will show how the project sets number conditions, as a hint (Task 36.7)
- **Trap under `"nonzero"`:** `if indexOf(s, "x")` is true for -1 ("not found")

---

## 5. Truth tables

Default settings: `[conditions] numbers = "positive"`.

#### Table 1: string and array length

`s` is a string, `a` an int array. The null column only applies when the project sets
`[strings] nullable = true` / `[arrays] nullable = true` - by default they are never null,
and an empty one has length 0.

| Expression | null | `""` / `[]` | `"abc"` / `[1, 2, 3]` | Use case |
|---|---|---|---|---|
| `s.length()` / `a.length` | NullError | 0 | 3 | everyday length, when the value is always there |
| `s?.length()` / `a?.length` | -1 | 0 | 3 | a length from data that may not be loaded yet |
| `if s?.length()` - "positive" (default) | false | false | true | "has text?" - missing and empty both count as no |
| `if s?.length()` - "nonzero" | **true** (-1) | false | true | (C / Python habit - a trap here) |
| `if s?.length()` - "off" | compile error | compile error | compile error | projects that want bool-only conditions |
| `if s?.length() > 0` | false | false | true | the same as above, written out - works with every setting |
| `if !(s?.length() > 0)` | true | true | false | "ask for a name" when missing or empty |
| `if s?.length() >= 0` | false | true | true | "loaded, even if empty" (missing is -1) |
| `s?.length() ?? 0` | -1 (warning: `??` never used here) | 0 | 3 | don't: -1 is not null |
| `s?.null` / `s == null` / `s is null` | true | false | false | "not set yet" vs "set to empty" |
| `!s?.null` | false | true | true | "was it set at all?" |

#### Table 2: a class

`Person p = new Person("Jake")`, and `Person pep` is never set (null). `getAge()` returns an
int; `getSpouse()` returns a Person, or null when there is none.

| Expression | age 30 | age 10 | age 0 | pep (null) | Use case |
|---|---|---|---|---|---|
| `x.getAge()` | 30 | 10 | 0 | NullError - only a catch handles it | the person must exist - a bug otherwise |
| `x?.getAge()` | 30 | 10 | 0 | null (getAge not run) | a person that may not be loaded yet |
| `if x?.getAge() >= 18` | true | false | false | false | "may buy alcohol?" - unknown means no |
| `if !(x?.getAge() >= 18)` | false | true | true | true | "ask for ID" - also when unknown |
| `if x?.getAge() < 18` | false | true | true | **false** (warning) | careful: unknown is not "under 18" - use the line above |
| `if x?.getAge()` | true | true | false | false | "born and known?" |
| `x?.getAge() ?? -1` | 30 | 10 | 0 | -1 | show "-1 = unknown" in a report |
| `(x?.getAge()) ? x.getAge() : -1` | 30 | 10 | **-1** (0 is false) | -1 | one-line value - but age 0 becomes -1; prefer `??` |
| `x?.null` / `x == null` / `x is null` | false | false | false | true | "nobody logged in" |
| `!x?.null` | true | true | true | false | "somebody logged in" |
| `x?.getSpouse()?.getName()` | the name, or null with no spouse | same | same | null | a chain of optional links |
| `x.getSpouse().getName()`, no spouse | NullError | NullError | NullError | NullError | don't - a chain needs `?.` at each optional link |

**Warnings (user, 2026-10-27):**
- **A guarded value in a comparison:** with null, `>= 18` and `< 18` are both false, so
  `!(x >= 18)` is not the same as `x < 18`. The exact rule is decided when it's built
  (Task 30.3)
- **`??` after `?.length()`:** the default is never used, because -1 is not null

---

## 6. When to use `?.` - and when not to

#### Use `?.` when missing is normal and means "no" or "skip"

| Case | Code | Why `?.` fits |
|---|---|---|
| Optional relation | `customer?.getCompany()?.getName() ?? "private customer"` | many customers have no company |
| Not loaded yet | `if order?.isPaid()` | the order may still be loading; "no" until it arrives |
| Optional settings | `config?.getTimeout() ?? 30` | missing setting: a default you chose |
| Search result | `found = people.find("Ann")` then `found?.getEmail() ?? "-"` | "not found" is a normal answer |
| UI / reports | `print(user?.getName() ?? "guest")` | show something sensible, never crash |
| Permission checks | `if user?.isAdmin()` | no user means no permission - false is the safe answer |
| JSON and other outside data | `if order?.getCustomer()?.getEmail()?.length() > 0` | a JSON field may be `null` or missing; the guard keeps the program running |
| User input | `string city = form?.getField("city") ?? "unknown"` | the user may leave a field empty or the form may not be sent |
| A class that failed to load | `report?.print()` | the report object may never have been created - nothing to print, no crash |

#### Don't use `?.` when missing is a bug

| Case | Instead | Why |
|---|---|---|
| A value that must exist (the logged-in user inside a page only users can reach) | plain `.` - a NullError points to the bug | `?.` would hide the bug and quietly take the "no" path |
| Money, medical, safety decisions | check first: `if account == null` -> an explicit error path | "missing" must never quietly mean "no" |
| `if x?.getAge() < 18` (or any "not" question) | `if !(x?.getAge() >= 18)`, or check null first | unknown is not "under 18" |
| A value you will use many times | check once: `if p == null` then return; use plain `.` after | a `?.` at every use is noise and hides where null is handled |
| Strings and structs (default settings) | nothing - they are never null | `?.` on a value that can't be null is a warning |
| `?.length() ?? 0` | `?.length() > 0`, or `?.null` to test for missing | -1 is not null, so `??` never applies |

**Rule of thumb:** `?.` answers "if it's there". When the honest answer for "not there" is
"no", "skip" or a default, use `?.`. When "not there" means something went wrong, let it
fail loudly (plain `.`), or check first and handle it on purpose.

---

## 7. Open points

- The exact warning rules (section 5) - decided when Task 30.3 is built
- Classes (Task 32) and `Weak<T>.lock()` (Task 38) use this model

## 8. Decisions log

| Date | Decision |
|---|---|
| 2026-10-27 | Null only for class objects (and strings when `[strings] nullable = true`; default false - a string is a value, default "") |
| 2026-10-27 | Arrays, List and Map are like strings: never null, empty by default; `[arrays]` / `[lists]` / `[maps]` `nullable` (default false); `"".length()` and `[].length()` are 0 |
| 2026-10-27 | Enums are treated as reference types like classes: `Status s` with no value is null, not the first value - **built 2026-10-28 (Task 30.11)** |
| 2026-10-28 | A null in a `match` equals no case value: it goes to `case null` (30.12), else to `else`; no else and every value covered: a NullError. Printing a null enum prints `null`. `break` inside a `match` ends the match; `continue` acts on the loop (30.12) |
| 2026-10-27 | `?.` is a guard: a null object's method is not run, no error; in an `if` it is false |
| 2026-10-27 | `??` gives a default when a value is expected and none is there |
| 2026-10-27 | Checks: `==`, `===`, `is null`; `x?.null` / `!x?.null` as quick typing; no `x!` |
| 2026-10-27 | `string?.length()` / `array?.length` on null give -1; everything else gives null |
| 2026-10-27 | `[conditions] numbers` = "positive" (default) / "nonzero" / "off"; an editor hint shows the setting (36.7) |
| 2026-10-27 | Warnings: a guarded value in a comparison; `??` after `?.length()` |
| 2026-10-27 | Numbers as bool only in `if` / `while` conditions (with and / or / not); `count == true` follows the setting; `count === true` false; `bool b = count` always an error |
| 2026-10-27 | `.len` and `.length` both; the conditional operator `(c) ? a : b` |
| 2026-10-31 | `null == null` and `null is null` are true, `null != null` false (a bug gave false - Task 32.2g) |
