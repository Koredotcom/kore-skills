from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from review_coverage import validate
from xo_export_parser import parse_condition
from xo_graph import walk


def fixture():
    return {
        "_id": "synthetic-bot", "name": "Synthetic flow", "dialogs": [
            {"_id": "dialog-a", "name": "Same title", "nodes": [
                {"nodeId": "first", "componentId": "shared", "type": "botAction", "transitions": [{"default": "second"}]},
                {"nodeId": "second", "componentId": "shared", "type": "botAction", "nodes": [
                    {"nodeId": "inline", "componentId": "message", "type": "message"}]},
                # No transition enters this node. It must still be expanded.
                {"nodeId": "isolated", "componentId": "composite", "type": "entity"}]},
            {"_id": "dialog-b", "name": "Same title", "isHidden": True, "nodes": [
                {"nodeId": "third", "componentId": "shared", "type": "botAction"}]}],
        "dialogComponents": [
            {"_id": "shared", "type": "botAction", "name": "Shared operation", "success": {"nodes": [
                {"nodeId": "nested", "componentId": "script", "type": "script", "transitions": [
                    {"if": {"conjoin": "or", "tests": [
                        {"field": "context.a", "op": "eq", "value": 1},
                        {"field": "context.b", "op": "exists"}]}, "then": "end"}]}]},
             "failure": {"nodes": [{"nodeId": "failure", "componentId": "message", "type": "message"}]}},
            {"_id": "script", "type": "script", "name": "Prepare result", "script": "context.result = response.body.result;"},
            {"_id": "message", "type": "message", "name": "Show result", "message": [{"text": "Result ready"}]},
            {"_id": "composite", "type": "entity", "name": "Delivery details", "entityType": "composite",
             "entityReferences": [{"componentId": "member"}]},
            {"_id": "member", "type": "entity", "name": "Postal code", "entityType": "string",
             "message": [{"text": "Enter postal code"}], "validation": {"pattern": "[0-9]{5}"},
             "entityReferences": [{"componentId": "composite"}]},
            {"_id": "detached", "type": "futureType", "name": "Detached configuration", "custom": {"keep": "offline evidence"}}],
        "otherGraph": [{"nodeId": "outside", "componentId": "member", "type": "entity", "settings": {"retry": 7}}],
    }


