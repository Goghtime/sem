#!/usr/bin/env python3
"""Parse raw Ansible output for fatals and recap. Raw log via stdin."""

import json
import re
import sys
from datetime import datetime

MAX_LEN = 200
# Fields that carry the real error when Ansible's "msg" is generic
# (e.g. "non-zero return code", "MODULE FAILURE"). Checked in order.
CAUSE_FIELDS = ("stderr", "stdout", "module_stderr", "module_stdout")
ERROR_HINT = re.compile(
    r"error|fatal|fail|exception|denied|refused|not found|timed? ?out", re.IGNORECASE
)


def _clip(text):
    text = text.strip()
    return text if len(text) <= MAX_LEN else text[: MAX_LEN - 1] + "…"


def _first_line(text):
    return text.strip().split("\n")[0] if text else ""


def _cause_from_text(text):
    """Pull the most informative line out of a stdout/stderr blob."""
    if not isinstance(text, str) or not text.strip():
        return None
    # Tools that emit JSON errors (e.g. {"error": "...", "code": 4})
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            for key in ("error", "message", "msg", "detail"):
                if isinstance(obj.get(key), str) and obj[key].strip():
                    return _first_line(obj[key])
    except ValueError:
        pass
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    hinted = [ln for ln in lines if ERROR_HINT.search(ln)]
    # Tracebacks and most CLIs put the decisive line last
    return (hinted or lines)[-1]


def extract_cause(payload):
    """Return the underlying error from a fatal payload, or None."""
    for field in CAUSE_FIELDS:
        cause = _cause_from_text(payload.get(field))
        if cause:
            return cause
    # Loop tasks: dig into the first failed item
    for item in payload.get("results") or []:
        if isinstance(item, dict) and item.get("failed"):
            cause = extract_cause(item) or _first_line(item.get("msg", ""))
            if cause:
                return cause
    return None


def find_fatals(raw):
    """Return [(host, task_name, payload_str)] for each fatal line."""
    fatals = []
    task_name = ""
    for line in raw.splitlines():
        m = re.match(r"TASK \[(.+?)\]", line)
        if m:
            task_name = m.group(1)
            continue
        m = re.search(r"fatal: \[([^\]]+)\].*?=> ({.*})", line)
        if m:
            fatals.append((m.group(1), task_name, m.group(2)))
    return fatals


def print_fatal(host, task_name, payload_str):
    try:
        payload = json.loads(payload_str)
    except ValueError:
        print(f"  {host} — {_clip(payload_str)}")
        return
    msg = _first_line(str(payload.get("msg", ""))) or "(no msg)"
    rc = payload.get("rc")
    print(f"  {host} — {_clip(msg)}" + (f" (rc={rc})" if rc is not None else ""))
    if task_name:
        print(f"    task:  {task_name}")
    cmd = payload.get("cmd")
    if cmd:
        print(
            f"    cmd:   {_clip(' '.join(cmd) if isinstance(cmd, list) else str(cmd))}"
        )
    cause = extract_cause(payload)
    if cause and cause != msg:
        print(f"    cause: {_clip(cause)}")


def main(task, raw, project_id):
    task_id = task.get("id", "")
    tpl = task.get("tpl_alias", "")
    created = task.get("created", "")

    try:
        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))  # noqa: FURB162 — py<3.11
        ts = dt.strftime("%b %d %H:%M")
    except (ValueError, TypeError, AttributeError):
        ts = created[:16] if created else ""

    print(f"#{task_id}  {tpl}  |  {ts}")
    print()

    fatals = find_fatals(raw)
    if fatals:
        print(f"Failed ({len(fatals)}):")
        for host, task_name, payload in fatals:
            print_fatal(host, task_name, payload)
    else:
        recap_failures = re.findall(r"^(\S+)\s+.*failed=([1-9]\d*)", raw, re.MULTILINE)
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
