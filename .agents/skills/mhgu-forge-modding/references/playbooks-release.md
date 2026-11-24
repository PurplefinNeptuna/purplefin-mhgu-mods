# Playbooks: promote, refresh, consolidate, finish

## P5 Promote a candidate

Only when the user explicitly approves this exact version for distribution. Approval is not a gameplay result unless they also report a run. If the version still carries test scaffolding, run-history comments or tester text in its README, say so and propose [P7](#p7-consolidate-after-acceptance) first. If this version is P7's output, its bytes were not the ones the user accepted. Ask whether to run it or promote it on static validation, and quote the choice in `approval.basis`, with the accepted version named as the runtime evidence.

1. Confirm the candidate files still match the `DISTRIBUTION.json` payload hashes. Do **not** rebuild: promotion ships the exact tested bytes.
2. Copy the candidate delivery folder and the current records into `backups/accepted/NAME/rN-distribution-approved/`.
3. Edit `DISTRIBUTION.json`: `status` = `READY_TO_DISTRIBUTE`, `archive` = `NAME-rN.zip` (drop `-candidate`), remove `candidate` and `candidate_builder`, add `approval` with `date` and `basis` (quote what the user approved and what it does *not* prove). Set `mod.json` version.
4. Record any user runtime report in `EVIDENCE.json`, scoped to the exact hashes and emulator.
5. `python3 scripts/mod_distribution.py package NAME` writes `build/NAME/releases/rN/`. Then run the full `check`.
6. Update `README.md` (root table), `docs/LOCAL_STATE.md` and the mod's DEVELOPMENT.md current-state paragraph. Commit.

## P6 Support-only refresh

For a READY mod whose README, DEVELOPMENT.md or EVIDENCE.json changed but whose runtime did not. The release folder keeps copies of these files, so `check` will report `Stale or modified release file`.

1. Make the doc change.
2. `python3 scripts/mod_distribution.py package NAME --refresh-support`. It refuses if any runtime byte would change, backs up the old release folder to `backups/NAME/distribution-support/<timestamp>/`, then rewrites only the support files.
3. Compare the ZIP SHA-256 before and after (it changes only when README.md changed, because the ZIP contains README.md). Run the full `check`. Commit.

## P7 Consolidate after acceptance

Run this when the user accepts a behaviour (or closes a phase) and before the next feature or a P5 promotion. Experiments add code; this playbook removes it. It is a P2 change with a new `rNEW`. Visible behaviour stays the same: anything that must change position or format gets a host test showing identical output on the accepted values.

Never combine it with a behaviour change: a rejected build then has no read-backs left to diagnose it. Before stripping, confirm the accepted candidate stays under `build/NAME/candidates/rN/` and list it in `docs/LOCAL_STATE.md`, because `rNEW`'s bytes will not be the accepted ones (P5 says what to ask next).

1. **List what the accepted build no longer needs.** For each item, grep its uses first and delete it only when nothing live reads it:
   - test controls: forced values, sliders, prototype steps, Plugin UI test panels;
   - core helpers kept only "as a record" of a refuted approach (a line in DEVELOPMENT.md's "Do not" list is enough);
   - sampled fields, counters and statics that nothing reads or prints;
   - probes and log lines whose question the user's acceptance answered. Keep one line per lifecycle event (inserted, failed with stage, torn down). Delete the host tests that only covered removed code. Keep every test for code that remains.
2. **Re-express tuned values in their own frame.** A value the user dialled in is stored relative to what it was measured on (an offset from, or a fraction of, the node rect), never as an absolute screen pixel. Add a host test showing the new form gives the accepted outputs on the measured rect.
3. **Fix stale wording.** For every feature, control or mode removed in this or earlier versions, grep its words in `src/`, `core/src/` and log strings (for example `slider|forced|prototype|diagnostic|panel`). Rename identifiers named after the experiment. Check the startup log line and each module's top comment against what the code does now.
4. **Rewrite comments as current contracts.** Offset, unit, owner, why, in a line or two. Run IDs and what a run printed go in EVIDENCE.json; refuted approaches go in DEVELOPMENT.md's "Do not" list. Leave audited assembly bytes unchanged. Gate: `grep -nE '\br[0-9]{1,3}\b' src core/src` returns nothing. The gate cannot see a comment that drops its run ID and keeps a refuted claim, so also check each native claim in a comment against DEVELOPMENT.md and its "Do not" list.
5. **Split the README.** README.md follows the release README standard in docs/DEVELOPMENT.md with nothing aimed at the tester. Tester steps, what to report and the log-line and stage-code reference go in `mods/NAME/TESTING.md` (outside the ZIP). Gate: `grep -nE 'Tell me|WSG r[0-9]|stage [0-9]{2}|run showed' mods/NAME/README.md` returns nothing. Refresh the export list after adding a file (from the mod folder: `python3 scripts/export_source.py --refresh`).
6. **Collapse DEVELOPMENT.md's head.** Exactly one current-state paragraph, then the commands, files and offset tables, corrected to `rNEW`, then a short "Do not" list and open items. Merge stacked "Current state:" paragraphs into one for `rNEW`. Delete run logs and superseded paragraphs: Git keeps them, and EVIDENCE.json keeps the dated results. A later result that overturns a reading corrects that fact in place.
7. Continue with P2 steps 6 to 10. In the report, give the line counts of `src/` and `core/src/` before and after, plus `git diff --stat`.

## Finish every playbook

```sh
git status --short
git diff --check
python3 scripts/mod_distribution.py check
git add <only the paths you changed>
git diff --cached --name-only
python3 scripts/mod_distribution.py check --staged
git commit
```

The pre-commit hook rejects trailing whitespace and blank lines at end of file. If a support copy was refreshed in P6 and you then fix whitespace in that doc, refresh again.

## Report template

```text
What changed: <one or two sentences, user-visible behaviour>
Version/status: <rN> DEVELOPMENT candidate | READY_TO_DISTRIBUTE
Files: <ZIP path> sha256 <hash>
Validated: <host tests, ARM tests, verify, package, check — counts if known>
Not validated: gameplay NOT RUN on <emulators/hardware>
To test: <numbered steps the user can do in game, what they should see;
         the same text goes in mods/NAME/TESTING.md, never in README.md>
Open questions: <unknowns, assumptions>
```

Never write "works", "fixed" or "tested" for something only built or unit-tested. Say "builds and passes host tests; not run in game".
