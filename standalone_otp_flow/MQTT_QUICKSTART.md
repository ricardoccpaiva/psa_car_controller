# PSA MQTT Connection - Quick Start Guide

This guide shows you how to connect to the PSA MQTT server and control your vehicle remotely.

## Overview

To send commands to your PSA vehicle, you need:

1. **OAuth Access Token** (you already have this)
2. **OTP Code** (from the OTP flow)
3. **Remote Access Token** (exchange OTP for this)
4. **MQTT Connection** (authenticate with remote token)

## Prerequisites

```bash
# Install required packages
pip install paho-mqtt requests pycryptodomex
```

## What You Need

Gather this information before starting:

- **Client ID**: Your PSA API client ID
- **Customer ID**: Your PSA customer ID (format: `AP-XXXXXX` for Peugeot, `AC-XXXXXX` for Citroën, etc.)
- **Realm**: Your brand realm (e.g., `clientsB2CPeugeot`, `clientsB2CCitroen`)
- **VIN**: Your vehicle identification number
- **OAuth Access Token**: The access token you already have
- **OAuth Refresh Token**: To refresh the OAuth token when needed

## Architecture

```
┌─────────────┐
│ OAuth Token │  (You have this)
└──────┬──────┘
       │
       │ 1. Use to call PSA APIs
       ▼
┌─────────────────┐
│   OTP Session   │
│   (otp.bin)     │
└──────┬──────────┘
       │
       │ 2. Generate OTP code
       ▼
┌─────────────────┐
│   OTP Code      │  (6 characters: e.g., "a3k9m2")
└──────┬──────────┘
       │
       │ 3. Exchange for remote token
       ▼
┌─────────────────────┐
│ Remote Access Token │  (For MQTT auth)
└──────┬──────────────┘
       │
       │ 4. Authenticate MQTT
       ▼
┌─────────────────────┐
│   MQTT Connection   │
│   mwa.mpsa.com:8885 │
└──────┬──────────────┘
       │
       │ 5. Send commands
       ▼
┌─────────────────────┐
│   Your Vehicle      │
└─────────────────────┘
```

## Step-by-Step Guide

### Step 1: Setup OTP Session (One-time)

If you haven't already set up your OTP session:

```bash
# Run OTP setup
python example_usage.py setup

# You'll need:
# - SMS code (request via PSA mobile app)
# - PIN code (choose a numeric PIN)
```

This creates `otp.bin` which stores your OTP session.

### Step 2: Generate OTP Code

```bash
# Generate an OTP code
python example_usage.py generate
```

Or programmatically:

```python
from otp import load_otp

# Load OTP session
otp_session = load_otp("otp.bin")

# Generate OTP code
otp_code = otp_session.get_otp_code()
print(f"OTP Code: {otp_code}")
```

### Step 3: Get Remote Access Token

The remote access token is different from your OAuth access token. You need it for MQTT authentication.

```python
import requests

# Your OAuth access token
oauth_access_token = "YOUR_OAUTH_ACCESS_TOKEN"
client_id = "YOUR_CLIENT_ID"
realm = "clientsB2CPeugeot"  # or your brand
otp_code = "a3k9m2"  # from Step 2

# Exchange OTP for remote token
url = f"https://api.groupe-psa.com/connectedcar/v4/virtualkey/remoteaccess/token?client_id={client_id}"
headers = {
    "Authorization": f"Bearer {oauth_access_token}",
    "x-introspect-realm": realm,
    "accept": "application/hal+json",
    "User-Agent": "okhttp/4.8.0",
}
payload = {
    "grant_type": "password",
    "password": otp_code  # OTP code here
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()

remote_access_token = data["access_token"]
remote_refresh_token = data["refresh_token"]

print(f"Remote Access Token: {remote_access_token}")
```

### Step 4: Connect to MQTT

