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
4. Focused host tests cover the pure logic, and `./build.sh test` passes.
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

Runtime changes require a new version. Keep user release approval separate from
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

### Starting a new version

1. Search the mod for the old version (`grep -rnw OLD mods/NAME`) and update
   every copy: `mod.json`, `manifest.json` and any build/path scripts, plugin labels and test
   expectations that repeat it. Ignore unrelated hits such as register names. A mod still
   on `manifest.txt` replaces it with `manifest.json` in the source, `build.py`, `verify.py`
   and `payloads`.
2. If the old version is READY_TO_DISTRIBUTE or PUBLISHED, copy
   `build/NAME/releases/OLD/` to `backups/accepted/NAME/OLD-before-CHANGE/release/`.
   Beside it, put the committed `DEVELOPMENT.md`, `DISTRIBUTION.json`,
   `EVIDENCE.json` and `README.md`, and a `preservation.json` with `version`,
   `release_sha256` (one entry per release file), `"runtime": "UNCHANGED"` and
   `reason`. Confirm the copy with `diff -r`, then remove the build copy and
   any empty `releases/`. `check` allows only a READY version there.
   `backups/` is optional and the user may clear it, so if OLD is the mod's last
   gameplay-accepted build, first copy its ZIP to `build/NAME/candidates/OLD/`
   with a `SHA256SUMS`, and update the table in `docs/LOCAL_STATE.md`.
3. In `DISTRIBUTION.json`, set `status` to DEVELOPMENT and update `version`,
   `reason`, `archive`, `candidate`, `candidate_builder`, payload sources and
   hashes, `limitations` and the evidence summaries. Delete `approval`; it
   belonged to the old version. While the status is still READY,
   `./build.sh package` re-verifies the old release instead of packaging the
   candidate.
4. Run `./build.sh build`, `test` and `verify`, in that order. Use only the
   wrapper: a plain `cargo` run inside the mod leaves a `target/` that blocks
   the next build. Update READMEs before `package`, because the ZIP includes
   README.md.
5. Replace the mod's DEVELOPMENT.md current-state paragraph and its
   `docs/LOCAL_STATE.md` rows; the old version's story goes nowhere but
   `EVIDENCE.json` (`scripts/doc_rules.py` refuses chains). The root README table lists the approved release,
   not the candidate.

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

The source README, adjacent release README, archived README and both HTML
descriptions must agree. Refresh them through the distribution packager and
run its full check. Preserve runtime bytes and back up the previous delivery.
