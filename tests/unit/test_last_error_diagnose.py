import json

import last_error_diagnose


def test_diagnose_with_fatal(fixtures, capsys):
    task = {
        "id": 2,
        "tpl_alias": "Deploy App",
        "created": "2026-01-02T10:00:00Z",
    }
    last_error_diagnose.main(task, fixtures["raw_output"], "1")
    out = capsys.readouterr().out

    assert "#2" in out
    assert "Deploy App" in out
    assert "Jan 02 10:00" in out
    assert "Failed (1):" in out
    assert "web1" in out
    assert "non-zero return code (rc=1)" in out
    assert "task:  Deploy container" in out
    assert "cmd:   docker compose up -d" in out
    assert "cause: Error: image build failed" in out
    assert "Recap:" in out
    assert "1 failed" in out
    assert "sem /api/project/1/tasks/2/raw_output" in out


def test_diagnose_no_recap():
    """Task that failed before any plays ran."""
    import last_error_diagnose

    task = {"id": 50, "tpl_alias": "Test", "created": "2026-01-01T00:00:00Z"}
    raw = "Some error before ansible ran\nNo recap here\n"

    import io
    import sys

    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        last_error_diagnose.main(task, raw, "1")
    finally:
        sys.stdout = old_stdout

    out = captured.getvalue()
    assert "could not extract failure details" in out
    assert "no PLAY RECAP found" in out


def test_diagnose_recap_failures_without_fatal():
    """PLAY RECAP shows failures but no fatal: lines captured."""
    task = {"id": 75, "tpl_alias": "Deploy", "created": "2026-01-15T12:00:00Z"}
    raw = (
        "PLAY RECAP *****\n"
        "web1                       : ok=5    changed=0    unreachable=0    failed=2    skipped=0    rescued=0    ignored=0\n"
        "web2                       : ok=5    changed=0    unreachable=1    failed=0    skipped=0    rescued=0    ignored=0\n"
    )

    import io
    import sys

    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        last_error_diagnose.main(task, raw, "1")
    finally:
        sys.stdout = old_stdout

    out = captured.getvalue()
    assert "Failed (1):" in out
    assert "web1" in out
    assert "2 failed task(s)" in out
    assert "0 passed, 1 failed, 1 unreachable" in out


def _fatal(payload, task="Run thing", host="h1"):
    return (
        f"TASK [{task}] ****\n"
        f"fatal: [{host}]: FAILED! => {json.dumps(payload)}\n"
        "PLAY RECAP *****\n"
        f"{host}                       : ok=1    changed=0    unreachable=0    failed=1    skipped=0\n"
    )


TASK = {"id": 9, "tpl_alias": "T", "created": "2026-01-01T00:00:00Z"}


def test_cause_from_json_stdout(capsys):
    """CLI that reports errors as JSON on stdout with empty stderr."""
    raw = _fatal(
        {
            "msg": "non-zero return code",
            "rc": 4,
            "cmd": ["docker", "run", "collector", "collect", "tep"],
            "stderr": "",
            "stdout": json.dumps(
                {
                    "error": "Page.goto: net::ERR_NAME_NOT_RESOLVED\nCall log: ...",
                    "code": 4,
                }
            ),
        }
    )
    last_error_diagnose.main(TASK, raw, "1")
    out = capsys.readouterr().out
    assert "cmd:   docker run collector collect tep" in out
    assert "cause: Page.goto: net::ERR_NAME_NOT_RESOLVED" in out
    assert "Call log" not in out


def test_cause_from_traceback_stderr(capsys):
    """Python traceback: the decisive line is the last one."""
    raw = _fatal(
        {
            "msg": "non-zero return code",
            "rc": 1,
            "stderr": "Traceback (most recent call last):\n  File \"x.py\", line 3\nKeyError: 'API_TOKEN'",
        }
    )
    last_error_diagnose.main(TASK, raw, "1")
    assert "cause: KeyError: 'API_TOKEN'" in capsys.readouterr().out


def test_cause_from_module_stderr(capsys):
    raw = _fatal(
        {
            "msg": "MODULE FAILURE\nSee stdout/stderr",
            "module_stderr": "sudo: a password is required\n",
        }
    )
    last_error_diagnose.main(TASK, raw, "1")
    out = capsys.readouterr().out
    assert "h1 — MODULE FAILURE" in out
    assert "cause: sudo: a password is required" in out


def test_cause_from_failed_loop_item(capsys):
    raw = _fatal(
        {
            "msg": "One or more items failed",
            "results": [
                {"item": "a", "failed": False, "stdout": "ok"},
                {
                    "item": "b",
                    "failed": True,
                    "msg": "non-zero return code",
                    "stderr": "E: Unable to locate package foo",
                },
            ],
        }
    )
    last_error_diagnose.main(TASK, raw, "1")
    assert "cause: E: Unable to locate package foo" in capsys.readouterr().out


def test_no_cause_line_when_msg_is_specific(capsys):
    """Specific msg with no extra output: don't print a redundant cause."""
    raw = _fatal({"msg": "Could not find or access 'files/app.conf'"})
    last_error_diagnose.main(TASK, raw, "1")
    out = capsys.readouterr().out
    assert "h1 — Could not find or access 'files/app.conf'" in out
    assert "cause:" not in out
    assert "cmd:" not in out


def test_long_cause_is_clipped(capsys):
    raw = _fatal({"msg": "non-zero return code", "stderr": "error: " + "x" * 500})
    last_error_diagnose.main(TASK, raw, "1")
    cause = next(ln for ln in capsys.readouterr().out.splitlines() if "cause:" in ln)
    assert cause.endswith("…")
    assert len(cause.split("cause: ", 1)[1]) == last_error_diagnose.MAX_LEN


def test_task_name_tracks_each_fatal(capsys):
    raw = (
        "TASK [First] ****\n"
        'fatal: [a]: FAILED! => {"msg": "boom a"}\n'
        "TASK [Second] ****\n"
        'fatal: [b]: UNREACHABLE! => {"msg": "ssh timeout", "unreachable": true}\n'
    )
    last_error_diagnose.main(TASK, raw, "1")
    out = capsys.readouterr().out
    assert "Failed (2):" in out
    assert (
        out.index("task:  First")
        < out.index("b — ssh timeout")
        < out.index("task:  Second")
    )
