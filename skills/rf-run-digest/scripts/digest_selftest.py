"""Self-check for run_digest.py on a tiny generated output.xml."""
import contextlib
import io
import os
import tempfile

from run_digest import cmd_diff, cmd_summary, cmd_trace, digest, norm, parse

SAMPLE = """<?xml version="1.0"?>
<robot generator="Robot 7">
<suite id="s1" name="Tests">
 <suite id="s1-s1" name="01 Orders">
  <test id="s1-s1-t1" name="Create Order Basic">
   <kw name="POST With Auth"><msg timestamp="1" level="INFO">POST Request : url=http://h/api/orders
path_url=/api/orders/{ID}</msg>
   <msg timestamp="2" level="INFO">POST Response : url=http://h/api/orders
status=400, reason=Bad Request
body=b'{{"error":"Validation failed"}}'</msg>
   <status status="FAIL"/></kw>
   <status status="FAIL">400.0 != 200.0</status>
  </test>
  <test id="s1-s1-t2" name="Create Order Duplicate">
   <kw name="POST With Auth"><msg timestamp="3" level="INFO">POST Request : url=http://h/api/orders
path_url=/api/orders/{ID2}</msg><status status="FAIL"/></kw>
   <status status="FAIL">400.0 != 200.0</status>
  </test>
  <test id="s1-s1-t3" name="Get Order">
   <kw name="GET With Auth"><msg timestamp="4" level="INFO">GET Request : url=http://h/api/orders
path_url=/api/orders</msg><status status="PASS"/></kw>
   <status status="PASS"></status>
  </test>
  <status status="FAIL"/>
 </suite>
 <status status="FAIL"/>
</suite>
</robot>
"""


def selftest():
    d = tempfile.mkdtemp()
    uid = "11111111-2222-3333-4444-555555555555"
    uid2 = "99999999-2222-3333-4444-555555555555"
    p = os.path.join(d, "out.xml")
    open(p, "w", encoding="utf-8").write(SAMPLE.format(ID=uid, ID2=uid2))
    tests = parse(p)
    assert len(tests) == 3, tests
    assert [t["status"] for t in tests] == ["FAIL", "FAIL", "PASS"]
    t = tests[0]
    assert t["suite"] == "01 Orders" and t["req"] == "/api/orders/" + uid, t
    assert t["res"] == "400", t
    # two failures differing only by UUID must collapse into ONE group
    sigs = set(norm(x["msg"]) for x in tests if x["status"] == "FAIL")
    assert len(sigs) == 1, sigs
    assert norm("Url: /api/x/%s Expected 504 != 200" % uid) == "Url: /api/x/{id} Expected 504 != 200"
    assert norm("Url: https://h.dev/api/x/42?p=1 504") == "Url: /api/x/{id} 504"
    q = os.path.join(d, "after.xml")
    open(q, "w", encoding="utf-8").write(
        SAMPLE.format(ID=uid, ID2=uid2).replace('status="FAIL">400.0 != 200.0', 'status="PASS">', 1))
    text, nfail = digest(p)
    assert nfail == 2 and "2x  400.0 != 200.0" in text, text
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cmd_summary(tests + [dict(tests[2], name="Skipped", status="SKIP")])
    assert buf.getvalue().startswith("4 tests, 1 passed, 2 failed, 1 skipped\n"), buf.getvalue()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cmd_summary(tests)
    assert buf.getvalue().startswith("3 tests, 1 passed, 2 failed\n"), buf.getvalue()
    cmd_diff(tests, parse(q))
    cmd_trace(tests, "Create Order Basic")
    print(text)
    print("selftest ok")
