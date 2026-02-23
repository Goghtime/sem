import last_error_find


def test_finds_first_failed(fixtures, capsys):
    last_error_find.main(fixtures["tasks_last"])
    out = capsys.readouterr().out.strip()
    assert out == "2"


def test_no_failures(capsys):
    tasks = [
        {"id": 1, "status": "success"},
        {"id": 2, "status": "success"},
    ]
    last_error_find.main(tasks)
    out = capsys.readouterr().out.strip()
    assert out == "NO_FAILURES"


def test_empty_list(capsys):
    last_error_find.main([])
    out = capsys.readouterr().out.strip()
    assert out == "NO_FAILURES"
