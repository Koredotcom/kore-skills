#!/usr/bin/env python3
"""Summarize supplied review observations; never claim to verify their provenance."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

MAX_BYTES = 8 * 1024 * 1024
MAX_ROWS = 10000


def number(value: object, label: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError(f"{label} must be finite") from exc
    if not math.isfinite(result) or result < 0 or (positive and result == 0):
        raise ValueError(f"{label} must be {'positive' if positive else 'nonnegative'} and finite")
    return result


def text_field(row: dict, key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a nonempty string")
    return value


def summarize(document: object) -> dict:
    if not isinstance(document, dict) or type(document.get('schema_version')) is not int or document['schema_version'] != 1:
        raise ValueError('schema_version must be 1')
    targets = document.get('targets_seconds')
    if not isinstance(targets, dict) or set(targets) != {'chat', 'voice'}:
        raise ValueError('targets_seconds must contain chat and voice')
    targets = {key: number(value, key, positive=True) for key, value in targets.items()}
    rows = document.get('observations')
    if not isinstance(rows, list) or len(rows) > MAX_ROWS:
        raise ValueError(f'observations must be a list of at most {MAX_ROWS} rows')
    groups: dict[tuple, list] = {}
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('each observation must be an object')
        snapshot = text_field(row, 'snapshot_id')
        session = text_field(row, 'session_id')
        text_field(row, 'evidence')
        channel = text_field(row, 'channel')
        measurement = text_field(row, 'measurement')
        allowed = {'chat': {'visible_response', 'debug_response'},
                   'voice': {'audible_response', 'debug_response'},
                   'unknown': {'debug_response'}}
        if channel not in allowed or measurement not in allowed[channel]:
            raise ValueError('incompatible channel/measurement')
        turn = row.get('turn')
        if type(turn) is not int or turn < 1:
            raise ValueError('turn must be a positive integer')
        key = (snapshot, channel, measurement, session, turn)
        if key in seen:
            raise ValueError('duplicate observation identity')
        seen.add(key)
        status = row.get('status')
        if status not in ('measured', 'missing', 'timeout'):
            raise ValueError('status must be measured, missing or timeout')
        if 'seconds' not in row:
            raise ValueError('seconds is required; use null for missing/timeout')
        if status == 'measured':
            seconds = number(row['seconds'], 'seconds')
        else:
            if row['seconds'] is not None:
                raise ValueError('missing/timeout seconds must be null')
            seconds = None
        groups.setdefault((snapshot, channel, measurement), []).append((status, seconds))

    summaries = []
    for (snapshot, channel, measurement), samples in sorted(groups.items()):
        measured = sorted(value for status, value in samples if status == 'measured')
        count = len(measured)
        target = None if measurement == 'debug_response' else targets[channel]
        within = sum(value <= target for value in measured) if target is not None else None
        summaries.append({
            'snapshot_id': snapshot, 'channel': channel, 'measurement': measurement,
            'attempts': len(samples), 'measured': count,
            'missing': sum(status == 'missing' for status, _ in samples),
            'timeouts': sum(status == 'timeout' for status, _ in samples),
            'mean_seconds': statistics.mean(measured) if count else None,
            'median_seconds': statistics.median(measured) if count else None,
            'observed_p95_seconds': measured[math.ceil(0.95 * count) - 1] if count else None,
            'maximum_seconds': measured[-1] if count else None,
            'target_seconds': target, 'within_target_count': within,
            'within_target_percent_of_measured': 100 * within / count if count and within is not None else None,
        })
    return {'schema_version': 1, 'observation_count': len(rows), 'groups': summaries,
            'limitations': ['Statistics exclude missing and timed-out responses; report their counts alongside distributions.',
                            'Observed p95 uses nearest rank; small samples do not certify production SLAs.',
                            'Input shape checked; evidence provenance, source identity and execution budgets are not verified.']}


def unique_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON field: {key}')
        result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('observations', type=Path)
    args = parser.parse_args()
    try:
        with args.observations.open('rb') as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError(f'input exceeds {MAX_BYTES} bytes')
        document = json.loads(raw, object_pairs_hook=unique_object)
        result = summarize(document)
        print(json.dumps(result, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(f'metrics error: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
