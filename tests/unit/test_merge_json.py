import json

import merge_json


def test_merge_updates_field(capsys):
    current = {"id": 58, "name": "Test", "view_id": 1}
    updates = {"view_id": 10}
    merge_json.main(current, updates)
    out = json.loads(capsys.readouterr().out)
    assert out["view_id"] == 10
    assert out["name"] == "Test"


def test_merge_strips_readonly_fields(capsys):
    current = {
        "id": 58,
        "name": "Test",
        "last_task": {"id": 100, "status": "success"},
        "tasks": 5,
        "task_params": {},
    }
    updates = {"name": "Updated"}
    merge_json.main(current, updates)
    out = json.loads(capsys.readouterr().out)
    assert "last_task" not in out
    assert "tasks" not in out
    assert "task_params" not in out
    assert out["name"] == "Updated"


def test_merge_adds_new_field(capsys):
    current = {"id": 1}
    updates = {"description": "new field"}
    merge_json.main(current, updates)
    out = json.loads(capsys.readouterr().out)
    assert out["description"] == "new field"
