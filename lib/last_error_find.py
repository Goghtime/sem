#!/usr/bin/env python3
"""Find the first failed task ID from a task list."""

import json
import sys


def main(tasks):
    failed = [t for t in tasks if t.get("status") == "error"]
    if not failed:
        print("NO_FAILURES")
        return
    print(failed[0]["id"])


if __name__ == "__main__":
    main(json.loads(sys.argv[1]))
