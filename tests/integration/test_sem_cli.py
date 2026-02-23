"""Integration tests — run against live Semaphore instance.

Skipped unless SEM_INTEGRATION=1 is set.
Requires config.env with valid credentials.
"""

import subprocess
from pathlib import Path

import pytest

SEM = str(Path(__file__).parent.parent.parent / "sem")

pytestmark = pytest.mark.skipif(
    subprocess.os.environ.get("SEM_INTEGRATION") != "1",
    reason="SEM_INTEGRATION=1 not set",
)


def _run(*args):
    result = subprocess.run(
        ["bash", SEM, *args],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result


def test_version():
    r = _run("--version")
    assert r.returncode == 0
    assert r.stdout.startswith("sem ")


def test_ping():
    r = _run("/api/ping")
    assert r.returncode == 0
    assert "pong" in r.stdout


def test_context():
    r = _run("--context")
    assert r.returncode == 0
    assert "Project:" in r.stdout
    assert "Views:" in r.stdout
    assert "Inventories:" in r.stdout


def test_compact_tasks():
    r = _run("/api/project/1/tasks/last", "--compact")
    assert r.returncode == 0
    # Should have at least one line with a # ID
    assert "#" in r.stdout


def test_failed_filter():
    r = _run("/api/project/1/tasks/last", "--compact", "--failed")
    assert r.returncode == 0
    # Either has errors or says "no failed tasks"
    assert "#" in r.stdout or "no failed tasks" in r.stdout


def test_last_error():
    r = _run("last-error")
    assert r.returncode == 0
    # Either has a diagnosis or no failures
    assert "Failed" in r.stdout or "no failed tasks" in r.stdout


def test_bad_endpoint():
    r = _run("/api/nonexistent")
    assert r.returncode != 0
    assert "sem:" in r.stderr


def test_no_args():
    r = _run()
    assert r.returncode != 0
    assert "usage:" in r.stderr
