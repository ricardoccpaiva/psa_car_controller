#!/usr/bin/env python3
"""
Extract Customer ID from PSA Mobile App APK

This script downloads the PSA mobile app APK and extracts the customer ID.

Requirements:
    pip install androguard cryptography requests

Usage:
    python extract_customer_id_from_apk.py
"""

import sys
import json
import bz2
import os
from pathlib import Path

try:
    import requests
    from androguard.core.apk import APK
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.serialization import pkcs12
except ModuleNotFoundError as e:
    print(f"✗ Missing dependency: {e.name}")
    print("\nInstall dependencies:")
    print("  pip install androguard cryptography requests")
    sys.exit(1)

# Constants
GITHUB_USER = "flobz"
GITHUB_REPO = "psa_apk"
TIMEOUT = 10

BRANDS = {
    "1": ("Peugeot", "mypeugeot.apk", "AP", "clientsB2CPeugeot", "com.psa.mym.mypeugeot"),
    "2": ("Citroën", "mycitroen.apk", "AC", "clientsB2CCitroen", "com.psa.mym.mycitroen"),
    "3": ("DS", "myds.apk", "DS", "clientsB2CDS", "com.psa.mym.myds"),
    "4": ("Opel", "myopel.apk", "OP", "clientsB2COpel", "com.psa.mym.myopel"),
    "5": ("Vauxhall", "myvauxhall.apk", "VX", "clientsB2CVauxhall", "com.psa.mym.myvauxhall")
}


