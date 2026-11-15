# CHANGES - rf-restinstance

## Source

- Upstream: https://github.com/MarketSquare/robotframework-plugins
- Original path: plugins/rf-api/skills/rf-restinstance
- Base commit: 4bd69c5
- License: Apache-2.0
- Copyright: Robot Framework Foundation and contributors

## Our changes

- `references/loose-assertions.md` (new, eebdf38): lists checks that pass against a broken endpoint (for example `Object    response body    required=["id"]` alone, `Integer    response body    id` alone, a status check alone after a write) and the check to use instead. Why (commit message): each entry names the check to use instead; the reference was added to rf-requests and rf-restinstance.
- `SKILL.md` (eebdf38): added a row to the references table that links to loose-assertions.md. Why: makes the new reference reachable from the skill entry point.
- Scope note: the bounded-polling change does not change this skill.
