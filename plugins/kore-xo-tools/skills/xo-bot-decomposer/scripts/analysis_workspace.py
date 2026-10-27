#!/usr/bin/env python3
"""Create durable local analysis folders and immutable checkpoints; no bot code runs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

AREAS = ('evidence', 'work', 'reports')
MARKER = '.xo-analysis-workspace.json'
MARKER_VALUE = {'kind': 'xo-bot-decomposer-analysis', 'schema_version': 1}


def is_analysis_workspace(path):
    marker = path / MARKER
    if not marker.exists() and not marker.is_symlink():
        return False
    if marker.is_symlink() or not marker.is_file() or marker.stat().st_size > 1024:
        raise ValueError('Invalid analysis workspace marker; inspect the folder before intake')
    if read_json(marker) != MARKER_VALUE:
        raise ValueError('Unknown analysis workspace marker; inspect the folder before intake')
    return True


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def read_session(root):
    session = read_json(root / 'session.json')
    if not isinstance(session, dict) or session.get('schema_version') != 1:
        raise ValueError('Unsupported session schema; preserve the file and inspect saved checkpoints')
    label = session.get('latest_checkpoint')
    if label is not None and (not isinstance(label, str) or not label.startswith('CP-') or not label[3:].isdigit()):
        raise ValueError('Invalid checkpoint identifier in session')
    sources = session.get('source_locations', [])
    if not isinstance(sources, list) or any(not isinstance(item, dict) or not isinstance(item.get('path'), str)
            or not Path(item['path']).is_absolute() or not isinstance(item.get('sha256'), str)
            or len(item['sha256']) != 64 or any(c not in '0123456789abcdef' for c in item['sha256']) for item in sources):
        raise ValueError('source_locations must contain absolute file paths and lowercase SHA-256 hashes')
    return session


def atomic_json(path, value):
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    try:
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def workspace(path):
    path = Path(path).absolute()
    if path.is_symlink() or path.resolve() != path:
        raise ValueError('Use a workspace path without symlinked components')
    if not (path / 'session.json').is_file():
        raise ValueError('Missing session.json; recover a saved checkpoint or initialize a new empty workspace')
    if (path / 'session.json').is_symlink():
        raise ValueError('Workspace session cannot be a symlink')
    for area in (*AREAS, 'checkpoints'):
        if not (path / area).is_dir() or (path / area).is_symlink():
            raise ValueError('Workspace areas must be ordinary directories')
    return path


def initialize(path):
    path = Path(path).absolute()
    if path.resolve() != path or path.is_symlink() or (path.exists() and (not path.is_dir() or any(path.iterdir()))):
        raise ValueError('Use a new or empty persistent workspace without symlinked components')
    for area in (*AREAS, 'checkpoints'):
        (path / area).mkdir(parents=True, exist_ok=True)
    for area in ('parents', 'children', 'shared_runtime', 'system_review'):
        (path / 'work' / area).mkdir()
    session = {
        'schema_version': 1, 'status': 'initialized', 'latest_checkpoint': None,
        'active_evidence_run': None, 'scope': None, 'identity_mode': None,
        'source_locations': [], 'work_packages': [], 'shared_contract_revision': None,
        'decisions': [], 'missing_inputs': [], 'next_actions': ['Run intake into evidence/run-001, then register source locations and work ownership.'],
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }
    atomic_json(path / 'session.json', session)
    atomic_json(path / MARKER, MARKER_VALUE)
    (path / 'README.md').write_text('# XO analysis workspace\n\nResume by reading session.json, work/_coverage.json and work/_system_plan.json where present.\nRun analysis_workspace.py status against this folder before continuing.\n\n- evidence/: immutable numbered intake runs; never overwrite an earlier run.\n- work/: current notes, reviewed ledgers, parent/child reports, shared contracts and handoffs.\n- reports/: deliverable copies and their referenced coverage files.\n- checkpoints/: immutable copies of saved work/reports/session plus hashes of retained evidence.\n\nOnly the coordinator writes session.json, checkpoints and shared ledgers. Stop worker writes briefly while checkpointing. Keep source exports at their original durable locations; record locations and original hashes locally. Do not commit or upload this workspace without explicit authorization and privacy review.\n', encoding='utf-8')
    return {'workspace': str(path), 'status': 'initialized'}


def inventory(root):
    files = {}
    for area in AREAS:
        for path in sorted((root / area).rglob('*')):
            if path.is_symlink():
                raise ValueError('Symlink in analysis workspace; checkpoint not created')
            if path.is_file():
                files[path.relative_to(root).as_posix()] = digest(path)
    return files


def checkpoint(path, note):
    root = workspace(path)
    session_hash = digest(root / 'session.json')
    session = read_session(root)
    before = inventory(root)
    existing = [int(p.name[3:]) for p in (root / 'checkpoints').iterdir() if p.name.startswith('CP-') and p.name[3:].isdigit()]
    label = f'CP-{max(existing, default=0) + 1:04}'
    destination = root / 'checkpoints' / label
    pending = Path(tempfile.mkdtemp(prefix='.pending-', dir=root / 'checkpoints'))
    try:
        for relative in before:
            if relative.startswith('evidence/'):
                continue  # Immutable evidence runs are retained once, with integrity hashes.
            target = pending / 'files' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / relative, target)
            if digest(target) != before[relative]:
                raise ValueError('Work changed during checkpoint; stop worker writes and retry')
        if inventory(root) != before or digest(root / 'session.json') != session_hash:
            raise ValueError('Workspace changed during checkpoint; stop worker writes and retry')
        session.update(latest_checkpoint=label, updated_at=datetime.now(timezone.utc).isoformat())
        atomic_json(pending / 'session.json', session)
        atomic_json(pending / 'manifest.json', {'schema_version': 1, 'checkpoint': label, 'note': note,
            'created_at': session['updated_at'], 'files': before, 'session_sha256': digest(pending / 'session.json')})
        if destination.exists():
            raise ValueError('Checkpoint name already exists; do not run concurrent coordinators')
        pending.rename(destination)
        atomic_json(root / 'session.json', session)
        return {'checkpoint': label, 'files_accounted': len(before), 'path': str(destination)}
    finally:
        if pending.exists():
            shutil.rmtree(pending)


def status(path):
    root = workspace(path)
    session = read_session(root)
    label = session.get('latest_checkpoint')
    result = {'workspace': str(root), 'session': session, 'checkpoint': label,
              'changed_since_checkpoint': [], 'missing_since_checkpoint': [], 'added_since_checkpoint': [],
              'checkpoint_snapshot_errors': [], 'orphan_checkpoints': [], 'source_issues': [],
              'source_locations_recorded': len(session.get('source_locations', []))}
    result['orphan_checkpoints'] = sorted(p.name for p in (root / 'checkpoints').iterdir()
        if p.name.startswith('CP-') and p.name[3:].isdigit() and p.is_dir() and not p.is_symlink()
        and (label is None or int(p.name[3:]) > int(label[3:])))
    for source in session.get('source_locations', []):
        original = Path(source['path'])
        if original.resolve() != original or original.is_symlink() or not original.is_file():
            issue = 'missing_or_not_regular_file'
        else:
            try:
                issue = 'changed' if digest(original) != source['sha256'] else None
            except OSError:
                issue = 'unreadable'
        if issue:
            result['source_issues'].append({'path': str(original), 'issue': issue})
    if label:
        snapshot = root / 'checkpoints' / label
        if snapshot.is_symlink() or (snapshot / 'manifest.json').is_symlink():
            raise ValueError('Checkpoint and manifest cannot be symlinks')
        manifest = read_json(snapshot / 'manifest.json')
        recorded = manifest['files']
        for relative in recorded:
            parts = Path(relative).parts
            if not parts or parts[0] not in AREAS or '..' in parts or Path(relative).is_absolute():
                raise ValueError('Invalid checkpoint file path')
        actual = inventory(root)
        result['changed_since_checkpoint'] = sorted(p for p in recorded if p in actual and actual[p] != recorded[p])
        result['missing_since_checkpoint'] = sorted(set(recorded) - set(actual))
        result['added_since_checkpoint'] = sorted(set(actual) - set(recorded))
        for relative, expected in recorded.items():
            if relative.startswith('evidence/'):
                continue
            saved = snapshot / 'files' / relative
            if not saved.is_file() or saved.resolve() != saved or digest(saved) != expected:
                result['checkpoint_snapshot_errors'].append(relative)
        saved_session = snapshot / 'session.json'
        if not saved_session.is_file() or saved_session.is_symlink() or digest(saved_session) != manifest.get('session_sha256'):
            result['checkpoint_snapshot_errors'].append('session.json')
        result['session_changed_since_checkpoint'] = digest(root / 'session.json') != manifest.get('session_sha256')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('init', 'checkpoint', 'status'))
    parser.add_argument('workspace', type=Path)
    parser.add_argument('--note', default='Saved analysis progress')
    args = parser.parse_args()
    try:
        result = initialize(args.workspace) if args.command == 'init' else checkpoint(args.workspace, args.note) if args.command == 'checkpoint' else status(args.workspace)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
