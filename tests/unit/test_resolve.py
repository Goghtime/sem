import resolve


def _lookups(fixtures):
    return resolve.build_lookups(
        fixtures["keys"],
        fixtures["inventory"],
        fixtures["environment"],
        fixtures["repositories"],
        fixtures["views"],
    )


def test_parse_key_map_multiple():
    result = resolve.parse_key_map("ansible=~/.ssh/ansible,MB=~/.ssh/mb_ed25519")
    assert result == {"ansible": "~/.ssh/ansible", "MB": "~/.ssh/mb_ed25519"}


def test_parse_key_map_single():
    result = resolve.parse_key_map("ansible=~/.ssh/ansible")
    assert result == {"ansible": "~/.ssh/ansible"}


def test_parse_key_map_empty():
    assert resolve.parse_key_map("") == {}
    assert resolve.parse_key_map(None) == {}


def test_find_resolvable_inventory():
    obj = {"id": 1, "name": "All Hosts", "ssh_key_id": 2, "repository_id": 1, "become_key_id": None}
    found = resolve.find_resolvable(obj)
    fields = [f[0] for f in found]
    assert "ssh_key_id" in fields
    assert "repository_id" in fields
    assert "become_key_id" not in fields


def test_find_resolvable_template():
    obj = {"id": 1, "inventory_id": 1, "environment_id": 1, "repository_id": 1, "view_id": 5}
    found = resolve.find_resolvable(obj)
    fields = [f[0] for f in found]
    assert "inventory_id" in fields
    assert "environment_id" in fields
    assert "repository_id" in fields
    assert "view_id" in fields


def test_find_resolvable_no_refs():
    obj = {"id": 1, "name": "just a thing", "status": "success"}
    assert resolve.find_resolvable(obj) == []


def test_resolve_item_inventory(fixtures):
    lookups = _lookups(fixtures)
    inventory = fixtures["inventory"][0]  # ssh_key_id: 2, repository_id: 1

    result = resolve.resolve_item(inventory, lookups, key_map={})
    assert "_resolved" in result
    assert result["_resolved"]["ssh_key"]["name"] == "infra-ssh"
    assert result["_resolved"]["repository"]["name"] == "demo-ansible"


def test_key_map_attaches_local_path(fixtures):
    lookups = _lookups(fixtures)
    inventory = fixtures["inventory"][0]

    result = resolve.resolve_item(
        inventory, lookups, key_map={"infra-ssh": "~/.ssh/infra_ssh"},
    )
    assert result["_resolved"]["ssh_key"]["local_path"] == "~/.ssh/infra_ssh"


def test_key_map_no_match(fixtures):
    lookups = _lookups(fixtures)
    inventory = fixtures["inventory"][0]

    result = resolve.resolve_item(
        inventory, lookups, key_map={"other-key": "~/.ssh/other"},
    )
    assert "local_path" not in result["_resolved"]["ssh_key"]


def test_resolve_array(fixtures):
    lookups = _lookups(fixtures)
    items = [
        {"id": 1, "ssh_key_id": 2},
        {"id": 2, "ssh_key_id": 2},
    ]

    results = [resolve.resolve_item(item, lookups, key_map={}) for item in items]
    assert all("_resolved" in r for r in results)


def test_null_id_skipped():
    obj = {"id": 1, "ssh_key_id": 3, "become_key_id": None}
    found = resolve.find_resolvable(obj)
    fields = [f[0] for f in found]
    assert "ssh_key_id" in fields
    assert "become_key_id" not in fields


def test_missing_id_skipped(fixtures):
    lookups = _lookups(fixtures)
    obj = {"id": 1, "ssh_key_id": 999}

    result = resolve.resolve_item(obj, lookups, key_map={})
    assert "_resolved" not in result
