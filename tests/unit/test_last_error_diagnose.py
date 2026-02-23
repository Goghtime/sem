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
    assert "non-zero return code" in out
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
