"""Tier 1 & 2: Schema, pattern coverage, examples DB, token sync, and archive integrity tests."""
import csv
import json
import re
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestDataIntegrity(unittest.TestCase):
    def test_patterns_json_schema_and_uniqueness(self):
        data = json.loads((REPO_ROOT / "anti-ai" / "patterns.json").read_text(encoding="utf-8"))
        for key in ("version", "updated", "categories", "phrases"):
            self.assertIn(key, data)

        declared_cats = set(data["categories"].keys())
        valid_sevs = {"low", "medium", "high"}
        valid_langs = {"any", "ro", "fr"}

        ids = [p["id"] for p in data["phrases"]]
        dups = [k for k, v in Counter(ids).items() if v > 1]
        self.assertEqual(dups, [], f"Duplicate pattern IDs: {dups}")

        regexes = [p["regex"] for p in data["phrases"]]
        dup_re = [k for k, v in Counter(regexes).items() if v > 1]
        self.assertEqual(dup_re, [], f"Duplicate regexes: {dup_re}")

        for p in data["phrases"]:
            self.assertIn(p["cat"], declared_cats, f"Undeclared cat on {p['id']}")
            self.assertIn(p["severity"], valid_sevs, f"Invalid severity on {p['id']}")
            self.assertIn(p.get("lang", "any"), valid_langs, f"Invalid lang on {p['id']}")
            self.assertFalse(
                any(ord(c) < 32 for c in p["regex"]),
                f"Control character found in regex for {p['id']}: {p['regex']!r}",
            )
            re.compile(p["regex"], re.I)

    def test_all_high_patterns_covered_by_fixtures(self):
        data = json.loads((REPO_ROOT / "anti-ai" / "patterns.json").read_text(encoding="utf-8"))
        covered = set()
        for fn in sorted((REPO_ROOT / "anti-ai" / "tests").glob("fixtures-*.csv")):
            with fn.open(encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    if (row.get("expect") or "").strip().upper() == "FAIL":
                        exid = (row.get("exid") or "").strip()
                        if exid:
                            covered.add(exid)
        high_ids = [p["id"] for p in data["phrases"] if p["severity"] == "high"]
        missing = [
            pid for pid in high_ids
            if not (pid in covered or any(c.endswith(".") and pid.startswith(c) for c in covered))
        ]
        self.assertEqual(missing, [], f"HIGH patterns missing fixture coverage: {missing}")

    def test_examples_database_valid_and_queryable(self):
        cli = REPO_ROOT / "anti-ai" / "scripts" / "examples.py"
        r = subprocess.run([sys.executable, str(cli), "validate"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

        q = subprocess.run(
            [sys.executable, str(cli), "query", "--lang", "en", "--topic", "leadership", "--limit", "3", "--format", "json"],
            capture_output=True, text=True,
        )
        self.assertEqual(q.returncode, 0, q.stderr)
        results = json.loads(q.stdout)
        self.assertEqual(len(results), 3)

        g = subprocess.run([sys.executable, str(cli), "gaps", "--json"], capture_output=True, text=True)
        self.assertEqual(g.returncode, 0, g.stderr)
        gap_data = json.loads(g.stdout)
        self.assertGreaterEqual(gap_data["uncaught_count"], 1)

    def test_writing_sample_retrieval_respects_register_and_relevance(self):
        cli = REPO_ROOT / "anti-ai" / "scripts" / "examples.py"

        def samples(lang, topic, *flags):
            result = subprocess.run(
                [sys.executable, str(cli), "query", "--lang", lang, "--topic", topic,
                 "--limit", "0", "--seed", "42", *flags],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            return [line for line in result.stdout.splitlines() if line.startswith("[")]

        engineering = samples("en", "engineering")
        self.assertEqual(len(engineering), 2)
        self.assertTrue(all("analytical" in line and "fiction" not in line for line in engineering))
        self.assertEqual(engineering, samples("en", "engineering"))
        fiction = samples("en", "fiction")
        self.assertEqual(len(fiction), 2)
        self.assertTrue(all(" | fiction | " in line for line in fiction))
        for lang in ("en", "fr", "ro"):
            self.assertEqual(samples(lang, "jurisprudence"), [])
        for lang in ("fr", "ro"):
            self.assertEqual(samples(lang, "engineering"), engineering)
        self.assertEqual(samples("en", "engineering", "--voice-samples", "0"), [])

    def test_design_system_tokens_match_canonical_css(self):
        tokens_css = (REPO_ROOT / "alexandru-style" / "brand" / "references" / "tokens.css").read_text(encoding="utf-8")
        design_md = (REPO_ROOT / "alexandru-style" / "design-system.md").read_text(encoding="utf-8")

        token_re = re.compile(r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})\b")
        canonical = {name: hx.upper() for name, hx in token_re.findall(tokens_css)}
        m = re.search(r"```css\s*:root\s*\{(.*?)\}\s*```", design_md, re.S)
        self.assertIsNotNone(m, "design-system.md missing :root CSS block")
        doc_tokens = {name: hx.upper() for name, hx in token_re.findall(m.group(1))}
        self.assertGreaterEqual(len(doc_tokens), 18)

        for name, hx in doc_tokens.items():
            self.assertIn(name, canonical, f"design-system.md token {name} absent from brand/references/tokens.css")
            self.assertEqual(
                hx,
                canonical[name],
                f"Token {name} hex mismatch: design-system.md={hx} vs tokens.css={canonical[name]}",
            )

    def test_brand_offline_check_script(self):
        script = REPO_ROOT / "alexandru-style" / "brand" / "scripts" / "check.py"
        r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_evals_datasets_valid(self):
        triggers = REPO_ROOT / "evals" / "triggers.csv"
        with triggers.open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertGreaterEqual(len(rows), 20)
        self.assertTrue(any(r["should_trigger"] == "false" for r in rows))

        cases = json.loads((REPO_ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases["cases"]), 5)
        for case in cases["cases"]:
            if "input_file" in case:
                self.assertTrue(
                    (REPO_ROOT / case["input_file"]).is_file(),
                    f"Missing eval input_file: {case['input_file']}",
                )


if __name__ == "__main__":
    unittest.main()
