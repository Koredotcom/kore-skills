from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
ENTRY_POINT = SKILL_DIR / "scripts" / "decompose_bot.py"
PARSER_PATH = SKILL_DIR / "scripts" / "xo_export_parser.py"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "botDefinition.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DecomposeBotTests(unittest.TestCase):
    def test_common_export_is_deterministic_and_redacts_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "first"
            second = root / "second"
            for output in (first, second):
                subprocess.run(
                    [sys.executable, str(ENTRY_POINT), str(FIXTURE), str(output)],
                    check=True,
                    capture_output=True,
                    text=True,
                )

            self.assertEqual(
                (first / "_inventory.json").read_bytes(),
                (second / "_inventory.json").read_bytes(),
            )
            inventory = json.loads((first / "_inventory.json").read_text())
            self.assertEqual(inventory["version_route"], "XO 10 or earlier")
            self.assertEqual(inventory["summary"]["services"], 1)
            self.assertEqual(inventory["summary"]["scripts"], 1)

            combined = "\n".join(
                path.read_text(encoding="utf-8")
                for path in first.iterdir()
                if path.is_file()
            )
            for private_value in (
                "private-query-value",
                "private-header-value",
                "private-api-value",
                "private-payload-value",
                "private-preprocessor-value",
                "private-script-value",
            ):
                self.assertNotIn(private_value, combined)
            self.assertIn("[REDACTED]", combined)
            self.assertIn("{{env.service_host}}", combined)

    def test_app_definition_routes_to_xo_11(self) -> None:
        entry = load_module(ENTRY_POINT, "decompose_bot")
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "appDefinition.json"
            path.write_text("{}", encoding="utf-8")
            self.assertEqual(entry.detect_version(path, None), 11)

    def test_zip_slip_is_rejected(self) -> None:
        entry = load_module(ENTRY_POINT, "decompose_bot_safe_extract")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive = root / "unsafe.zip"
            with zipfile.ZipFile(archive, "w") as stream:
                stream.writestr("../outside.txt", "unsafe")
            with self.assertRaises(ValueError):
                entry.safe_extract(archive, root / "output")

    def test_redaction_preserves_portable_references(self) -> None:
        parser = load_module(PARSER_PATH, "xo_export_parser")
        headers = parser._redact_structure(
            {
                "Authorization": "Bearer private-value",
                "X-API-Key": "{{env.api_key}}",
            }
        )
        self.assertEqual(headers["Authorization"], "[REDACTED]")
        self.assertEqual(headers["X-API-Key"], "{{env.api_key}}")

    def test_mixed_references_do_not_bypass_redaction(self) -> None:
        parser = load_module(PARSER_PATH, "xo_export_parser_mixed")
        result = parser._redact_structure({
            "Authorization": "Bearer literal-secret-{{env.suffix}}",
            "token": {"reference": "{{env.token}}", "value": "nested-secret"},
            "X-API-Key": "{{env.api_key}}",
        })
        self.assertEqual(result["Authorization"], "[REDACTED]")
        self.assertEqual(result["token"], "[REDACTED]")
        self.assertEqual(result["X-API-Key"], "{{env.api_key}}")
        for text in (
            'const token = "literal-secret-${env.suffix}";',
            'https://example.invalid/?token=literal-secret-{{env.suffix}}',
        ):
            self.assertNotIn("literal-secret", parser._redact_text(text))
        reference = '{"Authorization":"Bearer {{env.token}}"}'
        self.assertEqual(parser._redact_text(reference), reference)

    def test_wrapped_app_export_preserves_evidence_and_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "appDefinition.json"
            source.write_text(json.dumps({"appDefinition": json.loads(FIXTURE.read_text())}))
            original = source.read_bytes()
            outputs = [root / "first", root / "second"]
            for output in outputs:
                subprocess.run(
                    [sys.executable, str(ENTRY_POINT), str(source), str(output)],
                    check=True, capture_output=True, text=True,
                )
            inventory = json.loads((outputs[0] / "_inventory.json").read_text())
            self.assertEqual(inventory["version_route"], "XO 11")
            self.assertEqual(inventory["summary"]["services"], 1)
            self.assertEqual(inventory["summary"]["scripts"], 1)
            rendered = (outputs[0] / "_inventory.json").read_text()
            self.assertIn("{{env.service_host}}", rendered)
            self.assertIn("context.orderStatus = response.body.status;", rendered)
            self.assertNotIn("private-header-value", rendered)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(
                {p.name: p.read_bytes() for p in outputs[0].iterdir() if p.is_file()},
                {p.name: p.read_bytes() for p in outputs[1].iterdir() if p.is_file()},
            )


if __name__ == "__main__":
    unittest.main()
