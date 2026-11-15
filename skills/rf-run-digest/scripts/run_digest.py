#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["robotframework>=7"]
# ///
"""Read a robot run without reading output.xml. Stdlib only.

    run_digest.py summary  OUT.xml              # totals + per-suite
    run_digest.py failures OUT.xml [--max 3]    # grouped by signature
    run_digest.py diff     BEFORE.xml AFTER.xml # status vs message changes
    run_digest.py trace    OUT.xml --test NAME  # keyword path to the failure
    run_digest.py selftest

Never `cat` output.xml, never open log.html.
"""
import argparse
import io
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)
URL = re.compile(r"https?://\S+|/api/\S*")
TS = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}\S*")
PATH_URL = re.compile(r"path_url=(\S+)")
STATUS = re.compile(r"\bstatus=(\d+)")
IMG = re.compile(r"<img\s[^>]*?src=\"([^\"]+)\"", re.I)
FILE_PATH = re.compile(r"(?:\b[A-Za-z]:[\\/]|(?<![\w.{}])/(?!api/))(?:[^\s\\/]+[\\/])*([^\s\\/]+\.\w+)")
HEX_ID = re.compile(r"\b[0-9a-f]{32,}\b", re.I)


def _path_template(m):
    """Keep WHICH endpoint failed, drop what varies: host, query string, ids -> {id}."""
    u = re.sub(r"^https?://[^/\s]+", "", m.group(0)).split("?")[0]
    u = UUID.sub("{id}", u)
    return re.sub(r"/\d+(?=/|$)", "/{id}", u) or "/"


def norm(msg):
    """Grouping signature: drop what varies per test, keep status numbers and path template."""
    s = (msg or "").split("\nCall log:")[0]
    s = URL.sub(_path_template, s)
    s = FILE_PATH.sub(r"\1", s)
    s = UUID.sub("<uuid>", s)
    s = HEX_ID.sub("<id>", s)
    s = TS.sub("<ts>", s)
    return " ".join(s.split())[:200]


def clip(s, n=160):
    s = " ".join((s or "").split())
    return s[:n] + (" ..." if len(s) > n else "")


def parse(path):
    """-> one dict per test, in run order, with the last request path and response status.

    "last request" is not always the failing one; `trace` gives the failing keyword path.
    """
    tests, suites, cur = [], [], None
    for event, el in ET.iterparse(path, events=("start", "end")):
        tag = el.tag
        if event == "start":
            if tag == "suite":
                suites.append(el.get("name"))
            elif tag == "test":
                cur = {"name": el.get("name"), "suite": suites[-1],
                       "status": "", "msg": "", "req": None, "res": None,
                       "shot": None, "kws": []}
            continue
        if cur is not None and tag == "msg":
            text = el.text or ""
            shot = IMG.search(text)
            if shot:                                 # UI libraries log screenshots as <img>
                cur["shot"] = shot.group(1)
            m = PATH_URL.search(text)
            if m:
                cur["req"] = m.group(1)
            elif STATUS.search(text) and "body=" in text:
                cur["res"] = STATUS.search(text).group(1)
        elif cur is not None and tag == "kw":
            st = el.find("status")
            cur["kws"].append((el.get("name") or "", st.get("status", "") if st is not None else ""))
        elif tag == "test":
            st = el.find("status")
            cur["status"] = st.get("status", "") if st is not None else ""
            cur["msg"] = (st.text or "").strip() if st is not None else ""
            tests.append(cur)
            cur = None
            el.clear()
        elif tag == "suite":
            suites.pop()
            el.clear()
    return tests


def cmd_summary(tests):
    fail = [t for t in tests if t["status"] == "FAIL"]
    skip = sum(t["status"] == "SKIP" for t in tests)
    # SKIP counts as neither passed nor failed.
    line = "%d tests, %d passed, %d failed" % (len(tests), len(tests) - len(fail) - skip, len(fail))
    print(line + (", %d skipped" % skip if skip else ""))
    per = {}
    for t in tests:
        p, f = per.get(t["suite"], (0, 0))
        per[t["suite"]] = (p + (t["status"] == "PASS"), f + (t["status"] == "FAIL"))
    for suite, (p, f) in sorted(per.items(), key=lambda kv: -kv[1][1]):
        if f:
            print("  %3d failed / %-4d %s" % (f, p + f, suite))


