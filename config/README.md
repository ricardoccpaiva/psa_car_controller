# PSA Car Controller Configuration

This directory contains configuration files for PSA Car Controller.

## Files

- **config.json** - Main PSA API credentials
- **charge_config.json** - Charge control settings (optional)
- **psa_car_controller.db** - SQLite database (auto-created)

## Initial Setup

The `config.json` file is a template. To connect to your PSA account:

1. **Run the app** - It will start with the template config
2. **Access the web interface** - Go to http://localhost:5000 (or http://localhost:5173 in dev mode)
3. **Go to Settings** - Configure your PSA account via the OAuth flow
4. **Follow the setup wizard** - Enter your brand, email, and complete 2FA

The configuration will be automatically saved to this directory.

## Manual Configuration (Advanced)

If you want to configure manually, edit `config.json`:

```json
{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "remote_refresh_token": "your-refresh-token",
  "customer_id": "your-customer-id",
  "realm": "clientsB2CPeugeot"
}
```

**Note:** These credentials are obtained through the PSA OAuth flow. It's easier to use the web interface.

## Volumes

In Docker, this directory is mounted as a volume to persist:
- Configuration files
- Database
- Any other app data

## Security

⚠️ **Important:** Never commit real credentials to version control!

The `.gitignore` file excludes:
- `config.json` (except the template)
- `*.db` files
- Any files with credentials
