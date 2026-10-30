# Standalone mod development

Read README.md, DEVELOPMENT.md, DISTRIBUTION.json and dependencies.lock.json.
This folder owns source, recipes, tests, dependency snapshots and export lists.
No sibling mod, personal path, installed game/emulator or parent history is a
build dependency. Use build.sh and copied inputs from build.local.json; fetch
only explicitly. Validate dependency/input fingerprints and preserve originals.

Comments state the current contract: native offsets/units, data flow, lifetimes,
ownership and unsafe caller rules. Run IDs (r23), run narratives and refuted
approaches go in DEVELOPMENT.md history, never in source. Preserve NZCVQ and
all live state; audit GE and never require APSR_g/APSR_nzcvqg writes. Keep
native ownership/rollback.
Use Forge facilities before private substitutes; document any verified gap.

Settings use closed compact unframed Plugin UI tree rows, stable IDs and paired
TreePop. No settings means no panel. Background callbacks continue with rows
closed. Diagnostics use concise process-deduplicated logs outside hot hooks.
Primary-only INIs use explicit saves and balanced counted mount/handle cleanup;
never create/read/recover/delete `_backup` configs. Keep session state on errors.

Runtime changes require new versions. DISTRIBUTION.json is authoritative.
After relevant host/native tests, package and run the full distribution check.
Ready ZIPs contain only README.md beside the named runtime folder; the same
README stays adjacent. Keep README.html, GAMEBANANA_README.html, NOTICES.txt,
NOTICES.html, manifests and checksums outside ZIPs. Include current component
licenses/credits; development provenance is separate in THIRD_PARTY.md.
Use PurplefinNeptuna for project-owned copyright. Preserve upstream holders and
legal text, with exact source provenance. Include linked libraries and shipped
assets in release notices. Keep compiler tools and host-only fixtures in
development provenance.
GameBanana descriptions disclose actual AI assistance/software/scope and
applicable authors. Never infer provenance; recheck policy before publishing.
Static/host/build results are separate from exact binary gameplay acceptance.
Commit validated work locally; never install, activate, launch, edit saves,
publish or push implicitly. Preserve accepted artifacts and unrelated edits.

Target upstream Forge 1.5.1, native ARM32 Hook 24 and the actual 70-byte metadata
record. Do not restore retired custom loader shims or patches.

Release READMEs address mod users. Use Requirements, Installation, Usage,
Update and removal, then Compatibility and known issues when relevant.
Put Settings/INI subsections under Usage. Settings tables use Setting/Default/Effect,
controls use Action/Input, and installation includes exact platform paths.
Apply the full Humanizer process, use plain colour names, and omit maintainer
history/testing/approval material and unrelated-mod advice.
README credits use only linked Component by Author, ending after the name.
List forks/original projects separately. Keep explanations in provenance
records and preserve separate AI disclosures and legal notices.
