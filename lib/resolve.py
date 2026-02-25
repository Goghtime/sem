"""Resolve foreign-key IDs in Semaphore API responses.

Lookup tables passed as argv, data to resolve on stdin.
"""

import json
import os
import sys

# Field -> resolved_key, and which lookup table it comes from
RESOLVABLE = {
    "ssh_key_id": ("ssh_key", "keys"),
    "become_key_id": ("become_key", "keys"),
    "inventory_id": ("inventory", "inventory"),
    "environment_id": ("environment", "environment"),
    "repository_id": ("repository", "repositories"),
    "view_id": ("view", "views"),
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


def build_lookups(keys, inventory, environment, repositories, views):
    """Index each list by id for O(1) lookup."""
    return {
        "keys": {item["id"]: item for item in keys},
        "inventory": {item["id"]: item for item in inventory},
        "environment": {item["id"]: item for item in environment},
        "repositories": {item["id"]: item for item in repositories},
        "views": {item["id"]: item for item in views},
    }


def find_resolvable(obj):
    """Return list of (field, resolved_key, table_name) for known *_id fields."""
    found = []
    for field, (resolved_key, table_name) in RESOLVABLE.items():
        val = obj.get(field)
        if val is not None:
            found.append((field, resolved_key, table_name, val))
    return found


def resolve_item(obj, lookups, key_map):
    """Resolve foreign-key references in a single object."""
    refs = find_resolvable(obj)
    if not refs:
        return obj
    resolved = {}
    for field, resolved_key, table_name, ref_id in refs:
        data = lookups.get(table_name, {}).get(ref_id)
        if data is None:
            continue
        data = dict(data)
        if resolved_key in ("ssh_key", "become_key") and data.get("type") == "ssh":
            local = key_map.get(data.get("name", ""))
            if local:
                data["local_path"] = local
        resolved[resolved_key] = data
    if resolved:
        obj = dict(obj)
        obj["_resolved"] = resolved
    return obj


def main(data, keys, inventory, environment, repositories, views, key_map):
    lookups = build_lookups(keys, inventory, environment, repositories, views)
    if isinstance(data, list):
        result = [resolve_item(item, lookups, key_map) for item in data]
    else:
        result = resolve_item(data, lookups, key_map)
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    data = json.load(sys.stdin)
    keys = json.loads(sys.argv[1])
    inventory = json.loads(sys.argv[2])
    environment = json.loads(sys.argv[3])
    repositories = json.loads(sys.argv[4])
    views = json.loads(sys.argv[5])
    key_map = parse_key_map(os.environ.get("SEMAPHORE_KEY_MAP", ""))
    main(data, keys, inventory, environment, repositories, views, key_map)
