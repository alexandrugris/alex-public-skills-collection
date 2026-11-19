"""Use bundled OFL fonts without changing user or system font settings."""
from pathlib import Path
import base64
import os
from xml.sax.saxutils import escape
ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / 'fonts'

def font_css():
    rules = []
    for path in sorted(FONT_DIR.glob('*.ttf')):
        family, style = path.stem.split('-', 1)
        family = {'IBMPlexMono': 'IBM Plex Mono'}.get(family, family)
        weight = 700 if 'Bold' in style and 'Semi' not in style else 600 if 'SemiBold' in style else 500 if 'Medium' in style else 400
        data = base64.b64encode(path.read_bytes()).decode()
        for alias in ([family, 'Georgia'] if family == 'Gelasio' else [family]):
            rules.append(f'@font-face{{font-family:"{alias}";font-style:{"italic" if "Italic" in style else "normal"};font-weight:{weight};src:url(data:font/ttf;base64,{data}) format("truetype");}}')
    if not rules:
        raise RuntimeError('Bundled fonts missing; keep fonts/ with the skill')
    return '\n'.join(rules)

def font_environment():
    build = ROOT / 'build/fonts'
    build.mkdir(parents=True, exist_ok=True)
    config = build / 'fonts.conf'
    config.write_text(f'''<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
<include ignore_missing="yes">/etc/fonts/fonts.conf</include>
<dir>{escape(str(FONT_DIR))}</dir>
<cachedir>{escape(str(build / 'cache'))}</cachedir>
<match target="pattern"><test name="family" compare="eq"><string>Georgia</string></test><edit name="family" mode="assign" binding="strong"><string>Gelasio</string></edit></match>
</fontconfig>''')
    return dict(os.environ, FONTCONFIG_FILE=str(config))

if __name__ == '__main__':
    import subprocess
    env = font_environment()
    subprocess.run(['fc-cache', '-f', str(FONT_DIR)], env=env, check=True)
    for family in ('Georgia', 'Inter', 'IBM Plex Mono'):
        subprocess.run(['fc-match', family], env=env, check=True)