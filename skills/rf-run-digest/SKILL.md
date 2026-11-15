---
name: rf-run-digest
description: "Use after a Robot Framework run, to read its result from a short digest (summary, grouped failures) instead of output.xml or log.html."
license: Apache-2.0
compatibility: "Requires Python 3.10+ with robotframework>=7 in the project environment for the bundled run_digest script. Stdlib only otherwise."
metadata:
  author: manykarim
  version: "1.0.0"
---

# Robot Framework Run Digest Skill

## When to use

Load this skill after a `robot` or `pabot` run, before you look at its result. output.xml and log.html are large; reading them wastes time and hides the few failure groups that matter.

## The rule

Read the digest first, not output.xml. Open output.xml only for one named test, with `trace`.

## Write a digest on every run

Attach `scripts/digest_listener.py` as a listener; `<skill-dir>` is the folder containing this SKILL.md. When the run ends, it writes `digest.txt` next to output.xml:

```bash
robot --listener <skill-dir>/scripts/digest_listener.py -d results/run tests/
cat results/run/digest.txt
```

The listener leaves output.xml as robot wrote it. To shrink it, pass the `shrink`
argument: `--listener <skill-dir>/scripts/digest_listener.py:shrink`. This rewrites output.xml in
place with `rebot --removekeywords PASSED`, so the keywords of passed tests are gone
from it and from any log built from it later.

## Read an existing output.xml

```bash
uv run python "${CLAUDE_SKILL_DIR}/scripts/run_digest.py" summary  results/output.xml          # totals and per-suite counts
uv run python "${CLAUDE_SKILL_DIR}/scripts/run_digest.py" failures results/output.xml --max 3  # failures grouped by signature
uv run python "${CLAUDE_SKILL_DIR}/scripts/run_digest.py" diff     before.xml after.xml        # what changed between two runs
uv run python "${CLAUDE_SKILL_DIR}/scripts/run_digest.py" trace    results/output.xml --test "Name"
uv run python "${CLAUDE_SKILL_DIR}/scripts/run_digest.py" selftest
```

The script path is relative to this skill's directory; output.xml paths are relative to the project root. Not using uv? Run the same commands with `.venv/bin/python` or `poetry run python` instead of `uv run python`; see rf-setup.

Failures that differ only by ids, hosts or timestamps fall into one group, so a run with many failures reads as a few groups. Quote the summary line and the group messages when you report a run.

It reads Browser, SeleniumLibrary, AppiumLibrary, MaestroLibrary and RequestsLibrary failures; the `screenshot:` line on a failed test comes from the last `<img src>` that test logged.

## Companion Skills

| Need | Skill |
|------|-------|
| Install Robot Framework or a library, fix the environment | `rf-setup` |
| Write tests, suites, user keywords, resources and variables in Robot Framework syntax | `rf-language` |
