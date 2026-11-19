"""Check the portable skill and the shared palette contract."""
from pathlib import Path
import re
import runpy
r = Path(__file__).resolve().parent.parent
skill = (r / 'SKILL.md').read_text()
assert skill.startswith('---\nname: ag-trenches-style\n')
for path in re.findall(r'`((?:references|templates|scripts)/[^` ]+)`', skill):
    assert (r / path).is_file(), path
assert 'class="doc"' in (r / 'templates/document.html').read_text()
assert 'TOKENS_PATH' in (r / 'templates/document.html').read_text()
assert '--paper:' in (r / 'references/tokens.css').read_text()
ns = runpy.run_path(str(r / 'scripts/build_deck.py'))
assert str(ns['PAPER']) == 'FBFAF7'
assert str(ns['BURGUNDY']) == '8D2829'
print('Skill assets, document scale and shared slide palette verified.')