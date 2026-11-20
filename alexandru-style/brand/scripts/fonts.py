"""Use bundled OFL fonts without changing user or system font settings."""
import base64
import hashlib
import io
import os
import tarfile
from pathlib import Path
from xml.sax.saxutils import escape
ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / 'fonts'
SNAPSHOT = 'ag-personal-brand-main'
SNAPSHOT_SHA256 = '148dd36d700b4ddd741f670c52f763533ac09015604cdcc946edaf9508eb2173'


def font_files():
    paths = sorted(FONT_DIR.glob('*.ttf'))
    if paths:
        return [(path.name, path.read_bytes()) for path in paths]

    # The collection stores the original binary assets in a split archive.
    parts = sorted((ROOT / 'binaries-archive').glob('ag-personal-brand-snapshot.tar.gz.b64.part-*'))
    if not parts:
        raise RuntimeError('Bundled fonts missing. Keep fonts/ or binaries-archive/ with the skill.')
    data = base64.b64decode(b''.join(part.read_bytes() for part in parts))
    if hashlib.sha256(data).hexdigest() != SNAPSHOT_SHA256:
        raise RuntimeError('The bundled brand snapshot is incomplete or has changed.')
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        fonts = []
        for member in archive.getmembers():
            path = Path(member.name)
            if member.isfile() and path.parent.as_posix() == f'{SNAPSHOT}/fonts' and path.suffix == '.ttf':
                with archive.extractfile(member) as font:
                    fonts.append((path.name, font.read()))
    return sorted(fonts)


def font_css():
    rules = []
    for name, data in font_files():
        family, style = Path(name).stem.split('-', 1)
        family = {'IBMPlexMono': 'IBM Plex Mono'}.get(family, family)
        weight = 700 if 'Bold' in style and 'Semi' not in style else 600 if 'SemiBold' in style else 500 if 'Medium' in style else 400
        data = base64.b64encode(data).decode()
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
