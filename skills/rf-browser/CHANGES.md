# CHANGES - rf-browser

## Source

- Upstream: https://github.com/MarketSquare/robotframework-plugins
- Original path: plugins/rf-web/skills/rf-browser
- Base commit: 4bd69c5
- License: Apache-2.0
- Copyright: Robot Framework Foundation and contributors

## Our changes

- `references/selector-drift.md` (new, 83f1052): triage guide for UI tests that stop finding an element or pass only on some runs. Why (commit message): covers telling a test defect from an app defect, locator choice, and rerun rules for new tests.
- `SKILL.md` (83f1052): added a row to the task table and a row to the agent workflow table that point to selector-drift.md. Why: the commit adds the reference, so the skill entry points link to it.
- `SKILL.md` (f2a19cd): added selector-drift.md to the "When to read the references" table. Why (commit message): the reference was missing from that table, which failed test_reference_table_matches_files in CI.
- `references/selector-drift.md` (f2a19cd): removed the link to `references/locators.md`; the sentence now points to "the locators reference listed in SKILL.md". Why (commit message): a second-level link broke the one-level-deep rule, which failed test_references_are_one_level_deep in CI.
- `references/selector-drift.md` (0f15297, "scope reruns and match locator order"): the rerun rules and locator order text was changed. The commit has no body, so no reason beyond the title is recorded.
