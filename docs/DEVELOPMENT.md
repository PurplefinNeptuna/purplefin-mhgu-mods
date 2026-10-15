# Development and distribution

## Supported loaders and source updates

Switch development uses unmodified [Fexty's Forge fork](https://github.com/Fexty12573/forge)
1.5.1, based on Jeffi's original Forge, at
`tools/forge-local/` (`b23e114a23f41c9a8e2fd34b2f4df2a2102d0ee1`).
Native ARM32 Hook is 24 bytes: target/detour/original/context pointers at
0/4/8/12, ctx_cell at16 and has_ctx at20. Forge pools ordinary/context
trampolines; verify allocations, ownership and the actual headers at each boundary.
Forge PC uses stock 0.2.1 at `tools/forge-pc-local/`. forge-rs source is1.5.0
at `tools/forge-rs/`; its compatible converter is separately pinned at1.4.1.

Update the existing checkout from its official remote; do not create an extra
upstream clone/worktree. Keep old revisions in Git when research needs them.
Do not apply or recreate the retired loader, legacy Better Input, renderer,
mutex or PC support patches. Source updates never replace installed packages.

## Independent mod builds

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

Scaffold with `python3 scripts/mod_distribution.py init NAME --kind plugin`
(or resource, cheat, tool). PC plugins add `--platform forge-pc` and live in
separate `<name>-pc` folders. Default PC builds/verifies/packages require both
Linux x64 SO and Windows x64 DLL; single-target output is development-only.
Refresh `EXPORT.json` deliberately; exports exclude runtime/game binaries,
private configurations, ignored trees and unsafe paths. Validate exported source
outside this workspace using explicitly supplied copied inputs.

## Native implementation rules

Search saved Ghidra/DTI before gameplay work; see [research](RESEARCH.md).
Use Forge's callbacks, logging, input, memory, singleton, hooks, filesystem and
render APIs where applicable. Document a verified API gap before using a lower
level path. Validate pointers, signatures, allocation failures and rollback.
Explain native offsets, units, data flow, ownership, nested hooks, TLS borrows
and unsafe caller requirements beside substantial code. Preserve audited assembly.

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

A release lives at `build/NAME/releases/VERSION/`, with versioned ZIP, named
runtime folder, README.md, README.html, GAMEBANANA_README.html, NOTICES.txt,
NOTICES.html, release manifest and SHA256SUMS. The ZIP contains only README.md
beside the named runtime folder. The README is identical inside/outside the ZIP;
runtime folders contain no guides/notices/manifests. Keep notices and HTML outside
ZIPs. Support refreshes back up the prior release and preserve runtime bytes.
Archive superseded releases outside active releases.

`THIRD_PARTY.md` records development provenance;
`DISTRIBUTION_NOTICES.md` and current licenses cover only shipped components and
applicable authors, retaining copyright/license wording and Forge credits.
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
| Update and removal | Close the game, explain which files/folder to replace or remove, and preserve settings stored inside a PC mod folder. |
| Compatibility and known issues | Relevant conflicts, visible limitations and steps the user can take. Omit this section when there is nothing useful to say. |

Use `### Settings` and `### INI settings` below Usage when applicable. Settings
tables use `Setting | Default | Effect`. Control tables use `Action | Input`.
Write overlay paths as **Plugin UI > Plugin name**, keeping the actual UI name
and button labels exact. Use colour/grey consistently, with plain colour names
such as Green and Red. Gathering/objective labels belong in research records.

Switch installation steps give both Eden and Ryujinx destinations. PC steps
give the exported game's `mods/0100770008DD8000/` destination and retain both
platform libraries. Include hot-reload restrictions only where required by
that mod. Link Fexty's Forge fork for Switch and GURecomp's Forge PC for PC.
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
