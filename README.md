# envault

> CLI tool for encrypting and syncing .env files across team members securely

---

## Installation

```bash
pip install envault
```

---

## Usage

Initialize envault in your project and share encrypted `.env` files with your team without exposing secrets.

```bash
# Initialize envault in your project
envault init

# Encrypt your .env file
envault encrypt .env --output .env.vault

# Decrypt a received vault file
envault decrypt .env.vault --output .env

# Sync with a remote store (e.g., S3 or shared endpoint)
envault push .env.vault
envault pull .env.vault
```

Team members with the shared key can decrypt and use the file locally:

```bash
envault decrypt .env.vault --key $ENVAULT_SECRET_KEY
```

---

## How It Works

- Uses AES-256 encryption to secure your `.env` files
- Each project gets a unique encryption key
- Share the key securely (e.g., via a password manager) — never commit it
- The `.env.vault` file is safe to commit to version control

---

## .gitignore Recommendation

```
.env
.envault.key
```

```
.env.vault   # safe to commit
```

---

## License

MIT © [envault contributors](https://github.com/yourname/envault)