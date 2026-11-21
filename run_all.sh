#!/usr/bin/env bash
# Full gate run for alex-public-skills-collection.
# Every control must behave in its declared direction:
# an expected-ok control exits 0, an expected-fail control exits non-zero.
# Exit 0 = the repo is green.

set -u
cd "$(dirname "$0")"

pass=0
fail=0

check() {
  # check <label> <ok|fail> <command...>
  local label="$1" want="$2"
  shift 2
  local out rc got verdict
  out="$("$@" 2>&1)"
  rc=$?
  if [ "$rc" -eq 0 ]; then got=ok; else got=fail; fi
  if [ "$got" = "$want" ]; then verdict=PASS; else verdict=FAIL; fi
  if [ "$verdict" = "PASS" ]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
  fi
  printf "%-4s %s (exit %s, expected %s)\n" "$verdict" "$label" "$rc" "$want"
  if [ "$verdict" = "FAIL" ]; then
    printf '%s\n' "$out" | sed 's/^/    | /'
  fi
}

printf '%s\n' "run_all: gates for alex-public-skills-collection"

check "anti-ai fixtures + heuristics + examples + self-scan" ok \
  python3 anti-ai/tests/run_tests.py

check "blog-writer clean draft passes gate" ok \
  python3 blog-writer/tests/validate_draft.py blog-writer/tests/expected/clean-draft.md

check "seed-tell paragraph still fires (must FAIL)" fail \
  python3 blog-writer/tests/validate_draft.py blog-writer/tests/input/seed-tell-paragraph.md

check "planted-fabrication draft still fails gate" fail \
  python3 blog-writer/tests/validate_draft.py blog-writer/tests/input/draft-with-planted-fabrication.md

check "source-verifier clean draft passes pre-audit" ok \
  python3 source-verifier/scripts/audit_sources.py source-verifier/tests/expected/clean-verified.md

check "source-verifier bad citations still fail pre-audit" fail \
  python3 source-verifier/scripts/audit_sources.py source-verifier/tests/input/bad-citations.md

check "source-verifier guardrails allow surgical fix" ok \
  python3 -c "import pathlib,subprocess,sys,tempfile
with tempfile.TemporaryDirectory() as td:
  d=pathlib.Path(td)
  base=pathlib.Path('source-verifier/tests/expected/clean-verified.md').read_text(encoding='utf-8')
  snap=d/'snap.json'
  rev=d/'rev.md'
  rev.write_text(base.replace('AMLE 9(1)','AMLE 9(1), 44-60'),encoding='utf-8')
  r1=subprocess.run([sys.executable,'source-verifier/scripts/guardrails.py','snapshot','source-verifier/tests/expected/clean-verified.md','-o',str(snap)],capture_output=True,text=True)
  r2=subprocess.run([sys.executable,'source-verifier/scripts/guardrails.py','check',str(snap),str(rev)],capture_output=True,text=True)
  print(r1.stdout+r2.stdout+r1.stderr+r2.stderr)
  sys.exit(0 if r1.returncode==0 and r2.returncode==0 else 1)"

check "source-verifier guardrails block essay collapse (must FAIL)" fail \
  python3 -c "import pathlib,subprocess,sys,tempfile
with tempfile.TemporaryDirectory() as td:
  d=pathlib.Path(td)
  snap=d/'snap.json'
  rev=d/'collapsed.md'
  rev.write_text('# Holding environments need fair systems.\n\nRewritten opening.\n\n## Holding and identity workspaces.\n\nCut.\n',encoding='utf-8')
  subprocess.run([sys.executable,'source-verifier/scripts/guardrails.py','snapshot','source-verifier/tests/expected/clean-verified.md','-o',str(snap)],check=True,capture_output=True,text=True)
  r2=subprocess.run([sys.executable,'source-verifier/scripts/guardrails.py','check',str(snap),str(rev)],capture_output=True,text=True)
  print(r2.stdout+r2.stderr)
  sys.exit(r2.returncode)"

check "AG style sample page passes checker" ok \
  python3 alexandru-style/tests/check_styled.py alexandru-style/tests/expected/sample-page.html

check "AG style anti-sample fails checker (must FAIL)" fail \
  python3 alexandru-style/tests/check_styled.py alexandru-style/tests/expected/anti-sample.html

check "AG style brand offline check (templates + palette + archive)" ok \
  python3 alexandru-style/brand/scripts/check.py

check "repo-wide Tier 1-2 suite (spec, integrity, unit tests)" ok \
  python3 -m unittest discover -s tests -v

check "root files self-scan (0 HIGH/MEDIUM)" ok \
  python3 -c "import json,subprocess,sys
r=subprocess.run([sys.executable,'anti-ai/check_tells.py','--json','--severity','medium','AGENTS.md','run_all.sh','README.md'],capture_output=True,text=True)
if r.returncode!=0: print(r.stdout,r.stderr); sys.exit(1)
hits=json.loads(r.stdout)['hits']
bad=[h for h in hits if h['severity'] in ('high','medium')]
print('%d HIGH/MEDIUM hits on AGENTS.md + run_all.sh + README.md' % len(bad))
for h in bad: print('  %s %s L%s: %s' % (h['severity'].upper(), h['file'], h.get('line'), h['id']))
sys.exit(1 if bad else 0)"

total=$((pass + fail))
printf '%s\n' "----------------------------------------"
printf '%s\n' "controls: $pass/$total in declared direction"
if [ "$fail" -eq 0 ]; then
  printf 'ALL GREEN\n'
  exit 0
else
  printf 'RED: %d control(s) off direction\n' "$fail"
  exit 1
fi
