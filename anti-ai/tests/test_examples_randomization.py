"""Tests for reproducible randomized few-shot retrieval."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_CLI = ROOT / "scripts" / "examples.py"


def query(db: Path, seed: int) -> list[str]:
    result = subprocess.run(
        [
            sys.executable,
            str(EXAMPLES_CLI),
            "--db",
            str(db),
            "query",
            "--lang",
            "en",
            "--topic",
            "leadership",
            "--limit",
            "4",
            "--format",
            "json",
            "--seed",
            str(seed),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stderr.strip() == f"random seed: {seed}"
    return [entry["id"] for entry in json.loads(result.stdout)]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "corrections.jsonl"
        entries = [
            {
                "id": f"ex-{i:03d}",
                "date": "2026-11-20",
                "lang": "en",
                "bad": f"Leadership example number {i}.",
                "good": f"A manager takes action number {i}.",
                "why": "A leadership example.",
                "tags": ["leadership"],
                "rules": [str(i)],
                "scanner_caught": True,
            }
            for i in range(20)
        ]
        db.write_text(
            "\n".join(json.dumps(entry) for entry in entries) + "\n",
            encoding="utf-8",
        )

        first = query(db, 17)
        repeated = query(db, 17)
        alternate = query(db, 29)
        assert first == repeated, "same seed must reproduce the same selection"
        assert first != alternate, "different seeds should vary the selected examples"

    print("randomized retrieval: reproducible seeds and varied selections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
