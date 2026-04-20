# env_scope – Deployment Scope Tagging

Assign deployment scopes (`dev`, `staging`, `prod`) to individual `.env` keys so
you know which environments each variable belongs to.

## Supported scopes

| Scope     | Description              |
|-----------|--------------------------|
| `dev`     | Local development only   |
| `staging` | Staging / QA environment |
| `prod`    | Production environment   |

## CLI usage

### Assign scopes to a key

```bash
envault scope add DB_URL prod staging
```

### Remove a scope from a key

```bash
envault scope remove DB_URL staging
```

### Show scopes for a key

```bash
envault scope show DB_URL
# DB_URL: prod
```

### List all scope assignments

```bash
envault scope list
#   DB_URL: prod
#   DEBUG: dev
#   SECRET_KEY: dev, staging, prod
```

### Find all keys for a scope

```bash
envault scope find prod
#   DB_URL
#   SECRET_KEY
```

## Python API

```python
from envault.env_scope import assign_scope, get_scope, keys_for_scope

# Assign scopes
assign_scope("DB_URL", ["prod"])

# Query
result = get_scope("DB_URL")
print(result.scopes)  # ['prod']

# Find by scope
keys = keys_for_scope("prod")
```

## Storage

Scope assignments are stored in `.envault_scopes.json` in the current directory.
Add this file to version control to share scope metadata with your team.

```json
{
  "DB_URL": ["prod"],
  "DEBUG": ["dev"]
}
```
