#!/usr/bin/env python3
"""Kill ledger for hand-made mutants. Stdlib only.

A check is worth keeping only when it fails once its code or data is broken.
Each mutant run appends one JSON line; the kill rate is read back from the file.

    uv run python scripts/mutation_ledger.py rate LEDGER.jsonl   # {killed, total, rate, survivors}
    uv run python scripts/mutation_ledger.py selftest

Also importable as a Robot Framework library (see assets/mutants.resource).
"""
import json
import os
import re
import sys
import tempfile

# Failures that mean the mutant never ran its check (typo, bad call), not a kill.
_NOT_A_KILL = re.compile(
    r"No keyword with name|Variable '.*' not found|expected \d+(?: to \d+)? arguments?, got"
    r"|Importing .* failed|Resource file .* does not exist"
)


def is_kill(passed, message):
    """True only when the mutated check failed on its assertion."""
    return not passed and not _NOT_A_KILL.search(str(message))


def record_mutation(path, test_id, operator, killed):
    """Append one row. ``killed`` is True when the mutated run failed."""
    row = {"test": str(test_id), "operator": str(operator), "killed": bool(killed)}
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    return row


def kill_rate(path):
    """Summarise the ledger. A missing or empty ledger has rate 0.0, never 1.0."""
    rows = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            rows = [json.loads(line) for line in fh if line.strip()]
    # The ledger is append-only: a rerun of a mutant replaces its earlier row.
    rows = list({(r["test"], r["operator"]): r for r in rows}.values())
    killed = sum(1 for r in rows if r["killed"])
    survivors = [f'{r["test"]}:{r["operator"]}' for r in rows if not r["killed"]]
    total = len(rows)
    return {"killed": killed, "total": total,
            "rate": round(killed / total, 3) if total else 0.0,
            "survivors": survivors}


def _selftest():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "kills.jsonl")
        assert kill_rate(p)["rate"] == 0.0
        for op, killed in (("a", False), ("a", True), ("b", True), ("c", True), ("d", False)):
            record_mutation(p, "T1", op, killed)
        r = kill_rate(p)
        assert r == {"killed": 3, "total": 4, "rate": 0.75,
                     "survivors": ["T1:d"]}, r
        assert not is_kill(False, "No keyword with name 'X' found.")
    print(json.dumps({"selftest": "ok"}))


def main(argv):
    if argv[:1] == ["selftest"]:
        _selftest()
        return 0
    if len(argv) == 2 and argv[0] == "rate":
        print(json.dumps(kill_rate(argv[1])))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
