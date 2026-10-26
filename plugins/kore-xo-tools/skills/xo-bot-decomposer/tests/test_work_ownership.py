"""Work ownership is checked independently of semantic coverage completion."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from test_universal_config import parent, child
from test_coverage import run_cli
from reconcile_system import reconcile


class OwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        source = root / 'source'; source.mkdir()
        (source / 'parent.json').write_text(json.dumps(parent()))
        (source / 'child.json').write_text(json.dumps(child()))
        (source / 'botkit.js').write_text('function prepare(context) { return context; }')
        result = run_cli(source, root / 'out')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.ledger = json.loads((root / 'out' / '_coverage.json').read_text())
        self.plan = json.loads((root / 'out' / '_system_plan.json').read_text())
        self.packages = {p['role']: p for p in self.plan['work_packages']}

    def prepared(self):
        self.plan['ownership_policy'].update(assignments_locked=True, shared_contract_revision='baseline-1', shared_contract_refs=['shared_runtime/contracts.md'])
        artifacts = {a['id']: a for a in self.ledger['artifacts']}
        bots = {b['artifact_id']: b for b in self.ledger['bots']}
        handoffs = []
        for package in self.plan['work_packages']:
            owned = package['owned_artifact_ids']
            if not owned:
                continue
            identity = {'artifact_id': owned[0], 'source_hash': artifacts[owned[0]]['source_hash']}
            if owned[0] in bots:
                identity['bot_id'] = bots[owned[0]]['id']
            record = {key: [] for key in ('goals_events', 'entry_assumptions', 'routes_returns', 'state_contracts', 'dependencies', 'exclusions', 'gap_ids')}
            record.update(source_identity=identity, capability_scope='Assigned synthetic source slice', quality={'static': 'partial'},
                work_package_id=package['id'], shared_contract_revision='baseline-1',
                analyzed_artifacts=[{'artifact_id': aid, 'source_hash': artifacts[aid]['source_hash']} for aid in owned])
            handoffs.append(record)
        return handoffs

    def test_generated_plan_has_exclusive_botkit_owner_and_child_dependencies(self):
        owners = [aid for p in self.plan['work_packages'] for aid in p['owned_artifact_ids']]
        self.assertEqual(len(owners), len(set(owners)))
        self.assertEqual(set(owners), {a['id'] for a in self.ledger['artifacts']})
        self.assertEqual(self.packages['shared_runtime']['owned_artifact_ids'], ['source_001/botkit.js'])
        self.assertIn('shared_runtime', self.packages['child']['depends_on'])
        self.assertIn(self.packages['parent']['id'], self.packages['child']['depends_on'])
        with self.assertRaisesRegex(ValueError, 'Lock assignments'):
            reconcile(self.ledger, [], self.plan)

    def test_valid_assignments_merge_order_independently_without_global_closure(self):
        handoffs = self.prepared()
        result = reconcile(self.ledger, handoffs, self.plan)
        self.assertEqual(result, reconcile(self.ledger, list(reversed(handoffs)), self.plan))
        self.assertEqual(result['ownership_validation'], 'declared_assignments_checked')
        self.assertEqual(result['global_status'], 'partial')
        self.assertEqual(len(result['shared_handoffs']), 1)
        self.assertEqual(reconcile(self.ledger, handoffs)['ownership_validation'], 'not_checked_legacy_handoffs')

    def test_child_cannot_claim_botkit_or_another_bot(self):
        handoffs = self.prepared()
        child_handoff = next(h for h in handoffs if h['work_package_id'] == self.packages['child']['id'])
        for role in ('shared_runtime', 'parent'):
            changed = copy.deepcopy(handoffs)
            edited = next(h for h in changed if h['work_package_id'] == child_handoff['work_package_id'])
            owner = next(h for h in handoffs if h['work_package_id'] == self.packages[role]['id'])
            edited['analyzed_artifacts'].extend(owner['analyzed_artifacts'])
            with self.assertRaisesRegex(ValueError, 'Out-of-assignment'):
                reconcile(self.ledger, changed, self.plan)

    def test_overlap_duplicate_package_stale_contract_and_hash_are_rejected(self):
        handoffs = self.prepared()
        self.packages['child']['owned_artifact_ids'].append('source_001/botkit.js')
        with self.assertRaisesRegex(ValueError, 'multiply owned'):
            reconcile(self.ledger, handoffs, self.plan)
        self.packages['child']['owned_artifact_ids'].pop()
        with self.assertRaisesRegex(ValueError, 'duplicate work package'):
            reconcile(self.ledger, handoffs + [handoffs[0]], self.plan)
        for field, value, error in (('shared_contract_revision', 'old', 'Stale'), ('analyzed_artifacts', [{'artifact_id': handoffs[0]['source_identity']['artifact_id'], 'source_hash': 'wrong'}], 'hash')):
            changed = copy.deepcopy(handoffs); changed[0][field] = value
            with self.assertRaisesRegex(ValueError, error):
                reconcile(self.ledger, changed, self.plan)

    def test_missing_shared_handoff_stays_a_gap(self):
        handoffs = [h for h in self.prepared() if h['work_package_id'] != 'shared_runtime']
        result = reconcile(self.ledger, handoffs, self.plan)
        self.assertTrue(any(g['affected'] == ['shared_runtime'] and g['evidence'] == ['source_001/botkit.js'] for g in result['coverage_gaps']))
        self.assertEqual(result['global_status'], 'partial')

    def test_coordinator_can_reassign_coupled_sources_without_duplicate_coverage(self):
        handoffs = self.prepared()
        parent_package, child_package = self.packages['parent'], self.packages['child']
        parent_handoff = next(h for h in handoffs if h['work_package_id'] == parent_package['id'])
        child_handoff = next(h for h in handoffs if h['work_package_id'] == child_package['id'])
        parent_package['owned_artifact_ids'] += child_package['owned_artifact_ids']
        child_package['owned_artifact_ids'] = []
        parent_handoff['analyzed_artifacts'] += child_handoff['analyzed_artifacts']
        result = reconcile(self.ledger, [h for h in handoffs if h is not child_handoff], self.plan)
        self.assertFalse(any('has no validated handoff' in g['consequence'] for g in result['coverage_gaps']))
        self.assertFalse(any('Assigned source has no analysis handoff' in g['consequence'] for g in result['coverage_gaps']))


if __name__ == '__main__':
    unittest.main()