```python
import paho.mqtt.client as mqtt

# MQTT configuration
MQTT_SERVER = "mwa.mpsa.com"
MQTT_PORT = 8885

# Your info
mqtt_customer_id = "AP123456"  # Your MQTT customer ID
vin = "VF3XXXXXXXX"  # Your vehicle VIN

# Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

    # Subscribe to topics
    client.subscribe(f"psa/RemoteServices/to/cid/{mqtt_customer_id}/#")
    client.subscribe(f"psa/RemoteServices/events/MPHRTServices/{vin}")

def on_message(client, userdata, msg):
    print(f"Message: {msg.topic} - {msg.payload.decode()}")

# Create MQTT client
client = mqtt.Client(clean_session=True, protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

# Authenticate (username is ALWAYS "IMA_OAUTH_ACCESS_TOKEN")
client.username_pw_set("IMA_OAUTH_ACCESS_TOKEN", remote_access_token)

# Enable TLS
client.tls_set()

# Connect
client.connect(MQTT_SERVER, MQTT_PORT, 60)

# Start loop
client.loop_start()
```

### Step 5: Send Commands

```python
import json
from datetime import datetime
from uuid import uuid4

def send_command(client, mqtt_customer_id, vin, remote_access_token, command, parameters):
    """
    Send command to vehicle

    Args:
        command: e.g., "/VehCharge", "/Doors", "/Horn"
        parameters: command-specific parameters
    """
    # Build topic
    topic = f"psa/RemoteServices/from/cid/{mqtt_customer_id}{command}"

    # Build message
    message = {
        "access_token": remote_access_token,
        "customer_id": mqtt_customer_id,
        "correlation_id": str(uuid4()).replace("-", "") + datetime.utcnow().strftime("%Y%m%d%H%M%S%f")[:-3],
        "req_date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "vin": vin,
        "req_parameters": parameters
    }

    # Publish
    client.publish(topic, json.dumps(message))
    print(f"Command sent: {command}")

# Example: Start charging
send_command(
    client,
    mqtt_customer_id,
    vin,
    remote_access_token,
    "/VehCharge",
    {"program": {"hour": 0, "minute": 0}, "type": "immediate"}
)

# Example: Lock doors
send_command(
    client,
    mqtt_customer_id,
    vin,
    remote_access_token,
    "/Doors",
    {"action": "lock"}
)

# Example: Horn
send_command(
    client,
    mqtt_customer_id,
    vin,
    remote_access_token,
    "/Horn",
    {"nb_horn": 3, "action": "activate"}
)
```

## Using the Complete Example Script

We've created a complete example script that handles everything:

```bash
python mqtt_connection_example.py
```

This script will:
1. Ask for your configuration
2. Generate OTP code (if you have otp.bin)
3. Get remote access token
4. Connect to MQTT
5. Let you send commands interactively

## Available Commands

### Charging

```python
# Start charging now
parameters = {
    "program": {"hour": 0, "minute": 0},
    "type": "immediate"
}
send_command(client, mqtt_customer_id, vin, token, "/VehCharge", parameters)

# Delayed charging (e.g., 23:30)
parameters = {
    "program": {"hour": 23, "minute": 30},
    "type": "delayed"
}
send_command(client, mqtt_customer_id, vin, token, "/VehCharge", parameters)
```

### Doors

```python
# Lock doors
send_command(client, mqtt_customer_id, vin, token, "/Doors", {"action": "lock"})

# Unlock doors
send_command(client, mqtt_customer_id, vin, token, "/Doors", {"action": "unlock"})
```

### Horn and Lights

```python
# Horn (3 beeps)
send_command(client, mqtt_customer_id, vin, token, "/Horn", {
    "nb_horn": 3,
    "action": "activate"
})

# Lights (60 seconds)
send_command(client, mqtt_customer_id, vin, token, "/Lights", {
    "action": "activate",
    "duration": 60
})
```

### Preconditioning

```python
# Activate climate control
parameters = {
    "asap": "activate",
    "programs": {
        "program1": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
        "program2": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
        "program3": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
        "program4": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0}
    }
}
send_command(client, mqtt_customer_id, vin, token, "/ThermalPrecond", parameters)
```

### Wakeup (Get Status)

