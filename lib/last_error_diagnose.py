#!/usr/bin/env python3
"""Parse raw Ansible output for fatals and recap. Raw log via stdin."""

import json
import re
import sys
from datetime import datetime


def main(task, raw, project_id):
    task_id = task.get("id", "")
    tpl = task.get("tpl_alias", "")
    created = task.get("created", "")

    try:
        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        ts = dt.strftime("%b %d %H:%M")
    except Exception:
        ts = created[:16] if created else ""

    print(f"#{task_id}  {tpl}  |  {ts}")
    print()

    fatals = re.findall(r"fatal: \[([^\]]+)\].*?=> ({.*})", raw)
    if fatals:
        print(f"Failed ({len(fatals)}):")
        for host, payload in fatals:
            try:
                msg = json.loads(payload).get("msg", payload)
                first_line = msg.strip().split("\n")[0]
                print(f"  {host} — {first_line}")
            except Exception:
                print(f"  {host} — {payload[:120]}")
    else:
        recap_failures = re.findall(
            r"^(\S+)\s+.*failed=([1-9]\d*)", raw, re.MULTILINE
        )
        if recap_failures:
            print(f"Failed ({len(recap_failures)}):")
            for host, count in recap_failures:
                print(f"  {host} — {count} failed task(s)")
        else:
            print("Failed: (could not extract failure details)")
    print()

    recap_lines = re.findall(
        r"^(\S+)\s+:.*?ok=(\d+).*?unreachable=(\d+).*?failed=(\d+)",
        raw,
        re.MULTILINE,
    )
    passed = sum(1 for _, _, u, f in recap_lines if int(f) == 0 and int(u) == 0)
    failed = sum(1 for _, _, u, f in recap_lines if int(f) > 0)
    unreachable = sum(1 for _, _, u, f in recap_lines if int(u) > 0)

    if recap_lines:
        print(f"Recap: {passed} passed, {failed} failed, {unreachable} unreachable")
    else:
        print("Recap: (no PLAY RECAP found — task may have failed before execution)")
    print()
    print(f"Full log: sem /api/project/{project_id}/tasks/{task_id}/raw_output")


if __name__ == "__main__":
    task = json.loads(sys.argv[1])
    raw = sys.stdin.read()
    project_id = sys.argv[2]
    main(task, raw, project_id)
