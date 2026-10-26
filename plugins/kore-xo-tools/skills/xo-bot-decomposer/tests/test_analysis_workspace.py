import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys
import shutil
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'analysis_workspace.py'
spec = importlib.util.spec_from_file_location('analysis_workspace', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / 'analysis'
        module.initialize(self.root)
        (self.root / 'evidence' / 'run-001').mkdir()
        (self.root / 'evidence' / 'run-001' / 'inventory.json').write_text('{"source": "synthetic"}')
        self.notes = self.root / 'work' / 'children' / 'notes.md'
        self.notes.write_text('Completed dialog A; next: dialog B.')

    def test_checkpoint_survives_new_process_state_and_preserves_previous_work(self):
        first = module.checkpoint(self.root, 'first pass')
        self.assertEqual(first['checkpoint'], 'CP-0001')
        result = module.status(self.root)
        self.assertFalse(result['changed_since_checkpoint'])
        self.assertFalse(result['checkpoint_snapshot_errors'])
        self.notes.write_text('Completed dialog B; waiting for shared handler.')
        self.assertIn('work/children/notes.md', module.status(self.root)['changed_since_checkpoint'])
        second = module.checkpoint(self.root, 'second pass')
        self.assertEqual(second['checkpoint'], 'CP-0002')
        self.assertEqual((self.root / 'checkpoints/CP-0001/files/work/children/notes.md').read_text(), 'Completed dialog A; next: dialog B.')
        self.assertFalse((self.root / 'checkpoints/CP-0001/files/evidence').exists())

    def test_missing_work_and_changed_evidence_remain_visible_and_recoverable(self):
        module.checkpoint(self.root, 'saved')
        self.notes.unlink()
        (self.root / 'evidence/run-001/inventory.json').write_text('changed')
        result = module.status(self.root)
        self.assertEqual(result['missing_since_checkpoint'], ['work/children/notes.md'])
        self.assertEqual(result['changed_since_checkpoint'], ['evidence/run-001/inventory.json'])
        self.assertTrue((self.root / 'checkpoints/CP-0001/files/work/children/notes.md').exists())
        self.assertFalse(result['checkpoint_snapshot_errors'])

    def test_checkpoint_detects_concurrent_saved_work_changes(self):
        original = module.shutil.copyfile
        def changed_copy(source, destination):
            result = original(source, destination)
            self.notes.write_text('Concurrent new work')
            return result
        with patch.object(module.shutil, 'copyfile', side_effect=changed_copy):
            with self.assertRaisesRegex(ValueError, 'changed during checkpoint'):
                module.checkpoint(self.root, 'racing')
        self.assertIsNone(module.read_json(self.root / 'session.json')['latest_checkpoint'])
        self.assertEqual(list((self.root / 'checkpoints').iterdir()), [])

    def test_reinitialization_symlinks_and_corrupted_snapshot_are_rejected_or_reported(self):
        with self.assertRaises(ValueError):
            module.initialize(self.root)
        link = self.root / 'work' / 'external.md'
        link.symlink_to(self.notes)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            module.checkpoint(self.root, 'unsafe link')
        link.unlink()
        module.checkpoint(self.root, 'saved')
        (self.root / 'checkpoints/CP-0001/files/work/children/notes.md').write_text('corrupted')
        self.assertEqual(module.status(self.root)['checkpoint_snapshot_errors'], ['work/children/notes.md'])

    def test_session_decisions_changed_during_capture_are_not_overwritten(self):
        original = module.inventory
        calls = 0
        def changed_inventory(root):
            nonlocal calls
            calls += 1
            if calls == 1:
                session = module.read_json(root / 'session.json')
                session['decisions'] = ['User deferred missing companion source']
                module.atomic_json(root / 'session.json', session)
            return original(root)
        with patch.object(module, 'inventory', side_effect=changed_inventory):
            with self.assertRaisesRegex(ValueError, 'changed during checkpoint'):
                module.checkpoint(self.root, 'racing decisions')
        self.assertEqual(module.read_json(self.root / 'session.json')['decisions'], ['User deferred missing companion source'])
        self.assertEqual(list((self.root / 'checkpoints').iterdir()), [])

    def test_orphan_checkpoint_is_reported_without_silently_changing_session(self):
        module.checkpoint(self.root, 'saved')
        session = module.read_json(self.root / 'session.json')
        session['latest_checkpoint'] = None
        module.atomic_json(self.root / 'session.json', session)
        result = module.status(self.root)
        self.assertEqual(result['orphan_checkpoints'], ['CP-0001'])
        self.assertIsNone(result['checkpoint'])
        self.assertEqual(module.checkpoint(self.root, 'continue')['checkpoint'], 'CP-0002')

    def test_resume_checks_original_source_hashes_in_a_fresh_process(self):
        source = self.root.parent / 'synthetic-source.json'
        source.write_text('{"dialogs": []}')
        session = module.read_json(self.root / 'session.json')
        session['source_locations'] = [{'path': str(source), 'sha256': module.digest(source)}]
        module.atomic_json(self.root / 'session.json', session)
        module.checkpoint(self.root, 'source registered')
        self.assertFalse(module.status(self.root)['source_issues'])
        source.write_text('{"dialogs": [], "changed": true}')
        resumed = subprocess.run([sys.executable, str(SCRIPT), 'status', str(self.root)], check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(resumed.stdout)['source_issues'], [{'path': str(source), 'issue': 'changed'}])
        source.unlink()
        self.assertEqual(module.status(self.root)['source_issues'][0]['issue'], 'missing_or_not_regular_file')

    def test_intake_requires_an_explicit_persistent_output(self):
        result = subprocess.run([sys.executable, str(SCRIPT.parent / 'decompose_bot.py'), 'synthetic.json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('output', result.stderr)

    def test_nested_workspace_is_excluded_across_repeated_intake(self):
        exports = self.root.parent / 'exports'
        exports.mkdir()
        source = exports / 'botDefinition.json'
        shutil.copyfile(SCRIPT.parent.parent / 'tests/fixtures/botDefinition.json', source)
        original_hash = module.digest(source)
        analysis = exports / 'xo-analysis'
        module.initialize(analysis)
        # Even source-shaped copies in old work must not become new source evidence.
        shutil.copyfile(source, analysis / 'work/botDefinition.json')
        ledgers = []
        for number in (1, 2):
            output = analysis / 'evidence' / f'run-{number:03}'
            subprocess.run([sys.executable, str(SCRIPT.parent / 'decompose_bot.py'), str(exports), str(output)], check=True, capture_output=True, text=True)
            ledgers.append(module.read_json(output / '_coverage.json'))
            module.checkpoint(analysis, f'Run {number}')
        self.assertEqual(ledgers[0]['artifacts'], ledgers[1]['artifacts'])
        self.assertEqual(len(ledgers[1]['bots']), 1)
        self.assertEqual(len(ledgers[1]['artifacts']), 1)
        self.assertEqual(ledgers[1]['intake_exclusions'], [{'source_group': 'source_001', 'relative_path': 'xo-analysis', 'reason': 'generated_analysis_workspace'}])
        self.assertEqual(module.digest(source), original_hash)
        self.assertFalse(module.status(analysis)['changed_since_checkpoint'])

    def test_unmarked_analysis_folder_is_not_silently_excluded(self):
        exports = self.root.parent / 'exports'
        original_folder = exports / 'xo-analysis'
        original_folder.mkdir(parents=True)
        shutil.copyfile(SCRIPT.parent.parent / 'tests/fixtures/botDefinition.json', original_folder / 'botDefinition.json')
        output = self.root.parent / 'external-evidence'
        subprocess.run([sys.executable, str(SCRIPT.parent / 'decompose_bot.py'), str(exports), str(output)], check=True, capture_output=True, text=True)
        ledger = module.read_json(output / '_coverage.json')
        self.assertEqual(len(ledger['bots']), 1)
        self.assertEqual(ledger['intake_exclusions'], [])
        self.assertEqual(ledger['artifacts'][0]['logical_source'], 'xo-analysis/botDefinition.json')

    def test_generated_sources_and_arbitrary_nested_outputs_remain_rejected(self):
        exports = self.root.parent / 'exports'
        exports.mkdir()
        source = exports / 'botDefinition.json'
        shutil.copyfile(SCRIPT.parent.parent / 'tests/fixtures/botDefinition.json', source)
        analysis = exports / 'xo-analysis'
        module.initialize(analysis)
        copied = analysis / 'work/botDefinition.json'
        shutil.copyfile(source, copied)
        for selected, output in ((exports, exports / 'unmarked-output'), (exports, analysis / 'work/output'),
                                 (copied, self.root.parent / 'out'), (analysis, self.root.parent / 'out')):
            with self.subTest(selected=selected, output=output):
                result = subprocess.run([sys.executable, str(SCRIPT.parent / 'decompose_bot.py'), str(selected), str(output)], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())

    def test_invalid_marker_stops_intake_without_following_links(self):
        exports = self.root.parent / 'exports'
        exports.mkdir()
        shutil.copyfile(SCRIPT.parent.parent / 'tests/fixtures/botDefinition.json', exports / 'botDefinition.json')
        analysis = exports / 'xo-analysis'
        module.initialize(analysis)
        marker = analysis / module.MARKER
        marker.write_text('{"kind": "unknown"}')
        output = self.root.parent / 'bad-marker-output'
        result = subprocess.run([sys.executable, str(SCRIPT.parent / 'decompose_bot.py'), str(exports), str(output)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((output / '_coverage.json').exists())
        marker.unlink()
        marker.symlink_to(exports / 'botDefinition.json')
        result = subprocess.run([sys.executable, str(SCRIPT.parent / 'decompose_bot.py'), str(exports), str(output)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((output / '_coverage.json').exists())


if __name__ == '__main__':
    unittest.main()
