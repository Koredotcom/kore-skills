from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from xo_coverage import build, coverage_section, write
from decompose_bot import discover, safe_extract
from reconcile_system import reconcile
from review_coverage import validate
from source_scan import scan
from xo_graph import discover_graph
from xo_export_parser import _redact_structure, parse_condition, build_inventory


def bot(identity='bot-one', count=2):
    return {'_id': identity, 'name': identity, 'dialogs': [
        {'_id': f'dialog-{i}', 'localeData': {'en': {'name': 'Same display name'}},
         'isHidden': i == 0, 'nodes': [{'nodeId': f'outer-{i}', 'componentId': 'action', 'type': 'botAction'}]}
        for i in range(count)], 'dialogComponents': [
            {'_id': 'action', 'name': 'Shared action', 'type': 'botAction', 'nodes': [
                {'nodeId': 'nested', 'componentId': 'hook', 'type': 'SDKWebHook', 'webhookTimeout': 4}]},
            {'_id': 'hook', 'name': 'Prefetch', 'type': 'SDKWebHook'},
        ], 'events': {'onConnect': {'enabled': True, 'target': 'dialog-0'}}}


def run_cli(source, output, *args):
    return subprocess.run([sys.executable, str(ROOT / 'scripts/decompose_bot.py'), str(source), str(output), *map(str, args)], capture_output=True, text=True)