def cmd_failures(tests, max_per_group=3):
    groups = {}
    for t in tests:
        if t["status"] == "FAIL":
            groups.setdefault(norm(t["msg"]), []).append(t)
    if not groups:
        return print("no failures")
    for sig, ts in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        print("\n  %dx  %s" % (len(ts), sig))
        for t in ts[:max_per_group]:
            print("        %s :: %s" % (t["suite"], t["name"]))
            if t["req"]:
                print("          last request: %s  -> %s" % (t["req"], t["res"] or "?"))
            if t["shot"]:
                print("          screenshot: %s" % t["shot"])
        if len(ts) > max_per_group:
            print("        ... and %d more (not shown)" % (len(ts) - max_per_group))


def cmd_diff(before, after):
    b = dict(((t["suite"], t["name"]), t) for t in before)
    a = dict(((t["suite"], t["name"]), t) for t in after)
    status, message = [], 0
    for k in sorted(set(a) & set(b)):
        if a[k]["status"] != b[k]["status"]:
            status.append((k, b[k]["status"], a[k]["status"]))
        elif norm(a[k]["msg"]) != norm(b[k]["msg"]):
            message += 1
    print("%d status changes, %d message changes, +%d new, -%d gone"
          % (len(status), message, len(set(a) - set(b)), len(set(b) - set(a))))
    for (suite, name), old, new in status[:40]:
        print("  %s -> %s  %s :: %s" % (old, new, suite, name))


def cmd_trace(tests, name):
    hits = [t for t in tests if t["name"] == name]
    if not hits:
        sys.exit("no test named %r" % name)
    for t in hits:
        print("%s :: %s  [%s]" % (t["suite"], t["name"], t["status"]))
        for kw, st in t["kws"]:
            if st == "FAIL":
                print("  FAIL  %s" % kw)
        print("  message: %s" % clip(t["msg"], 400))
        if t["req"]:
            print("  last request: %s -> %s" % (t["req"], t["res"] or "?"))
        if t["shot"] and t["status"] == "FAIL":
            print("  screenshot: %s" % t["shot"])


def shrink(output_xml):
    """Rewrite output.xml without PASSED keywords, via rebot in a child process.

    In process, rebot() would re-fire the calling listener's close(): robot's LOGGER is global.
    """
    tmp = output_xml + ".small"
    r = subprocess.run([sys.executable, "-m", "robot.rebot", "--removekeywords", "PASSED",
                        "--log", "NONE", "--report", "NONE", "--output", tmp, output_xml],
                       capture_output=True)
    # rebot exits with the failed test count (0-249).
    if r.returncode < 250 and os.path.exists(tmp):
        os.replace(tmp, output_xml)
        return True
    return False


def digest(output_xml, max_per_group=3):
    """summary + failures as one string, for digest_listener.py."""
    tests = parse(output_xml)
    buf, real = io.StringIO(), sys.stdout
    try:
        sys.stdout = buf
        cmd_summary(tests)
        cmd_failures(tests, max_per_group)
    finally:
        sys.stdout = real
    return buf.getvalue(), sum(1 for t in tests if t["status"] == "FAIL")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["summary", "failures", "diff", "trace", "selftest"])
    ap.add_argument("xml", nargs="*")
    ap.add_argument("--max", type=int, default=3)
    ap.add_argument("--test")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        from digest_selftest import selftest
        return selftest()
    if a.cmd == "diff":
        return cmd_diff(parse(a.xml[0]), parse(a.xml[1]))
    tests = parse(a.xml[0])
    if a.cmd == "trace":
        return cmd_trace(tests, a.test)
    cmd_summary(tests)
    if a.cmd == "failures":
        cmd_failures(tests, a.max)


if __name__ == "__main__":
    main(sys.argv[1:])
