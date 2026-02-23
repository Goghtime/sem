#!/usr/bin/env python3
"""GET→merge for --set workflow. Current JSON on stdin, updates as argv[1]."""

import json
import sys


def main(current, updates):
    for k in ["last_task", "tasks", "task_params"]:
        current.pop(k, None)
    current.update(updates)
    print(json.dumps(current))


if __name__ == "__main__":
    current = json.load(sys.stdin)
    updates = json.loads(sys.argv[1])
    main(current, updates)
