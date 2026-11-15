# robotframework-agent-skills

Agent skills for Robot Framework test work. Each skill is a folder with a
`SKILL.md` in the open Agent Skills format, so any agent that reads that format
can use it.

## Install

As a Claude Code plugin:

```bash
claude plugin marketplace add ai94iq/robotframework-agent-skills
claude plugin install robotframework-agent-skills@robotframework-agent-skills
```

For other agents, copy the folders under `skills/` into the agent's skills
directory.

## Skills

| Skill | Use it for |
|---|---|
| [rf-maestro](skills/rf-maestro) | Android and iOS tests with [MaestroLibrary](https://github.com/ai94iq/robotframework-maestrolibrary) (Maestro, no Appium server) |
| [rf-mind](skills/rf-mind) | exact lookups in a test repo with [robotframework-mind](https://github.com/ai94iq/robotframework-mind): tests by ticket or tag, keyword callers, variables |
| [rf-run-digest](skills/rf-run-digest) | reading a run from a short digest (summary, grouped failures) instead of output.xml |
| [rf-test-quality](skills/rf-test-quality) | proving a test fails when its code breaks (mutant checks, kill rate) |
| [rf-browser](skills/rf-browser) | web tests with Browser Library, including selector-drift triage |
| [rf-requests](skills/rf-requests) | HTTP API tests with RequestsLibrary, including loose-assertion checks and bounded polling for async jobs |
| [rf-restinstance](skills/rf-restinstance) | API tests with RESTinstance, including loose-assertion checks |

| Agent | Use it for |
|---|---|
| [rf-debug-expert](agents/rf-debug-expert.md) | debugging failed runs, with failure fingerprints |

## License

Apache License 2.0. See [LICENSE](LICENSE). Some skills build on Apache-2.0
work by others; [NOTICE](NOTICE) and the `CHANGES.md` file in those folders
give the source and what changed.
