# env-cast

The `cast` command lets you interpret raw string values from a `.env` file as typed Python objects — useful for validation, config generation, or downstream tooling.

## Usage

```bash
envault cast run .env -r PORT:int -r DEBUG:bool -r RATIO:float
```

### Options

| Option | Description |
|--------|-------------|
| `-r KEY:TYPE` / `--rule KEY:TYPE` | Declare a casting rule. Repeatable. |
| `--json` | Print the result as a JSON object instead of human-readable lines. |

### Supported types

| Type | Example input | Python value |
|------|--------------|-------------|
| `str` | `hello` | `'hello'` |
| `int` | `8080` | `8080` |
| `float` | `3.14` | `3.14` |
| `bool` | `true` / `yes` / `1` | `True` |

For `bool`, the values `true`, `yes`, `1` (case-insensitive) map to `True`; `false`, `no`, `0` map to `False`.

## Examples

```bash
# Human-readable output
envault cast run .env -r PORT:int -r DEBUG:bool
  PORT = 8080  (int)
  DEBUG = True  (bool)
  NAME = 'myapp'  (str)

  2 key(s) not in rules — kept as str.

# JSON output (pipe-friendly)
envault cast run .env -r PORT:int --json
{
  "PORT": 8080,
  "DEBUG": "true",
  "NAME": "myapp"
}
```

## Error handling

If a value cannot be cast to the requested type, an error line is printed and the raw string value is kept in the output. The command still exits `0` so pipelines are not broken.

```
  error  PORT: invalid literal for int() with base 10: 'abc'
```
