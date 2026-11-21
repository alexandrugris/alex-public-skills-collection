"""Tier 1: Unit tests for check_tells.py, validate_draft.py, and check_styled.py."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "anti-ai"))
sys.path.insert(0, str(REPO_ROOT / "alexandru-style" / "tests"))

import check_tells as ct  # noqa: E402
import check_styled as cs  # noqa: E402


class TestCheckTellsUnit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = ct.load_list()
        cls.scanner = REPO_ROOT / "anti-ai" / "check_tells.py"

    def run_cli(self, args):
        return subprocess.run(
            [sys.executable, str(self.scanner)] + args,
            capture_output=True,
            text=True,
        )

    def test_verdict_matrix(self):
        self.assertEqual(ct.compute_verdict({}), "PASS")
        self.assertEqual(ct.compute_verdict({"low": 5}), "PASS")
        self.assertEqual(ct.compute_verdict({"medium": 1, "low": 3}), "REVIEW")
        self.assertEqual(ct.compute_verdict({"high": 1, "medium": 2}), "FAIL")

    def test_severity_and_cat_filter_apply_to_heuristics(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "longwords.md"
            # Triggers house.word_len (low) and nothing high.
            p.write_text(("documentation architecture implementation configuration " * 12) + "\n", encoding="utf-8")
            r = self.run_cli(["--severity", "high", "--json", str(p)])
            self.assertEqual(r.returncode, 0)
            out = json.loads(r.stdout)
            self.assertEqual(out["hits"], [])
            self.assertEqual(out["verdict"], "PASS")

            r_text = self.run_cli(["--severity", "high", str(p)])
            self.assertIn("VERDICT: PASS", r_text.stdout)

    def test_diacritic_person_and_literal_exemptions(self):
        self.assertTrue(ct.person_follows("un ", " collègue"))
        self.assertTrue(ct.person_follows("un ", " bărbat"))
        self.assertEqual(ct.scan("Un collègue honnête prévient tôt.", self.data, lang="fr"), [])
        self.assertEqual(ct.scan("Un bărbat sincer spune adevărul.", self.data, lang="ro"), [])
        self.assertEqual(ct.scan("L'armée entretient ses armes.", self.data, lang="fr"), [])

    def test_markdown_masks_frontmatter_code_fences_and_urls(self):
        md = (
            "---\n"
            "title: delve tapestry\n"
            "---\n"
            "```python\n"
            "# delve into robust synergy tapestry\n"
            "```\n"
            "See https://example.com/delve-tapestry-leverage for details.\n"
            "We delve into the real bug here.\n"
        )
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sample.md"
            p.write_text(md, encoding="utf-8")
            r = self.run_cli(["--severity", "high", "--json", str(p)])
            out = json.loads(r.stdout)
            self.assertEqual(len(out["hits"]), 1)
            self.assertEqual(out["hits"][0]["id"], "inf.delve")
            self.assertEqual(out["hits"][0]["line"], 8)

    def test_lang_flag_scopes_rules(self):
        ro_text = "Vom furniza raportul ulterior."
        hits_en = ct.scan(ro_text, self.data, lang="en")
        hits_ro = ct.scan(ro_text, self.data, lang="ro")
        self.assertEqual(hits_en, [])
        self.assertTrue(any(h["id"].startswith("complex.ro.") for h in hits_ro))

    def test_heuristics_fire_on_synthetic_inputs(self):
        # em_dash_density
        em_text = "\n\n".join(["One - two - three." for _ in range(5)])
        self.assertIn("struct.em_dash_density", {n["id"] for n in ct.structural_heuristics(em_text, "x")})
        # gerund_list
        gerund_text = "- Building systems\n- Building tools\n- Building teams\n"
        self.assertIn("struct.gerund_list", {n["id"] for n in ct.structural_heuristics(gerund_text, "x")})
        # parallel_prose
        par_text = "Alpha tracks server boot speed. Beta tracks disk write latency. Gamma tracks cache hit ratios."
        self.assertIn("list.parallel_prose", {n["id"] for n in ct.parallel_list_notes(par_text, "x")})


class TestValidateDraftUnit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = REPO_ROOT / "blog-writer" / "tests" / "validate_draft.py"

    def run_val(self, content: str):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "draft.md"
            p.write_text(content, encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(self.validator), "--json", str(p)],
                capture_output=True, text=True,
            )
            return r.returncode, json.loads(r.stdout)

    def test_valid_draft_with_inline_and_sources_passes(self):
        rc, res = self.run_val(
            "# Small scripts beat big frameworks.\n\n"
            "Our deploy script ran in four seconds after reading [the spec](https://agentskills.io/specification).\n\n"
            "## Sources\n\n"
            "- [Agent Skills specification](https://agentskills.io/specification)\n"
        )
        self.assertEqual(rc, 0, res)
        self.assertEqual(res["verdict"], "PASS")

    def test_rejects_placeholder_url(self):
        rc, res = self.run_val(
            "# Logs cost real money.\n\n"
            "See [notes](https://ops.example.invalid/notes).\n\n"
            "## Sources\n\n"
            "- [Notes](https://ops.example.invalid/notes)\n"
        )
        self.assertEqual(rc, 1)
        self.assertTrue(any("placeholder or invalid URL" in p for p in res["problems"]))

    def test_rejects_banned_heading(self):
        rc, res = self.run_val(
            "# Title.\n\n"
            "## Introduction\n\n"
            "Plain prose with [spec](https://agentskills.io/specification).\n\n"
            "## Sources\n\n"
            "- [Spec](https://agentskills.io/specification)\n"
        )
        self.assertEqual(rc, 1)
        self.assertTrue(any("banned generic heading" in p for p in res["problems"]))

    def test_rejects_inline_url_missing_from_sources(self):
        rc, res = self.run_val(
            "# Title.\n\n"
            "See [A](https://agentskills.io/specification) and [B](https://diataxis.fr/start-here/).\n\n"
            "## Sources\n\n"
            "- [A](https://agentskills.io/specification)\n"
        )
        self.assertEqual(rc, 1)
        self.assertTrue(any("missing from `## Sources`" in p for p in res["problems"]))


class TestCheckStyledUnit(unittest.TestCase):
    def test_official_brand_templates_and_architecture_html_pass(self):
        targets = [
            REPO_ROOT / "alexandru-style" / "brand" / "templates" / "article.html",
            REPO_ROOT / "alexandru-style" / "brand" / "templates" / "page.html",
            REPO_ROOT / "alexandru-style" / "brand" / "templates" / "document.html",
            REPO_ROOT / "docs" / "skills-architecture.html",
            REPO_ROOT / "alexandru-style" / "tests" / "expected" / "sample-page.html",
        ]
        for path in targets:
            probs = cs.check_html(path.read_text(encoding="utf-8"), base_dir=path.parent)
            self.assertEqual(probs, [], f"{path} failed check_styled: {probs}")

    def test_anti_sample_fails_every_planted_defect(self):
        path = REPO_ROOT / "alexandru-style" / "tests" / "expected" / "anti-sample.html"
        probs = cs.check_html(path.read_text(encoding="utf-8"), base_dir=path.parent)
        joined = "\n".join(probs)
        for expected in (
            "no paper ground",
            "no uppercase Inter label pair",
            "h1 rule uses a heavy font-weight",
            "h3 rule uses a heavy font-weight",
            "dashed or double border",
            "gradient type",
            "text shadow",
            "white surface background",
            "centred body copy",
            "emoji found",
        ):
            self.assertIn(expected, joined, f"anti-sample missing expected finding: {expected}")

    def test_typographic_arrows_not_flagged_as_emoji(self):
        sample = (REPO_ROOT / "alexandru-style" / "tests" / "expected" / "sample-page.html").read_text(encoding="utf-8")
        with_arrows = sample.replace("What it shows", "Brief → Research → Draft")
        self.assertEqual(cs.check_html(with_arrows), [])

    def test_rejects_external_cdn_fonts(self):
        sample = (REPO_ROOT / "alexandru-style" / "tests" / "expected" / "sample-page.html").read_text(encoding="utf-8")
        with_cdn = sample.replace("<head>", '<head><link href="https://fonts.googleapis.com/css2?family=Inter">')
        probs = cs.check_html(with_cdn)
        self.assertTrue(any("external CDN" in p for p in probs))

    def test_marp_checks_valid_and_bullet_overflow(self):
        good_marp = (
            "<!-- theme: default -->\n<!-- size: 16:9 -->\n<!-- paginate: true -->\n"
            "<!-- style: |\n  section { background: #fbfaf7; font-family: Georgia, serif; border-top: 6px solid #8d2829; }\n-->\n"
            "# Slide 1\n\n- One\n- Two\n"
        )
        self.assertEqual(cs.check_marp(good_marp), [])

        bad_marp = good_marp + "\n---\n# Crowded slide\n" + "\n".join(f"- Bullet {i}" for i in range(7)) + "\n"
        probs = cs.check_marp(bad_marp)
        self.assertTrue(any("max 6" in p for p in probs))


class TestSourceVerifierUnit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.auditor = REPO_ROOT / "source-verifier" / "scripts" / "audit_sources.py"
        cls.guardrails = REPO_ROOT / "source-verifier" / "scripts" / "guardrails.py"

    def test_clean_fixture_passes_and_extracts_quotes(self):
        p = REPO_ROOT / "source-verifier" / "tests" / "expected" / "clean-verified.md"
        r = subprocess.run([sys.executable, str(self.auditor), "--json", str(p)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = json.loads(r.stdout)
        self.assertEqual(out["verdict"], "PASS")
        self.assertGreaterEqual(out["counts"]["quotes_needing_verbatim_check"], 1)

    def test_bad_citations_fixture_catches_all_four_defects(self):
        p = REPO_ROOT / "source-verifier" / "tests" / "input" / "bad-citations.md"
        r = subprocess.run([sys.executable, str(self.auditor), "--json", str(p)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        out = json.loads(r.stdout)
        rules = {b["rule"] for b in out["blocking"]}
        for expected in (
            "secondary_source_as_study",
            "inline_source_year_mismatch",
            "dual_year_conflation",
            "missing_author_in_sources",
        ):
            self.assertIn(expected, rules, f"Missing expected rule {expected}; got {rules}")

    def test_guardrails_allow_surgical_fix_and_block_collapse(self):
        base = (
            "# Title.\n\n"
            "The opening scene sits on the twelfth floor while the projector hums.\n\n"
            "## First section.\n\n"
            "In their [2010 paper](https://example.org/p), Petriglieri defines a holding environment as a social context "
            "that reduces disturbing affect and facilitates sense making for every worker in the room during uncertainty.\n\n"
            "## Second section.\n\n"
            "Kets de Vries explains how collusive relationships weaken reality testing in executive teams under pressure.\n\n"
            "## Sources\n\n"
            "- [Petriglieri (2010)](https://example.org/p)\n"
        )
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            draft = td_path / "draft.md"
            snap = td_path / "snap.json"
            draft.write_text(base, encoding="utf-8")

            r_snap = subprocess.run(
                [sys.executable, str(self.guardrails), "snapshot", str(draft), "-o", str(snap)],
                capture_output=True, text=True,
            )
            self.assertEqual(r_snap.returncode, 0, r_snap.stdout + r_snap.stderr)

            # Surgical URL + tiny quote fix passes
            surgical = td_path / "surgical.md"
            surgical.write_text(
                base.replace("https://example.org/p", "https://doi.org/10.5465/amle.2010.48661190")
                    .replace("a social context", '"a social context"'),
                encoding="utf-8",
            )
            r_ok = subprocess.run(
                [sys.executable, str(self.guardrails), "check", "--json", str(snap), str(surgical)],
                capture_output=True, text=True,
            )
            self.assertEqual(r_ok.returncode, 0, r_ok.stdout + r_ok.stderr)

            # Dropping a section heading + panic deletion fails
            collapsed = td_path / "collapsed.md"
            collapsed.write_text(
                "# Title.\n\n"
                "Changed opening scene.\n\n"
                "## First section.\n\n"
                "Shortened.\n",
                encoding="utf-8",
            )
            r_bad = subprocess.run(
                [sys.executable, str(self.guardrails), "check", "--json", str(snap), str(collapsed)],
                capture_output=True, text=True,
            )
            self.assertEqual(r_bad.returncode, 1)
            rules = {v["rule"] for v in json.loads(r_bad.stdout)["violations"]}
            self.assertIn("missing_headings", rules)
            self.assertIn("opening_scene_mutated", rules)
            self.assertIn("word_count_shrinkage", rules)
            self.assertIn("diff_budget_exceeded", rules)


if __name__ == "__main__":
    unittest.main()
