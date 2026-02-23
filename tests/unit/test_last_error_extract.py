import json

import last_error_extract


def test_extracts_task_by_id(fixtures, capsys):
    last_error_extract.main(fixtures["tasks_last"], "2")
    out = capsys.readouterr().out.strip()
    task = json.loads(out)
    assert task["id"] == 2
    assert task["status"] == "error"
    assert task["tpl_alias"] == "Deploy App"


def test_missing_id_returns_empty(fixtures, capsys):
    last_error_extract.main(fixtures["tasks_last"], "999999")
    out = capsys.readouterr().out.strip()
    assert json.loads(out) == {}
