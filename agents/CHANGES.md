# CHANGES - rf-debug-expert (agent)

## Source

- Upstream: https://github.com/MarketSquare/robotframework-plugins
- Original path: plugins/rf-core/agents/rf-debug-expert.md
- Base commit: 4bd69c5
- License: Apache-2.0
- Copyright: Robot Framework Foundation and contributors

## Our changes

- Section 2 (b3ceff2): added a fingerprint step. Each failure group gets a stable signature: keep the error message's status codes and counts, replace concrete ids with a placeholder, drop hosts, query strings and timestamps, and keep endpoint paths as templates. Why (commit message): the agent names each failure group by a stable signature, so the same failure in a later run can match a known cause.
- Section 2 (b1e34a8): the fingerprint goes in the bug title or BUGS.md entry, not only in a file name. Why: the commit names this placement; no further reason is given.
- Section 6 (b3ceff2): new "Rule out the test before reporting an app or environment cause" checklist with eight checks (comparison order, failing step, outage cascade, shared state, expired token in long runs, absent versus null, correlation versus cause, tracing the expected value). Why (commit message): the agent checks the test before it reports an app or environment cause.
- Section 6 (b1e34a8): the first check now says RequestsLibrary puts the actual value first and that other libraries order it differently. Why: the commit names this wording; no further reason is given.
- Output block (b3ceff2): added a `FINGERPRINT:` line to the per-cause report block. Why: carries the fingerprint into each reported cause.
- Copies (b3ceff2, b1e34a8): the bundle and agent variant copies are regenerated from this file; the commit notes they are identical (cmp).
