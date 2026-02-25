# semaphore-manage — Agent Interface

CLI wrapper (`sem`) around the Ansible Semaphore API.
Auth and project context load from `config.env` — never pass tokens in conversation.

## Quick Start

```bash
sem --context              # project briefing: IDs, views, keys, conventions
```

Read the output. It has everything you need to construct API calls.

## Commands

| Command | What it does |
|---------|-------------|
| `sem --context [project]` | Project briefing (IDs, views, keys, conventions) |
| `sem last-error [project]` | Diagnose most recent failed task |
| `sem <api-path>` | Raw API call (pretty-printed JSON) |
| `sem <api-path> --compact` | One-line-per-item summary |
| `sem <api-path> --failed` | Filter to status=error only |
| `sem <api-path> --resolve` | Expand foreign-key IDs into referenced objects |
| `sem <api-path> --set '{"key":"val"}'` | GET → merge → PUT |
| `sem --version` | Print version |
| `sem --help` | Full endpoint reference |

## Flags

| Flag | Short | Effect |
|------|-------|--------|
| `--compact` | `-c` | One-liner output per item |
| `--failed` | `-f` | Filter to failed tasks only |
| `--resolve` | `-r` | Expand `*_id` foreign keys into referenced objects (+ local SSH key paths) |
| `--set '{...}'` | | Merge JSON into existing resource and PUT |

Flags combine: `sem /api/project/1/tasks/last -c -f` → compact failed tasks.

## Common Workflows

### Inspect recent tasks
```bash
sem /api/project/1/tasks/last -c           # all recent
sem /api/project/1/tasks/last -c -f        # only failures
```

### Diagnose a failure
```bash
sem last-error                             # auto-finds most recent failure
sem /api/project/1/tasks/197/raw_output    # full Ansible log for task 197
```

### Run a template
```bash
sem /api/project/1/tasks -X POST -d '{"template_id":5}'
```

### Update a resource field
```bash
sem /api/project/1/templates/58 --set '{"view_id":10}'
```

### Resolve references
```bash
sem /api/project/1/inventory/6 --resolve   # inline SSH key, repository details
sem /api/project/1/templates/1 --resolve   # inline inventory, environment, repo, view
```

### List project resources
```bash
sem /api/project/1/templates -c
sem /api/project/1/inventory -c
sem /api/project/1/environment -c
sem /api/project/1/keys -c
sem /api/project/1/views -c
```

## Output Formats

| Mode | Format |
|------|--------|
| Default | Pretty-printed JSON |
| `--compact` | `#ID  status  name  timestamp` (type-detected) |
| `--context` | Structured briefing (not JSON) |
| `--resolve` | Original JSON with `_resolved` key containing expanded references |
| `last-error` | Diagnosis: header, failed hosts, recap, log path |
| Errors | `sem: <message>` to stderr, exit 1 |

## Error Behavior

- Non-zero exit on any failure
- All errors go to stderr, prefixed with `sem:`
- HTTP errors include status code: `sem: HTTP 404 on /api/project/1/tasks/999`
- Connection failures include the URL attempted

## Project Structure

```
sem                  CLI entry point (Bash)
config.env           SEMAPHORE_URL, SEMAPHORE_API_TOKEN, SEMAPHORE_DEFAULT_PROJECT, SEMAPHORE_KEY_MAP
config.env.example   Template for config.env
conventions.txt      Project naming conventions (loaded by --context)
lib/                 Python modules (called by sem)
  context.py         Format --context briefing
  compact.py         Type-detect and format one-liners
  filter_failed.py   Filter to status=error
  merge_json.py      GET→merge for --set
  last_error_find.py       Find first failed task ID
  last_error_extract.py    Extract single task JSON
  last_error_diagnose.py   Parse raw output for fatals/recap
  resolve.py               Expand foreign-key IDs via API + local key map
```

## Requirements

- `bash`, `curl`, `python3` (validated at startup)
- Network access to Semaphore instance
- **Windows:** Git for Windows (provides bash), then run `install.ps1` to add to PATH
- **Linux/macOS:** Run `install.sh` to symlink into `~/.local/bin`
