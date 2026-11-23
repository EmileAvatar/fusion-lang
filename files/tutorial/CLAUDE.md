# files/tutorial/ - the Fusion site (user, 2026-11-22)

A site in the style of w3schools. The top bar holds the site's parts - Home, Learn, Ownership, Services, HIDL, Cross
Compiler, GitHub - not the tutorial itself; each part may have its own index on the left. Plain HTML, no build step.

| File | What it is |
|---|---|
| `index.html` | Home: what Fusion is, why, its major features (with Home's own index) |
| `learn.html` | Learn: the tutorial's index (as w3schools' C# one) and its first page |
| `ownership.html` | Ownership: one owner, moving, borrowing, one writer (a first page) |
| `services.html` | Services: the problem, what a service is, why it solves it (designed - a first page) |
| `hidl.html`, `cross-compiler.html` | HIDL and the cross compiler (ideas - a first page each) |
| `site.css` | The whole site's look - bar, index, pages, examples, notes; one file for every page |
| `fusion-code.css` | The colours of Fusion code blocks (`<pre class="fusion">`, spans kw / type / fn / str / num / com / op) |
| `tutorial.json` | The structure: the bar's parts, each part's index, each lesson's example program (`examples/<topic>/<name>`) |
| `main.md` | The plan in words: the site as a simple text hierarchy - what will be built |

## Rules
1. An index as w3schools' C# one (user, 2026-11-22): the main items always visible; only an item with items of its own
   folds (a caret on the right); a group heading never folds
2. Two CSS files only: `site.css` for the site, `fusion-code.css` for Fusion code - never styles in a page
3. One JS file (to come) for all interactivity - the bar and the indexes built from `tutorial.json`, and the colouring
   of every `<pre class="fusion">` block (keywords, types - a capitalised name too -, function names, strings,
   numbers, comments); until then a page's code is coloured by hand with fusion-code.css's spans
4. Every example is a real program from `examples/` (built and run by the test suite) - copy it, don't invent code the
   compiler hasn't seen; a part not built yet is marked designed / idea (Services, HIDL, Cross Compiler)
5. ASCII in the files (Rule 2) - HTML entities where a character needs it (the icon: `&#127959;&#65039;`)
6. `tutorial.json` and `main.md` change together - the same parts, indexes and lessons
7. The same top bar on every page (Home, Learn, Ownership, Services, HIDL, Cross Compiler, GitHub - GitHub opens in a
   new tab); a page made by hand copies it exactly until the JS builds it
