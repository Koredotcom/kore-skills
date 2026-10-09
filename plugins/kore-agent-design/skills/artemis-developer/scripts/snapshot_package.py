#!/usr/bin/env python3
"""Read-only, bounded file inventory and content comparison for exported folders."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys

MAX_FILES = 10000
MAX_BYTES = 128 * 1024 * 1024


class SnapshotError(ValueError):
    pass


def digest(files: list[dict]) -> str:
    payload = json.dumps(files, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def walk_error(error: OSError) -> None:
    raise error


def snapshot(root: Path) -> dict:
    if root.is_symlink() or not root.is_dir():
        raise SnapshotError("Input must be a regular directory, not a symlink or ZIP.")
    files = []
    total = 0
    names = set()
    for parent, directories, filenames in os.walk(root, followlinks=False, onerror=walk_error):
        directories.sort()
        for name in directories + sorted(filenames):
            path = Path(parent) / name
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise SnapshotError("Symlinks are not supported in a source snapshot.")
            if name in directories:
                continue
            if not stat.S_ISREG(info.st_mode):
                raise SnapshotError("Source snapshot contains a non-regular file.")
            relative = path.relative_to(root).as_posix()
            if "\\" in relative:
                raise SnapshotError("Backslashes in source names are not portable.")
            if relative.casefold() in names:
                raise SnapshotError("Source paths collide when compared without case.")
            names.add(relative.casefold())
            if len(files) >= MAX_FILES or total + info.st_size > MAX_BYTES:
                raise SnapshotError("Source exceeds the file-count or byte limit.")
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            with os.fdopen(os.open(path, flags), "rb") as handle:
                start = os.fstat(handle.fileno())
                if not stat.S_ISREG(start.st_mode) or (start.st_dev, start.st_ino) != (info.st_dev, info.st_ino):
                    raise SnapshotError("Source changed during inventory; retry a stable copy.")
                h = hashlib.sha256()
                size = 0
                while chunk := handle.read(1024 * 1024):
                    size += len(chunk)
                    if total + size > MAX_BYTES:
                        raise SnapshotError("Source exceeds the byte limit.")
                    h.update(chunk)
                end = os.fstat(handle.fileno())
            fields = ("st_size", "st_mtime_ns", "st_ctime_ns")
            if any(getattr(start, f) != getattr(end, f) for f in fields) or size != start.st_size:
                raise SnapshotError("Source changed during inventory; retry a stable copy.")
            total += size
            files.append({"path": relative, "size": size, "sha256": h.hexdigest()})
    files.sort(key=lambda item: item["path"])
    return {"schema_version": 1, "files": files, "digest": digest(files)}


def read_manifest(path: Path) -> dict:
    with path.open("rb") as handle:
        data = handle.read(8 * 1024 * 1024 + 1)
    if len(data) > 8 * 1024 * 1024:
        raise SnapshotError("Comparison manifest is too large.")
    value = json.loads(data)
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise SnapshotError("Unsupported comparison manifest.")
    files = value.get("files")
    if not isinstance(files, list) or len(files) > MAX_FILES:
        raise SnapshotError("Invalid comparison file list.")
    seen = set()
    for item in files:
        if not isinstance(item, dict) or set(item) != {"path", "size", "sha256"}:
            raise SnapshotError("Invalid comparison entry.")
        name = item["path"]
        if not isinstance(name, str) or not name or "\\" in name or "\0" in name:
            raise SnapshotError("Invalid comparison path.")
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or str(relative) != name or name == ".":
            raise SnapshotError("Comparison paths must be normalized relative paths.")
        if name.casefold() in seen:
            raise SnapshotError("Duplicate comparison path.")
        seen.add(name.casefold())
        if type(item["size"]) is not int or item["size"] < 0:
            raise SnapshotError("Invalid comparison size.")
        if not isinstance(item["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
            raise SnapshotError("Invalid comparison hash.")
    files.sort(key=lambda item: item["path"])
    if value.get("digest") != digest(files):
        raise SnapshotError("Comparison digest does not match its file inventory.")
    return value


def compare(current: dict, previous: dict) -> dict:
    now = {item["path"]: item for item in current["files"]}
    old = {item["path"]: item for item in previous["files"]}
    shared = now.keys() & old.keys()
    changed = sorted(name for name in shared if now[name] != old[name])
    return {
        "added": sorted(now.keys() - old.keys()),
        "removed": sorted(old.keys() - now.keys()),
        "changed": changed,
        "unchanged_count": len(shared) - len(changed),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--compare", type=Path, metavar="MANIFEST")
    args = parser.parse_args()
    try:
        current = snapshot(args.root)
        if args.compare:
            current["comparison"] = compare(current, read_manifest(args.compare))
        print(json.dumps(current, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError) as exc:
        print(f"snapshot failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
