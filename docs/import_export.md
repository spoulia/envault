# Bulk Import / Export

envault supports exporting and importing `.env` variables in **JSON** and **CSV** formats for easy sharing, auditing, or migration.

## Export

Print variables from an existing `.env` file to stdout:

```bash
# JSON (default)
envault impexp export .env

# CSV
envault impexp export .env --format csv

# Save to file
envault impexp export .env --format json -o vars.json
```

Example JSON output:
```json
{
  "API_KEY": "abc123",
  "DB_URL": "postgres://localhost/db"
}
```

Example CSV output:
```
key,value
API_KEY,abc123
DB_URL,postgres://localhost/db
```

## Import

Write variables from a JSON or CSV file into a `.env` file:

```bash
# Replace contents
envault impexp import vars.json .env

# Merge with existing keys (new values overwrite duplicates)
envault impexp import vars.json .env --merge

# Import from CSV
envault impexp import vars.csv .env --format csv
```

### Merge behaviour

Without `--merge`, the target `.env` is **replaced** entirely.
With `--merge`, existing keys are preserved and only new/updated keys are applied.

## Notes

- Comments and blank lines are stripped during export.
- Keys are written in alphabetical order.
- JSON input must be a flat `{"KEY": "value"}` object.
- CSV input must have `key` and `value` column headers.
