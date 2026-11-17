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
    def run_checker(self, *args: str, cwd: Path | None = None) -> dict:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", *args],
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        return json.loads(completed.stdout)

    def test_modular_standard_package_passes(self) -> None:
        result = self.run_checker("--package", str(FIXTURES / "modular_standard"))
        self.assertEqual(result["package"]["status"], "PASS")
        self.assertEqual(result["package"]["inventory"]["documentCount"], 10)
        self.assertEqual(result["package"]["inventory"]["undefinedReferences"], [])

    def test_brief_uses_index_governance_without_embedded_ids(self) -> None:
        result = self.run_checker("--package", str(FIXTURES / "modular_standard"))["package"]
        brief = result["documents"][0]
        self.assertEqual(brief["path"], "00-business-brief.md")
        self.assertEqual(brief["metadataSource"], "00-design-index.md#document-register")
        self.assertEqual(brief["metadata"]["document id"], "DOC-009")
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            index = package / "00-design-index.md"
            index.write_text(index.read_text().replace(
                "](00-business-brief.md)", "](./00-business-brief.md)"
            ), encoding="utf-8")
            self.assertEqual(self.run_checker("--package", str(package))["package"]["status"], "PASS")
            path = package / "00-business-brief.md"
            path.write_text(path.read_text() + "\nUC-001 and API-001\n", encoding="utf-8")
            warnings = "\n".join(self.run_checker("--package", str(package))["package"]["warnings"])
            self.assertIn("Executive brief must contain no IDs", warnings)

    def test_older_modular_business_gaps_remain_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            (package / "00-business-brief.md").unlink()
            index = package / "00-design-index.md"
            text = index.read_text()
            for heading in ("Status Legend", "Kickoff decisions and customer actions", "Sign-off Matrix"):
                start = text.index("## " + heading)
                end = text.index("\n## ", start + 3)
                text = text[:start] + text[end + 1:]
            index.write_text(text, encoding="utf-8")
            result = self.run_checker("--package", str(package))
        self.assertTrue(result["advisory"])
        warnings = "\n".join(result["package"]["warnings"])
        for message in ("Missing first-file executive brief", "Status Legend", "Kickoff decisions and customer actions table", "Sign-off Matrix table"):
            self.assertIn(message, warnings)

    def test_wave_one_samples_and_required_fields_report_missing_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            path = package / "use-cases/UC-001-equipment-request.md"
            text = path.read_text()
            text = text.replace("**Trigger:** An employee asks to request an item from the approved catalog.", "**Trigger:**")
            start = text.index("### Failure path")
            end = text.index("## Long-Running Behavior", start)
            text = text[:start] + text[end:]
            path.write_text(text, encoding="utf-8")
            warnings = "\n".join(self.run_checker("--package", str(package))["package"]["warnings"])
        self.assertIn("missing required Trigger field", warnings)
        self.assertIn("needs a Failure path Speaker/Message sample", warnings)
        self.assertNotIn("needs a Happy path", warnings)

    def test_process_samples_accept_event_participants(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            path = package / "use-cases/UC-001-equipment-request.md"
            text = path.read_text()
            start = text.index("## Sample Conversations")
            end = text.index("## Long-Running Behavior", start)
            text = text[:start] + '''## Sample Conversations

Illustrative process exchanges, not a conversational interface.

### Happy path

| Speaker | Message |
|---|---|
| Request event | An employee submitted a valid equipment request. |
| Agent | Request recorded; awaiting manager decision. |
| Manager event | Request approved. |
| Agent | Approval recorded and employee notified. |

### Failure path

| Speaker | Message |
|---|---|
| Request event | An employee submitted a request with no item. |
| Agent | Request rejected as incomplete; source notified to supply an item. |

''' + text[end:]
            path.write_text(text, encoding="utf-8")
            result = self.run_checker("--package", str(package))["package"]
        self.assertEqual(result["status"], "PASS", result["warnings"])

    def test_business_tables_report_missing_values_without_inventing_them(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            path = package / "01-agent-definition.md"
            path.write_text(path.read_text().replace("60% in the fictional pre-launch month", ""), encoding="utf-8")
            index = package / "00-design-index.md"
            index.write_text(index.read_text().replace("TBD — agree before setup", ""), encoding="utf-8")
            warnings = "\n".join(self.run_checker("--package", str(package))["package"]["warnings"])
        self.assertIn("outcome row 1 missing: baseline", warnings)
        self.assertIn("row 1 has empty fields: needed-by date", warnings)

    def test_package_under_hidden_ancestors_or_with_hidden_name_passes(self) -> None:
        baseline = self.run_checker("--package", str(FIXTURES / "modular_standard"))["package"]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for relative in (".agents/skills/design", ".claude/skills/design", ".design"):
                package = root / relative
                shutil.copytree(FIXTURES / "modular_standard", package)
                for argument in (str(package), relative):
                    with self.subTest(package=relative, argument=argument):
                        result = self.run_checker("--package", argument, cwd=root)["package"]
                        self.assertEqual(result["status"], "PASS")
                        for key in ("warnings", "documents", "inventory"):
                            self.assertEqual(result[key], baseline[key])

    def test_hidden_content_inside_package_remains_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            baseline = self.run_checker("--package", str(package))["package"]
            for relative in (".notes.md", ".git/ignored.md", "technical/.cache/ignored.md", "technical/.draft.md"):
                hidden = package / relative
                hidden.parent.mkdir(parents=True, exist_ok=True)
                hidden.write_text("# Unindexed draft\n\nFR-999\n", encoding="utf-8")
            result = self.run_checker("--package", str(package))["package"]
            self.assertEqual(result, baseline)

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

    def test_missing_checklist_is_advisory_for_existing_modular_packages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            index = package / "00-design-index.md"
            before, rest = index.read_text().split("## Design Completion Checklist", 1)
            index.write_text(before + "## Foundation Register" + rest.split("## Foundation Register", 1)[1])
            result = self.run_checker("--package", str(package))
        self.assertTrue(result["advisory"])
        self.assertIn("Index has no Design Completion Checklist tasks", result["package"]["warnings"])

    def test_finalization_cannot_hide_pending_validation_and_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            index = package / "00-design-index.md"
            index.write_text(index.read_text().replace(
                "| Finalize design | Finalization | Wave 1 design package v0.1 | Pending |",
                "| Finalize design | Finalization | Wave 1 design package v0.1 | Complete |",
            ))
            result = self.run_checker("--package", str(package))
        warnings = "\n".join(result["package"]["warnings"])
        self.assertIn("Design marked finalized with unfinished checklist tasks", warnings)
        for task in ("Check structure", "Review semantics", "Confirm design"):
            self.assertIn(task, warnings)

    def test_completion_and_dispositions_require_evidence_and_valid_tracking(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            index = package / "00-design-index.md"
            source = index.read_text()
            source = source.replace("**Finalization scope:**", "**Unspecified scope:**")
            source = source.replace("| Approval |", "| Confirmation |")
            source = source.replace("| Complete | Fixture document version 0.1 drafted |", "| Complete | |")
            source = source.replace("| Pending | Not yet checked |", "| Done | Not yet checked |")
            source = source.replace("| Pending | Not yet reviewed |", "| Deferred | |")
            source = source.replace("| Pending | Scope approval does not approve this design |", "| Not applicable | |")
            source = source.replace("| 2026-11-13 |", "| yesterday |")
            index.write_text(source)
            result = self.run_checker("--package", str(package))
        warnings = "\n".join(result["package"]["warnings"])
        for expected in ("no finalization scope", "missing stages: Approval", "invalid stage: Confirmation",
                         "invalid status: Done", "invalid updated date",
                         "'Draft shared behavior' has no completion evidence",
                         "'Review semantics' has no completion evidence",
                         "'Confirm design' has no completion evidence"):
            self.assertIn(expected, warnings)

    def test_finalized_package_and_change_reopening(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "design"
            shutil.copytree(FIXTURES / "modular_standard", package)
            index = package / "00-design-index.md"
            source = index.read_text().replace("| Pending |", "| Complete |")
            source = source.replace("Not yet checked", "Synthetic structural review v0.1: PASS")
            source = source.replace("Not yet reviewed", "Synthetic semantic review v0.1: no findings")
            source = source.replace("Scope approval does not approve this design", "Synthetic design owner confirmation, v0.1, 2026-11-13")
            source = source.replace("Awaiting validation and design confirmation", "Synthetic scoped finalization gate v0.1 met")
            index.write_text(source)
            self.assertEqual(self.run_checker("--package", str(package))["package"]["status"], "PASS")

            source = source.replace("| Review semantics | Validation | All registered files v0.1 | Complete |",
                                    "| Review semantics | Validation | Changed voice design | Blocked |")
            index.write_text(source)
            stale = self.run_checker("--package", str(package))
            self.assertIn("Design marked finalized with unfinished checklist tasks: Review semantics", stale["package"]["warnings"])

            source = source.replace("| Finalize design | Finalization | Wave 1 design package v0.1 | Complete |",
                                    "| Finalize design | Finalization | Revised design scope | Pending |")
            index.write_text(source)
            self.assertEqual(self.run_checker("--package", str(package))["package"]["status"], "PASS")

    def test_freeform_legacy_file_is_unrecognized_without_rejection(self) -> None:
        result = self.run_checker(
            "--functional", str(FIXTURES / "freeform_design.md")
        )
        self.assertEqual(result["functional"]["status"], "UNRECOGNIZED_FORMAT")
        self.assertTrue(result["advisory"])


if __name__ == "__main__":
    unittest.main()
