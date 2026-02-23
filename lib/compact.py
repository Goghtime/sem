#!/usr/bin/env python3
"""Type-detect and format one-liners. JSON on stdin."""

import json
import sys
from datetime import datetime


def short_time(iso):
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%b %d %H:%M")
    except Exception:
        return iso[:16]


def main(data):
    if not isinstance(data, list):
        data = [data]

    for item in data:
        lt = item.get("last_task") or {}

        iid = item.get("id", "")
        name = (
            item.get("tpl_alias") or lt.get("tpl_alias") or item.get("name", "")
        )
        status = item.get("status") or lt.get("status", "")
        playbook = (
            item.get("tpl_playbook")
            or lt.get("tpl_playbook")
            or item.get("playbook", "")
        )
        itype = item.get("type", "")
        created = item.get("created") or lt.get("created", "")

        # inventories
        if "ssh_key_id" in item or (
            "inventory" in item and "tpl_alias" not in item
        ):
            inv = item.get("inventory") or ""
            print(f"#{iid:<5} {name:<25} {inv}")

        # tasks
        elif "tpl_alias" in item or (
            "template_id" in item and item.get("template_id")
        ):
            print(f"#{iid:<5} {status:<8} {name:<35} {short_time(created)}")

        # templates
        elif "last_task" in item or "tasks" in item:
            task_count = item.get("tasks", 0)
            print(
                f"#{iid:<5} {name:<35} {playbook:<55} [{status}] x{task_count}"
            )

        # environments, keys, repos
        elif "password" in item or "key_id" in item:
            print(
                f"#{iid:<5} {name:<25} type={itype}"
                if itype
                else f"#{iid:<5} {name}"
            )

        elif "project_id" in item and itype:
            print(f"#{iid:<5} {name:<25} type={itype}")

        # projects
        elif "alert" in item:
            print(f"#{iid:<5} {name:<35} {short_time(created)}")

        # fallback
        else:
            parts = [f"#{iid}", name, status, itype]
            print("  ".join(p for p in parts if p))


if __name__ == "__main__":
    main(json.load(sys.stdin))