def download_apk(filename):
    """Download APK from GitHub"""
    archive_name = filename + ".bz2"

    if os.path.exists(filename):
        print(f"✓ APK already exists: {filename}")
        return filename

    print(f"Downloading {archive_name} from GitHub...")

    url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/raw/main/{archive_name}"

    try:
        response = requests.get(url, stream=True, timeout=TIMEOUT)
        response.raise_for_status()

        # Save compressed file
        with open(archive_name, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        print(f"✓ Downloaded {archive_name}")

        # Decompress
        print(f"Decompressing...")
        with bz2.BZ2File(archive_name, 'rb') as bz_file:
            with open(filename, 'wb') as out_file:
                out_file.write(bz_file.read())

        print(f"✓ Extracted {filename}")

        # Clean up compressed file
        os.remove(archive_name)

        return filename

    except Exception as e:
        print(f"✗ Download failed: {e}")
        return None


def extract_certificates(apk_obj):
    """Extract certificates from APK"""
    try:
        pfx_cert = apk_obj.get_file("assets/MWPMYMA1.pfx")
        pfx_password = b"y5Y2my5B"

        private_key, certificate = pkcs12.load_key_and_certificates(
            pfx_cert, pfx_password, default_backend()
        )[:2]

        # Create certs directory
        os.makedirs("certs", exist_ok=True)

        # Save certificates
        with open("certs/public.pem", "wb") as f:
            f.write(certificate.public_bytes(encoding=serialization.Encoding.PEM))

        with open("certs/private.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        print("✓ Certificates extracted to certs/")
        return True

    except Exception as e:
        print(f"⚠ Could not extract certificates: {e}")
        return False


def get_cultures_code(cultures_json, country_code):
    """Get culture code for country"""
    cultures = json.loads(cultures_json)
    return cultures.get(country_code, {}).get("languages", [None])[0]


def parse_apk(filename, country_code, brand_code):
    """Parse APK and extract configuration"""
    print(f"\nParsing APK: {filename}")

    try:
        apk = APK(filename)
        package_name = apk.get_package()
        resources = apk.get_android_resources()

        print(f"✓ Package: {package_name}")

        # Get host
        host_brandid_prod = resources.get_string(package_name, "HOST_BRANDID_PROD")[1]
        print(f"✓ Host: {host_brandid_prod}")

        # Get culture
        cultures_file = apk.get_file("res/raw/cultures.json")
        culture = get_cultures_code(cultures_file, country_code)
        print(f"✓ Culture: {culture}")

        # Get parameters
        language, country = culture.split("_")
        parameters_path = f"res/raw-{language}-r{country}/parameters.json"
        parameters = json.loads(apk.get_file(parameters_path))

        client_id = parameters.get("cvsClientId")
        client_secret = parameters.get("cvsSecret")

        print(f"✓ Client ID: {client_id}")
        print(f"✓ Client Secret: {client_secret[:10]}..." if client_secret else "✗ No client secret")

        # Site code
        site_code = f"{brand_code}_{country_code}_ESP"
        print(f"✓ Site Code: {site_code}")

        # Extract certificates
        extract_certificates(apk)

        return {
            "package_name": package_name,
            "host": host_brandid_prod,
            "culture": culture,
            "client_id": client_id,
            "client_secret": client_secret,
            "site_code": site_code,
            "brand_code": brand_code
        }

    except Exception as e:
        print(f"✗ Failed to parse APK: {e}")
        import traceback
        traceback.print_exc()
        return None


def authenticate_and_get_user_id(config, email, password):
    """Authenticate with PSA and get user ID"""
    print(f"\nAuthenticating with PSA...")

    url = config["host"] + "/GetAccessToken"

    payload = {
        "siteCode": config["site_code"],
        "culture": config["culture"],
        "action": "authenticate",
        "fields": {
            "USR_EMAIL": {"value": email},
            "USR_PASSWORD": {"value": password}
        }
    }

    headers = {
        "Connection": "Keep-Alive",
        "Content-Type": "application/json",
        "User-Agent": "okhttp/2.3.0"
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            params={"jsonRequest": json.dumps(payload)},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        if "accessToken" in data:
            access_token = data["accessToken"]
            print(f"✓ Access token obtained")
            return access_token
        else:
            print(f"✗ No access token in response: {data}")
            return None

    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return None


def get_user_info(config, access_token):
    """Get user info from mobile API"""
    print(f"\nFetching user info...")

    brand_code = config["brand_code"].lower()
    url = f"https://mw-{brand_code}-m2c.mym.awsmpsa.com/api/v1/user"

    headers = {
        "Connection": "Keep-Alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Source-Agent": "App-Android",
        "Token": access_token,
        "User-Agent": "okhttp/4.8.0",
        "Version": "1.48.2"
    }

    payload = {
        "site_code": config["site_code"],
        "ticket": access_token
    }

    params = {
        "culture": config["culture"],
        "width": 1080,
        "version": "1.48.2"
    }

    try:
        # Check if certificates exist
        if not (os.path.exists("certs/public.pem") and os.path.exists("certs/private.pem")):
            print("✗ Certificates not found. Cannot call mobile API.")
            return None

        response = requests.post(
            url,
            params=params,
            json=payload,
            headers=headers,
            cert=("certs/public.pem", "certs/private.pem"),
            timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        if "success" in data:
            user_info = data["success"]
            print(f"✓ User info retrieved")
            return user_info
        else:
            print(f"✗ Unexpected response: {data}")
            return None

    except Exception as e:
        print(f"✗ Failed to get user info: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main program"""
    print("=" * 70)
    print("  Extract PSA Customer ID from Mobile App APK")
    print("=" * 70)
    print()

    # Select brand
    print("Select your brand:")
    for key, (name, _, _, _, _) in BRANDS.items():
        print(f"  {key}. {name}")

    choice = input("\nEnter number (1-5): ").strip()

    if choice not in BRANDS:
        print("✗ Invalid choice")
        return 1

    brand_name, apk_file, brand_code, realm, package = BRANDS[choice]
    print(f"\n✓ Selected: {brand_name}")

    # Get country code
    country_code = input("\nEnter your country code (e.g., FR, GB, DE): ").strip().upper()

    # Download APK
    print()
    apk_path = download_apk(apk_file)
    if not apk_path:
        return 1

    # Parse APK
    config = parse_apk(apk_path, country_code, brand_code)
    if not config:
        return 1

    # Get credentials
    print("\n" + "=" * 70)
    print("PSA Account Credentials")
    print("=" * 70)
    email = input("\nEmail: ").strip()
    password = input("Password: ").strip()

    # Authenticate
    access_token = authenticate_and_get_user_id(config, email, password)
    if not access_token:
        return 1

    # Get user info
    user_info = get_user_info(config, access_token)
    if not user_info:
        print("\n⚠ Could not retrieve user ID from mobile API")
        print("\nHowever, you can use these values:")
        print(f"\n  Client ID: {config['client_id']}")
        print(f"  Client Secret: {config['client_secret']}")
        print(f"  Realm: {realm}")
        return 1

    # Extract user ID and build customer ID
    user_id = user_info.get("id")
    if user_id:
        customer_id = f"{brand_code}-{user_id}"
        mqtt_customer_id = customer_id.replace("-", "")

        print("\n" + "=" * 70)
        print("✓ SUCCESS - All Configuration Values")
        print("=" * 70)
        print(f"\nClient ID: {config['client_id']}")
        print(f"Client Secret: {config['client_secret']}")
        print(f"Realm: {realm}")
        print(f"Country Code: {country_code}")
        print(f"Customer ID: {customer_id}")
        print(f"MQTT Customer ID: {mqtt_customer_id}")

        # Show vehicles if available
        if "vehicles" in user_info and user_info["vehicles"]:
            print(f"\nVehicles ({len(user_info['vehicles'])}):")
            for i, vehicle in enumerate(user_info["vehicles"], 1):
                vin = vehicle.get("vin", "N/A")
                label = vehicle.get("short_label", "Unknown")
                print(f"  {i}. {label} - VIN: {vin}")

        print("\n✓ You can now use these values for MQTT connection!")
        print()

        return 0
    else:
        print("\n✗ Could not extract user ID from user info")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
