#!/usr/bin/env python3
"""Copy only public static site content, never checkout metadata or tooling."""
from pathlib import Path
import shutil
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

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
        if str(relative) == 'docs/legacy/index_placeholder_b4413b13.html':
            # Preserve the original snapshot in Git, not as a broken mini-app.
            target.write_text('''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Archived dashboard · GOLD4</title><link rel="stylesheet" href="../../assets/style.css">
<main class="wrap"><h1>Archived dashboard</h1><p>This historical placeholder is not current ring research.</p>
<p><a href="../../index.html">Open the current dashboard</a> ·
<a href="https://github.com/karagemop466-tech/GOLD4/blob/b34ae17/docs/legacy/index_placeholder_b4413b13.html">Read the original preserved snapshot</a></p></main></html>''')
        else:
            shutil.copyfile(source, target)
        count += 1
    verify_links(destination)
    print(f'Staged {count} public files (no Git metadata, workflows or Python tooling)')
    return count


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        self.urls.extend(v for k, v in attrs if k in ('href', 'src') and v)


def verify_links(destination):
    """Fail publication if any staged HTML has a missing local file target."""
    errors = []
    for page in destination.rglob('*.html'):
        parser = Links()
        parser.feed(page.read_text())
        for url in parser.urls:
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith('/'):
                continue
            target = (page.parent / unquote(parsed.path)).resolve()
            if not target.is_relative_to(destination.resolve()) or not target.exists():
                errors.append(f'{page.relative_to(destination)}: {url}')
    if errors:
        raise ValueError('Missing staged HTML local-file targets: ' + '; '.join(errors))


if __name__ == '__main__':
    stage(sys.argv[1])
