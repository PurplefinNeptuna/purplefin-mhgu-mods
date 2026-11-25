# Development and distribution

## Supported loaders and source updates

Baselines, update rules and retired patches: "Always" in the root AGENTS.md.
Loader version checks, ABI layouts and the converter pin: the forge-modding
skill's [api-and-builds.md](../.agents/skills/mhgu-forge-modding/references/api-and-builds.md).
Source updates never replace installed packages.

## Independent mod builds

Switch Rust/GCC NRO targets retain `"relocation-model": "pic"` and GCC pre-link
arguments `-nostartfiles` and `-Wl,-z,text`. Add these to newly generated mod
targets before their first build, preserving other required arguments. Forge's
Rust runtime supplies startup metadata and init/fini. Reject DT_TEXTREL/DF_TEXTREL
and verify that final ELF/NRO dynamic relocation writes target writable data/BSS.
Keep linker errors and exact artifact hashes. See the modding skill's
[build requirements](../.agents/skills/mhgu-forge-modding/references/rust-builds.md#rust-nro-relocation-requirements)
for the reviewed Lawrence hardware-test fork and its separate validation scope.

Each `mods/NAME/` owns its source, recipes, tests, dependency locks, licenses,
export list and build entry point. No sibling mod, installed emulator, personal
path or parent Git history may be required. Third-party sources are fetched,
never committed: Rust mods run `./build.sh fetch` (forge-rs and crates.io into
ignored `vendor/forge-rs/` and `vendor/crates/`), C plugins `prepare --fetch`
(Forge, libnx, cimgui into `vendor/forge/` and `vendor/sdk/`). Fetched files are
checked against `dependencies.lock.json`, crates against `Cargo.lock`. Build/work
folders are ignored outputs.

Use `./build.sh doctor`, `prepare`, `build`, `test`, `verify`, `package`,
and `export --output DEST`. Host-only tests omit native verification;
Rust mods run `fetch` once first; the C template's `prepare --fetch` downloads its compiler image.
Configure copied native/resource inputs with `build.local.json`; never edit
original dumps, libraries or saves. Preserve unknown binary fields and unrelated
resources. Record source paths and SHA-256; re-extract changed archives and
compare inventories. Same-path ARC changes require an internal-resource merge.
Repack ARCs only with supported MHGU tools against an original repacking baseline.

Scaffold with `python3 scripts/mod_distribution.py init NAME --kind plugin`
(or resource, cheat, tool). Refresh `EXPORT.json` deliberately; exports exclude runtime/game binaries,
private configurations, ignored trees and unsafe paths. Validate exported source
outside this workspace using explicitly supplied copied inputs.

Scaffolded C++ plugins compile with the shipped mods' ARMv8 flags
(`-march=armv8-a+crc+crypto -mfloat-abi=softfp -mfpu=crypto-neon-fp-armv8`),
so Forge and libnx headers work. Include them; do not hand-declare Forge
symbols. Packages stage `romfs/nativeNX/...`, `exefs/` or
`cheats/<build-id>.txt` directly inside the named runtime folder.

### New plugin: definition of done

A new plugin task is complete when all of these hold, unless the user scoped
the task to one phase:

1. The scaffold builds, and it includes Forge headers instead of re-declaring them.
2. Research findings (offsets, ABI, register/GE audit) are recorded in the mod's
   DEVELOPMENT.md or `work/NAME/`, with their sources.
3. The code implements the requested behavior, not only a diagnostic. Verified
   API gaps are documented beside the workaround.
4. Focused host tests cover the pure logic, in `tests/` folders outside the source files, and
   `./build.sh test` passes.
5. The README follows the release README standard below, since candidate ZIPs ship it.
   What the tester should try and which log lines to send go in
   `mods/NAME/TESTING.md`, outside the ZIP, and into the report's "To test".
6. A registered DEVELOPMENT candidate is packaged and the full `check` passes.
7. The report gives the candidate hashes and the runtime checks still needed.

Stop earlier only when a missing input or an unresolved native contract blocks
the next step. Name the blocker and what would remove it. When a tool refuses,
read the error and the code that raised it before treating it as a rule.

## Source file size

A hand-written source file (Rust, C, C++, Python, shell, assembly, JS) stays under 600 lines
and holds one topic: one screen, one table, one hook family. When a change would push a file
past 600, split it first, as its own commit with no behaviour change, and then make the change.
Split along the topics the file already has (`mods/wishfinder/src/native/` is the model: a
`mod.rs` with the shared state and helpers, then one file per screen) and never into numbered
parts. Tests follow the same rule: one test file per area.

The limit counts lines, so it only means something while each line is readable. Every line a
commit adds or changes holds one statement and is at most 120 characters (`scripts/line_rules.py`):

- Python, read with `ast`: no `a; b`, no block body on its header line (`if x: y`, `def f():
  return y`) and no `import a, b`.
- Rust, C, C++, JS: one `;` per line outside strings, comments and brackets.
- A line that is a single string literal may be longer.

Never meet the limit by joining lines, shortening names or dropping comments. Split the file by topic
instead. Older lines are checked once a commit touches them.

`scripts/code_size_limits.json` lists the files that were already longer, each with its length
as a ceiling; a mod's own files are listed in that mod's `scripts/code_size_limits.json`, keyed
from the mod's folder. A listed file may shrink but not grow; when it shrinks, lower its entry in the
same commit, and remove the entry once the file is under 600. Never raise an entry or add a
new one. `scripts/code_rules.py` checks this in the pre-commit hook (`python3
scripts/code_rules.py` checks every tracked file; `--repo mods/NAME` reads a mod's own repo). Generated and third-party trees (`vendor/`,
`tools/`, mdBook's `book/html/`, rendered test assets) are exempt.

## Native implementation rules

Hooks, GE/NZCVQ, settings panels, INI storage and logging rules live in the
forge-modding skill (`SKILL.md` and its references); "Research first", "Forge
first" and "Native writes" are in the root AGENTS.md. Rules kept here are the
workspace's own:

- Explain native offsets, units, data flow, ownership, nested hooks, TLS borrows
  and unsafe caller requirements beside substantial code. A comment states the
  current contract in a line or two and never just repeats the code.
  Comments-only work keeps pinned assembly and third-party bytes unchanged.
- A mod's DEVELOPMENT.md holds the current project only: exactly one current-state
  paragraph, then the facts a change needs, a short "Do not" list and open items.
  "Writing project docs" in the root AGENTS.md has the full rules.
- Diagnostics, forced values, test sliders and probes are scaffolding. Once the
  user accepts the behaviour they were for, remove them with the consolidation
  playbook (forge-modding P7) before adding the next feature or promoting.
- Static tests do not establish emulator or gameplay correctness.

## Releases

`DISTRIBUTION.json` is the authoritative record for every mod directory.
DEVELOPMENT means unapproved work; LOCAL_ONLY means a local dependency/tool;
READY_TO_DISTRIBUTE requires approved, verified local delivery; PUBLISHED also
requires the publication URL/date. Retired trees belong in Git history.

Runtime changes require a new version. A change that leaves the runtime as it is (READMEs,
notices, the API book, example code in the API kit) refreshes the current version with
`package NAME --refresh-support`, which backs up the old files and refuses if any runtime file
differs. Keep user release approval separate from
exact binary gameplay acceptance. Build/host/static results never become manual
results; preserve limitations for Linux, Windows, Eden, Ryujinx and hardware.
Use `python3 scripts/mod_distribution.py package NAME` after mod-specific tests,
then `python3 scripts/mod_distribution.py check` before committing or claiming
readiness. Source-only checks do not establish readiness. Preserve the tracked
pre-commit check and other hooks; `scripts/install_hooks.sh` turns them on after a clone, for the
workspace and for each mod checked out as a submodule (`.githooks/mod/pre-commit`). A mod change
is two commits: in `mods/NAME` (its hook runs the code and doc rules and the workspace's
`scripts/mod_distribution.py` on the mod's index), then the new pointer in the main repo. A mod's
own `scripts/mod_distribution.py` is a helper its builder imports; its `check` predates
`manifest.json` and does not decide. A mod whose repo is still private is `update = none` in
`.gitmodules`, so a recursive clone without access skips it; publishing a mod removes that line. The hook checks the whole index, but packages, records on disk
and doc rules only for what the commit stages (`check --touched`), so several mods can be worked
on at once; stage a mod's whole change together. Staging `scripts/mod_distribution.py`,
`scripts/standalone_mods.py` or `templates/` checks every mod's package.

DEVELOPMENT candidates package only after registration. Set the candidate
version in `mod.json`, then add these fields to `DISTRIBUTION.json`:
`version`, `package_name`, `archive` (`NAME-VERSION-candidate.zip`), `candidate`
(`build/NAME/candidates/VERSION/delivery`), `candidate_builder`
(`scripts/build.py` for scaffolded mods) and the `gamebanana` record. Optional
`notices` lists shipped license files; otherwise the mod's `LICENSE` and vendor
licenses are used. Rust mods list tracked copies in `licenses/`, never a fetched
`vendor/` path. Then run `./build.sh build`, `./build.sh test` and
`python3 scripts/mod_distribution.py package NAME`. Without `candidate_builder`
the packager refuses DEVELOPMENT mods. Status stays DEVELOPMENT.

A release lives at `build/NAME/releases/VERSION/`, with versioned ZIP, named
runtime folder, README.md, README.html, GAMEBANANA_README.html, NOTICES.txt,
NOTICES.html, release manifest and SHA256SUMS. The ZIP contains only README.md
beside the named runtime folder. The README is identical inside/outside the ZIP;
runtime folders contain no guides/notices/release manifests. Every new candidate or
release ships `manifest.json` beside `romfs/` for mod managers, with exactly these keys in order:

```json
{
  "manifest_version": 1,
  "id": "PurplefinNeptuna/NAME",
  "version": "0.N.0",
  "name": "README title",
  "authors": ["PurplefinNeptuna"],
  "description": "One sentence on what the mod does.",
  "gamebananalink": "",
  "requires": {"PurplefinNeptuna/purple-lib": ">=0.20.0"},
  "conflicts": {},
  "load": {"after": [], "before": []}
}
```

`version` is this version rN written as `0.N.0`, and ranges in `requires` use the same
form. `gamebananalink` is `""` until the mod has a GameBanana page. Ids are `author/mod`.
Register it in `payloads`; `package` refuses a new candidate or release without it
(`scripts/mod_manifest.py`). The mods in its `MANIFEST_TXT` list, whose current version shipped
the old `manifest.txt`, re-package that version with it and ship `manifest.json` from their next version;
releases packaged before either rule keep their bytes. Keep notices and HTML outside
ZIPs. Support refreshes back up the prior release and preserve runtime bytes.
Archive superseded releases outside active releases.
A renamed mod sets `archive_stem` in `DISTRIBUTION.json`, and its archive starts with that stem. Its
ID, folders and runtime keep the old name, so the runtime bytes don't change.

### Version and status changes

Change a mod's version or status only with `scripts/mod_lifecycle.py`, from the workspace root. Each
command checks its inputs before it writes anything. A release leaves `build/NAME/releases/` only by
move into `backups/accepted/NAME/`, with hashes checked after the move.

| Step | Command | What it does |
| --- | --- | --- |
| New version | `start NAME --reason TEXT` | Next unused rN as DEVELOPMENT. Archives a READY release first and keeps its candidate. Moves `mod.json`, `scripts/paths.py` and `manifest.json` to rN. |
| Promote | `promote NAME --basis TEXT` | Releases the packaged candidate's exact bytes. The basis quotes the user's approval and names the installed NRO hash. |
| Withdraw | `withdraw NAME --reason TEXT` | A release goes back to DEVELOPMENT at the same version. Needs that version's packaged delivery. |
| Roll back | `rollback NAME --to rK --reason TEXT` | An archived release is current again: same runtime and ZIP, support files refreshed. |

Run `start` before the first code change of a version, on a clean mod repo, and commit it alone.
It prints what it leaves to you: lines still naming the old version, `limitations`, the evidence
summaries, the current-state paragraph and the `docs/LOCAL_STATE.md` rows. A mod still on
`manifest.txt` writes `manifest.json` and moves `build.py`, `verify.py` and `payloads` to it.
After `promote`, `rollback` or `withdraw`, update DEVELOPMENT.md, both `docs/LOCAL_STATE.md` tables
and the root README table. The root README lists the approved release, never a candidate.

Every `./build.sh` command runs through `scripts/candidate_guard.py`, a copy of
`templates/standalone/scripts/candidate_guard.py` that `check` holds every mod to. It refuses
before running when `scripts/paths.py` and `DISTRIBUTION.json` name different versions, or when the
version is not DEVELOPMENT. Once a candidate has a `delivery/`, a run that leaves another runtime is
undone: the folder is restored and the command fails. A runtime change after packaging is a new
version. Use only the wrapper: a plain `cargo` run leaves a `target/` that blocks the next build.

`THIRD_PARTY.md` records development provenance;
`DISTRIBUTION_NOTICES.md` and current licenses cover only shipped components and
applicable authors, retaining copyright/license wording and Forge credits,
including the Skyline Project/Jeffi license text.
Notices must work without a checkout and exclude local paths/history and
unrelated development tools.
Use `PurplefinNeptuna` for project-owned copyright and author credits. Preserve
third-party holders and license text exactly. Copy licenses from the pinned
upstream source and record their origin in `THIRD_PARTY.md`. Never fill a
third-party template with guessed names or dates. Examples inside an upstream
license's application appendix remain unchanged. A programming language alone
does not add a license requirement. Include notices for linked library code and
shipped assets, keeping compiler tools and host-only fixtures in development
provenance.

GAMEBANANA_README.html combines the install guide with the explicit `gamebanana`
record. Disclose actual AI code assistance prominently, name/link its software
and scope, and credit applicable authors/sources. Code assistance requires no
training-dataset inventory. Model-generated creative assets require known
software/input/dataset credits; never invent provenance or claim unperformed
human review. Recheck [the live policy](https://gamebanana.com/wikis/2175) before
publication. Packaging does not publish or establish moderation approval.
`"compact_html": true` in the `gamebanana` record spaces the guide part of that
page with `<br><br>` instead of `<p>`. The packager appends the record's credits
there, so a README with its own Credits section lists them twice.

GameBanana can reject literal INI text such as `style = wilds` as forbidden
inline styling. HTML code examples encode equals signs as `&#61;` so displayed
and copied INI text stays correct. Keep the Markdown and actual config unchanged.
Use literal apostrophes in HTML output. GameBanana rejects `&#x27;`. Generated
attributes use double quotes, which remain escaped along with HTML markup.
Keep copyright symbols and author names as literal UTF-8 text. GameBanana
rejects numeric references such as `&#169;`. Preserve original license wording.

### Release README standard

Every READY_TO_DISTRIBUTE or PUBLISHED guide starts with the mod's name and a
short description of what it does. Use these sections in this order:

| Heading | Content |
| --- | --- |
| Requirements | Bullet list of the game/version, platform, linked loader and other actual requirements. |
| Installation | Numbered steps to close the game, extract the named ZIP, copy the whole named folder, and enable/start it. Include the destination paths and any required loader configuration. |
| Usage | What the user does and sees. Put controls, badges, settings and INI examples here as needed. |
| Update and removal | Close the game, explain which files/folder to replace or remove, and preserve settings stored inside a mod folder. |
| Compatibility and known issues | Visible limitations and steps the user can take. Omit this section when there is nothing useful to say. |

A README names another mod only in Requirements: a requirement (a minimum version of a mod the user
may run beside it counts), or a recommended mod listed by name and version alone, without what it
does there; conflicts live in `manifest.json`. Use `### Settings` and `### INI settings` below Usage when applicable. Settings
tables use `Setting | Default | Effect`. Control tables use `Action | Input`.
Write overlay paths as **Plugin UI > Plugin name**, keeping the actual UI name
and button labels exact. Use colour/grey consistently, with plain colour names
such as Green and Red. Gathering/objective labels belong in research records.

Switch installation steps give both Eden and Ryujinx destinations. Include
hot-reload restrictions only where required by that mod. Link Fexty's Forge fork.
Build fixtures and co-installed mods do not establish runtime dependencies.

Apply the full local Humanizer process: read the whole guide, rewrite awkward
passages, then check the result for lost facts and remaining writing patterns.
Avoid semicolon-heavy prose, em/en dashes, repeated instructions and empty
sections. Keep code examples, config values and technical claims accurate.
Keep implementation, research, testing, approval and release history in
developer records. Do not add advice about unrelated or retired mods.

Credits use only `[Component](public URL) by Author`, one entry per item.
End each entry after the author's name. Keep purpose, contribution details,
provenance and license explanations out of README credit lists. Credit a fork
and its original project as separate entries. Keep scope metadata, AI
disclosures and complete legal notices in their respective records/sections.

A published mod's README ends with this License section, word for word apart from the name and
repository. Never paste a license's own legal wording ("at your option", "without warranty")
into a README or release notes; say it in plain words.

```markdown
## License

Copyright (c) 2026 PurplefinNeptuna. NAME is licensed under the GNU GPL, version 3 or
later. The source code and the license text are at
https://github.com/PurplefinNeptuna/mhgu-MOD.
```

The source README, adjacent release README, archived README and both HTML
descriptions must agree. Refresh them through the distribution packager and
run its full check. Preserve runtime bytes and back up the previous delivery.

### GitHub release notes

A published mod's GitHub release is tagged with the version (`rN`) on the mod-repo commit its ZIP
was packaged from, and attaches the release ZIP and `NOTICES.txt`. Its notes hold only:

- A later release: the changelog since the previous published release, one short line per change
  a player notices, in players' terms.
- A mod's first release: two or three sentences on what the mod does, and its requirements.

Leave out everything else: install steps, credits, license, test scope, checksums and history.
The notes go through the full Humanizer process like any player-facing text, and the user sees
the final text before the release is created.

### Publishing a mod repo

Before a mod repo (or the main repo) becomes public, scan its whole history and read the full
result: every commit address must be the noreply one, and no file in any commit may hold a
personal address, a home path, ROM file names or release-site tags, decompiled code, a large or
binary blob, or third-party material such as cheat lines (any code type), a copied cheat or wiki
file, or those words inside code. Never truncate the scan's output; list every matching file and
read it. Make the repo public only afterwards, as its own step, once the result is clean.
