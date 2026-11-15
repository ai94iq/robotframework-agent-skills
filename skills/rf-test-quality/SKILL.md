---
name: rf-test-quality
description: "Use after writing or changing a Robot Framework test, to prove it fails when its code breaks (mutant checks and kill rate)."
license: Apache-2.0
compatibility: Requires Robot Framework 7.0+ and Python 3.10+. Stdlib only.
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

Import `assets/mutants.resource` and wrap the real check in `Mutant Must Fail`, feeding it the value the test produced and a mutated expectation:

```robotframework
*** Settings ***
Resource    ${CLAUDE_SKILL_DIR}/assets/mutants.resource

*** Test Cases ***
Status Check Catches A Wrong Code
    ${resp}=    GET On Session    api    /health
    Should Be Equal As Integers    ${resp.status_code}    200
    ${killed}=    Mutant Must Fail    T1    flip-status
    ...    Should Be Equal As Integers    ${resp.status_code}    500
    Should Be True    ${killed}
```

Only an assertion failure counts as a kill. A mutant that fails because of a typo, a missing keyword, a missing variable or a wrong argument count is recorded as a survivor: fix the mutant call.

Each call writes one row to `mutation-ledger.jsonl` in the output directory. `Mutation Kill Rate` returns `{killed, total, rate, survivors}`. A rerun of the same test and operator replaces its earlier row, so the rate uses the latest result per mutant. Quote the rate for each changed test. A survivor means the check is too weak: fix the check, not the mutant.

## Reading the ledger

```bash
uv run python "${CLAUDE_SKILL_DIR}/scripts/mutation_ledger.py" rate results/mutation-ledger.jsonl
uv run python "${CLAUDE_SKILL_DIR}/scripts/mutation_ledger.py" selftest
```

An empty or missing ledger reports a rate of 0.0, so a run with no mutants never looks like a full kill.
