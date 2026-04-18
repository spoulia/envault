# Vault Search

The `search` command lets you find keys (and optionally values) inside encrypted vaults without fully decrypting them to disk.

## Usage

```bash
envault search run PATTERN [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `PATTERN` | Regular expression to match against key names |

### Options

| Option | Description |
|--------|-------------|
| `--vault / -v` | Path to vault file (repeatable, default: `.env.vault`) |
| `--password / -p` | Vault password (prompted if omitted) |
| `--values` | Also search inside values |
| `--ignore-case / -i` | Case-insensitive matching |

## Examples

### Find all database-related keys

```bash
envault search run "^DB_" --vault .env.vault
```

### Search across multiple vaults

```bash
envault search run "API_KEY" -v staging.vault -v production.vault
```

### Search values too

```bash
envault search run "localhost" --values
```

### Case-insensitive search

```bash
envault search run "secret" -i
```

## Output

Results are grouped by vault file:

```
[.env.vault]
  line    1: DB_HOST = ***
  line    2: DB_PORT = ***
```

When `--values` is used, the actual value is shown instead of `***`.

## Notes

- Patterns are standard Python regular expressions.
- Wrong passwords cause the vault to be skipped when using `search_many`.
- Line numbers refer to the decrypted `.env` content.
