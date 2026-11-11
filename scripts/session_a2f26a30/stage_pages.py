#!/usr/bin/env python3
"""Copy only public static site content, never checkout metadata or tooling."""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DIRS = {'assets', 'static', 'data', 'docs', 'pages', 'categories', 'reviews', 'reports', 'audit'}
EXTENSIONS = {'.html', '.css', '.js', '.json', '.md', '.txt', '.svg', '.png', '.jpg', '.jpeg', '.webp', '.ico', '.woff', '.woff2'}


def stage(destination, root=ROOT):
    destination = Path(destination).resolve()
    if destination == root.resolve() or root.resolve() in destination.parents:
        raise ValueError('Stage outside the repository to avoid recursive copies')
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError('Staging directory must be empty')
    count = 0
    for source in sorted(root.rglob('*')):
        relative = source.relative_to(root)
        if any(p.startswith('.') for p in relative.parts) and str(relative) != '.nojekyll':
            continue
        if source.is_symlink() or any(p.is_symlink() for p in source.parents if p != root):
            continue
        if not source.is_file():
            continue
        if len(relative.parts) > 1 and relative.parts[0] not in PUBLIC_DIRS:
            continue
        if source.suffix.lower() not in EXTENSIONS and str(relative) != '.nojekyll':
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        count += 1
    print(f'Staged {count} public files (no Git metadata, workflows or Python tooling)')
    return count


if __name__ == '__main__':
    stage(sys.argv[1])