class CoverageTests(unittest.TestCase):
    def test_shared_referenced_actions_keep_each_occurrence(self):
        data = bot(count=5)
        graph = discover_graph(data)
        self.assertEqual(graph['discovery']['outer_nodes'], 5)
        self.assertEqual(graph['discovery']['physical_nodes'], 6)
        self.assertEqual(len(graph['node_occurrences']), 10)
        hooks = [o for o in graph['node_occurrences'] if o['type'] == 'SDKWebHook']
        self.assertEqual(len(hooks), 5)
        self.assertEqual(len({h['source_pointer'] for h in hooks}), 1)
        self.assertEqual(len({h['occurrence_path'] for h in hooks}), 5)
        inv = build_inventory(data, 'fixture', 'XO 10 or earlier')
        self.assertEqual(inv['summary']['nodes_total'], 10)

    def test_inline_cycles_null_unknown_and_unexpanded_stay_visible(self):
        data = bot(count=1)
        data['dialogs'][0]['nodes'][0]['nodes'] = [{'nodeId': 'inline', 'componentId': None, 'type': 'futureNode'}]
        data['dialogComponents'][0]['nodes'].append({'nodeId': 'cycle', 'componentId': 'action', 'type': 'botAction'})
        data['otherGraph'] = [{'nodeId': 'orphan', 'type': 'mystery'}]
        graph = discover_graph(data)
        kinds = {i['kind'] for i in graph['graph_issues']}
        self.assertTrue({'component_cycle', 'unresolved_component', 'unsupported_node_type', 'unexpanded_node'} <= kinds)
        self.assertLess(len(graph['node_occurrences']), 20)

    def test_condition_tree_and_absent_operators(self):
        condition = {'conjoin': 'and', 'tests': [{'field': 'x', 'op': 'eq', 'value': 1}, {'conjoin': 'or', 'tests': [{'field': 'y'}, {'context': 'context.z', 'op': 'exists'}]}]}
        rendered = parse_condition(condition)
        self.assertIn('AND (', rendered)
        self.assertIn(' OR ', rendered)
        self.assertIn('Unresolved condition', rendered)
        self.assertNotIn('y ==', rendered)

    def test_zip_manifest_and_companions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); src = root/'fixture.zip'; out = root/'out'
            with zipfile.ZipFile(src, 'w') as z:
                z.writestr('botDefinition.json', json.dumps(bot()))
                z.writestr('botFunctions.js', 'function prepare() { context.ready = true; }')
                z.writestr('config.json', json.dumps({'timeout': 10000, 'token': 'synthetic-config-value'}))
                z.writestr('icon.png', b'not-a-real-image')
            self.assertEqual(run_cli(src, out).returncode, 0)
            ledger = json.loads((out/'_coverage.json').read_text())
            self.assertEqual(len(ledger['artifacts']), 4)
            self.assertEqual({a['role'] for a in ledger['artifacts']}, {'definition', 'javascript', 'configuration', 'asset'})
            self.assertTrue(ledger['bot_functions'])
            self.assertTrue(ledger['events'])
            self.assertNotIn('synthetic-config-value', ''.join(p.read_text() for p in out.rglob('*') if p.is_file()))

    def test_ambiguous_definitions_require_explicit_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'source'; src.mkdir()
            for name in ('botDefinition.json', 'appDefinition.json'):
                (src/name).write_text(json.dumps(bot()))
            out=root/'out'; self.assertEqual(run_cli(src,out).returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            self.assertFalse(ledger['bots'])
            self.assertTrue(any(g['category']=='awaiting_scope_decision' for g in ledger['coverage_gaps']))
            out2=root/'all'; self.assertEqual(run_cli(src,out2,'--all-definitions').returncode,0)
            self.assertEqual(len(json.loads((out2/'_coverage.json').read_text())['bots']),2)

    def test_two_webhooks_23_occurrences_one_generic_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'source'; src.mkdir()
            data=bot('parent-bot',23)
            data['dialogComponents'].append({'_id':'hook-two','name':'Other Prefetch','type':'SDKWebHook'})
            for i,d in enumerate(data['dialogs']):
                d['nodes']=[{'nodeId':f'hook-{i}','componentId':'hook' if i<5 else 'hook-two','type':'SDKWebHook','webhookTimeout':4}]
            (src/'botDefinition.json').write_text(json.dumps(data))
            (src/'botkit.js').write_text("function shared(request, componentName, callback) { context.cache = request; callback(); }\nsdk.registerBot({botId: 'parent-bot', handlers: {on_webhook: shared}});")
            out=root/'out'; self.assertEqual(run_cli(src,out).returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            self.assertEqual(ledger['counts']['webhooks'],2)
            self.assertEqual(ledger['counts']['webhook_occurrences'],23)
            for wh in ledger['webhooks']:
                self.assertEqual(wh['handler_status'],'source_candidate_requires_dispatch_review')
                self.assertEqual(wh['handler_candidates'][0]['dispatch'],'generic_candidate')
                self.assertEqual(wh['occurrences'][0]['timeout_unit'],'unknown')
                self.assertEqual(wh['runtime_binding'],'unverified')
            self.assertEqual(len({w['handler_candidates'][0]['handler'] for w in ledger['webhooks']}),1)

    def test_helpers_comments_expressions_arrows_and_module_methods(self):
        code = '''// function phantom() { fake(); }
        /* const invented = () => boom(); */
        function prepare(value) { context.ready = value; return finish(); }
        const finish = function() { return env.FLAG; };
        const reset = (x) => { context.ready = x; };
        module.exports = { method(x) { return prepare(x); } };
        prepare(true); missingHelper();'''
        result=scan(code,'functions.js')
        names={f['name'] for f in result['functions']}
        self.assertTrue({'prepare','finish','reset','method'} <= names)
        self.assertFalse({'phantom','invented'} & names)
        self.assertFalse({'fake','boom'} & {c['name'] for c in result['calls']})
        self.assertTrue(any(s['access']=='write_or_replace' for s in result['states']))

    def test_helper_resolution_and_missing_file_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'source'; src.mkdir()
            data=bot(count=1); data['dialogComponents'].append({'_id':'script','type':'script','script':'prepare(); missingHelper();'})
            (src/'botDefinition.json').write_text(json.dumps(data))
            helper=src/'botFunctions.js'; helper.write_text('function prepare() { context.ready = true; }')
            out=root/'out'; self.assertEqual(run_cli(src,out).returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            self.assertEqual(next(c for c in ledger['calls'] if c['name']=='prepare')['resolution'],'source_candidate')
            self.assertTrue(any('missingHelper' in g['affected'] for g in ledger['coverage_gaps']))
            helper.unlink(); out2=root/'without'; self.assertEqual(run_cli(src,out2).returncode,0)
            self.assertTrue(any('prepare' in g['affected'] for g in json.loads((out2/'_coverage.json').read_text())['coverage_gaps']))

    def test_inline_retry_scripted_transfer_config_and_state_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'botDefinition.json'
            data=bot(count=1)
            data['dialogComponents'].append({'_id':'entity','type':'entity','retryCallback':'context.TaskEnd.Action = "AgentTransfer"; context.Cache = {}; context.cache.failed = true; env["FLAG"]; env.TIMEOUT; {{env.HOST}};','message':'<vxml><transfer/></vxml>'})
            src.write_text(json.dumps(data)); out=root/'out'
            self.assertEqual(run_cli(src,out,'--scope','goals-only').returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            self.assertTrue(any(e.get('mechanism')=='script_or_markup_candidate' for e in ledger['events']))
            refs={c['field'] for c in ledger['configuration'] if c.get('kind')=='reference'}
            self.assertTrue({'env.FLAG','env.TIMEOUT','env.HOST'} <= refs)
            self.assertTrue(any(g['category']=='intentionally_excluded' for g in ledger['coverage_gaps']))

    def test_global_hooks_exist_without_webhook_nodes_samples_not_active(self):
        result=scan("function adjust(r, cb) { cb(); }\nsdk.registerBot({botId:'b', handlers:{on_user_message:adjust}});\nconst sample={on_bot_message:adjust};",'botkit.js')
        hooks={h['event']:h for h in result['hooks']}
        self.assertEqual(hooks['on_user_message']['registration'],'registration_candidate')
        self.assertEqual(hooks['on_bot_message']['registration'],'unresolved')
        self.assertTrue(all(f['activation']=='not_established' for f in result['functions']))

    def test_credential_redaction_all_forms(self):
        data={'config':[{'name':'apiKey','value':'planted-a','isSecured':False}],
              'code':'const cfg = {token: "planted-b"}; const secret = `planted-c`; const url = "https://u:planted-d@example.invalid/?token=planted-e";',
              'headers':{'Authorization':'Bearer planted-f'},'fixture':{'password':'planted-g'}}
        rendered=json.dumps(_redact_structure(data))
        for suffix in 'abcdefg': self.assertNotIn('planted-'+suffix,rendered)

    def test_unsupported_partial_and_output_source_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'botDefinition.json'; src.write_text('{"unsupported":true}')
            out=root/'out'; self.assertEqual(run_cli(src,out).returncode,0)
            self.assertTrue(json.loads((out/'_coverage.json').read_text())['coverage_gaps'])
            self.assertNotEqual(run_cli(root,root/'nested').returncode,0)
            self.assertNotEqual(run_cli(src,out).returncode,0)

    def test_symlink_and_duplicate_zip_members_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); archive=root/'link.zip'
            with zipfile.ZipFile(archive,'w') as z:
                info=zipfile.ZipInfo('link'); info.create_system=3; info.external_attr=0o120777 << 16; z.writestr(info,'outside')
            with self.assertRaises(ValueError): safe_extract(archive,root/'extract')
            src=root/'src'; src.mkdir(); (src/'link.js').symlink_to(root/'absent')
            self.assertEqual(discover(src,'source_001','export')[0]['reason'],'Symlink not followed')

    def test_warning_consistency_order_and_review_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'botDefinition.json'; src.write_text(json.dumps(bot(count=1)))
            out=root/'out'; self.assertEqual(run_cli(src,out).returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            docs=[out/'_analysis_draft.md',out/'_technical_reference_draft.md']
            warning=coverage_section(ledger).strip()
            self.assertTrue(all(p.read_text().partition('\n')[2].lstrip().startswith(warning) for p in docs))
            self.assertTrue(any('Unreviewed disposition' in e for e in validate(ledger,docs)))
            for item in ledger['review_items']:
                item.update(disposition='unresolved',reason='Source reviewed; behavior awaits recorded dependency contracts.')
            self.assertFalse(validate(ledger,docs))
            docs[0].write_text('# Test\n\n**Source:** too early\n'+warning)
            self.assertTrue(any('misplaced' in e for e in validate(ledger,docs)))
            ledger['status']['implementation_dependencies']='complete'
            self.assertTrue(any('implementation-complete' in e for e in validate(ledger,docs)))

    def test_universal_missing_parent_owner_mismatch_and_order_independent_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'src'; src.mkdir()
            first=bot('child-a',1); second=bot('child-b',1)
            second['dialogs'][0]['_id']='resume'; second['dialogs'][0]['localeData']['en']['name']='Resume Task'
            first['dialogComponents'].append({'_id':'script','type':'script','script':'sdk.executeTask("child-a", "Resume Task");'})
            (src/'one.json').write_text(json.dumps(first)); (src/'two.json').write_text(json.dumps(second))
            out=root/'out'; self.assertEqual(run_cli(src,out,'--all-definitions','--universal').returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            self.assertTrue((out/'_system_plan.json').exists())
            self.assertEqual(ledger['routing_dependencies'][0]['status'],'owner_mismatch')
            handoffs=[]
            for b in ledger['bots']:
                a=next(a for a in ledger['artifacts'] if a['id']==b['artifact_id'])
                handoffs.append({'source_identity':{'artifact_id':a['id'],'source_hash':a['source_hash'],'bot_id':b['id']},'capability_scope':'selected fixture outcomes','goals_events':[{'name':'Shared Outcome'}],'entry_assumptions':[], 'routes_returns':[], 'state_contracts':[], 'dependencies':[], 'exclusions':[], 'gap_ids':[], 'quality':{'static':'complete','runtime':'not_established'}})
            merged=reconcile(ledger,handoffs)
            self.assertEqual(merged,reconcile(ledger,list(reversed(handoffs))))
            self.assertEqual(merged['global_status'],'partial')
            self.assertTrue(any(g['category']=='routing_overlap' for g in merged['coverage_gaps']))
            broken=copy.deepcopy(handoffs); broken[0]['source_identity']['source_hash']='wrong'
            with self.assertRaises(ValueError): reconcile(ledger,broken)

    def test_fifty_dialog_detail_limit_does_not_limit_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'botDefinition.json'; src.write_text(json.dumps(bot(count=51)))
            out=root/'out'; self.assertEqual(run_cli(src,out).returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            self.assertEqual(ledger['counts']['webhook_occurrences'],51)
            self.assertEqual(len(list(out.glob('dialog_*.md'))),51)


    def test_same_line_hooks_and_functions_have_independent_dispositions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'src'; src.mkdir()
            (src/'botDefinition.json').write_text(json.dumps(bot(count=1)))
            (src/'hooks.js').write_text("function one(r, cb) { cb(); } function two(r, cb) { cb(); } sdk.registerBot({botId:'bot-one',handlers:{on_webhook:one,on_user_message:two}});")
            out=root/'out'; self.assertEqual(run_cli(src,out).returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            self.assertEqual(len({h['review_id'] for h in ledger['botkit_hooks']}),2)
            self.assertEqual(len({f['review_id'] for f in ledger['bot_functions']}),2)

    def test_exact_dispatch_and_unknown_registration_are_not_generic_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'src'; src.mkdir()
            (src/'botDefinition.json').write_text(json.dumps(bot(count=1)))
            code="function shared(r, componentName, cb) { if (componentName === 'Prefetch') { cb(); } } sdk.registerBot({botId:'different-bot',handlers:{on_webhook:shared}});"
            (src/'hooks.js').write_text(code)
            out=root/'out'; self.assertEqual(run_cli(src,out).returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            self.assertEqual(ledger['botkit_hooks'][0]['dispatch'],'component_name_candidate')
            self.assertFalse(ledger['webhooks'][0]['handler_candidates'])
            self.assertEqual(ledger['webhooks'][0]['handler_status'],'missing_source')

    def test_unused_webhook_definition_is_counted_without_inventing_active_dependency(self):
        data=bot(count=0)
        artifacts=[{'id':'source_001/bot.json','role':'definition','source_group':'source_001','source_hash':'fixture'}]
        ledger=build(artifacts,[{'data':data,'artifact_id':'source_001/bot.json','version_route':'XO 10 or earlier'}])
        self.assertEqual(ledger['counts']['webhooks'],1)
        self.assertEqual(ledger['counts']['webhook_occurrences'],0)
        self.assertEqual(ledger['webhooks'][0]['handler_status'],'uncalled_definition')

    def test_explicit_single_bot_companion_resolves_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'botDefinition.json'
            data=bot(count=1); data['dialogComponents'].append({'_id':'script','type':'script','script':'prepare();'})
            src.write_text(json.dumps(data)); companion=root/'helper.js'; companion.write_text('function prepare() { context.ready=true; }')
            out=root/'out'; self.assertEqual(run_cli(src,out,'--companion-source',companion).returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            self.assertEqual(next(c for c in ledger['calls'] if c['name']=='prepare')['resolution'],'source_candidate')

    def test_schema_contract_config_layers_and_secrets_remain_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'src'; src.mkdir()
            (src/'botDefinition.json').write_text(json.dumps(bot(count=1)))
            (src/'config.json').write_text(json.dumps({'timeout':4000}))
            contracts=root/'contract.json'; contracts.write_text(json.dumps({'schema':{'token':'planted-contract'},'timeout':10000}))
            out=root/'out'; self.assertEqual(run_cli(src,out,'--contracts',contracts,'--defer','runtime override').returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            timeout_records=[c for c in ledger['configuration'] if c.get('field')=='timeout']
            self.assertEqual({c['value'] for c in timeout_records},{4000,10000})
            self.assertTrue(all(c['effective_value']=='unknown' for c in timeout_records))
            self.assertEqual(ledger['webhooks'][0]['provider_contract'],'unverified')
            self.assertNotIn('planted-contract',''.join(p.read_text() for p in out.rglob('*') if p.is_file()))
            self.assertTrue(any('runtime override' in g['affected'] for g in ledger['coverage_gaps']))

    def test_unknown_format_and_malformed_definition_are_partial_not_crashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'src'; src.mkdir()
            (src/'botDefinition.json').write_text(json.dumps({'dialogs':[None],'dialogComponents':[]}))
            (src/'settings.yaml').write_text('secret: planted-unsupported')
            out=root/'out'; self.assertEqual(run_cli(src,out).returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            self.assertFalse(ledger['bots'])
            self.assertTrue(any(g['category']=='unsupported_parse' for g in ledger['coverage_gaps']))
            self.assertNotIn('planted-unsupported',''.join(p.read_text() for p in out.rglob('*') if p.is_file()))

    def test_extended_evidence_determinism_and_source_preservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'src'; src.mkdir()
            (src/'appDefinition.json').write_text(json.dumps({'appDefinition':bot(count=3)}))
            (src/'botFunctions.js').write_text('function init() { context.ready=true; }')
            originals={p.name:p.read_bytes() for p in src.iterdir()}
            outs=[root/'one',root/'two']
            for out in outs: self.assertEqual(run_cli(src,out,'--universal').returncode,0)
            files=lambda out:{p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()}
            self.assertEqual(files(outs[0]),files(outs[1]))
            self.assertEqual(originals,{p.name:p.read_bytes() for p in src.iterdir()})
            ledger=json.loads((outs[0]/'_coverage.json').read_text())
            self.assertEqual(ledger['bots'][0]['version_route'],'XO 11')

    def test_graph_discovery_denominator_cannot_be_hidden_by_editing_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'botDefinition.json'; src.write_text(json.dumps(bot(count=1)))
            out=root/'out'; self.assertEqual(run_cli(src,out).returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            ledger['node_occurrences'].pop(); ledger['counts']['node_occurrences']-=1
            self.assertTrue(any('graph totals' in e for e in validate(ledger,[])))

    def test_runtime_and_gap_closure_require_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'botDefinition.json'; src.write_text(json.dumps(bot(count=1)))
            out=root/'out'; self.assertEqual(run_cli(src,out).returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            ledger['coverage_gaps'][0]['status']='resolved'; ledger['status']['runtime_validation']='passed'
            errors=validate(ledger,[])
            self.assertTrue(any('closure lacks evidence' in e for e in errors))
            self.assertTrue(any('Runtime status' in e for e in errors))

    def test_malformed_peer_does_not_discard_supported_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'src'; src.mkdir()
            (src/'good.json').write_text(json.dumps(bot(count=1)))
            malformed=bot(count=1); malformed['dialogs'][0]['nodes']=[None]
            (src/'bad.json').write_text(json.dumps(malformed))
            out=root/'out'; self.assertEqual(run_cli(src,out,'--all-definitions').returncode,0)
            ledger=json.loads((out/'_coverage.json').read_text())
            self.assertEqual(len(ledger['bots']),1)
            self.assertTrue(any(g['category']=='unsupported_parse' for g in ledger['coverage_gaps']))


if __name__=='__main__': unittest.main()
