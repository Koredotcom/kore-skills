"""Regression checks for distribution drift and broken plugin resources."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("parity", REPO / "scripts/check_marketplace_parity.py")
parity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(parity)


class MarketplaceParityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plugin = self.root / "plugins/sample"
        self.codex = self.plugin / ".codex-plugin/plugin.json"
        self.claude = self.plugin / ".claude-plugin/plugin.json"
        self.catalog = self.root / ".claude-plugin/marketplace.json"
        manifest = {"name": "sample", "version": "1.0.0", "description": "Synthetic plugin", "skills": "./skills/"}
        self.write(self.codex, {**manifest, "interface": {"displayName": "Sample"}})
        self.write(self.claude, manifest)
        self.write(self.root / ".agents/plugins/marketplace.json", {
            "name": "kore-skills", "plugins": [{"name": "sample", "source": {"source": "local", "path": "./plugins/sample"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Productivity"}]})
        self.write(self.catalog, {"name": "kore-skills", "owner": {"name": "Example"}, "plugins": [
            {"name": "sample", "source": "./plugins/sample", "description": "Synthetic plugin"}]})
        skill = self.plugin / "skills/example/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("---\nname: example\ndescription: Synthetic fixture.\n---\n")

    def write(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    def mutate(self, path, transform):
        data = json.loads(path.read_text())
        transform(data)
        self.write(path, data)

    def assert_problem(self, fragment):
        self.assertTrue(any(fragment in error for error in parity.check_repository(self.root)), fragment)

    def test_shared_layout_passes(self):
        self.assertEqual(parity.check_repository(self.root), [])

    def test_version_drift_fails(self):
        self.mutate(self.claude, lambda d: d.update(version="1.0.1"))
        self.assert_problem("version differs")

    def test_missing_catalog_entry_fails(self):
        self.mutate(self.catalog, lambda d: d.update(plugins=[]))
        self.assert_problem("inventories differ")

    def test_duplicate_catalog_entry_fails(self):
        self.mutate(self.catalog, lambda d: d["plugins"].append(d["plugins"][0].copy()))
        self.assert_problem("duplicate plugin")

    def test_separate_skill_copy_fails(self):
        self.mutate(self.claude, lambda d: d.update(skills="./claude-skills/"))
        self.assert_problem("skills differs")

    def test_missing_skill_resources_fail(self):
        (self.plugin / "skills/example/SKILL.md").unlink()
        self.assert_problem("contains no skills")

    def test_source_escape_fails(self):
        self.mutate(self.catalog, lambda d: d["plugins"][0].update(source="./../outside"))
        self.assert_problem("source must reference shared root")

    def test_resource_symlink_escape_fails(self):
        external = self.root / "external.json"
        self.write(external, {"mcpServers": {"sample": {"command": "example"}}})
        (self.plugin / ".mcp.json").symlink_to(external)
        for path in (self.codex, self.claude):
            self.mutate(path, lambda d: d.update(mcpServers="./.mcp.json"))
        self.assert_problem("external mcpServers path")

    def test_codex_policy_regression_fails(self):
        path = self.root / ".agents/plugins/marketplace.json"
        self.mutate(path, lambda d: d["plugins"][0].pop("policy"))
        self.assert_problem("preserve installation/authentication policy")

    def test_invalid_json_fails(self):
        self.claude.write_text("{")
        self.assert_problem(".claude-plugin/plugin.json")


if __name__ == "__main__":
    unittest.main()
