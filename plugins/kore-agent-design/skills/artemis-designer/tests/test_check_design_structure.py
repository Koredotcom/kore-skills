import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "check_design_structure.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class CheckDesignStructureTests(unittest.TestCase):
    def run_checker(self, *args: str) -> dict:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    def test_modular_standard_package_passes(self) -> None:
        result = self.run_checker("--package", str(FIXTURES / "modular_standard"))
        self.assertEqual(result["package"]["status"], "PASS")
        self.assertEqual(result["package"]["inventory"]["documentCount"], 9)
        self.assertEqual(result["package"]["inventory"]["undefinedReferences"], [])

    def test_manifest_drift_and_broken_link_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            index = package / "00-design-index.md"
            source = index.read_text(encoding="utf-8")
            source = source.replace(
                "| DOC-003 | [Voice Experience](experience/voice.md) | Voice Experience | 0.1 | In Review | Wave 1 |",
                "| DOC-003 | [Voice Experience](experience/missing.md) | Voice Experience | 0.2 | Approved | Wave 2 |",
            )
            index.write_text(source, encoding="utf-8")
            result = self.run_checker("--package", str(package))

        warnings = "\n".join(result["package"]["warnings"])
        self.assertEqual(result["package"]["status"], "WARN")
        self.assertIn("Broken local links: experience/missing.md", warnings)
        self.assertIn("Document absent from index: experience/voice.md", warnings)
        self.assertIn("Index references missing document: experience/missing.md", warnings)

    def test_identifier_errors_and_missing_api_trace_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            api = package / "technical" / "use-case-apis.md"
            source = api.read_text(encoding="utf-8")
            source = source.replace("UC-001, FR-001, AC-001", "Not stated")
            source = source.replace("INT-001", "Not stated")
            source += "\nMalformed reference for regression coverage: FR-1.\n"
            api.write_text(source, encoding="utf-8")
            result = self.run_checker("--package", str(package))

        warnings = "\n".join(result["package"]["warnings"])
        self.assertIn("Identifiers do not use three digits: FR-1", warnings)
        self.assertIn("API-001 has no functional or non-functional trace", warnings)
        self.assertIn("API-001 has no integration reference", warnings)

    def test_wave_mismatch_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            use_case = package / "use-cases" / "UC-001-equipment-request.md"
            source = use_case.read_text(encoding="utf-8").replace(
                "| Wave | Wave 1 |", "| Wave | Wave 2 |"
            )
            use_case.write_text(source, encoding="utf-8")
            result = self.run_checker("--package", str(package))

        warnings = "\n".join(result["package"]["warnings"])
        self.assertIn("Manifest mismatch", warnings)
        self.assertIn("Wave mismatch for UC-001", warnings)

    def test_wave_one_governance_and_component_trace_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            index = package / "00-design-index.md"
            source = index.read_text(encoding="utf-8")
            source = source.replace(
                "| FND-001 | Development, test, and production setup | Wave 1 | Confirmed | Environment access | Platform owner |\n",
                "",
            ).replace("| 5 | 4 | 4 | 80 |", "| 5 | 4 | 4 | 79 |")
            index.write_text(source, encoding="utf-8")

            architecture = package / "technical" / "architecture.md"
            architecture.write_text(
                architecture.read_text(encoding="utf-8").replace(
                    "| Durable approval | Agent plus durable workflow | UC-001, FR-001, NFR-001 |",
                    "| Durable approval | Agent plus durable workflow | Not stated |",
                ),
                encoding="utf-8",
            )
            result = self.run_checker("--package", str(package))

        warnings = "\n".join(result["package"]["warnings"])
        self.assertIn("Foundation Register has no Wave 1 foundation item", warnings)
        self.assertIn("UC-001 references unknown foundation items: FND-001", warnings)
        self.assertIn("UC-001 prioritization score is 79; expected 80", warnings)
        self.assertIn("Architecture component 'Agent plus durable workflow' has no functional", warnings)

    def test_cross_wave_foundation_and_local_duplicate_definition_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            index = package / "00-design-index.md"
            source = index.read_text(encoding="utf-8")
            source = source.replace(
                "| FND-001 | Development, test, and production setup | Wave 1 | Confirmed | Environment access | Platform owner |",
                "| FND-001 | Development, test, and production setup | Wave 1 | Confirmed | Environment access | Platform owner |\n"
                "| FND-002 | Later integration foundation | Wave 2 | Proposed | Contract access | Integration owner |",
            ).replace(
                "| [UC-001](use-cases/UC-001-equipment-request.md) | Wave 1 | Confirmed | FND-001 |",
                "| [UC-001](use-cases/UC-001-equipment-request.md) | Wave 1 | Confirmed | FND-002 |",
            )
            index.write_text(source, encoding="utf-8")

            use_case = package / "use-cases" / "UC-001-equipment-request.md"
            use_case.write_text(
                use_case.read_text(encoding="utf-8").replace(
                    "| FR-001 | Persist the request while approval is pending | Confirmed | NFR-001 |",
                    "| FR-001 | Persist the request while approval is pending | Confirmed | NFR-001 |\n"
                    "| FR-001 | Duplicate requirement definition | Confirmed | NFR-001 |",
                ),
                encoding="utf-8",
            )
            result = self.run_checker("--package", str(package))

        warnings = "\n".join(result["package"]["warnings"])
        self.assertIn("UC-001 depends on foundation items outside Wave 1: FND-002", warnings)
        self.assertIn("Identifiers defined more than once in this document: FR-001", warnings)

    def test_experience_decision_table_is_canonical_and_index_summary_stays_aligned(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            voice = package / "experience" / "voice.md"
            voice.write_text(
                voice.read_text(encoding="utf-8")
                + "\n## Experience Decisions\n\n"
                "| EXP ID | Recommended behavior | Confirmation status |\n"
                "|---|---|---|\n"
                "| EXP-001 | Stop playback on interruption | Confirmed |\n",
                encoding="utf-8",
            )
            index = package / "00-design-index.md"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    "## Decisions and Changes",
                    "## Experience Decision Summary\n\n"
                    "| Experience ID | Canonical decision | Confirmation status |\n"
                    "|---|---|---|\n"
                    "| EXP-001 | [Voice decision](experience/voice.md) | Confirmed |\n\n"
                    "## Decisions and Changes",
                ),
                encoding="utf-8",
            )
            aligned = self.run_checker("--package", str(package))
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    "| EXP-001 | [Voice decision]", "| EXP-002 | [Voice decision]"
                ),
                encoding="utf-8",
            )
            drifted = self.run_checker("--package", str(package))

        self.assertEqual(aligned["package"]["status"], "PASS")
        warnings = "\n".join(drifted["package"]["warnings"])
        self.assertIn("Experience decisions absent from index summary: EXP-001", warnings)
        self.assertIn("Index experience summary references undefined decisions: EXP-002", warnings)

    def test_unprovided_priority_scores_are_unresolved_not_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            index = package / "00-design-index.md"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    "| 5 | 4 | 4 | 80 |", "| TBD | TBD | TBD | TBD |"
                ),
                encoding="utf-8",
            )
            result = self.run_checker("--package", str(package))

        warnings = "\n".join(result["package"]["warnings"])
        for dimension in ("value", "speed", "readiness"):
            self.assertIn(f"UC-001 has unresolved {dimension} score: TBD", warnings)
            self.assertNotIn(f"UC-001 has invalid {dimension} score", warnings)

    def test_legacy_pair_remains_supported(self) -> None:
        result = self.run_checker(
            "--functional",
            str(FIXTURES / "standard_functional.md"),
            "--technical",
            str(FIXTURES / "standard_technical.md"),
        )
        self.assertEqual(result["functional"]["status"], "PASS")
        self.assertEqual(result["technical"]["status"], "PASS")
        self.assertEqual(result["traceability"]["status"], "PASS")

    def test_freeform_legacy_file_is_unrecognized_without_rejection(self) -> None:
        result = self.run_checker(
            "--functional", str(FIXTURES / "freeform_design.md")
        )
        self.assertEqual(result["functional"]["status"], "UNRECOGNIZED_FORMAT")
        self.assertTrue(result["advisory"])


if __name__ == "__main__":
    unittest.main()
