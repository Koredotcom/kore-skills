import hashlib
import json
from pathlib import Path
import unittest

SKILL = Path(__file__).resolve().parents[1]
PLUGIN = SKILL.parents[1]


class ReferenceProvenanceTests(unittest.TestCase):
    def test_borrowed_sources_match_reviewed_content(self):
        record = json.loads((SKILL / "references/source-provenance.json").read_text())
        for source in record["sources"]:
            with self.subTest(source=source["path"]):
                path = (PLUGIN / source["path"]).resolve()
                self.assertTrue(path.is_relative_to(PLUGIN.resolve()))
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), source["sha256"], "Review impacted Developer guidance before updating this source hash.")
                for adapted in source["adapted_into"]:
                    self.assertTrue((SKILL / adapted).is_file(), adapted)


if __name__ == "__main__":
    unittest.main()