```python
# Wake up vehicle and get charge status
send_command(client, mqtt_customer_id, vin, token, "/VehCharge/state", {
    "action": "state"
})
```

## MQTT Topics

### Publish (Send Commands)

```
psa/RemoteServices/from/cid/{MQTT_CUSTOMER_ID}{COMMAND}
```

Examples:
- `psa/RemoteServices/from/cid/AP123456/VehCharge`
- `psa/RemoteServices/from/cid/AP123456/Doors`

### Subscribe (Receive Responses)

```
psa/RemoteServices/to/cid/{MQTT_CUSTOMER_ID}/#
psa/RemoteServices/events/MPHRTServices/{VIN}
```

## Response Codes

When you receive a message, check the `return_code`:

- **"0"**: Success
- **"400"**: Token expired (need to refresh)
- **Other**: Error (check `reason` field)

Example response:

```json
{
  "return_code": "0",
  "correlation_id": "...",
  "resp_date": "2025-12-20T20:30:00Z"
}
```

## Token Refresh

### OAuth Token Refresh

```python
# Refresh OAuth access token
response = requests.post(
    "https://idpcvs.peugeot.com/am/oauth2/access_token",  # or your brand
    data={
        "grant_type": "refresh_token",
        "refresh_token": oauth_refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }
)
new_oauth_token = response.json()["access_token"]
```

### Remote Token Refresh

```python
# Refresh remote access token (valid for ~15 minutes)
response = requests.post(
    f"https://api.groupe-psa.com/connectedcar/v4/virtualkey/remoteaccess/token?client_id={client_id}",
    json={
        "grant_type": "refresh_token",
        "refresh_token": remote_refresh_token
    },
    headers={
        "Authorization": f"Bearer {oauth_access_token}",
        "x-introspect-realm": realm,
        "accept": "application/hal+json"
    }
)
new_remote_token = response.json()["access_token"]

# Update MQTT credentials
mqtt_client.username_pw_set("IMA_OAUTH_ACCESS_TOKEN", new_remote_token)
```

## Troubleshooting

### Connection refused

- Check that you're using port **8885** (not 8883)
- Ensure TLS is enabled: `client.tls_set()`

### Authentication failed

- Verify you're using the **remote access token**, not the OAuth token
- Username must be exactly: `IMA_OAUTH_ACCESS_TOKEN`
- Check token hasn't expired (valid for ~15 minutes)

### Commands not working

- Ensure you're subscribed to response topics
- Check `return_code` in responses
- Verify VIN is correct
- Make sure vehicle is connected to network

### OTP errors

- OTP codes expire quickly (use within 1-2 minutes)
- Limit: 6 OTP codes per 24 hours
- Check `otp.bin` exists and is valid

## Rate Limits

- **OTP codes**: 6 per 24 hours (PSA server-side)
- **Wakeup command**: 6 per 20 minutes
- **Other commands**: Generally no strict limits, but avoid spam

## Security Notes

1. **Never share tokens**: Keep access tokens secure
2. **Token expiration**:
   - OAuth token: Typically 1 hour
   - Remote token: ~15 minutes
3. **Use refresh tokens**: Don't request new OTP codes unnecessarily
4. **Secure storage**: Store `otp.bin` safely (contains encryption keys)

## Complete Example

See `mqtt_connection_example.py` for a complete working example with:
- OTP integration
- Token management
- MQTT connection
- Command interface
- Error handling

Run it:

```bash
python mqtt_connection_example.py
```

## Next Steps

1. Set up OTP session (if not done): `python example_usage.py setup`
2. Test MQTT connection: `python mqtt_connection_example.py`
3. Integrate into your own application
4. Set up token refresh automation
5. Handle MQTT reconnection

## References

- **MQTT Server**: `mwa.mpsa.com:8885` (TLS required)
- **Remote Token API**: `https://api.groupe-psa.com/connectedcar/v4/virtualkey/remoteaccess/token`
- **MQTT Username**: Always `IMA_OAUTH_ACCESS_TOKEN`
- **MQTT Password**: Your remote access token

For more details, see the main PSA Car Controller documentation.
