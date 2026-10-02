#!/usr/bin/env python3
"""Focused checks for the dumper's host-tested JSON and copied-dump ingestion."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import dti_dumper


class DumperTests(unittest.TestCase):
    def test_arm_json_helper_on_host(self):
        helper = dti_dumper.RECIPE / "json.rs"
        tools = dti_dumper.TOOLS
        compiler = tools / "rustup/toolchains/nightly-x86_64-unknown-linux-gnu/bin/rustc"
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "format.rs"
            source.write_text('''use std::fmt::Write;
mod json { include!(r#"''' + str(helper) + '''"#); }
fn main() {
    let fixtures: &[&[&str]] = &[&[], &[""], &["quote\\\"", "slash\\\\", "line\\n", "tab\\t", "nul\\0", "日本語"]];
    for fixture in fixtures {
        let mut output = String::from("[");
        let mut first = true;
        for value in *fixture {
            json::separator(&mut output, &mut first);
            write!(&mut output, "{}", json::JsonString(value)).unwrap();
        }
        output.push(']'); println!("{output}");
    }
}
''')
            executable = directory / "format"
            subprocess.run([str(compiler), "--edition=2024", str(source), "-o", str(executable)], check=True)
            lines = subprocess.check_output([str(executable)], text=True).splitlines()
            self.assertEqual([json.loads(line) for line in lines],
                             [[], [""], ['quote"', 'slash\\', 'line\n', 'tab\t', 'nul\0', '日本語']])

    def test_ingest_preserves_source_and_vtable_kind(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "copied.json"
            rows = [{"dti": "Example", "vft": 12, "vft_kind": "object", "properties": []},
                    {"dti": "Skipped", "vft": 24, "vft_kind": "dti", "properties": [], "skipped": True}]
            source.write_text(json.dumps(rows))
            original = source.read_bytes()
            previous = dti_dumper.WORK
            dti_dumper.WORK = root / "work"
            try:
                with contextlib.redirect_stdout(io.StringIO()): dti_dumper.ingest(source)
                indexed = [json.loads(line) for line in (dti_dumper.WORK / "dti/dti.jsonl").read_text().splitlines()]
                self.assertEqual(indexed, rows)
                self.assertEqual(source.read_bytes(), original)
                provenance = json.loads((dti_dumper.WORK / "dti/provenance.json").read_text())
                self.assertFalse(provenance["runtime_build_verified"])
                source.write_text(json.dumps(rows[:1]))
                with self.assertRaisesRegex(ValueError, "different runtime dump"):
                    dti_dumper.ingest(source)
            finally:
                dti_dumper.WORK = previous

    def test_rejects_ambiguous_vtable_and_invalid_json(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "bad.json"
            source.write_text('[{"dti":"Example","properties":[]}]')
            with self.assertRaisesRegex(ValueError, "Ambiguous vtable"):
                dti_dumper.ingest(source)
            source.write_text('[{"dti":"Example","properties":[]},]')
            with self.assertRaises(json.JSONDecodeError):
                dti_dumper.ingest(source)


if __name__ == "__main__":
    unittest.main()
