# Rule and log shapes

## The simple version (explained like you're 2)

**What are logs?**  
Logs are like a **diary**. Every line is one thing that happened. "Someone did this. Then someone did that."

**What are rules?**  
Rules are like a **list of bad words**. We write down words we don't want to see. If the diary says one of those bad words, we **ring the bell** (that's the alert).

**So what do we do?**  
1. We have a diary (the log file).  
2. We have a list of bad words (the rule file).  
3. The program reads the diary.  
4. For each line, it asks: "Is any bad word in this line?"  
5. If yes → **ring the bell** (alert!). If no → say nothing.

**What's a "rule shape"?**  
It's the **format** of our list. We all agree: the list has a name (id), and then the bad words go under "patterns." So the program knows where to look.

**What's a "log shape"?**  
It's the **format** of the diary. We all agree: each thing that happened is one block, and the actual text we check is in a box called "message." So the program knows where to look.

**That's it.** Rules = list of bad words. Logs = diary of what happened. Program = read diary, look for bad words, ring the bell when you find one.

---

## The detailed version

This document explains how **rules** and **logs** are structured so the detection engine knows what to load and how to match.

---

### Why we define shapes

- **Rules** tell the engine: "when you see *this* in a log, raise an alert."
- **Logs** are the data we run the rules against (one "event" per log entry).

The engine expects rules and logs to follow a fixed **shape** (fields and structure). That way we can add new rules and new log files without changing the engine code.

---

### Rule shape (YAML)

Each rule is **one YAML file** under `rules/`. One file = one detection.

#### Top-level fields

| Field         | Required | Description |
|---------------|----------|-------------|
| `id`          | yes      | Unique rule ID (e.g. `suspicious-command-001`). Used in alerts. |
| `enabled`     | no       | If `false`, the rule is skipped. Default: `true`. |
| `name`        | no       | Short name for the rule (for alerts and docs). |
| `description` | no       | What the rule detects (for docs and alert text). |
| `severity`    | no       | `low`, `medium`, `high`, `critical`. Default: `medium`. |
| `condition`   | yes      | Defines *when* to alert (see below). |

#### Condition: `log_match`

For `condition.type: log_match`, the rule checks **one field** of each log entry and looks for **any** of the given patterns in that field.

| Field      | Required | Description |
|------------|----------|-------------|
| `type`     | yes      | Must be `log_match` for this behaviour. |
| `field`    | no       | The log entry key to check (e.g. `message`). Default: `message`. |
| `patterns` | yes      | List of strings. If **any** appears in the chosen field, the rule matches and we raise an alert. |

**Example:** If `field: message` and `patterns: ["IEX ", "base64 -d"]`, then any log whose `message` contains `"IEX "` or `"base64 -d"` will trigger this rule.

---

### Log shape (JSON)

Log input is a **JSON file**. The engine expects either:

- A **JSON array** of log entries, or  
- An object with a key **`logs`** or **`entries`** whose value is that array.

Each **log entry** is one object (one event). The engine only cares about the fields that rules use (e.g. `message` when the rule has `condition.field: message`). Other fields are allowed and can be passed through to the alert.

#### Common fields (recommended)

| Field       | Description |
|-------------|-------------|
| `timestamp` | When the event happened (e.g. ISO 8601: `2025-03-04T10:00:00Z`). |
| `source`    | Where the log came from (e.g. `audit`, `auth`, `app`). |
| `message`   | Main text that rules often match against (e.g. command line, log line). |

You can add more fields (e.g. `user`, `ip`, `host`). Rules refer to them via `condition.field`.

---

### Explanation of `logs/sample.json`

JSON does not support comments, so the log shape is explained here.

The file is a **single JSON array** of two log entries:

1. **First entry**  
   - `timestamp`: when it happened  
   - `source`: `"audit"` (audit log)  
   - `message`: `"user=admin cmd=git status"`  
   - This is **normal** activity; no suspicious pattern, so no rule should fire.

2. **Second entry**  
   - Same structure  
   - `message`: `"user=admin cmd=powershell -Enc IEX (New-Object Net.WebClient)"`  
   - The string **`IEX `** appears in `message`, so a rule with `patterns: ["IEX "]` and `field: message` **should** fire for this entry.

So when you run the engine on `logs/sample.json` with the rule in `rules/suspicious-command.yaml`, you should get **one alert** (for the second log entry).

---

### Summary

- **Rule** = YAML with `id`, `enabled`, and `condition`. For `log_match`, we give `field` and `patterns`; the engine checks that field and raises an alert when any pattern is found.
- **Log** = JSON array (or object with `logs`/`entries`) of objects; each object is one event. Rules use the field names (e.g. `message`) to decide when to alert.
