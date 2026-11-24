# Validate and deliver a Switch mod

These are the original workspace's release conventions. In another project, use its explicit delivery contract while retaining exact-byte provenance and honest validation scope.

## Evidence that reaches the behavior

| Check | Establishes | Does not establish |
| --- | --- | --- |
| Host unit/policy tests | Parsers, classifications, bounds, state decisions | Native calls or game output |
| Original ARM execution with doubles | Selected native instructions, argument/state preservation, rollback | Real GPU, scheduling, all gameplay |
| Target build / import / layout checks | Artifact architecture, export resolution, pinned ABI/signatures | Activation or runtime compatibility |
| Package/full distribution check | Delivery inventory, support records, hashes and release rules | Installation or user acceptance |
| Fresh log + exact installed hash | Particular launch/load and recorded behavior | Every feature or platform |
| User gameplay acceptance | Reported behavior for the identified payload/session | Exhaustive scenario coverage |

For Switch Rust/GCC NROs, verify the [target flags and final relocation destinations](api-and-builds.md#rust-nro-relocation-requirements) before packaging. Retain the ELF/NRO hashes and any linker errors; a clean `-z text` link and absent TEXTREL flags complement the destination scan. Treat hardware-test rebuilds as new DEVELOPMENT candidates, preserving accepted artifacts and their original runtime scope.

A double that builds the value the code reads proves only the code's own belief about it: model the game's layout as a game reader shows it, and pick test inputs whose wrong reading gives a different result (WishFinder r130's in-quest Quest Info case used a quest with nothing to list, so a lookup that read quest ID 0 passed).

Use relevant mod-local tests and `verify`. Prefer existing native fixtures over assertions that only mirror source wording. Exercise allocation, short read/write, mapping, partial publication, foreign patch, nested entry, teardown, and fallback failures where changed. Existing damages tests cover mailbox concurrency and thread exit, native pool failure, ARM state, projection scaling, and actual ImGui pixel scenes. GUI fixtures execute native materials/destruction. Input fixtures execute classifiers/evaluator. Reward fixtures execute count bodies and ownership/quantity preflight.

No automated in-game suite exists. After a reported run, read that emulator's latest log and match game/version, loader, mod set, NRO/assets, exceptions, and user observation. Preserve logs before another launch. A build recipe's `runtime_test: NOT RUN` is compatible with a separate dated accepted runtime record. Do not rewrite either into broader evidence.

## Versioning and packaging

Each `mods/NAME/DISTRIBUTION.json` is authoritative. DEVELOPMENT is unapproved work, LOCAL_ONLY is local tooling/dependency, READY_TO_DISTRIBUTE is approved verified local delivery, and PUBLISHED additionally records URL/date. Distribution approval and exact-binary gameplay acceptance remain distinct.

Runtime changes require a new version. Promote accepted candidate bytes without rebuilding. Keep the last gameplay-accepted build under `build/NAME/`, and treat `backups/` as an optional archive. Support-only refreshes back up the prior delivery and keep runtime hashes unchanged. Do not rebuild into a candidate/output directory whose receipts an immutable release still references.

The payload NRO hash identifies a build. An archive's hash moves with any repackaging or README refresh, so record both and scope acceptance to the NRO. A comment-only source edit is not a runtime change once a scratch rebuild gives the released NRO hash: rebuild outside `build/NAME/`, never into a folder an immutable release references.

Version diagnostic/prototype candidates before manual testing too. Set DEVELOPMENT, run relevant tests/build/verify, package and run the full distribution check, then record source/loader revisions and NRO/assets/ZIP hashes before supplying bytes for an authorized run. Follow-up runtime changes get another version. Record observations against those exact hashes and promote unchanged accepted bytes only with release approval. Do not put the first version/distribution record after the acceptance loop.

The packager accepts a DEVELOPMENT mod only when `DISTRIBUTION.json` registers `version`, `package_name`, `archive` (`NAME-VERSION-candidate.zip`), `candidate` (`build/NAME/candidates/VERSION/delivery`), `candidate_builder` (`scripts/build.py` for scaffolded mods) and `gamebanana`. The builder writes the delivery, and `verify_candidate` in `scripts/mod_distribution.py` checks it. Without `candidate_builder` the refusal is a missing registration, not a ban on candidates.

From the workspace root:

```sh
python3 scripts/mod_distribution.py package NAME
python3 scripts/mod_distribution.py check
```

Packaging a new DEVELOPMENT candidate does not rewrite the `sha256` pins in `payloads`, and `check` does not compare them for a DEVELOPMENT mod: Skin Loader r18's candidate kept r17's NRO and manifest pins until the release packaging. After each candidate package, compare every pin with its staged file, and set them to the bytes that ran before promoting. A `target/` folder inside the mod blocks `./build.sh build` ("Preserving existing target/ or loose NRO"); besides a plain `cargo` run, the editor's rust-analyzer can make one. It is a cargo cache: move it aside, then build.

The full `check` is required before readiness or commit. `--source-only` is not a readiness check. Use mod-local packaging when building an independent export. Follow the current command's help for support refresh options.

A release under `build/NAME/releases/VERSION/` has versioned ZIP, named runtime folder, README.md/HTML/GameBanana HTML, notices text/HTML, manifest, and SHA256SUMS. The ZIP contains README.md beside the named runtime folder. That README matches its adjacent copy. Runtime folders contain payloads only, with `romfs/nativeNX/...`, `exefs/`, or `cheats/<build-id>.txt` directly inside, plus the mod-manager `manifest.json` (format in docs/DEVELOPMENT.md, "Releases"; version rN is `0.N.0`) that every new candidate or release ships and `package` requires (source: `scripts/mod_manifest.py`). HTML, legal notices, receipts, and checksums stay outside the ZIP.

## Player guides and legal records

Release README order: Requirements, Installation, Usage, Update and removal, then Compatibility and known issues when useful. Put settings/INI subsections under Usage. Tables use `Setting | Default | Effect` or `Action | Input`. Give complete Eden and Ryujinx installation destinations, actual loader requirements, and relevant conflicts. A co-installed plugin or build fixture alone does not establish a dependency. Modern Weapon Controls does not require Better Input merely because both appeared in an accepted run.

Keep research, testing history, backups, approval, and build instructions in developer records. Use plain Green/Red/Grey and the complete Humanizer review. Credits are linked `Component by Author`, one entry ending at the author. Credit Fexty's fork and the original Forge separately. Preserve Skyline Project/Jeffi and other holders' legal text. Project-owned copyright is PurplefinNeptuna.

`THIRD_PARTY.md` records source provenance. `DISTRIBUTION_NOTICES.md` and shipped license files cover linked/shipped code/assets and applicable credits. Programming languages, compiler tools, and host-only fixtures alone do not belong in runtime notices. Never invent license terms, dates, authors, AI provenance, or human-review claims.

Publication requires a fresh check of the applicable GameBanana policy. The saved packaging rules require actual AI assistance/software/scope disclosures and applicable source credits. Known HTML acceptance pitfalls: encode equals signs in code examples as `&#61;`, keep apostrophes literal instead of `&#x27;`, and preserve copyright/international names as literal UTF-8 instead of numeric references. Keep real INI and Markdown values unchanged. Packaging is not publication/moderation approval.

## Export and commit

Refresh `EXPORT.json` deliberately. Export source and approved dependency snapshots, excluding private configs, original game/runtime binaries, ignored output trees, and unsafe paths. Validate outside the parent workspace with explicitly supplied copied inputs. Missing private inputs must remain an explicit verification limit.

Inspect status and staged paths, run `git diff --check` and the full distribution check, preserve custom Git hooks, and commit coherent authorized changes locally. Installation, activation, launch, save/settings changes, publication, and push need their own task authorization.

Sources: `docs/DEVELOPMENT.md`, `scripts/mod_distribution.py`, `templates/standalone/AGENTS.md`, maintained mod `build.sh`, `EXPORT.json`, `DISTRIBUTION.json`, `EVIDENCE.json`, tests, notices, and source/release READMEs.

## Review before you report

Do this after the tests pass and before the report. Each item is a question a passing test
suite does not answer. Any "no" or "not checked" goes in the report.

1. **Trace one real press end to end.** Follow the actual values from input to what is stored,
   shown and later cleared, through every function, with numbers from a log or data file.
2. **Every number's base.** For each level, index and count crossing a function or file, write
   where it counts from and check both sides agree.
3. **Every key, both ends.** List each place a key or ID is built and each place it is compared,
   for every state that reaches them. Try the craft path and the upgrade path separately.
4. **Every call in a loop.** Read the callee's queue and limit, and try the largest input the real
   data produces (measure it from the RomFS, do not guess). Does a failure change what the user hears?
5. **Run the rule over the whole data set.** A script over every RomFS row costs seconds. Print how
   many rows each branch takes, and read the rows that look unusual.
6. **Compare with something that does not come from your code**: the tester's list, a save file, a
   log from another mod. If the mismatch has an explanation, test that explanation on other cases.
7. **Reread the docs you changed against the code**: `rg` each number, version and claim. Check
   `mod.json`, the plugin label and the zip name carry the new version.
