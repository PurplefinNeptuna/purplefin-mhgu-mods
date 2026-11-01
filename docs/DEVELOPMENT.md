# Development and distribution

## Supported loaders and source updates

Switch development uses unmodified [Fexty's Forge fork](https://github.com/Fexty12573/forge)
1.5.1, based on Jeffi's original Forge, at
`tools/forge-local/` (`b23e114a23f41c9a8e2fd34b2f4df2a2102d0ee1`).
Native ARM32 Hook is 24 bytes: target/detour/original/context pointers at
0/4/8/12, ctx_cell at16 and has_ctx at20. Forge pools ordinary/context
trampolines; verify allocations, ownership and the actual headers at each boundary.
forge-rs source is1.5.0
at `tools/forge-rs/`; its compatible converter is separately pinned at1.4.1.

Update the existing checkout from its official remote; do not create an extra
upstream clone/worktree. Keep old revisions in Git when research needs them.
Do not apply or recreate the retired loader, legacy Better Input, renderer,
mutex or PC support patches, or GURecomp/Forge PC ports: MHGURecomp loads the
Switch NROs. Source updates never replace installed packages.

## Independent mod builds

Switch Rust/GCC NRO targets retain `"relocation-model": "pic"` and GCC pre-link
arguments `-nostartfiles` and `-Wl,-z,text`. Add these to newly generated mod
targets before their first build, preserving other required arguments. Forge's
Rust runtime supplies startup metadata and init/fini. Reject DT_TEXTREL/DF_TEXTREL
and verify that final ELF/NRO dynamic relocation writes target writable data/BSS.
Keep linker errors and exact artifact hashes. See the modding skill's
[build requirements](../.agents/skills/mhgu-forge-modding/references/api-and-builds.md#rust-nro-relocation-requirements)
for the reviewed Lawrence hardware-test fork and its separate validation scope.

Each `mods/NAME/` owns its source, recipes, tests, dependency locks, licenses,
export list and build entry point. No sibling mod, installed emulator, personal
path or parent Git history may be required. Minimal vendored dependencies are
intentional standalone inputs. Build/work folders are ignored outputs.

Use `./build.sh doctor`, `prepare`, `build`, `test`, `verify`, `package`,
and `export --output DEST`. Host-only tests omit native verification;
`prepare --fetch` is the explicit dependency-download operation where supported.
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

## Native implementation rules

Search saved Ghidra/DTI before gameplay work; see [research](RESEARCH.md).
Use Forge's callbacks, logging, input, memory, singleton, hooks, filesystem and
render APIs where applicable. Document a verified API gap before using a lower
level path. Validate pointers, signatures, allocation failures and rollback.
Explain native offsets, units, data flow, ownership, nested hooks, TLS borrows
and unsafe caller requirements beside substantial code. Preserve audited assembly.
Comments-only work keeps pinned assembly and third-party bytes unchanged. Skip
comments that only repeat the code. A comment states the current contract in a
line or two. Run IDs (`r23`), what a run printed and approaches that were
refuted stay out of source.

Store a tuned or user-accepted value in the frame it was measured against: an
offset from, or a fraction of, the node or rect it was read on. Never store
absolute screen pixels. Record the frame it was measured in beside the value.

A mod's DEVELOPMENT.md holds the current project only: exactly one current-state
paragraph, replaced for each version, then the facts a change needs, a short
"Do not" list of refuted approaches, and open items. Run logs and superseded
paragraphs do not go in it: dated results go in EVIDENCE.json and Git keeps the
rest. Keep it short enough to read in full at the start of every task. `work/`
research notes follow the same rule once a phase closes.

Diagnostics, forced values, test sliders and probes are scaffolding. Once the
user accepts the behaviour they were for, remove them with the consolidation
playbook (forge-modding P7) before adding the next feature or promoting.

Preserve NZCVQ and all live registers. Audit GE liveness at every hook and
continuation; never require `msr APSR_g` or `msr APSR_nzcvqg`. Choose another hook
site when required state cannot be preserved compatibly. Static tests do not
establish emulator/gameplay correctness.

Settings use stable plugin-specific IDs in a closed-by-default, unframed tree
row under Plugin UI. Pair every opened TreeNode with TreePop. Panels contain
settings/save feedback only; no settings means no panel. Closing a row leaves
update/render callbacks active. Use concise process-deduplicated logs outside
hot hooks; normal frames/hits/rewards produce no periodic diagnostics.

Use one plugin-specific primary INI on Forge's counted save-data mount. Never
create/read/recover/delete `_backup` configs. Validate before writing, flush,
verify, commit and balance mounts/handles on every failure; preserve session
settings on failure. Missing/invalid primary uses defaults; disk contents after
a failed write are not guaranteed. Damage Numbers retains its expressly
authorized upstream forge-rs config load/default-creation/ScopedMount/Writer
behavior. Saving remains explicit in its settings UI.

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
pre-commit check and other hooks.

DEVELOPMENT candidates package only after registration. Set the candidate
version in `mod.json`, then add these fields to `DISTRIBUTION.json`:
`version`, `package_name`, `archive` (`NAME-VERSION-candidate.zip`), `candidate`
(`build/NAME/candidates/VERSION/delivery`), `candidate_builder`
(`scripts/build.py` for scaffolded mods) and the `gamebanana` record. Optional
`notices` lists shipped license files; otherwise the mod's `LICENSE` and vendor
licenses are used. Then run `./build.sh build`, `./build.sh test` and
`python3 scripts/mod_distribution.py package NAME`. Without `candidate_builder`
the packager refuses DEVELOPMENT mods. Status stays DEVELOPMENT.

A release lives at `build/NAME/releases/VERSION/`, with versioned ZIP, named
runtime folder, README.md, README.html, GAMEBANANA_README.html, NOTICES.txt,
NOTICES.html, release manifest and SHA256SUMS. The ZIP contains only README.md
beside the named runtime folder. The README is identical inside/outside the ZIP;
runtime folders contain no guides/notices/manifests. Keep notices and HTML outside
ZIPs. Support refreshes back up the prior release and preserve runtime bytes.
Archive superseded releases outside active releases.

### Starting a new version

1. Search the mod for the old version (`grep -rnw OLD mods/NAME`) and update
   every copy: `mod.json` and any build/path scripts, plugin labels and test
   expectations that repeat it. Ignore unrelated hits such as register names.
2. If the old version is READY_TO_DISTRIBUTE or PUBLISHED, copy
   `build/NAME/releases/OLD/` to `backups/accepted/NAME/OLD-before-CHANGE/release/`.
   Beside it, put the committed `DEVELOPMENT.md`, `DISTRIBUTION.json`,
   `EVIDENCE.json` and `README.md`, and a `preservation.json` with `version`,
   `release_sha256` (one entry per release file), `"runtime": "UNCHANGED"` and
   `reason`. Confirm the copy with `diff -r`, then remove the build copy and
   any empty `releases/`. `check` allows only a READY version there.
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
5. Update the mod's DEVELOPMENT.md (current state and release table) and
   `docs/LOCAL_STATE.md`. The root README table lists the approved release,
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
| Compatibility and known issues | Relevant conflicts, visible limitations and steps the user can take. Omit this section when there is nothing useful to say. |

Use `### Settings` and `### INI settings` below Usage when applicable. Settings
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

Commit coherent validated work locally after reviewing staged paths. Never
install, activate, launch, edit saves, publish or push implicitly.
