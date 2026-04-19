# env_schema — Schema Validation for .env Files

Validate your `.env` files against a JSON schema to enforce required keys, types, allowed values, and patterns.

## Schema Format

A schema is a JSON file with a `keys` object. Each key maps to a rules object:

```json
{
  "keys": {
    "DATABASE_URL": { "required": true, "type": "string" },
    "PORT":         { "required": true, "type": "integer" },
    "DEBUG":        { "required": false, "type": "boolean" },
    "ENV":          { "required": true, "allowed": ["prod", "staging", "dev"] },
    "VERSION":      { "required": true, "pattern": "\\d+\\.\\d+\\.\\d+" }
  }
}
```

### Supported Rules

| Rule      | Description                                         |
|-----------|-----------------------------------------------------|
| `required`| If `true`, key must be present in the .env file     |
| `type`    | One of `string`, `integer`, `float`, `boolean`      |
| `allowed` | List of permitted values                            |
| `pattern` | Python `re.fullmatch` pattern the value must satisfy|

## CLI Usage

### Validate a file

```bash
envault schema check .env schema.json
```

Exits with code `1` if any errors are found.

#### JSON output

```bash
envault schema check .env schema.json --json-output
```

### Generate a starter schema

Bootstrap a schema from an existing `.env` file:

```bash
envault schema init .env schema.json
```

This creates a schema with all keys marked as `required` and typed as `string`. Edit the output to refine types and add rules.

## Python API

```python
from pathlib import Path
from envault.env_schema import validate_schema

result = validate_schema(Path(".env"), Path("schema.json"))
if not result.valid:
    for issue in result.issues:
        print(f"[{issue.severity.upper()}] {issue.key}: {issue.message}")
```
