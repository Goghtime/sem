"""Resolve foreign-key IDs in Semaphore API responses."""

import json
import os
import ssl
import sys
from urllib.request import Request, urlopen

# Field -> (resolved_key, endpoint_pattern)
RESOLVABLE = {
    "ssh_key_id": ("ssh_key", "/api/project/{p}/keys/{id}"),
    "become_key_id": ("become_key", "/api/project/{p}/keys/{id}"),
    "inventory_id": ("inventory", "/api/project/{p}/inventory/{id}"),
    "environment_id": ("environment", "/api/project/{p}/environment/{id}"),
    "repository_id": ("repository", "/api/project/{p}/repositories/{id}"),
    "view_id": ("view", "/api/project/{p}/views/{id}"),
}


def parse_key_map(raw):
    """Parse 'name=path,name=path' into {name: path}."""
    if not raw or not raw.strip():
        return {}
    result = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if "=" in entry:
            name, path = entry.split("=", 1)
            result[name.strip()] = path.strip()
    return result


def find_resolvable(obj):
    """Return list of (field, resolved_key, endpoint) for known *_id fields."""
    found = []
    for field, (resolved_key, endpoint) in RESOLVABLE.items():
        val = obj.get(field)
        if val is not None:
            found.append((field, resolved_key, endpoint, val))
    return found


def fetch_resource(url, token):
    """GET a Semaphore API resource. Returns parsed JSON."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    with urlopen(req, timeout=10, context=ctx) as resp:
        return json.loads(resp.read())


def resolve_item(obj, project_id, base_url, token, key_map, fetcher=None):
    """Resolve foreign-key references in a single object."""
    if fetcher is None:
        fetcher = fetch_resource
    refs = find_resolvable(obj)
    if not refs:
        return obj
    resolved = {}
    for field, resolved_key, endpoint, ref_id in refs:
        url = base_url + endpoint.format(p=project_id, id=ref_id)
        try:
            data = fetcher(url, token)
        except Exception:
            continue
        # Attach local_path for SSH keys
        if resolved_key in ("ssh_key", "become_key") and data.get("type") == "ssh":
            local = key_map.get(data.get("name", ""))
            if local:
                data["local_path"] = local
        resolved[resolved_key] = data
    if resolved:
        obj = dict(obj)
        obj["_resolved"] = resolved
    return obj


def main():
    data = json.loads(sys.stdin.read())
    project_id = os.environ.get("SEM_PROJECT", "")
    base_url = os.environ.get("SEMAPHORE_URL", "").rstrip("/")
    token = os.environ.get("SEMAPHORE_API_TOKEN", "")
    key_map = parse_key_map(os.environ.get("SEMAPHORE_KEY_MAP", ""))

    if isinstance(data, list):
        result = [resolve_item(item, project_id, base_url, token, key_map) for item in data]
    else:
        result = resolve_item(data, project_id, base_url, token, key_map)

    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()
