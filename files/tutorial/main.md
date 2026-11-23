# The Fusion site - what will be built

A simple view of the site. The **top bar** holds the site's parts - not the tutorial itself; each part may have its own
**index** on the left. In an index (as w3schools' C# tutorial): the main items are always visible; only an item with
items of its own folds (a caret on the right); a group heading never folds. Each lesson's example is a real program
from `examples/`, built and run by the test suite. `tutorial.json` holds the same structure for the site.

```text
Top bar
|
+-- Home                  what Fusion is, why, and its major features          index.html
|   +-- Welcome
|   +-- What is Fusion?
|   +-- Why Fusion?
|   +-- Major features   (folds)
|   |   +-- Configurable / Syntax without lock-in / One owner, one writer / Services / Generics
|   +-- What works today
|   +-- Start learning  -> Learn
|
+-- Learn                 the tutorial - its index                               learn.html
|   +-- Fusion HOME / Intro / Get Started / Syntax / Output / Comments
|   +-- Fusion Variables (folds)      Declaring, let and var, const
|   +-- Fusion Data Types / Type Casting / User Input
|   +-- Fusion Operators (folds)      Arithmetic, Comparison, and / or / not, the conditional
|   +-- Fusion Strings (folds)        Strings, Interpolation, the string library, Unicode and bytes
|   +-- Fusion If...Else
|   +-- Fusion match (folds)          match, ranges in a case, fall match
|   +-- Fusion While Loop
|   +-- Fusion For Loop (folds)       for, ranges and step, foreach
|   +-- Fusion Arrays (folds)         arrays, growable, 2 and 3 dimensions
|   +-- [Fusion Functions]            Functions, Parameters, Lambdas, Any number of values
|   +-- [Fusion Classes]              Structs, Classes, Interfaces, Inheritance, Enums
|   +-- [Fusion Collections]          Lists, Maps, Generics
|   +-- [Fusion Errors]               Errors, try / catch, the null guard
|
+-- Ownership             one owner, one writer - in detail
|   +-- One owner / Moving / Borrowing / readonly / One writer
|
+-- Services              what a service is and why - in detail      (designed - Task 42)
|   +-- The problem: races, locks, deadlocks / What a service is / Using one / Why it solves them
|
+-- HIDL                  hardware described in Fusion                (an idea - Task 41)
+-- Cross Compiler        other languages through Fusion: Lang.<Language>.Fusion   (an idea)
+-- GitHub                the project's repository - opens in a new tab
```
`[...]` a group heading - never folds. `(folds)` an item with items of its own.

**Built so far (2026-11-22) - a first version to work with, completed later:** `index.html` (Home), `learn.html`
(the Learn index and its first page), `ownership.html`, `services.html`, `hidl.html`, `cross-compiler.html` (a
first page each, with its own index), `site.css`, `fusion-code.css`, `tutorial.json`. **Next:** one JS file - it
builds the bar and each part's index from `tutorial.json`; then a page per lesson.
