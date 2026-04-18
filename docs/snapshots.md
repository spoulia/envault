# Vault Snapshots

Snapshots let you save a named copy of your encrypted vault at any point in time and restore it later.

## Commands

### Save a snapshot

```bash
envault snapshots save <name> [--vault .env.vault] [--desc "description"]
```

Creates a named snapshot of the specified vault file.

**Example:**
```bash
envault snapshots save before-deploy --desc "pre-deployment state"
```

### Restore a snapshot

```bash
envault snapshots restore <name> [--vault .env.vault]
```

Restores the vault file from the named snapshot.

**Example:**
```bash
envault snapshots restore before-deploy
```

### Delete a snapshot

```bash
envault snapshots delete <name>
```

### List all snapshots

```bash
envault snapshots list
```

Outputs all saved snapshots with their descriptions and timestamps.

## Storage

Snapshots are stored in `.envault_snapshots/` in the project directory. Add this folder to `.gitignore` if you do not want snapshots committed, or commit it to share snapshots with your team.

## Notes

- Snapshot names must be unique. Use `delete` before re-saving under the same name.
- Snapshots store the raw encrypted vault bytes — the password is never stored.
- Restoring a snapshot overwrites the target vault file.
