"""Tier 1: Agent Skills specification & manifest integrity tests."""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_SKILLS = {"anti-ai", "blog-writer", "source-verifier", "alexandru-style"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LOCAL_REF_RE = re.compile(
    r"`((?:references|tests|scripts|examples|brand)/[A-Za-z0-9_./-]+|(?:design-system\.md|patterns\.json|check_tells\.py))`"
)


def parse_frontmatter(text: str):
    m = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    if not m:
        return None, ""
    raw = m.group(1)
    lines = raw.splitlines()
    fields = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        km = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not km:
            i += 1
            continue
        key, val = km.group(1), km.group(2)
        if val in ("|", ">", "|-", ">-"):
            block = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                block.append(lines[i][2:] if lines[i].startswith("  ") else "")
                i += 1
            fields[key] = {"style": val, "value": "\n".join(block).strip()}
        else:
            fields[key] = {"style": "plain", "value": val.strip().strip('"').strip("'")}
            i += 1
    return fields, raw


class TestSkillSpec(unittest.TestCase):
    def test_exact_skill_manifest_set(self):
        found = {p.parent.relative_to(REPO_ROOT).as_posix() for p in REPO_ROOT.rglob("SKILL.md")}
        self.assertEqual(
            found,
            EXPECTED_SKILLS,
            f"Unexpected SKILL.md layout (nested duplicates break recursive discovery): {sorted(found)}",
        )

    def test_frontmatter_and_size_limits(self):
        for skill in sorted(EXPECTED_SKILLS):
            manifest = REPO_ROOT / skill / "SKILL.md"
            text = manifest.read_text(encoding="utf-8")
            lines = text.splitlines()
            self.assertLessEqual(len(lines), 500, f"{manifest} exceeds 500-line spec limit ({len(lines)})")

            fields, _ = parse_frontmatter(text)
            self.assertIsNotNone(fields, f"{manifest}: missing YAML frontmatter")
            self.assertIn("name", fields, f"{manifest}: missing name")
            self.assertIn("description", fields, f"{manifest}: missing description")

            # Guard against the literal-block `name: |` newline bug that breaks Vibe.
            self.assertEqual(
                fields["name"]["style"],
                "plain",
                f"{manifest}: name must be a plain scalar, not block scalar {fields['name']['style']!r}",
            )
            name = fields["name"]["value"]
            self.assertRegex(name, NAME_RE, f"{manifest}: invalid name {name!r}")
            self.assertEqual(name, skill, f"{manifest}: name {name!r} must match folder {skill!r}")

            desc = fields["description"]["value"]
            self.assertTrue(desc, f"{manifest}: empty description")
            self.assertLessEqual(len(desc), 1024, f"{manifest}: description exceeds 1024 chars ({len(desc)})")

    def test_referenced_local_paths_exist(self):
        for skill in sorted(EXPECTED_SKILLS):
            skill_dir = REPO_ROOT / skill
            text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            for rel in sorted(set(LOCAL_REF_RE.findall(text))):
                target = skill_dir / rel.rstrip("/")
                self.assertTrue(
                    target.exists(),
                    f"{skill}/SKILL.md references missing path: {rel}",
                )


if __name__ == "__main__":
    unittest.main()
