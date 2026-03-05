# Logs folder

**Simple:** This folder holds the **diary** (log files). Each file is a list of "what happened." The program reads it and looks for bad words from the rules. When it finds one → bell rings (alert).

This folder holds **log files** (JSON) that the detection engine runs rules against.

## File format

- Each file is **JSON**.
- The engine accepts:
  - A **top-level array** of log entries, e.g. `[ { ... }, { ... } ]`
  - Or an object with key **`logs`** or **`entries`** containing that array.

## Each log entry (one object)

One object = one event. Recommended fields:

| Field       | Meaning |
|------------|---------|
| `timestamp`| When the event occurred (e.g. `"2025-03-04T10:00:00Z"`) |
| `source`   | Where the log came from (e.g. `"audit"`, `"auth"`) |
| `message`  | Main text that rules match on (e.g. command line, log line) |

Rules use `condition.field` to choose which key to check (often `message`). You can add more fields (e.g. `user`, `ip`); the engine will pass the whole entry into the alert.

## Sample file: `sample.json`

- **First entry:** `message` is `"user=admin cmd=git status"` → normal activity, no alert.
- **Second entry:** `message` contains `"IEX "` (PowerShell shorthand for running code) → should trigger a rule that has `"IEX "` in its `patterns` and `field: message`.

See `docs/shapes.md` for the full rule and log shape reference.
