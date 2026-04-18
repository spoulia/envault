# Vault Tagging

envault supports tagging vault files to help organise and discover them across projects.

## Commands

### Add a tag
```bash
envault tags add <vault> <tag>
```
Example:
```bash
envault tags add .env.vault production
```

### Remove a tag
```bash
envault tags remove <vault> <tag>
```

### List tags for a vault
```bash
envault tags list <vault>
```

### Find vaults by tag
```bash
envault tags find <tag>
```
Returns all vault paths that carry the given tag.

### Clear all tags from a vault
```bash
envault tags clear <vault>
```

## Storage

Tags are stored locally in `.envault_tags.json` in the working directory. This file should be added to `.gitignore` or committed depending on your team's workflow.

## Use Cases

- Mark vaults as `production`, `staging`, or `development`
- Group vaults by service: `backend`, `frontend`, `infra`
- Quickly find all vaults relevant to a deployment target
