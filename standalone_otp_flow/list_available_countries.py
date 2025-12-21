#!/usr/bin/env python3
"""
List available country codes in PSA APK

Shows which country codes are supported by each brand's APK.
"""

import sys
import json
import os

try:
    from androguard.core.apk import APK
except ModuleNotFoundError:
    print("✗ Missing androguard")
    print("  pip install androguard")
    sys.exit(1)

BRANDS = {
    "1": ("Peugeot", "mypeugeot.apk"),
    "2": ("Citroën", "mycitroen.apk"),
    "3": ("DS", "myds.apk"),
    "4": ("Opel", "myopel.apk"),
    "5": ("Vauxhall", "myvauxhall.apk")
}

def list_cultures(apk_file):
    """List available cultures in APK"""
    if not os.path.exists(apk_file):
        print(f"✗ APK not found: {apk_file}")
        print(f"  Run extract_customer_id_from_apk.py first to download it")
        return

    print(f"\nAnalyzing: {apk_file}")

    try:
        apk = APK(apk_file)
        cultures_json = apk.get_file("res/raw/cultures.json")
        cultures = json.loads(cultures_json)

        print(f"\n{'='*60}")
        print(f"Available Country Codes ({len(cultures)} total)")
        print(f"{'='*60}\n")

        for country_code, info in sorted(cultures.items()):
            languages = info.get("languages", [])
            print(f"  {country_code:3s} - Languages: {', '.join(languages)}")

        print()

    except Exception as e:
        print(f"✗ Error: {e}")

def main():
    print("="*60)
    print("  PSA APK - Available Country Codes")
    print("="*60)

    print("\nSelect brand to check:")
    for key, (name, _) in BRANDS.items():
        print(f"  {key}. {name}")

    choice = input("\nEnter number (1-5): ").strip()

    if choice not in BRANDS:
        print("✗ Invalid choice")
        return 1

    brand_name, apk_file = BRANDS[choice]
    list_cultures(apk_file)

    return 0

if __name__ == "__main__":
    sys.exit(main())
