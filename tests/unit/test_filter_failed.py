import json

import filter_failed


def test_filters_to_errors(fixtures, capsys):
    filter_failed.main(fixtures["tasks_last"])
    out = capsys.readouterr().out.strip()
    tasks = json.loads(out)
    assert len(tasks) > 0
    assert all(t["status"] == "error" for t in tasks)


def test_empty_when_no_errors(capsys):
    tasks = [
        {"id": 1, "status": "success"},
        {"id": 2, "status": "success"},
    ]
    filter_failed.main(tasks)
    out = capsys.readouterr().out.strip()
    assert out == "[]"


def test_passthrough_non_list(capsys):
    single = {"id": 1, "status": "error", "name": "test"}
    filter_failed.main(single)
    out = json.loads(capsys.readouterr().out)
    assert out["id"] == 1
