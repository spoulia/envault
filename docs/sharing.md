# Vault Sharing

envault lets you securely share encrypted `.env` files with teammates via **bundles** — self-contained JSON files that wrap the vault in an additional encryption layer.

## How it works

1. One team member **locks** their `.env` file into a `.env.vault`.
2. They **export** the vault as a shareable bundle (re-encrypted with the shared team password).
3. The bundle is distributed (Slack, email, shared drive, etc.).
4. Recipients **import** the bundle to obtain their own local `.env.vault`.
5. They then **unlock** the vault using the team password to get the plain `.env`.

## Commands

### Export a bundle

```bash
envault share export .env.vault \
  --password <team-password> \
  --recipient alice@example.com \
  --output vault_bundle.json
```

| Option | Default | Description |
|---|---|---|
| `--password` | prompted | Encryption password |
| `--recipient` | *(empty)* | Optional hint for the recipient |
| `--output` | `vault_bundle.json` | Output file path |

### Import a bundle

```bash
envault share import vault_bundle.json \
  --password <team-password> \
  --output .env.vault
```

| Option | Default | Description |
|---|---|---|
| `--password` | prompted | Decryption password |
| `--output` | `.env.vault` | Destination vault file |

### Verify a bundle

Before importing, you can verify that a bundle is intact and was encrypted with the correct password without writing any files:

```bash
envault share verify vault_bundle.json --password <team-password>
```

This is useful for confirming the right password before distributing a bundle to teammates.

## Security notes

- Bundles use the same AES-256-GCM encryption as the vault itself.
- The team password is **never** stored in the bundle.
- Distribute the password through a separate secure channel (e.g. a secrets manager).
- Treat bundle files as sensitive — while encrypted, they should not be committed to version control.
