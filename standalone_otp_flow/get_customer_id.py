#!/usr/bin/env python3
"""
Get PSA Customer ID

This script retrieves your PSA customer ID using your OAuth access token.

Usage:
    python get_customer_id.py

Requirements:
    pip install requests
"""

import sys
import json

try:
    import requests
except ModuleNotFoundError:
    print("✗ Missing dependency: requests")
    print("\nInstall it:")
    print("  pip install requests")
    sys.exit(1)

# PSA API endpoints
USER_INFO_URL = "https://api.groupe-psa.com/connectedcar/v4/user"
VEHICLES_URL = "https://api.groupe-psa.com/connectedcar/v4/user/vehicles"

# Brand/realm info
REALMS = {
    "1": ("clientsB2CPeugeot", "Peugeot"),
    "2": ("clientsB2CCitroen", "Citroën"),
    "3": ("clientsB2CDS", "DS"),
    "4": ("clientsB2COpel", "Opel"),
    "5": ("clientsB2CVauxhall", "Vauxhall")
}


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def get_user_info(client_id, realm, access_token):
    """
    Get user information from PSA API

    Returns:
        dict with user info, or None on error
    """
    print("Fetching user information...")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-introspect-realm": realm,
        "accept": "application/hal+json",
    }
    params = {
        "client_id": client_id
    }

    try:
        response = requests.get(USER_INFO_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"✗ Failed to get user info: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def get_vehicles(client_id, realm, access_token):
    """
    Get vehicles list from PSA API

    Returns:
        dict with vehicles info, or None on error
    """
    print("Fetching vehicles information...")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-introspect-realm": realm,
        "accept": "application/hal+json",
    }
    params = {
        "client_id": client_id
    }

    try:
        response = requests.get(VEHICLES_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"✗ Failed to get vehicles: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def main():
    """Main program"""
    print_header("PSA Customer ID Retrieval")

    print("This script will retrieve your PSA customer ID using your OAuth token.\n")

    # Get inputs
    print("Select your brand:")
    for key, (realm, name) in REALMS.items():
        print(f"  {key}. {name}")

    brand_choice = input("\nEnter number (1-5): ").strip()

    if brand_choice not in REALMS:
        print("✗ Invalid choice")
        return 1

    realm, brand_name = REALMS[brand_choice]
    print(f"✓ Selected: {brand_name} ({realm})\n")

    client_id = input("Enter your client ID: ").strip()
    if not client_id:
        print("✗ Client ID is required")
        return 1

    access_token = input("Enter your OAuth access token: ").strip()
    if not access_token:
        print("✗ Access token is required")
        return 1

    print()

    # Get user info
    user_info = get_user_info(client_id, realm, access_token)

    if user_info:
        print("\n" + "=" * 70)
        print("USER INFORMATION")
        print("=" * 70)
        print(json.dumps(user_info, indent=2))

        # Extract customer ID if available
        if "id" in user_info:
            customer_id = user_info["id"]
            print("\n" + "=" * 70)
            print("✓ CUSTOMER ID FOUND")
            print("=" * 70)
            print(f"\nCustomer ID: {customer_id}")
            print(f"MQTT Customer ID: {customer_id.replace('-', '')}")
            print()
        else:
            print("\n⚠ Customer ID not found in user info")

    # Get vehicles info
    print("\n")
    vehicles_info = get_vehicles(client_id, realm, access_token)

    if vehicles_info:
        print("\n" + "=" * 70)
        print("VEHICLES INFORMATION")
        print("=" * 70)
        print(json.dumps(vehicles_info, indent=2))

        # Extract VINs
        if "_embedded" in vehicles_info and "vehicles" in vehicles_info["_embedded"]:
            vins = [v.get("vin") for v in vehicles_info["_embedded"]["vehicles"] if "vin" in v]
            if vins:
                print("\n" + "=" * 70)
                print("✓ VEHICLE VIN(S) FOUND")
                print("=" * 70)
                for i, vin in enumerate(vins, 1):
                    print(f"{i}. {vin}")
                print()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if user_info and "id" in user_info:
        customer_id = user_info["id"]
        mqtt_customer_id = customer_id.replace('-', '')

        print(f"\nRealm: {realm}")
        print(f"Customer ID: {customer_id}")
        print(f"MQTT Customer ID: {mqtt_customer_id}")

        if vehicles_info and "_embedded" in vehicles_info:
            vehicles = vehicles_info["_embedded"].get("vehicles", [])
            if vehicles:
                print(f"\nVehicles found: {len(vehicles)}")
                for i, vehicle in enumerate(vehicles, 1):
                    vin = vehicle.get("vin", "N/A")
                    label = vehicle.get("label", "Unknown")
                    print(f"  {i}. {label} - VIN: {vin}")

        print("\n✓ You can now use these values for MQTT connection!")
        print("\nFor standalone_mqtt.py, use:")
        print(f"  - Customer ID: {customer_id}")
        print(f"  - Realm: {realm}")
        if vehicles_info and "_embedded" in vehicles_info:
            vehicles = vehicles_info["_embedded"].get("vehicles", [])
            if vehicles and "vin" in vehicles[0]:
                print(f"  - VIN: {vehicles[0]['vin']}")
    else:
        print("\n✗ Could not retrieve customer ID")
        print("\nTroubleshooting:")
        print("  1. Check that your access token is valid")
        print("  2. Make sure you selected the correct brand")
        print("  3. Verify your client ID is correct")
        print("  4. Try refreshing your OAuth token")

    print()
    return 0


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
