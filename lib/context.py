#!/usr/bin/env python3
"""Format --context project briefing."""

import json
import os
import sys


def main(views, inventories, environments, repositories, keys, projects, project_id):
    pname = next(
        (p["name"] for p in projects if p["id"] == int(project_id)), "Unknown"
    )

    print(f"Project: {pname} (#{project_id})")
    print()

    print("Views:")
    for v in sorted(views, key=lambda x: x.get("position", 0)):
        print(f'  #{v["id"]:<5} {v["title"]}')
    print()

    print("Inventories:")
    for i in inventories:
        inv = i.get("inventory", "")
        print(f'  #{i["id"]:<5} {i["name"]:<25} {inv}')
    print()

    print("Environments:")
    for e in environments:
        jdata = json.loads(e.get("json", "{}") or "{}")
        varnames = ", ".join(jdata.keys()) if jdata else "(empty)"
        print(f'  #{e["id"]:<5} {e["name"]:<25} vars: {varnames}')
    print()

    print("Repositories:")
    for r in repositories:
        url = r.get("git_url", "")
        print(f'  #{r["id"]:<5} {r["name"]:<25} {url}')
    print()

    print("Keys:")
    for k in keys:
        ktype = k.get("type", "")
        print(f'  #{k["id"]:<5} {k["name"]:<25} type={ktype}')
    print()

    conv_file = os.environ.get("SEM_CONVENTIONS", "")
    if conv_file and os.path.isfile(conv_file):
        print("Conventions:")
        with open(conv_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    print(f"  - {line}")
    else:
        print("Conventions: (no conventions.txt found)")


if __name__ == "__main__":
    main(
        json.loads(sys.argv[1]),
        json.loads(sys.argv[2]),
        json.loads(sys.argv[3]),
        json.loads(sys.argv[4]),
        json.loads(sys.argv[5]),
        json.loads(sys.argv[6]),
        sys.argv[7],
    )
