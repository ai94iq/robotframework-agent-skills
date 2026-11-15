---
name: rf-test-quality
description: "Use after writing or changing a Robot Framework test, to prove it fails when its code breaks (mutant checks and kill rate)."
license: Apache-2.0
compatibility: "Requires Python 3.10+ with robotframework>=7 in the project environment for the bundled mutation_ledger script (stdlib only otherwise)."
metadata:
  author: manykarim
  version: "1.0.0"
---

# Robot Framework Test Quality Skill

## When to use

Load this skill after you add or change a test, before you call it done. A test that passes against broken code proves nothing.

## The rule

Every new or changed test is seen failing once. Break the thing it checks, run it, and confirm it goes red. Then restore the code and confirm it goes green.

## Mutant checks in a suite

Copy `assets/mutants.resource` from this skill into the project's `resources/` folder, import it, and wrap the real check in `Mutant Must Fail`, feeding it the value the test produced and a mutated expectation:

```robotframework
*** Settings ***
Resource    ../resources/mutants.resource

*** Test Cases ***
Status Check Catches A Wrong Code
    ${total}=    Evaluate    2 + 3
    Should Be Equal As Integers    ${total}    5
    ${killed}=    Mutant Must Fail    T1    flip-total
    ...    Should Be Equal As Integers    ${total}    6
    Should Be True    ${killed}
```

Only an assertion failure counts as a kill. A mutant that fails because of a typo, a missing keyword, a missing variable or a wrong argument count is recorded as a survivor: fix the mutant call.

Each call writes one row to `mutation-ledger.jsonl` in the output directory. `Mutation Kill Rate` returns `{killed, total, rate, survivors}`. A rerun of the same test and operator replaces its earlier row, so the rate uses the latest result per mutant. Quote the rate for each changed test. A survivor means the check is too weak: fix the check, not the mutant.

## Reading the ledger

```bash
uv run python "${CLAUDE_SKILL_DIR}/scripts/mutation_ledger.py" rate results/mutation-ledger.jsonl
uv run python "${CLAUDE_SKILL_DIR}/scripts/mutation_ledger.py" selftest
uv run python "${CLAUDE_SKILL_DIR}/scripts/mutation_ledger.py" rate output/mutation-ledger.jsonl
```

The script path is relative to this skill's directory. Not using uv? Run the same commands with `.venv/bin/python` or `poetry run python` instead of `uv run python`; see rf-setup.

An empty or missing ledger reports a rate of 0.0, so a run with no mutants never looks like a full kill.

## Companion Skills

| Need | Skill |
|------|-------|
| Write tests, suites, user keywords, resources and variables in Robot Framework syntax | `rf-language` |
| Install Robot Framework or a library, fix the environment | `rf-setup` |
