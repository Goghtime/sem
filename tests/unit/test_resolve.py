import json

import resolve


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
    found = resolve.find_resolvable(obj)
    assert found == []


def test_resolve_item_with_mock_fetcher(fixtures):
    inventory = fixtures["inventory"][0]  # ssh_key_id: 2, repository_id: 1
    keys_by_id = {k["id"]: k for k in fixtures["keys"]}
    repos_by_id = {r["id"]: r for r in fixtures["repositories"]}

    def mock_fetcher(url, token):
        if "/keys/" in url:
            kid = int(url.rstrip("/").split("/")[-1])
            return keys_by_id[kid]
        if "/repositories/" in url:
            rid = int(url.rstrip("/").split("/")[-1])
            return repos_by_id[rid]
        raise ValueError(f"unexpected url: {url}")

    result = resolve.resolve_item(
        inventory, project_id="1", base_url="https://test",
        token="tok", key_map={}, fetcher=mock_fetcher,
    )
    assert "_resolved" in result
    assert result["_resolved"]["ssh_key"]["name"] == "infra-ssh"
    assert result["_resolved"]["repository"]["name"] == "demo-ansible"


def test_key_map_attaches_local_path(fixtures):
    inventory = fixtures["inventory"][0]  # ssh_key_id: 2 -> infra-ssh
    keys_by_id = {k["id"]: k for k in fixtures["keys"]}

    def mock_fetcher(url, token):
        if "/keys/" in url:
            kid = int(url.rstrip("/").split("/")[-1])
            return keys_by_id[kid]
        return {}

    result = resolve.resolve_item(
        inventory, project_id="1", base_url="https://test",
        token="tok", key_map={"infra-ssh": "~/.ssh/infra_ssh"},
        fetcher=mock_fetcher,
    )
    assert result["_resolved"]["ssh_key"]["local_path"] == "~/.ssh/infra_ssh"


def test_key_map_no_match(fixtures):
    inventory = fixtures["inventory"][0]
    keys_by_id = {k["id"]: k for k in fixtures["keys"]}

    def mock_fetcher(url, token):
        if "/keys/" in url:
            kid = int(url.rstrip("/").split("/")[-1])
            return keys_by_id[kid]
        return {}

    result = resolve.resolve_item(
        inventory, project_id="1", base_url="https://test",
        token="tok", key_map={"other-key": "~/.ssh/other"},
        fetcher=mock_fetcher,
    )
    assert "local_path" not in result["_resolved"]["ssh_key"]


def test_resolve_array(fixtures):
    items = [
        {"id": 1, "ssh_key_id": 2},
        {"id": 2, "ssh_key_id": 2},
    ]
    keys_by_id = {k["id"]: k for k in fixtures["keys"]}

    def mock_fetcher(url, token):
        if "/keys/" in url:
            kid = int(url.rstrip("/").split("/")[-1])
            return keys_by_id[kid]
        return {}

    results = [
        resolve.resolve_item(item, "1", "https://test", "tok", {}, mock_fetcher)
        for item in items
    ]
    assert all("_resolved" in r for r in results)


def test_null_id_skipped():
    obj = {"id": 1, "ssh_key_id": 3, "become_key_id": None}
    found = resolve.find_resolvable(obj)
    fields = [f[0] for f in found]
    assert "ssh_key_id" in fields
    assert "become_key_id" not in fields


def test_fetch_failure_skips_gracefully():
    obj = {"id": 1, "ssh_key_id": 99}

    def failing_fetcher(url, token):
        raise ConnectionError("nope")

    result = resolve.resolve_item(
        obj, project_id="1", base_url="https://test",
        token="tok", key_map={}, fetcher=failing_fetcher,
    )
    assert "_resolved" not in result
