#!/usr/bin/env python3
"""Extract a single task JSON by ID from a task list."""

import json
import sys


def main(tasks, task_id):
    task = next((t for t in tasks if t["id"] == int(task_id)), {})
    print(json.dumps(task))


if __name__ == "__main__":
    main(json.loads(sys.argv[1]), sys.argv[2])
