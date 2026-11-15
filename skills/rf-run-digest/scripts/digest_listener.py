#!/usr/bin/env python
"""Robot listener: write digest.txt, point the human at report.html.

With the `shrink` argument (`--listener digest_listener.py:shrink`) it also rewrites
output.xml in place with the keywords of PASSED tests removed. Off by default.

Attach it to any `robot` or `pabot` command; it fires when the run tears down.

    robot --listener scripts/digest_listener.py -d results/run \
          --output output.xml --log NONE --report NONE tests/ > /dev/null 2>&1
    cat results/run/digest.txt

Always-on for a shell:

    # PowerShell
    $env:ROBOT_OPTIONS = '--listener "C:\\path\\to\\tools\\digest_listener.py"'
    # bash
    export ROBOT_OPTIONS='--listener /abs/path/scripts/digest_listener.py'

Read digest.txt first. A person opens robot's own report.html (the listener prints its path
when a run fails and never opens it). Neither one ever reads output.xml or log.html.

Under pabot each process writes its own digest.txt; read the merged run's instead
(`uv run python scripts/run_digest.py failures <merged output.xml>`).

Errors are swallowed: a reporting tool must never fail a run.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_digest  # noqa: E402  (sibling file)

ROBOT_LISTENER_API_VERSION = 3



def _max_per_group():
    try:
        return max(1, int(os.environ.get("DIGEST_MAX_PER_GROUP", "3")))
    except ValueError:
        return 3


class digest_listener:  # noqa: N801 (robot resolves the listener by file/class name)

    def __init__(self, *args):
        self.output_xml = None
        self.report = None
        self.shrink = "shrink" in args

    def output_file(self, path):
        self.output_xml = str(path)

    def report_file(self, path):
        self.report = str(path) if path and str(path) != "NONE" else None

    def close(self):
        try:
            self._write_digest()
        except Exception as e:                       # never raise into the run
            print("[digest_listener] skipped: %s" % e)

    def _write_digest(self):
        if not self.output_xml or not os.path.exists(self.output_xml):
            return
        if self.shrink:
            run_digest.shrink(self.output_xml)       # rewrites output.xml without PASSED keywords
        text, failed = run_digest.digest(self.output_xml, _max_per_group())
        path = os.path.join(os.path.dirname(self.output_xml), "digest.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print("\n[digest_listener] %d failed -> %s" % (failed, path))
        if failed and self.report and os.path.exists(self.report):
            print("[digest_listener] report: %s" % os.path.abspath(self.report))
