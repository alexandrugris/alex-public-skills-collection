"""Verify preserved samples and reproduce the original deck's structure."""
from pathlib import Path
import hashlib
import json
import runpy
import tempfile
from pptx import Presentation

ROOT = Path(__file__).resolve().parent.parent

def signature(prs):
    return (prs.slide_width, prs.slide_height, [
        [(s.shape_type, s.left, s.top, s.width, s.height,
          s.text if s.has_text_frame else None) for s in slide.shapes]
        for slide in prs.slides])

def main():
    manifest = json.loads((ROOT / 'samples/manifest.json').read_text())
    for entry in manifest['files']:
        path = ROOT / 'samples' / entry['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], path
    for entry in json.loads((ROOT / 'fonts/manifest.json').read_text()):
        assert hashlib.sha256((ROOT / 'fonts' / entry['file']).read_bytes()).hexdigest() == entry['sha256']
    css = (ROOT / 'references/tokens.css').read_text()
    for name in ('sample-document.html', 'sample-page.html'):
        assert css in (ROOT / 'samples/original' / name).read_text(), name
    ns = runpy.run_path(str(ROOT / 'scripts/build_deck.py'))
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'deck.pptx'
        ns['build'](path)
        original = Presentation(ROOT / 'samples/original/sample-deck.pptx')
        current = Presentation(path)
        assert signature(original) == signature(current), 'Slide text or geometry changed'
        assert [str(s._element.xml) for s in original.slides] == [str(s._element.xml) for s in current.slides], 'Slide styling changed'
    print(f"PASS: {len(manifest['files'])} source checksums; original HTML CSS; all 9 slide XML trees, text and geometry.")
    print('Visual comparison still requires fonts, assets and rendered inspection; see samples/validation.md.')

if __name__ == '__main__':
    main()
