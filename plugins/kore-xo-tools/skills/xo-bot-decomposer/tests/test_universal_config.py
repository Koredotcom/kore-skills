"""Synthetic universal exports: identities are deliberately unrelated strings."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from xo_graph import unwrap
from review_coverage import validate
from reconcile_system import reconcile
from test_coverage import run_cli


def dialog(identity, ref, name='Same task label'):
    return {'_id': identity, 'refId': ref, 'name': name, 'isHidden': True, 'nodes': []}


def event(task, owner=None, enabled=True, action='triggerDialog'):
    return {'enabled': enabled, 'action': action, 'task': task, 'linkedBotStreamId': owner,
            'pre_conditions': {'channels': ['web']}, 'manageFirstMessage': {'task': 'retain'}}


def parent():
    return {'_id': 'parent-stream', 'refId': 'parent-reference', 'type': 'universalbot',
            'localeData': {'en': {'name': 'Synthetic umbrella'}}, 'universalBotVersion': 2,
            'linkedBotsDetails': [{'_id': 'child-reference', 'name': 'First label'},
                                  {'_id': 'child-reference', 'name': 'Older label'}],
            'fallbackDetails': [{'_id': 'child-reference', 'streamId': 'child-stream', 'name': 'Metadata label'}],
            'dialogs': [dialog('local-dialog', 'local-reference')], 'dialogComponents': [],
            'defaultDialogId': 'recovery-reference', 'botEvents': {
                'INTENT_UNIDENTIFIED': event('recovery-reference', 'child-reference'),
                'ON_CONNECT_EVENT': event('welcome-reference', 'child-reference'),
                'TELEPHONY_WELCOME_EVENT': event('welcome-reference', 'child-reference'),
                'WELCOME_MESSAGE_EVENT': event('welcome-reference', 'child-reference'),
                'REPEAT_RESPONSE_EVENT': event('stale-task', 'stale-owner', False),
                'TASK_FAILURE_EVENT': event('stale-task', 'stale-owner', action='showMsg')}}


def child():
    return {'_id': 'child-stream', 'refId': 'different-child-reference', 'name': 'Unrelated display label',
            'dialogs': [dialog('recovery-dialog', 'recovery-reference'), dialog('welcome-dialog', 'welcome-reference')], 'dialogComponents': []}


class UniversalConfigTests(unittest.TestCase):
    def intake(self, definitions, *args):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name); source = root / 'source'; source.mkdir()
        for name, data in definitions.items():
            (source / name).write_text(json.dumps(data))
        out = root / 'out'
        result = run_cli(source, out, *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads((out / '_coverage.json').read_text()), out

    def test_type_detects_parent_and_preserves_duplicate_registry_and_owner(self):
        ledger, out = self.intake({'parent.json': parent(), 'child.json': child()})
        self.assertTrue(ledger['universal'])
        self.assertEqual(ledger['parent_id'], 'parent-stream')
        self.assertEqual(len(ledger['bots']), 2)
        self.assertEqual(ledger['counts']['registry_entries'], 2)
        self.assertEqual(ledger['counts']['linked_bots'], 1)
        linked = ledger['linked_bots'][0]
        self.assertEqual(linked['status'], 'matched_source')
        self.assertEqual(linked['names'], ['First label', 'Older label'])
        self.assertIn('child-stream', linked['identity_aliases'])
        self.assertEqual(len(ledger['event_bindings']), 7)
        by_event = {r['event_name']: r for r in ledger['event_bindings']}
        for name in ('INTENT_UNIDENTIFIED', 'ON_CONNECT_EVENT', 'TELEPHONY_WELCOME_EVENT', 'WELCOME_MESSAGE_EVENT', 'defaultDialogId'):
            self.assertEqual(by_event[name]['status'], 'matched_source')
            self.assertEqual(by_event[name]['owner_scope'], 'linked_bot')
            self.assertEqual(by_event[name]['runtime_binding'], 'unverified')
        self.assertEqual(by_event['INTENT_UNIDENTIFIED']['source_candidates'][0]['dialog_id'], 'recovery-dialog')
        self.assertEqual(by_event['REPEAT_RESPONSE_EVENT']['status'], 'disabled')
        self.assertEqual(by_event['TASK_FAILURE_EVENT']['status'], 'non_dialog_action')
        self.assertFalse(any('stale-task' in str(g) or 'stale-owner' in str(g) for g in ledger['coverage_gaps']))
        self.assertEqual(by_event['WELCOME_MESSAGE_EVENT']['configuration']['pre_conditions'], {'channels': ['web']})
        self.assertEqual(ledger['universal_parents'][0]['local_dialog_ids'], ['local-dialog'])
        plan = json.loads((out / '_system_plan.json').read_text())
        self.assertEqual({p['role'] for p in plan['work_packages'] if 'artifact_id' in p}, {'parent', 'child'})
        self.assertEqual(plan['linked_source_dependencies'], ledger['linked_bots'])
        for inventory in out.glob('bot_*/_inventory.json'):
            self.assertTrue(all(d['name'] == 'Same task label' for d in json.loads(inventory.read_text())['dialogs']))

    def test_missing_children_do_not_resolve_to_parent_hidden_dialog(self):
        ledger, _ = self.intake({'parent.json': parent()})
        self.assertEqual(ledger['linked_bots'][0]['status'], 'missing_source')
        self.assertEqual(ledger['event_bindings'][0]['status'], 'missing_owner_source')
        self.assertTrue(any(g['category'] == 'missing_source' for g in ledger['coverage_gaps']))
        self.assertFalse(any(g['evidence'] == ['selected-system'] and g['category'] == 'missing_source' for g in ledger['coverage_gaps']))

    def test_parent_owned_events_resolve_id_and_ref_id(self):
        data = parent(); data['linkedBotsDetails'] = []; data['defaultDialogId'] = 'local-reference'
        data['botEvents'] = {'INTENT_UNIDENTIFIED': event('local-reference'),
                             'WELCOME_MESSAGE_EVENT': event('local-dialog', 'parent-reference')}
        ledger, _ = self.intake({'parent.json': data})
        for binding in ledger['event_bindings']:
            self.assertEqual(binding['status'], 'matched_source')
            self.assertEqual(binding['owner_scope'], 'parent')
        self.assertEqual(len(ledger['linked_bots']), 0)

    def test_registry_only_wrapped_parent_has_no_fabricated_dialogs(self):
        data = parent(); del data['dialogs']; del data['dialogComponents']
        original = copy.deepcopy(data)
        self.assertEqual(unwrap({'botDefinition': data}), (data, '/botDefinition'))
        self.assertEqual(data, original)
        ledger, out = self.intake({'parent.json': {'botDefinition': data}})
        self.assertEqual(ledger['counts']['bots'], 1)
        self.assertEqual(ledger['counts']['node_occurrences'], 0)
        self.assertTrue(ledger['registry_entries'][0]['source_pointer'].startswith('/botDefinition/'))
        self.assertTrue(ledger['event_bindings'][0]['source'].endswith('/botDefinition/botEvents/INTENT_UNIDENTIFIED'))
        self.assertEqual(json.loads((out / '_inventory.json').read_text())['dialogs'], [])

    def test_explicit_selection_does_not_expand_scope(self):
        ledger, _ = self.intake({'parent.json': parent(), 'child.json': child()}, '--definition', 'source_001/parent.json')
        self.assertEqual(len(ledger['bots']), 1)
        self.assertEqual(ledger['linked_bots'][0]['status'], 'source_unselected')
        self.assertEqual(ledger['linked_bots'][0]['unselected_artifact_ids'], ['source_001/child.json'])

    def test_unrelated_name_match_is_unselected_and_no_prefix_stripping(self):
        data = parent(); data['fallbackDetails'] = []
        other = child(); other['_id'] = 'st-child-reference'; other['name'] = 'First label'
        ledger, _ = self.intake({'parent.json': data, 'other.json': other})
        self.assertEqual(len(ledger['bots']), 1)
        self.assertEqual(ledger['linked_bots'][0]['status'], 'missing_source')

    def test_duplicate_exports_are_not_silently_chosen(self):
        ledger, _ = self.intake({'parent.json': parent(), 'one.json': child(), 'two.json': child()})
        self.assertEqual(len(ledger['bots']), 1)
        self.assertEqual(len(ledger['linked_bots'][0]['unselected_artifact_ids']), 2)
        all_ledger, _ = self.intake({'parent.json': parent(), 'one.json': child(), 'two.json': child()}, '--all-definitions')
        self.assertEqual(all_ledger['linked_bots'][0]['status'], 'ambiguous_source')
        self.assertEqual(all_ledger['event_bindings'][0]['status'], 'ambiguous_owner_source')

    def test_task_from_wrong_owner_and_same_label_are_not_substituted(self):
        data = parent(); data['botEvents'] = {'WELCOME_MESSAGE_EVENT': event('welcome-reference')}; data.pop('defaultDialogId')
        ledger, _ = self.intake({'parent.json': data, 'child.json': child()})
        self.assertEqual(ledger['event_bindings'][0]['status'], 'task_owner_mismatch')
        data['botEvents']['WELCOME_MESSAGE_EVENT']['task'] = 'Same task label'
        ledger, _ = self.intake({'parent.json': data, 'child.json': child()})
        self.assertEqual(ledger['event_bindings'][0]['status'], 'missing_task_source')

    def test_default_and_event_disagreement_preserves_both(self):
        data = parent(); data['defaultDialogId'] = 'local-reference'
        ledger, _ = self.intake({'parent.json': data, 'child.json': child()})
        bindings = {r['event_name']: r for r in ledger['event_bindings']}
        self.assertEqual(bindings['defaultDialogId']['owner_scope'], 'parent')
        self.assertEqual(bindings['INTENT_UNIDENTIFIED']['owner_scope'], 'linked_bot')
        self.assertTrue(any(g['category'] == 'configuration_disagreement' for g in ledger['coverage_gaps']))

    def test_disabled_fallback_cannot_establish_default_activation(self):
        data = parent(); data['botEvents']['INTENT_UNIDENTIFIED']['enabled'] = False
        ledger, _ = self.intake({'parent.json': data, 'child.json': child()})
        binding = next(r for r in ledger['event_bindings'] if r['event_name'] == 'defaultDialogId')
        self.assertEqual(binding['status'], 'fallback_activation_unverified')

    def test_discovery_denominators_survive_record_deletion(self):
        ledger, _ = self.intake({'parent.json': parent()})
        ledger['registry_entries'].pop(); ledger['counts']['registry_entries'] -= 1
        self.assertTrue(any('Universal discovery' in e for e in validate(ledger, [])))

    def test_parent_handoff_is_not_reported_as_child(self):
        ledger, _ = self.intake({'parent.json': parent()})
        source = ledger['bots'][0]
        handoff = {k: [] for k in ('goals_events', 'entry_assumptions', 'routes_returns', 'state_contracts', 'dependencies', 'exclusions', 'gap_ids')}
        handoff.update(source_identity={'artifact_id': source['artifact_id'], 'bot_id': source['id'],
            'source_hash': ledger['artifacts'][0]['source_hash']}, capability_scope=['local recovery and registry'], quality={'status': 'partial'})
        merged = reconcile(ledger, [handoff])
        self.assertEqual(len(merged['parents']), 1)
        self.assertEqual(merged['children'], [])
        self.assertEqual(merged['global_status'], 'partial')
        self.assertEqual(merged['event_bindings'], ledger['event_bindings'])

    def test_nested_registry_discovery_is_bounded_and_preserves_roles(self):
        data = parent()
        nested = child(); nested['type'] = 'universalbot'; nested['linkedBotsDetails'] = [{'_id': 'leaf-reference'}]
        leaf = {'_id': 'leaf-stream', 'refId': 'leaf-reference', 'dialogs': [], 'dialogComponents': []}
        # Multiple parent candidates need explicit root input; linked dependencies are in a second selected folder.
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        root = Path(tmp.name); direct = root / 'parent.json'; direct.write_text(json.dumps(data))
        rest = root / 'children'; rest.mkdir()
        (rest / 'nested.json').write_text(json.dumps(nested)); (rest / 'leaf.json').write_text(json.dumps(leaf))
        result = run_cli(direct, root / 'out', '--additional-export', rest)
        self.assertEqual(result.returncode, 0, result.stderr)
        ledger = json.loads((root / 'out' / '_coverage.json').read_text())
        self.assertEqual(len(ledger['bots']), 3)
        self.assertEqual(len(ledger['universal_parents']), 2)
        self.assertTrue(all(r['status'] == 'matched_source' for r in ledger['linked_bots']))

    def test_overlapping_registry_aliases_require_reconciliation(self):
        data = parent()
        data['linkedBotsDetails'].append({'_id': 'second-reference', 'name': 'Second child'})
        data['fallbackDetails'].append({'_id': 'second-reference', 'streamId': 'child-stream'})
        ledger, _ = self.intake({'parent.json': data, 'child.json': child()})
        self.assertEqual(len(ledger['bots']), 1)
        self.assertTrue(all(r['status'] == 'ambiguous_registry_identity' for r in ledger['linked_bots']))
        self.assertEqual(ledger['event_bindings'][0]['status'], 'ambiguous_registry_identity')

    def test_direct_child_ref_id_and_ambiguous_task_ids(self):
        data = parent(); data['fallbackDetails'] = []
        linked = child(); linked['refId'] = 'child-reference'
        linked['dialogs'].append(dialog('duplicate-welcome', 'welcome-reference'))
        ledger, _ = self.intake({'parent.json': data, 'child.json': linked})
        self.assertEqual(ledger['linked_bots'][0]['status'], 'matched_source')
        welcome = next(r for r in ledger['event_bindings'] if r['event_name'] == 'WELCOME_MESSAGE_EVENT')
        self.assertEqual(welcome['status'], 'ambiguous_task')

    def test_invalid_owner_and_unknown_action_do_not_guess_local_execution(self):
        data = parent(); data.pop('defaultDialogId')
        data['botEvents'] = {'WELCOME_MESSAGE_EVENT': event('local-dialog', ['parent-stream']),
                             'FUTURE_EVENT': event('local-dialog', action='futureAction')}
        ledger, _ = self.intake({'parent.json': data})
        self.assertEqual([r['status'] for r in ledger['event_bindings']], ['unsupported_owner_reference', 'unsupported_event_action'])

    def test_repeated_intake_is_deterministic(self):
        definitions = {'parent.json': parent(), 'child.json': child()}
        first, _ = self.intake(definitions)
        second, _ = self.intake(definitions)
        self.assertEqual(first, second)

    def test_name_mode_keeps_same_id_different_names_and_ambiguous_routes(self):
        data = parent()
        data['linkedBotsDetails'] = [{'_id': 'reused-id', 'name': 'Child Alpha'}, {'_id': 'reused-id', 'name': 'Child Beta'}]
        data['fallbackDetails'] = []
        data['botEvents'] = {'WELCOME_MESSAGE_EVENT': event('welcome-reference', 'reused-id')}
        data.pop('defaultDialogId')
        first = child(); first['name'] = 'Child Alpha'
        second = child(); second['_id'] = 'second-stream'; second['refId'] = 'second-reference'; second['name'] = 'Child Beta'
        ledger, _ = self.intake({'parent.json': data, 'alpha.json': first, 'beta.json': second}, '--linked-identity', 'name')
        self.assertEqual(len(ledger['bots']), 3)
        self.assertEqual(len(ledger['linked_bots']), 2)
        self.assertTrue(all(r['status'] == 'matched_source' for r in ledger['linked_bots']))
        self.assertEqual({r['identity_key'] for r in ledger['linked_bots']}, {'Child Alpha', 'Child Beta'})
        self.assertEqual(ledger['event_bindings'][0]['status'], 'ambiguous_owner')
        self.assertEqual(len(ledger['event_bindings'][0]['registry_owner_candidates']), 2)
        self.assertTrue(any(g['category'] == 'registry_identity_disagreement' for g in ledger['coverage_gaps']))
        counts = next(iter(ledger['universal_discovery'].values()))
        self.assertEqual((counts['registry_entries'], counts['distinct_id_values'], counts['distinct_name_values']), (2, 1, 2))

    def test_name_mode_resolves_unique_owner_and_preserves_source_basis(self):
        data = parent(); data['linkedBotsDetails'] = data['linkedBotsDetails'][:1]; data['fallbackDetails'] = []
        linked = child(); linked['name'] = 'First label'
        ledger, out = self.intake({'parent.json': data, 'child.json': linked}, '--linked-identity', 'name')
        binding = ledger['event_bindings'][0]
        self.assertEqual(binding['status'], 'matched_source')
        self.assertEqual(binding['owner_source_identity_mode'], 'name')
        self.assertEqual(binding['owner_source_identity_key'], 'First label')
        self.assertEqual(binding['source_candidates'][0]['dialog_id'], 'recovery-dialog')
        self.assertEqual(json.loads((out / '_system_plan.json').read_text())['linked_identity_mode'], 'name')
        # Explicit source selection still overrides automatic dependency expansion.
        selected, _ = self.intake({'parent.json': data, 'child.json': linked}, '--linked-identity', 'name', '--definition', 'source_001/parent.json')
        self.assertEqual(selected['linked_bots'][0]['status'], 'source_unselected')

    def test_name_mode_does_not_choose_duplicate_sources_or_conflicting_name_ids(self):
        data = parent(); data['linkedBotsDetails'] = [{'_id': 'first-id', 'name': 'Named child'}]
        first = child(); first['name'] = 'Named child'
        second = copy.deepcopy(first); second['_id'] = 'other-stream'
        ledger, _ = self.intake({'parent.json': data, 'one.json': first, 'two.json': second}, '--linked-identity', 'name')
        self.assertEqual(len(ledger['bots']), 1)
        self.assertEqual(ledger['linked_bots'][0]['status'], 'ambiguous_source')
        data['linkedBotsDetails'].append({'_id': 'second-id', 'name': 'Named child'})
        ledger, _ = self.intake({'parent.json': data, 'one.json': first}, '--linked-identity', 'name')
        self.assertEqual(len(ledger['bots']), 1)
        self.assertEqual(ledger['linked_bots'][0]['status'], 'ambiguous_registry_identity')

    def test_name_mode_never_substitutes_missing_name_id_or_case_match(self):
        data = parent(); data['linkedBotsDetails'] = [{'_id': 'child-stream', 'name': 'child-stream'}]; data['fallbackDetails'] = []
        linked = child(); linked.pop('name')
        ledger, _ = self.intake({'parent.json': data, 'child.json': linked}, '--linked-identity', 'name', '--all-definitions')
        self.assertEqual(ledger['linked_bots'][0]['status'], 'missing_source')
        linked['name'] = 'CHILD-STREAM'
        ledger, _ = self.intake({'parent.json': data, 'child.json': linked}, '--linked-identity', 'name')
        self.assertEqual(len(ledger['bots']), 1)
        data['linkedBotsDetails'][0].pop('name')
        ledger, _ = self.intake({'parent.json': data, 'child.json': linked}, '--linked-identity', 'name')
        self.assertEqual(ledger['linked_bots'][0]['status'], 'unresolved_identity')

    def test_name_mode_stream_alias_stays_with_matching_registry_name(self):
        data = parent(); data['linkedBotsDetails'] = [{'_id': 'shared-id', 'name': 'Child Alpha'}, {'_id': 'shared-id', 'name': 'Child Beta'}]
        data['fallbackDetails'] = [{'_id': 'shared-id', 'name': 'Child Alpha', 'streamId': 'alpha-stream-alias'}]
        data['botEvents'] = {'WELCOME_MESSAGE_EVENT': event('welcome-reference', 'alpha-stream-alias')}; data.pop('defaultDialogId')
        alpha = child(); alpha['name'] = 'Child Alpha'
        beta = child(); beta['name'] = 'Child Beta'; beta['_id'] = 'beta-stream'
        ledger, _ = self.intake({'parent.json': data, 'alpha.json': alpha, 'beta.json': beta}, '--linked-identity', 'name')
        binding = ledger['event_bindings'][0]
        self.assertEqual(binding['status'], 'matched_source')
        self.assertEqual(binding['owner_source_identity_key'], 'Child Alpha')
        beta_record = next(r for r in ledger['linked_bots'] if r['identity_key'] == 'Child Beta')
        self.assertNotIn('alpha-stream-alias', beta_record['identity_aliases'])

    def test_malformed_parent_collections_and_events_remain_gaps(self):
        data = parent(); data['dialogs'] = None
        ledger, _ = self.intake({'botDefinition.json': data})
        self.assertEqual(ledger['bots'], [])
        self.assertTrue(any(g['category'] == 'unsupported_parse' for g in ledger['coverage_gaps']))
        data = parent(); data['linkedBotsDetails'] = [None, {'name': 'No ID'}]; data['botEvents'] = {'ODD_EVENT': []}
        ledger, _ = self.intake({'parent.json': data})
        self.assertEqual(len(ledger['registry_entries']), 2)
        self.assertTrue(all(r['status'] == 'unresolved_identity' for r in ledger['linked_bots']))
        self.assertEqual(ledger['event_bindings'][0]['status'], 'unsupported_event_shape')


if __name__ == '__main__':
    unittest.main()
