import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts/snapshot_package.py"
spec = importlib.util.spec_from_file_location("snapshot_package", SCRIPT)
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.root = self.work / "package"
        self.root.mkdir()
        (self.root / "agent.abl").write_text("synthetic source\n")

    def manifest(self, value):
        path = self.work / "baseline.json"
        path.write_text(json.dumps(value))
        return path

    def test_deterministic_across_directory_and_creation_order(self):
        (self.root / "config.json").write_text('{}\n')
        other = self.work / "other"
        other.mkdir()
        (other / "config.json").write_text('{}\n')
        (other / "agent.abl").write_text("synthetic source\n")
        self.assertEqual(snapshot.snapshot(self.root), snapshot.snapshot(other))

    def test_add_change_remove_and_unchanged(self):
        (self.root / "removed.txt").write_text("remove")
        (self.root / "same.txt").write_text("same")
        before = snapshot.snapshot(self.root)
        (self.root / "removed.txt").unlink()
        (self.root / "agent.abl").write_text("changed")
        (self.root / "added.txt").write_text("add")
        delta = snapshot.compare(snapshot.snapshot(self.root), before)
        self.assertEqual(delta, {"added": ["added.txt"], "changed": ["agent.abl"], "removed": ["removed.txt"], "unchanged_count": 1})

    def test_empty_package_is_valid(self):
        (self.root / "agent.abl").unlink()
        value = snapshot.snapshot(self.root)
        self.assertEqual(value["files"], [])
        self.assertEqual(snapshot.read_manifest(self.manifest(value)), value)

    def test_reject_symlink_file_directory_and_root(self):
        for target in [self.root / "agent.abl", self.work]:
            link = self.root / "link"
            link.symlink_to(target)
            with self.assertRaises(snapshot.SnapshotError):
                snapshot.snapshot(self.root)
            link.unlink()
        root_link = self.work / "root-link"
        root_link.symlink_to(self.root)
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.snapshot(root_link)

    def test_bounds_are_enforced(self):
        for setting in ["MAX_BYTES", "MAX_FILES"]:
            with patch.object(snapshot, setting, 0), self.assertRaises(snapshot.SnapshotError):
                snapshot.snapshot(self.root)

    def test_invalid_or_tampered_manifest_is_rejected(self):
        value = snapshot.snapshot(self.root)
        value["files"][0]["sha256"] = "0" * 64
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.read_manifest(self.manifest(value))
        for name in ["../outside", "/absolute", "a/../b", "a\\b", "", "."]:
            value = snapshot.snapshot(self.root)
            value["files"][0]["path"] = name
            value["digest"] = snapshot.digest(value["files"])
            with self.subTest(name=name), self.assertRaises(snapshot.SnapshotError):
                snapshot.read_manifest(self.manifest(value))

    def test_duplicate_paths_and_bad_types_are_rejected(self):
        value = snapshot.snapshot(self.root)
        value["files"].append(dict(value["files"][0]))
        value["digest"] = snapshot.digest(value["files"])
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.read_manifest(self.manifest(value))
        for bad in [[], {"schema_version": 1, "files": None}, {"schema_version": 2}]:
            with self.assertRaises(snapshot.SnapshotError):
                snapshot.read_manifest(self.manifest(bad))

    def test_cli_comparison_is_read_only(self):
        before = snapshot.snapshot(self.root)
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root), "--compare", str(self.manifest(before))], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["comparison"]["unchanged_count"], 1)
        self.assertEqual(before, snapshot.snapshot(self.root))

    def test_cli_failure_has_no_partial_json(self):
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.work / "missing")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
