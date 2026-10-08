# Standalone mod development

Read README.md, DEVELOPMENT.md, DISTRIBUTION.json and dependencies.lock.json. This folder owns its source, tests, recipes, notices and snapshots. Do not import sibling mod folders, installed emulator packages, personal paths or parent Git history. Configure supplied inputs in ignored build.local.json. Use build.sh; downloads require explicit prepare --fetch. Preserve inputs and immutable accepted releases. Panels contain settings only, with concise lifetime-deduplicated Forge logs outside hot hooks. Preserve background callbacks, ARM32 ABI, NZCVQ and all live GE state; unsupported APSR_g writes are forbidden. Static fixtures do not establish gameplay acceptance. Commit validated changes locally; never install, activate, publish or push without a user request.

## Primary-only plugin configs

Configs use one plugin-specific primary INI only. Do not create, read, recover
from or delete `_backup` configs, and do not imitate the game's save backups.
Validate before writing, flush and verify the primary, then commit through
Forge's counted save mount. Balance handles and mounts on every failure path.
Keep session settings on failure; previous disk contents are not guaranteed.
Missing or invalid primary files use defaults. Save controls remain explicit.

## Release ZIP layout

Ready and published ZIPs include `README.md` at the archive root beside the named
mod folder. Keep only runtime files inside the mod folder. The archived README
must match the adjacent release README. Use the distribution packager and full
check; support refreshes preserve runtime bytes and back up the previous ZIP.

Notices/licenses stay outside the ZIP. Supply combined `NOTICES.txt` and a
notices-only `NOTICES.html` alternative beside the ZIP, formatted as a paste-ready
GameBanana fragment. Preserve license wording.

Release notices cover only the package's current code, assets and applicable
credits, including Forge where used. Preserve required copyright and license
text. Exclude unrelated mods, development tools, local source paths, Git/history
references and previous-license commentary. Keep development provenance in
`THIRD_PARTY.md`; use dedicated `DISTRIBUTION_NOTICES.md` for release credits and
component notices, alongside current license files. Notices must be usable
without a source checkout.
