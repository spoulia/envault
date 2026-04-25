# env-whitelist

Filter an `.env` file so that **only explicitly allowed keys** are retained. All other keys are removed. This is useful for producing a minimal, safe subset of your environment before sharing or deploying.

## Library API

```python
from pathlib import Path
from envault.env_whitelist import whitelist_file

result = whitelist_file(
    Path(".env"),
    allowed=["DB_HOST", "DB_PORT"],
    patterns=["APP_*"],          # optional glob patterns
    output=Path(".env.slim"),    # optional separate output file
)

print(result.kept)          # ['DB_HOST', 'DB_PORT', 'APP_NAME']
print(result.removed)       # ['SECRET_KEY', 'DEBUG', ...]
print(result.kept_count)    # 3
print(result.removed_count) # 2
```

### `whitelist_file` parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `src` | `Path` | Source `.env` file to process. |
| `allowed` | `list[str]` | Exact key names to keep. |
| `patterns` | `list[str]` | Glob patterns (e.g. `DB_*`) to keep. |
| `output` | `Path \| None` | Destination file. Defaults to overwriting `src`. |

## CLI

```
envault whitelist run [OPTIONS] SRC
```

### Options

| Flag | Description |
|------|-------------|
| `-k / --key KEY` | Exact key to keep (repeatable). |
| `-p / --pattern PAT` | Glob pattern to keep (repeatable). |
| `-o / --output PATH` | Write result to a separate file. |
| `--dry-run` | Print what would change without writing. |

### Examples

```bash
# Keep only DB_* keys, overwrite in place
envault whitelist run .env -p "DB_*"

# Keep specific keys, write to new file
envault whitelist run .env -k APP_NAME -k APP_PORT -o .env.slim

# Preview without modifying
envault whitelist run .env -k DEBUG --dry-run
```