class ExpandedMarkdownTests(unittest.TestCase):
    def run_export(self, data, root, name="out"):
        source = root / "botDefinition.json"
        source.write_text(json.dumps(data), encoding="utf-8")
        before = source.read_bytes()
        output = root / name
        result = subprocess.run([sys.executable, str(ROOT / "scripts/decompose_bot.py"), str(source), str(output)],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(source.read_bytes(), before)
        return output, json.loads((output / "_inventory.json").read_text()), json.loads((output / "_coverage.json").read_text())

    def test_expanded_occurrences_and_disconnected_composite_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, inv, ledger = self.run_export(fixture(), Path(tmp))
            self.assertEqual(len(inv["node_occurrences"]), 11)
            self.assertEqual(len({o["occurrence_path"] for o in inv["node_occurrences"]}), 11)
            self.assertEqual(len({o["id"] for o in ledger["node_occurrences"]}), 11)
            self.assertEqual(inv["discovery"]["physical_nodes"], 8)
            self.assertEqual(len(inv["unexpanded_nodes"]), 1)
            physical = {p for p, value in walk(fixture()) if isinstance(value, dict) and "nodeId" in value}
            retained = {o["source_pointer"] for o in inv["node_occurrences"]} | {n["source_pointer"] for n in inv["unexpanded_nodes"]}
            self.assertEqual(physical, retained)
            files = sorted(output.glob("dialog_*.md"))
            self.assertEqual(len(files), 2)
            for dialog, file in zip(inv["dialogs"], files):
                text = file.read_text()
                occurrences = [o for o in inv["node_occurrences"] if o["dialog_pointer"] == dialog["source_pointer"]]
                self.assertEqual(len(re.findall(r"^## Node \d+:", text, re.M)), len(occurrences))
                for occurrence in occurrences:
                    self.assertIn(occurrence["occurrence_path"], text)
                    self.assertIn(occurrence["source_pointer"], text)
                self.assertIn("context.result = response.body.result;", text)
                self.assertIn("Result ready", text)
                self.assertNotIn("```json", text)
            first = files[0].read_text()
            self.assertIn("isolated", first)
            self.assertIn("Postal code", first)
            self.assertIn("Enter postal code", first)
            self.assertIn("[0-9]{5}", first)
            member = inv["component_definitions"][4]
            self.assertEqual(member["placement"], "no_expanded_dialog_occurrence")
            self.assertEqual(member["occurrence_paths"], [])
            self.assertIn("/dialogComponents/3/entityReferences/0/componentId", {r["source_pointer"] for r in member["reference_candidates"]})
            self.assertEqual(member["definition"]["validation"]["pattern"], "[0-9]{5}")
            self.assertEqual(ledger["unexpanded_nodes"][0]["node"]["settings"]["retry"], 7)
            self.assertIn(ledger["unexpanded_nodes"][0]["id"], {r["id"] for r in ledger["review_items"]})
            combined = (output / "_all_dialogs.md").read_text()
            for value in ("Detached configuration", "offline evidence", "outside", "/otherGraph/0", "Enter postal code"):
                self.assertIn(value, combined)
            for path in output.glob("*.md"):
                for filename in re.findall(r"\]\(([^)#]+\.\w+)(?:#[^)]*)?\)", path.read_text()):
                    self.assertTrue((output / filename).is_file(), (path.name, filename))
            # A tampered count cannot silently remove the newly preserved evidence.
            ledger["unexpanded_nodes"] = []
            self.assertIn("Unexpanded physical node totals do not reconcile", validate(ledger, []))

    def test_repeated_ids_do_not_merge_dialogs_or_drop_definitions(self):
        data = fixture()
        data["dialogs"][1]["_id"] = "dialog-a"
        data["dialogComponents"].append({"_id": "member", "type": "entity", "name": "Alternate member", "custom": "retain duplicate"})
        with tempfile.TemporaryDirectory() as tmp:
            output, inv, ledger = self.run_export(data, Path(tmp))
            self.assertEqual([d["node_count"] for d in inv["dialogs"]], [8, 3])
            self.assertEqual(len(inv["component_definitions"]), 7)
            self.assertEqual(len(ledger["component_definitions"]), 7)
            self.assertIn("retain duplicate", (output / "_components.md").read_text())
            self.assertTrue(any(i["kind"] == "duplicate_component_id" for i in inv["graph_issues"]))

    def test_cycles_missing_unknown_and_unexpanded_nodes_remain_visible(self):
        data = fixture()
        data["dialogComponents"][0]["success"]["nodes"].append({"nodeId": "cycle", "componentId": "shared", "type": "botAction"})
        data["dialogs"][0]["nodes"].append({"nodeId": "missing", "componentId": None, "type": "futureType", "custom": "retained inline"})
        with tempfile.TemporaryDirectory() as tmp:
            output, inv, _ = self.run_export(data, Path(tmp))
            self.assertLess(len(inv["node_occurrences"]), 50)
            combined = (output / "_all_dialogs.md").read_text()
            self.assertIn("retained inline", combined)
            self.assertIn("cycle", combined)
            issues = {i["kind"] for i in inv["graph_issues"]}
            self.assertTrue({"component_cycle", "unsupported_node_type", "unresolved_component", "unexpanded_node"} <= issues)

    def test_wrapper_provenance_determinism_and_redaction(self):
        data = fixture()
        data["dialogComponents"][4]["Authorization"] = "Bearer synthetic-detached-secret"
        data["otherGraph"][0]["password"] = "synthetic-orphan-secret"
        data["dialogComponents"][1]["script"] = 'const%20token%20%3D%20%22synthetic-encoded-secret%22%3B%20context.done%20%3D%20true%3B'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first, inv, ledger = self.run_export({"botDefinition": data}, root)
            second, _, _ = self.run_export({"botDefinition": data}, root, "second")
            self.assertEqual({p.name: p.read_bytes() for p in first.iterdir()}, {p.name: p.read_bytes() for p in second.iterdir()})
            rendered = "\n".join(p.read_text() for p in first.iterdir())
            self.assertNotIn("synthetic-detached-secret", rendered)
            self.assertNotIn("synthetic-orphan-secret", rendered)
            self.assertNotIn("synthetic-encoded-secret", rendered)
            self.assertIn("context.done = true;", (first / "_all_dialogs.md").read_text())
            self.assertEqual(ledger["unexpanded_nodes"][0]["source_pointer"], "/botDefinition/otherGraph/0")
            self.assertEqual(ledger["component_definitions"][4]["source_pointer"], "/botDefinition/dialogComponents/4")

    def test_registry_only_bot_retains_component_only_entities(self):
        data = {"type": "universalbot", "linkedBotsDetails": [], "dialogComponents": fixture()["dialogComponents"][3:]}
        with tempfile.TemporaryDirectory() as tmp:
            output, inv, _ = self.run_export(data, Path(tmp))
            self.assertEqual(inv["dialogs"], [])
            self.assertEqual(len(inv["component_definitions"]), 3)
            self.assertIn("Enter postal code", (output / "_all_dialogs.md").read_text())

    def test_service_prompts_payload_processors_and_unknown_settings_are_readable(self):
        data = json.loads((ROOT / "tests/fixtures/botDefinition.json").read_text())
        service = next(c for c in data["dialogComponents"] if c["type"] == "service")
        service["futureRetryPolicy"] = {"attempts": 3, "failureContext": "context.integrationFailed"}
        with tempfile.TemporaryDirectory() as tmp:
            output, inv, _ = self.run_export(data, Path(tmp))
            text = next(output.glob("dialog_*.md")).read_text()
            for value in ("What is your order number?", "GET", "{{env.service_host}}", "orderId",
                          "context.orderStatus = response.body.status;", "context.message = context.orderStatus;",
                          "context.integrationFailed", "futureRetryPolicy/attempts"):
                self.assertIn(value, text)
            definition = next(d["definition"] for d in inv["component_definitions"] if d["definition"]["type"] == "service")
            self.assertEqual(definition["futureRetryPolicy"], service["futureRetryPolicy"])
            self.assertNotIn("private-", "\n".join(p.read_text() for p in output.iterdir()))

    def test_malformed_boolean_conditions_preserve_unknowns(self):
        data = fixture()
        for tests in (None, [], "invalid", {"field": "x"}):
            condition = {"tests": tests}
            self.assertIn("Unresolved condition", parse_condition(condition))
            data["dialogs"][0]["nodes"][0]["transitions"] = [{"if": condition, "then": "second"}]
            with tempfile.TemporaryDirectory() as tmp:
                output, inv, _ = self.run_export(data, Path(tmp))
                self.assertEqual(inv["node_occurrences"][0]["transitions_raw"][0]["if"], condition)
                self.assertIn("Unresolved condition", (output / "_all_dialogs.md").read_text())
        missing = parse_condition({"tests": [{"field": "x", "op": "exists"}, {"field": "y", "op": "exists"}]})
        self.assertIn("UNRESOLVED CONJUNCTION", missing)
        self.assertNotIn(" AND ", missing)


if __name__ == "__main__":
    unittest.main()
