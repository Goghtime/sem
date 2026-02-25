# semaphore-manage

Thin CLI wrapper around the Ansible Semaphore API. Auth, URL, and project context load from config so every call skips the boilerplate.

## Why

Every interaction with Semaphore — human or agent — starts with the same overhead: what's the URL, what's the token, what endpoint, what format. That's wasted tokens and wasted time.

`sem` front-loads that into a config file and a single discoverable entry point. The actual work starts immediately.

## Setup

```bash
cp config.env.example config.env
# Fill in your Semaphore URL, API token, and default project ID
```

## Usage

```bash
./sem --help                             # endpoint reference
./sem --context                          # live project briefing (IDs, views, keys, conventions)
./sem /api/ping                          # health check
./sem /api/project/1/tasks/last -c       # recent tasks, compact
./sem /api/project/1/templates --compact # templates, compact
./sem /api/project/1/templates/58 --set '{"view_id":10}'  # update a field
```

Run `./sem --help` for the full endpoint list and examples.

## For agents

`./sem --context` gives the full project briefing in one call — IDs, views, keys, conventions. `--compact` keeps responses short. Auth is never in the conversation.
