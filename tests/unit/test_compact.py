import compact


def test_compact_tasks(fixtures, capsys):
    # Grab first 3 tasks from fixture
    tasks = fixtures["tasks_last"][:3]
    compact.main(tasks)
    out = capsys.readouterr().out
    lines = out.strip().split("\n")
    assert len(lines) == 3
    # First task is id 3, success
    assert "#3" in lines[0]
    assert "success" in lines[0]
    assert "Deploy App" in lines[0]


def test_compact_templates(fixtures, capsys):
    templates = fixtures["templates"][:2]
    compact.main(templates)
    out = capsys.readouterr().out
    lines = out.strip().split("\n")
    assert len(lines) == 2
    # Templates have playbook and task count
    for line in lines:
        assert "#" in line


def test_compact_inventories(fixtures, capsys):
    compact.main(fixtures["inventory"])
    out = capsys.readouterr().out
    assert "#1" in out
    assert "All Hosts" in out
    assert "inventory/hosts.yml" in out


def test_compact_keys(fixtures, capsys):
    compact.main(fixtures["keys"])
    out = capsys.readouterr().out
    assert "deploy-key" in out
    assert "type=login_password" in out
    assert "infra-ssh" in out
    assert "type=ssh" in out


def test_compact_projects(fixtures, capsys):
    compact.main(fixtures["projects"])
    out = capsys.readouterr().out
    assert "#1" in out
    assert "Demo Project" in out


def test_compact_single_item(capsys):
    item = {"id": 5, "status": "success", "tpl_alias": "Test", "template_id": 1, "created": "2026-01-01T00:00:00Z"}
    compact.main(item)
    out = capsys.readouterr().out
    assert "#5" in out
    assert "success" in out
    assert "Test" in out


def test_compact_empty_list(capsys):
    compact.main([])
    out = capsys.readouterr().out
    assert out == ""
