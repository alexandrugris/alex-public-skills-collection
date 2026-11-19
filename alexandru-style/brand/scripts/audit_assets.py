"""Verify the full shipped asset inventory against Git and disk, offline."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent
ASSET_SUFFIXES = {'.ttf', '.png', '.pdf', '.pptx', '.zip', '.html'}

def main():
    tracked = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0'))
    entries = json.loads((ROOT / 'references/assets-manifest.json').read_text())['files']
    expected = {e['path'] for e in entries}
    actual = {str(p.relative_to(ROOT)) for folder in ('fonts', 'samples')
              for p in (ROOT / folder).rglob('*') if p.is_file() and p.suffix.lower() in ASSET_SUFFIXES}
    assert expected == actual, f'Inventory mismatch: {expected ^ actual}'
    for entry in entries:
        path = ROOT / entry['path']
        assert entry['path'] in tracked, f"Not tracked: {entry['path']}"
        data = path.read_bytes()
        assert len(data) == entry['bytes'], path
        assert hashlib.sha256(data).hexdigest() == entry['sha256'], path
        # No LFS pointer can masquerade as an available binary.
        assert not data.startswith(b'version https://git-lfs.github.com/spec/'), path
    for family in ('Gelasio', 'Inter', 'IBMPlexMono'):
        license_path = f'fonts/{family}-OFL.txt'
        assert license_path in tracked
        assert 'SIL OPEN FONT LICENSE' in (ROOT / license_path).read_text()
    for folder in ('templates', 'references'):
        for path in (ROOT / folder).rglob('*'):
            if path.suffix not in {'.html', '.css'}:
                continue
            for reference in re.findall(r'''(?:url\(\s*["']?([^\s)"']+)|(?:src|href)=["']([^"']+))''', path.read_text()):
                value = next(v for v in reference if v)
                if value == 'TOKENS_PATH' or value.startswith(('data:', 'https:', 'http:', '#')):
                    continue
                target = (path.parent / value).resolve()
                assert target.is_file(), f'Missing dependency: {path}: {value}'
                assert str(target.relative_to(ROOT)) in tracked, f'Untracked dependency: {target}'
    print(f'PASS: {len(entries)} assets tracked, present, checksum-valid, no LFS placeholders; 3 licenses; maintained HTML/CSS dependencies complete.')
    print('Original archived HTML still names the unavailable historical hero photograph; see samples/validation.md.')

if __name__ == '__main__':
    main()
