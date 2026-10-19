# Developing key-quest-markers

Run `./build.sh` from any directory; it defaults to `build`. Commands: `doctor`, `prepare`, `build`, `test --host`, `test`, `verify`, `package` and `export --output DEST`. Only `prepare --fetch` downloads dependencies. Default builds use the pinned compiler image offline and stage candidates.

Copy `build.local.example.json` to ignored `build.local.json`, then set explicit main, SDK and Forge inputs. Their supported SHA-256 values are in `dependencies.lock.json`; the main build ID and hook signatures are checked too. Changing dependencies or hook sites requires a reviewed lock update, ABI/import checks, focused fixtures and GE liveness revalidation.

Use the configured Python environment for the exact `requirements.txt` versions. Host tests need no game files, installed emulator or parent checkout. Complete ARM/resource fixtures require the supplied inputs. Forge headers and required helper snapshots live in this folder. Outputs stay under the coordinating workspace's root build/work, or this repo's ignored local build/work after export.

`build --diagnostics` enables developer captures without diagnostic UI. It cannot be packaged with `package --release`. A release requires an approved, versioned `DISTRIBUTION.json`, matching payload hashes and completed tests; earlier releases stay immutable. A DEVELOPMENT candidate needs `version`, `package_name`, `archive`, `candidate`, `candidate_builder` (`scripts/build.py`) and `gamebanana` in `DISTRIBUTION.json`, then `./build.sh test` and `./build.sh package`. It writes `build/NAME/candidates/VERSION/delivery/`. Runtime acceptance remains scoped to its recorded version, even when cleanup builds pass static fixtures.

Use settings-only panels. Format logs in Forge callbacks, outside native hooks. Keep one startup summary, meaningful committed preference changes and readable actionable failures. Never reset failure reason masks; unchanged frames stay silent. Overlays and background work run with settings panels closed.

Export only `EXPORT.json` entries. `source-export.json` records the parent commit and source/export hashes. Exports omit game assets, outputs, caches, backups, private configurations, historical asset editions and Git metadata. Initialize remotes and publish separately.

## Primary-only plugin configs

Configs use one plugin-specific primary INI only. Do not create, read, recover
from or delete `_backup` configs, and do not imitate the game's save backups.
Validate before writing, flush and verify the primary, then commit through
Forge's counted save mount. Balance handles and mounts on every failure path.
Keep session settings on failure; previous disk contents are not guaranteed.
Missing or invalid primary files use defaults. Save controls remain explicit.
