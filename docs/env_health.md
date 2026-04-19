# env health

Run a comprehensive health check on a `.env` file in a single pass.

## Checks performed

| Level   | Condition                                              |
|---------|--------------------------------------------------------|
| error   | File not found                                         |
| error   | Line missing `=` separator                             |
| warning | Key is not uppercase                                   |
| warning | Duplicate key detected                                 |
| info    | Value is empty, `CHANGE_ME`, `TODO`, or `<your_value>` |

## Usage

```bash
# Basic check (exits 0 if no errors)
envault health check .env

# Strict mode — exits 1 on warnings too
envault health check --strict .env
```

## Example output

```
[ERROR  ] Line 3: missing '=' separator
[WARNING] Key 'db_host' is not uppercase
[WARNING] Duplicate key 'PORT' (first at line 2)
[INFO   ] Key 'SECRET' has a placeholder or empty value

1 error(s), 2 warning(s) in .env.
```

When the file is healthy:

```
✓ .env looks healthy (12 keys).
```

## Python API

```python
from pathlib import Path
from envault.env_health import check_health

result = check_health(Path(".env"))
print(result.healthy)   # True / False
print(result.errors)    # list of HealthIssue
print(result.warnings)  # list of HealthIssue
```
