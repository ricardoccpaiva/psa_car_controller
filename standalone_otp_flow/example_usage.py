#!/usr/bin/env python3
"""
PSA OTP Flow - End-to-End Example

This script demonstrates the complete OTP (One-Time Password) flow
for PSA vehicle authentication.

Usage:
    # First time setup
    python example_usage.py setup

    # Generate OTP code
    python example_usage.py generate

    # Interactive mode
    python example_usage.py
"""

import sys
import os
from otp import Otp, new_otp_session, load_otp, save_otp, ConfigException


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def setup_otp_session():
    """
    First-time OTP setup flow

    Steps:
    1. Request SMS code from PSA (done outside this script)
    2. User enters SMS code received
    3. User enters PIN code
    4. Activate OTP session
    5. Save session to disk
    """
    print_header("PSA OTP Setup - First Time Activation")

    print("Before running this setup, you need to:")
    print("1. Log into your PSA mobile app (MyPeugeot/MyCitroen/etc.)")
    print("2. Request an SMS code for remote access")
    print("3. Check your phone for the SMS code\n")

    # Get SMS code from user
    sms_code = input("Enter the SMS code you received: ").strip()
    if not sms_code:
        print("✗ Error: SMS code is required")
        return False

    # Get PIN code from user
    pin_code = input("Enter your PIN code (digits only): ").strip()
    if not pin_code or not pin_code.isdigit():
        print("✗ Error: PIN code must be numeric")
        return False

    print("\n⏳ Activating OTP session...")
    print("   Connecting to PSA OTP server...")

    try:
        # Create new OTP session
        otp_session = new_otp_session(sms_code, pin_code)

        if otp_session:
            # Save session to disk
            save_otp(otp_session, "otp.bin")

            print("✓ OTP session activated successfully!")
            print(f"✓ Session saved to: otp.bin")
            print(f"✓ Device ID: {otp_session.device_id}")
            print("\nYou can now generate OTP codes using: python example_usage.py generate")
            return True
        else:
            print("✗ Failed to activate OTP session")
            print("   Please check your SMS code and PIN and try again")
            return False

    except ConfigException as e:
        print(f"✗ Configuration error: {e}")
        print("   The SMS code may be invalid or expired")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def generate_otp_code():
    """
    Generate OTP code from saved session

    Steps:
    1. Load saved OTP session
    2. Request OTP from PSA server
    3. Generate and display OTP code
    4. Save updated session
    """
    print_header("PSA OTP Code Generation")

    # Check if session file exists
    if not os.path.exists("otp.bin"):
        print("✗ No saved OTP session found")
        print("   Please run setup first: python example_usage.py setup")
        return None

    print("⏳ Loading OTP session...")

    # Load saved session
    otp_session = load_otp("otp.bin")
    if not otp_session:
        print("✗ Failed to load OTP session")
        print("   The session file may be corrupted")
        return None

    print(f"✓ Session loaded (Device: {otp_session.device_id})")
    print("⏳ Generating OTP code...")
    print("   Communicating with PSA server...")

    try:
        # Generate OTP code
        code = otp_session.get_otp_code()

        # Save updated session (counter incremented)
        save_otp(otp_session, "otp.bin")

        print("\n" + "=" * 60)
        print(f"  OTP CODE: {code.upper()}")
        print("=" * 60)
        print("\n✓ OTP code generated successfully!")
        print(f"  OTP Count: {otp_session.otp_count}")
        print("\n⚠  Note: This code can only be used once")
        print("⚠  PSA limits: 6 OTP codes per 24 hours")

        return code

    except ConfigException as e:
        print(f"✗ Configuration error: {e}")
        print("   Your session may have expired. Try running setup again.")
        return None
    except Exception as e:
        print(f"✗ Failed to generate OTP: {e}")
        return None


def display_session_info():
    """Display information about saved OTP session"""
    print_header("PSA OTP Session Information")

    if not os.path.exists("otp.bin"):
        print("✗ No saved OTP session found")
        return

    otp_session = load_otp("otp.bin")
    if not otp_session:
        print("✗ Failed to load OTP session")
        return

    print(f"Device ID:        {otp_session.device_id}")
    print(f"OTP Version:      {otp_session.version}")
    print(f"InWebo Access ID: {otp_session.macid}")
    print(f"OTP Count:        {otp_session.otp_count}")
    print(f"Session File:     otp.bin")
    print(f"\nStatus: ✓ Active")


def interactive_menu():
    """Interactive menu for OTP operations"""
    while True:
        print_header("PSA OTP Flow - Interactive Mode")
        print("1. Setup new OTP session")
        print("2. Generate OTP code")
        print("3. View session info")
        print("4. Exit")
        print()

        choice = input("Select an option (1-4): ").strip()

        if choice == "1":
            setup_otp_session()
        elif choice == "2":
            generate_otp_code()
        elif choice == "3":
            display_session_info()
        elif choice == "4":
            print("\nGoodbye!")
            break
        else:
            print("✗ Invalid option. Please choose 1-4.")

        input("\nPress Enter to continue...")


def print_usage():
    """Print usage information"""
    print("""
PSA OTP Flow - End-to-End Example

Usage:
    python example_usage.py [command]

Commands:
    setup       - First time OTP session setup
    generate    - Generate OTP code from saved session
    info        - Display session information
    interactive - Interactive menu (default)

Examples:
    # First time setup
    python example_usage.py setup

    # Generate OTP code
    python example_usage.py generate

    # Interactive mode
    python example_usage.py
    """)


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "setup":
            setup_otp_session()
        elif command == "generate":
            generate_otp_code()
        elif command == "info":
            display_session_info()
        elif command in ["help", "-h", "--help"]:
            print_usage()
        else:
            print(f"✗ Unknown command: {command}")
            print_usage()
    else:
        # No arguments - run interactive mode
        interactive_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)
