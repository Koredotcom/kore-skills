import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'summarize_metrics.py'
SPEC = importlib.util.spec_from_file_location('review_metrics', SCRIPT)
METRICS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(METRICS)


def sample(**changes):
    row = dict(snapshot_id='v1', channel='chat', measurement='visible_response',
               session_id='session-a', turn=1, status='measured', seconds=3.0,
               evidence='evidence/timing.json#turn-1')
    row.update(changes)
    return row


def document(*rows):
    return dict(schema_version=1, targets_seconds={'chat': 3, 'voice': 2}, observations=list(rows))


class MetricsTests(unittest.TestCase):
    def test_statistics_and_censored_counts(self):
        rows = [sample(turn=i + 1, seconds=value) for i, value in enumerate([1, 2, 3, 4, 10])]
        rows += [sample(turn=6, status='missing', seconds=None), sample(turn=7, status='timeout', seconds=None)]
        group = METRICS.summarize(document(*rows))['groups'][0]
        self.assertEqual((group['attempts'], group['measured'], group['missing'], group['timeouts']), (7, 5, 1, 1))
        self.assertEqual((group['mean_seconds'], group['median_seconds'], group['observed_p95_seconds']), (4, 3, 10))
        self.assertEqual(group['within_target_percent_of_measured'], 60)

    def test_groups_preserve_snapshot_channel_and_measurement(self):
        result = METRICS.summarize(document(sample(), sample(snapshot_id='v2'),
            sample(measurement='debug_response'), sample(channel='voice', measurement='audible_response')))
        self.assertEqual(len(result['groups']), 4)
        debug = next(g for g in result['groups'] if g['measurement'] == 'debug_response')
        self.assertIsNone(debug['target_seconds'])
        self.assertIsNone(debug['within_target_percent_of_measured'])

    def test_missing_is_not_zero_or_pass(self):
        group = METRICS.summarize(document(sample(status='missing', seconds=None)))['groups'][0]
        self.assertIsNone(group['mean_seconds'])
        self.assertIsNone(group['within_target_percent_of_measured'])
        self.assertEqual(METRICS.summarize(document())['groups'], [])

    def test_unknown_route_debug_keeps_no_channel_claim(self):
        group = METRICS.summarize(document(sample(channel='unknown', measurement='debug_response', seconds=4.8)))['groups'][0]
        self.assertEqual(group['mean_seconds'], 4.8)
        self.assertEqual(group['channel'], 'unknown')
        self.assertIsNone(group['target_seconds'])
        self.assertIsNone(group['within_target_percent_of_measured'])
        with self.assertRaises(ValueError):
            METRICS.summarize(document(sample(channel='unknown')))

    def test_user_target_override(self):
        data = document(sample(seconds=4))
        data['targets_seconds']['chat'] = 5
        self.assertEqual(METRICS.summarize(data)['groups'][0]['within_target_count'], 1)

    def test_reject_invalid_times(self):
        for value in [-1, True, '2', None, float('inf'), float('nan'), 10**400]:
            with self.subTest(value=str(value)), self.assertRaises(ValueError):
                METRICS.summarize(document(sample(seconds=value)))

    def test_reject_invalid_identity_and_types(self):
        for changes in [dict(turn=True), dict(turn=0), dict(snapshot_id=''), dict(evidence=' '),
                        dict(channel='voice'), dict(status='passed'), dict(status='timeout'),
                        dict(measurement='model_ttft')]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                METRICS.summarize(document(sample(**changes)))
        with self.assertRaises(ValueError):
            METRICS.summarize(document(sample(), sample()))

    def test_input_unchanged_and_order_independent(self):
        data = document(sample(seconds=7), sample(turn=2, seconds=2))
        before = copy.deepcopy(data)
        result = METRICS.summarize(data)
        self.assertEqual(data, before)
        data['observations'].reverse()
        self.assertEqual(result, METRICS.summarize(data))

    def test_bad_document_and_targets(self):
        for data in [[], {}, dict(schema_version=True), dict(schema_version=1, targets_seconds={})]:
            with self.assertRaises(ValueError):
                METRICS.summarize(data)
        for value in [0, -1, True, float('nan')]:
            data = document(sample())
            data['targets_seconds']['chat'] = value
            with self.assertRaises(ValueError):
                METRICS.summarize(data)

    def test_cli_error_and_no_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'metrics.json'
            content = json.dumps(document(sample()))
            path.write_text(content)
            result = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['observation_count'], 1)
            self.assertEqual(path.read_text(), content)
            path.write_text('{"schema_version":1,"schema_version":1}')
            failed = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(failed.returncode, 2)
            self.assertEqual(failed.stdout, '')
            self.assertIn('duplicate JSON field', failed.stderr)


if __name__ == '__main__':
    unittest.main()
