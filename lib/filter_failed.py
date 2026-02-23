#!/usr/bin/env python3
"""Filter task list to status=error only. JSON on stdin."""

import json
import sys


def main(data):
    if isinstance(data, list):
        data = [t for t in data if t.get("status") == "error"]
        if not data:
            print("[]")
            return
    print(json.dumps(data))


if __name__ == "__main__":
    main(json.load(sys.stdin))
