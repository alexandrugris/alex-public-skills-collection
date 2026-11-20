"""Offline stdlib check of the brand toolkit assets and shared palette contract."""
import base64
import hashlib
import re
from pathlib import Path

BRAND_ROOT = Path(__file__).resolve().parent.parent
SKILL_ROOT = BRAND_ROOT.parent
SNAPSHOT_SHA256 = "148dd36d700b4ddd741f670c52f763533ac09015604cdcc946edaf9508eb2173"


def main():
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert skill.startswith("---\nname: alexandru-style\n"), "parent SKILL.md name mismatch"
    assert not (BRAND_ROOT / "SKILL.md").exists(), "duplicate nested brand/SKILL.md must not exist"

    workflow = (BRAND_ROOT / "references" / "production-workflow.md").read_text(encoding="utf-8")
    for rel in re.findall(r"`((?:references|templates|scripts)/[^` ]+)`", workflow):
        assert (BRAND_ROOT / rel).is_file(), f"missing brand asset: {rel}"

    doc_html = (BRAND_ROOT / "templates" / "document.html").read_text(encoding="utf-8")
    assert 'class="doc"' in doc_html
    assert "TOKENS_PATH" in doc_html

    article_html = (BRAND_ROOT / "templates" / "article.html").read_text(encoding="utf-8")
    assert "doc--flow" in article_html
    assert "tokens.css" in article_html

    tokens = (BRAND_ROOT / "references" / "tokens.css").read_text(encoding="utf-8")
    paper = re.search(r"--paper\s*:\s*#([0-9A-Fa-f]{6})", tokens)
    burgundy = re.search(r"--burgundy\s*:\s*#([0-9A-Fa-f]{6})", tokens)
    assert paper and paper.group(1).upper() == "FBFAF7"
    assert burgundy and burgundy.group(1).upper() == "8D2829"

    deck_src = (BRAND_ROOT / "scripts" / "build_deck.py").read_text(encoding="utf-8")
    assert 'color("paper")' in deck_src and 'color("burgundy")' in deck_src

    parts = sorted((BRAND_ROOT / "binaries-archive").glob("ag-personal-brand-snapshot.tar.gz.b64.part-*"))
    assert len(parts) == 11, f"expected 11 archive parts, found {len(parts)}"
    raw = base64.b64decode(b"".join(p.read_bytes() for p in parts))
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == SNAPSHOT_SHA256, f"archive SHA-256 mismatch: {digest}"

    print("Brand assets, templates, shared palette, and snapshot archive verified.")


if __name__ == "__main__":
    main()