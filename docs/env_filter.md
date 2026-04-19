# env filter

The `filter` command lets you keep or remove keys from a `.env` file based on exact names, a prefix, or a glob pattern.

## Usage

```
envault filter run [OPTIONS] ENV_FILE
```

### Options

| Option | Description |
|---|---|
| `--key TEXT` | Exact key name to match (repeatable) |
| `--prefix TEXT` | Keep keys whose name starts with this prefix |
| `--pattern TEXT` | Glob pattern matched against key names |
| `--exclude` | Remove matching keys instead of keeping them |
| `--write` | Write the filtered result back to the file |

## Examples

### Keep only database keys

```bash
envault filter run .env --prefix DB_
```

### Remove all debug/test keys and save

```bash
envault filter run .env --pattern '*_DEBUG' --pattern '*_TEST' --exclude --write
```

### Extract specific keys to stdout

```bash
envault filter run .env --key API_KEY --key API_SECRET
```

## Behaviour

- Without `--write` the filtered pairs are printed to stdout and the file is **not** modified.
- Multiple criteria (`--key`, `--prefix`, `--pattern`) are combined with **OR** logic — a key matching any one criterion is selected.
- Comments and blank lines in the original file are not preserved when `--write` is used.
