#!/usr/bin/env python3
"""Deterministic graders for Tier 4 behavioral skill evals.

Grade a candidate output file produced by an agent run (baseline or skill-enabled)
against a case defined in evals/cases.json:

    python3 evals/graders.py --case blog-writer-tc2-seed --artifact /path/to/output.md [--json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_PATH = Path(__file__).resolve().parent / "cases.json"


def load_case(case_id: str) -> dict:
    data = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    for case in data["cases"]:
        if case["id"] == case_id:
            return case
    raise KeyError(f"Unknown eval case: {case_id}")


def grade_artifact(case: dict, artifact: Path) -> dict:
    text = artifact.read_text(encoding="utf-8")
    checks = case.get("deterministic_checks", {})
    results = []

    if checks.get("anti_ai_zero_high"):
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "anti-ai" / "check_tells.py"), "--json", str(artifact)],
            capture_output=True, text=True,
        )
        out = json.loads(r.stdout) if r.stdout.strip() else {"hits": []}
        highs = [h for h in out["hits"] if h["severity"] == "high"]
        results.append({
            "check": "anti_ai_zero_high",
            "pass": len(highs) == 0,
            "detail": f"{len(highs)} HIGH hit(s)",
        })

    if checks.get("validate_draft"):
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "blog-writer" / "tests" / "validate_draft.py"), "--json", str(artifact)],
            capture_output=True, text=True,
        )
        out = json.loads(r.stdout) if r.stdout.strip() else {"problems": ["validator error"]}
        results.append({
            "check": "validate_draft",
            "pass": r.returncode == 0,
            "detail": "; ".join(out.get("problems", [])) or "PASS",
        })

    if checks.get("check_styled_html") or checks.get("check_styled_marp"):
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "alexandru-style" / "tests" / "check_styled.py"), "--json", str(artifact)],
            capture_output=True, text=True,
        )
        out = json.loads(r.stdout) if r.stdout.strip() else {"problems": ["checker error"]}
        results.append({
            "check": "check_styled",
            "pass": r.returncode == 0,
            "detail": "; ".join(out.get("problems", [])) or "PASS",
        })

    if checks.get("audit_sources_pass"):
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "source-verifier" / "scripts" / "audit_sources.py"), "--json", str(artifact)],
            capture_output=True, text=True,
        )
        out = json.loads(r.stdout) if r.stdout.strip() else {"blocking": [{"detail": "auditor error"}]}
        results.append({
            "check": "audit_sources_pass",
            "pass": r.returncode == 0,
            "detail": "; ".join(b.get("rule", b.get("detail", "")) for b in out.get("blocking", [])) or "PASS",
        })

    for needle in checks.get("must_contain", []):
        results.append({
            "check": f"must_contain:{needle}",
            "pass": needle in text,
            "detail": "present" if needle in text else "missing",
        })

    lower_text = text.lower()
    for needle in checks.get("must_not_contain", []):
        absent = needle.lower() not in lower_text
        results.append({
            "check": f"must_not_contain:{needle}",
            "pass": absent,
            "detail": "absent" if absent else "still present",
        })

    passed = all(r["pass"] for r in results)
    return {
        "case_id": case["id"],
        "skill": case["skill"],
        "artifact": str(artifact),
        "deterministic_pass": passed,
        "checks": results,
        "rubric_pending_judge": case.get("rubric", []),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Run deterministic eval graders on an artifact.")
    ap.add_argument("--case", required=True, help="case ID from evals/cases.json")
    ap.add_argument("--artifact", required=True, help="path to generated output file")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    case = load_case(args.case)
    report = grade_artifact(case, Path(args.artifact))

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for c in report["checks"]:
            status = "PASS" if c["pass"] else "FAIL"
            print(f"{status:4s} {c['check']} ({c['detail']})")
        print(f"VERDICT: {'PASS' if report['deterministic_pass'] else 'FAIL'}")
        if report["rubric_pending_judge"]:
            print("Manual / LLM-judge rubric items:")
            for item in report["rubric_pending_judge"]:
                print(f"  - {item}")
    return 0 if report["deterministic_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
