#!/usr/bin/env python3
"""
Get Remote Access Token for MQTT

This script:
1. Calls your local OTP API to generate an OTP code
2. Exchanges the OTP code for a remote access token
3. Shows you what to put in the MQTT password field

Prerequisites:
- OTP API running: python psa_otp_api/app.py
- Valid OAuth access token
- OTP session already set up (via /otp/setup endpoint)
"""

import sys
import requests
import json

def get_otp_code(api_url="http://localhost:5000"):
    """Generate OTP code from local API"""
    print("📱 Step 1: Generating OTP code from local API...")

    try:
        response = requests.post(f"{api_url}/otp/generate", json={})

        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                otp_code = data["otp_code"]
                print(f"   ✓ Generated OTP code: {otp_code}")
                return otp_code
            else:
                print(f"   ✗ API error: {data.get('error', 'Unknown error')}")
                return None
        else:
            print(f"   ✗ HTTP {response.status_code}: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print("   ✗ Cannot connect to OTP API at", api_url)
        print("   ℹ  Make sure the API is running: python psa_otp_api/app.py")
        return None
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None


def exchange_otp_for_remote_token(otp_code, oauth_token, client_id, realm):
    """Exchange OTP code for remote access token"""
    print("\n🔐 Step 2: Exchanging OTP for remote access token...")

    url = "https://api.groupe-psa.com/connectedcar/v4/virtualkey"

    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "x-introspect-realm": realm,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "otp": otp_code,
        "client_id": client_id
    }

    print(f"   Calling: POST {url}")
    print(f"   Realm: {realm}")
    print(f"   Client ID: {client_id}")

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                token = data["access_token"]
                expires_in = data.get("expires_at", "unknown")
                print(f"   ✓ Got remote access token!")
                print(f"   ℹ  Expires: {expires_in}")
                return token
            else:
                print(f"   ✗ No access_token in response: {data}")
                return None
        else:
            print(f"   ✗ HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   ℹ  Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   ℹ  Response: {response.text}")
            return None

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None


def main():
    print("=" * 70)
    print("PSA MQTT Remote Access Token Generator")
    print("=" * 70)

    # Get inputs
    if len(sys.argv) < 4:
        print("\n❌ Usage: python get_remote_token_for_mqtt.py <oauth_token> <client_id> <realm>")
        print("\nExample:")
        print("  python get_remote_token_for_mqtt.py \\")
        print("    'eyJhbGc...' \\")
        print("    'APACNT200001549013' \\")
        print("    'clientsB2CPeugeot'")
        print("\nRealm values:")
        print("  - clientsB2CPeugeot")
        print("  - clientsB2CCitroen")
        print("  - clientsB2CDS")
        print("  - clientsB2COpel")
        print("  - clientsB2CVauxhall")
        print("\n💡 Tip: Your client ID is in the MQTT Client ID field")
        sys.exit(1)

    oauth_token = sys.argv[1]
    client_id = sys.argv[2]
    realm = sys.argv[3]

    print(f"\n📋 Configuration:")
    print(f"   OAuth Token: {oauth_token[:20]}...")
    print(f"   Client ID: {client_id}")
    print(f"   Realm: {realm}")
    print()

    # Step 1: Get OTP code from local API
    otp_code = get_otp_code()
    if not otp_code:
        print("\n❌ Failed to generate OTP code")
        print("\n📝 Troubleshooting:")
        print("   1. Make sure OTP API is running: python psa_otp_api/app.py")
        print("   2. Make sure you ran setup first: curl -X POST http://localhost:5000/otp/setup ...")
        print("   3. Check API logs for errors")
        sys.exit(1)

    # Step 2: Exchange OTP for remote token
    remote_token = exchange_otp_for_remote_token(otp_code, oauth_token, client_id, realm)
    if not remote_token:
        print("\n❌ Failed to get remote access token")
        print("\n📝 Troubleshooting:")
        print("   1. Check OAuth token is valid and not expired")
        print("   2. Verify client_id matches your account")
        print("   3. Verify realm is correct for your brand")
        sys.exit(1)

    # Success!
    print("\n" + "=" * 70)
    print("✅ SUCCESS! Use this in your MQTT client:")
    print("=" * 70)
    print()
    print("MQTT Connection Settings:")
    print("  Host:        mwa.mpsa.com")
    print("  Port:        8885")
    print("  Client ID:   " + client_id)
    print("  Username:    IMA_OAUTH_ACCESS_TOKEN")
    print("  Password:    " + remote_token)
    print("  SSL/TLS:     Enabled (CA signed server certificate)")
    print()
    print("🔑 Remote Access Token (copy to Password field):")
    print("─" * 70)
    print(remote_token)
    print("─" * 70)
    print()
    print("⏰ Note: This token will expire. Generate a new one if connection fails.")
    print()


if __name__ == "__main__":
    main()
