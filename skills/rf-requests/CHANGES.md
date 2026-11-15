# CHANGES - rf-requests

## Source

- Upstream: https://github.com/MarketSquare/robotframework-plugins
- Original path: plugins/rf-api/skills/rf-requests
- Base commit: 4bd69c5
- License: Apache-2.0
- Copyright: Robot Framework Foundation and contributors

## Our changes

- `references/loose-assertions.md` (new, eebdf38): lists checks that pass against a broken endpoint (for example a bare Should Not Be Empty on a body, Should Be True on resp.ok, a status check alone after a write) and the check to use instead. Why (commit message): each entry names the check to use instead.
- `SKILL.md` (eebdf38): added a row to the references table that links to loose-assertions.md. Why: makes the new reference reachable from the skill entry point.
- `references/async-jobs.md` (new, 03b96c0): shows how to wait for an async job with a bounded WHILE loop instead of one long Sleep. Why (commit message): the reference waits for an async API job with a bounded loop instead of Sleep.
- `references/async-jobs.md` (972f2d0): moved the WHILE loop into a keyword, switched the limit to a time value (`limit=60s`, since a bare number counts iterations), added a short Sleep between polls, used the `$state` expression form, and corrected the version note (limit since RF 5.0, on_limit_message since RF 6.1). Why (commit message): these are the stated changes; the commit gives no other reason.
- `SKILL.md` (03b96c0, 972f2d0): added a row to the task table and a row to the references table for async-jobs.md. Why (commit message): the SKILL.md links to the new reference.
- Merge 85a2d9b: both reference-table rows were kept so the branches merge cleanly in order. Why (commit message): both branches add one row to the same table.
