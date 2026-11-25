# API books for mod authors

A mod with an API for other plugins ships an mdBook for their authors. WishFinder's and Purple-lib's books are the standard (`mods/wishfinder/book/`, `mods/purple-lib/book/`). Copy their layout, theme and `build.py` for a new book.

## Layout

`book/src/SUMMARY.md` has three parts, in this order:

| Part | Pages |
| --- | --- |
| Manual | Introduction (`README.md`) with Getting started under it, FAQ, one chapter per task, Glossary |
| API Reference | The table record with a page per function under it, then Callbacks (if any), Records, Constants and Behavior, each with its pages under it |
| Complete examples | C header, C++ plugin, Rust bindings, Rust plugin |

`build.py` numbers the Manual only. The other parts show no numbers.

### Manual

- The Introduction says what the mod is and lists what a client plugin can do. It has a "How this book works" section and names the API version and the first release that has it.
- Getting started has four sections. How your plugin gets the table, Setup (C++ steps, then Rust steps), the smallest working plugin, and what happens when the library isn't installed.
- A task chapter opens with one or two sentences and a numbered list of its sections. It ends with a `Reference:` line linking the reference pages it used.
- The FAQ has one heading per question. Each answer is a few sentences and ends with a link to the full section.
- The Glossary is one table, `Word | Meaning`, in alphabetical order.

### API Reference

A function page has, in order:

1. The C++ signature and the Rust signature, each marked `<!-- check: copy -->`, with a trailing comment naming the source.
2. One paragraph on what it does, then `Used in:` links to the manual chapters.
3. `## Parameters`: a table `Name | C++ | Rust | Description`.
4. `## Returns`, listing every refusal. Then `## When to call`, `## Notes` and `## Example` in both languages.

A record page shows the C++ struct, the Rust struct (copied) and a field table. The table page has `Function | C++ returns | Rust returns | What it does`. The Constants page maps each C++ name to its Rust name. Behavior covers threads and timing, limits and versions.

## Code

- Every example is a C++ block followed by its Rust block. `theme/tabs.js` turns each pair into tabs. A plain C block is allowed only in the C header page.
- `examples/cpp/example.cpp` and `examples/rust/example.rs` are twins. Every function has the same name, inputs and result in both.
- The Rust kit is two files. The bindings (`wishfinder.rs`, `purplelib.rs`) hold the records, the constants, a safe function per table entry and the kept table (`api()`). The example plugin uses them.
- Manual chapters include example regions with `{{#include ../../../examples/...:anchor}}`. Both example files carry the same `ANCHOR` names.
- A library that takes registration only inside its callback can't export that callback from the bindings. Purple-lib's `keep` checks the version and keeps the table, and the plugin's own export calls it.

## build.py

`python3 book/build.py` checks before it builds:

- A page's C++ blocks compile as one unit with the C++ plugin template's flags under `-Werror`. `<!-- check: uses NAME -->` declares context names from `CONTEXT`.
- A page's Rust blocks build as one module beside the bindings and the example, under `-D warnings`. Purple-lib type-checks only (`--emit=metadata`), so a page may define its own `purplelib_on_register`.
- A `check: copy` block must appear in the header, the bindings or an example, comments and spacing aside. A copied C++ struct must match the header's.

Then it builds `book/html/` (committed, stable names, byte-identical on rebuild), renumbers the sidebar and checks every local link and anchor. It also checks that `DISTRIBUTION.json` `archives` lists exactly the API kit's files. `--sync` rewrites that entry after a version bump or a new page.

Theme: `theme/compact.css` (tight spacing, a 920px column, tab styles) and `theme/tabs.js` (its storage key names the book). `book.toml` adds both, sets `hash-files = false` and turns off MathJax and the playground.

## Tests

- The host tests include both Rust example files as modules. They run the records through the library's real checks and drive the example through a table built as the library builds its own (`mods/purple-lib/core/tests/examples.rs`, `mods/wishfinder/core/tests/examples.rs`).
- `build.py test` builds the Rust pair as a `no_std` rlib.
- `verify.py` compiles the C++ example for the Switch with the template flags. It refuses any import but `_GLOBAL_OFFSET_TABLE_` and requires the exported callback.

## Before committing

1. Run the whole humanizer process on the prose, every code comment, and every string the example shows in game. Show the final text to the user ([Humanize user-facing text](../../../../AGENTS.md)).
2. Screenshot a few pages with headless Firefox and look at them. Make the profile folder first, or Firefox writes nothing: `firefox --headless --profile DIR --no-remote --window-size=1400,1800 --screenshot OUT.png file://.../page.html`.
3. A book or example change leaves the runtime as it is. It ships in the current version with `python3 scripts/mod_distribution.py package NAME --refresh-support`, which rebuilds the API kit in place.
