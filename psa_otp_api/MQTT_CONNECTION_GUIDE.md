# MQTT Connection Guide

This guide shows you exactly how to connect to the PSA MQTT server using your MQTT client.

## Problem: "Connection refused: Identifier rejected"

This error means your MQTT password (remote access token) is invalid or expired.

## Solution: Get a Fresh Remote Access Token

### Prerequisites

1. **OTP API running**
   ```bash
   cd psa_otp_api
   python app.py
   ```
   Server should be running at `http://localhost:5000`

2. **OTP session set up**
   ```bash
   curl -X POST http://localhost:5000/otp/setup \
     -H "Content-Type: application/json" \
     -d '{"sms_code":"123456","pin_code":"1234"}'
   ```

3. **You have these values:**
   - OAuth access token (from PSA authentication)
   - Client ID (same as MQTT Client ID, e.g., `APACNT200001549013`)
   - Realm (your brand, e.g., `clientsB2CPeugeot`)

### Step-by-Step

1. **Run the helper script:**
   ```bash
   cd /home/user/psa_car_controller

   python get_remote_token_for_mqtt.py \
     'YOUR_OAUTH_ACCESS_TOKEN' \
     'YOUR_CLIENT_ID' \
     'YOUR_REALM'
   ```

   Example:
   ```bash
   python get_remote_token_for_mqtt.py \
     'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...' \
     'APACNT200001549013' \
     'clientsB2CPeugeot'
   ```

2. **The script will:**
   - ✅ Generate an OTP code from your local API
   - ✅ Exchange it for a remote access token
   - ✅ Show you the exact token to use

3. **Copy the remote access token** from the output

4. **Put it in your MQTT client:**
   ```
   Host:        mwa.mpsa.com
   Port:        8885
   Client ID:   APACNT200001549013    (your actual client ID)
   Username:    IMA_OAUTH_ACCESS_TOKEN    (literal string, don't change)
   Password:    eyJhbGc...              (the remote access token)
   SSL/TLS:     ✅ Enabled (CA signed server certificate)
   ```

5. **Connect!**

## Your Exact Values

Based on your screenshot, you should use:

```
Host:        mwa.mpsa.com
Port:        8885
Client ID:   APACNT200001549013
Username:    IMA_OAUTH_ACCESS_TOKEN
Password:    <USE THE TOKEN FROM THE SCRIPT>
SSL/TLS:     ✅ Enabled
```

## Finding Your Values

### OAuth Access Token

If you used the APK extraction script:
```bash
python extract_customer_id_from_apk.py
```
The script prints your access token after authentication.

Or authenticate directly:
```bash
curl -X POST https://idpcvs.peugeot.com/am/oauth2/access_token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=YOUR_EMAIL&password=YOUR_PASSWORD&client_id=YOUR_CLIENT_ID"
```

### Client ID

This is the same as your MQTT Client ID. You already have it: `APACNT200001549013`

### Realm

Based on your brand:
- Peugeot: `clientsB2CPeugeot`
- Citroën: `clientsB2CCitroen`
- DS: `clientsB2CDS`
- Opel: `clientsB2COpel`
- Vauxhall: `clientsB2CVauxhall`

## Common Issues

### "Connection refused: Identifier rejected"
- ❌ Password is wrong/expired → Run the script again to get a fresh token
- ❌ Username is wrong → Must be exactly `IMA_OAUTH_ACCESS_TOKEN`

### "Session file not found"
- Run OTP setup first: `curl -X POST http://localhost:5000/otp/setup ...`

### "Cannot connect to OTP API"
- Start the API: `python psa_otp_api/app.py`

### "No access_token in response"
- OAuth token expired → Get a fresh one
- Wrong realm → Check your brand
- Wrong client ID → Use the one from your account

## Rate Limits

⚠️ **PSA allows only 6 OTP codes per 24 hours**

Each time you run the script, it uses one OTP code. Don't run it too many times!

## Token Expiration

Remote access tokens expire after some time. If your MQTT connection suddenly drops, generate a new token using the script.

## Testing the Connection

Once connected, subscribe to your vehicle topics:
```
psa/RemoteServices/from/cid/VIN/xxx
psa/RemoteServices/events/MPHRTServices/VIN/xxx
```

Replace `VIN` with your vehicle's VIN number.

## Quick Reference

```bash
# 1. Start OTP API
python psa_otp_api/app.py

# 2. Setup OTP session (only needed once)
curl -X POST http://localhost:5000/otp/setup \
  -H "Content-Type: application/json" \
  -d '{"sms_code":"123456","pin_code":"1234"}'

# 3. Get remote token for MQTT
python get_remote_token_for_mqtt.py \
  'YOUR_OAUTH_TOKEN' \
  'YOUR_CLIENT_ID' \
  'YOUR_REALM'

# 4. Copy the token to MQTT password field
# 5. Connect!
```

## Need Help?

If you're still getting "Identifier rejected":
1. Double-check username is exactly: `IMA_OAUTH_ACCESS_TOKEN`
2. Make sure you copied the ENTIRE token (they're very long)
3. Verify your OAuth token hasn't expired
4. Try generating a fresh OAuth token first
