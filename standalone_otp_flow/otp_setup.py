#!/usr/bin/env python3
"""
PSA OTP Setup - Standalone Script

Sets up OTP session with SMS code and PIN code.
Creates otp.bin file for future OTP generation.

Usage:
    python otp_setup.py <sms_code> <pin_code>

Example:
    python otp_setup.py 123456 1234

Output:
    Prints "SUCCESS" on success
    Prints "ERROR: <message>" on failure
    Exit code 0 on success, 1 on failure

File created:
    otp.bin - OTP session file
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from otp import new_otp_session, save_otp, ConfigException
except ImportError as e:
    print(f"ERROR: Missing OTP module - {e}", file=sys.stderr)
    sys.exit(1)


def main():
    """Main entry point"""
    # Check arguments
    if len(sys.argv) != 3:
        print("ERROR: Invalid arguments", file=sys.stderr)
        print("Usage: python otp_setup.py <sms_code> <pin_code>", file=sys.stderr)
        print("Example: python otp_setup.py 123456 1234", file=sys.stderr)
        sys.exit(1)

    sms_code = sys.argv[1].strip()
    pin_code = sys.argv[2].strip()

    # Validate inputs
    if not sms_code:
        print("ERROR: SMS code is required", file=sys.stderr)
        sys.exit(1)

    if not pin_code:
        print("ERROR: PIN code is required", file=sys.stderr)
        sys.exit(1)

    if not pin_code.isdigit():
        print("ERROR: PIN code must be numeric", file=sys.stderr)
        sys.exit(1)

    # Create OTP session
    try:
        otp_session = new_otp_session(sms_code, pin_code)

        if otp_session is None:
            print("ERROR: Failed to create OTP session", file=sys.stderr)
            sys.exit(1)

        # Save session
        save_otp(otp_session, "otp.bin")

        # Success - output for Elixir to capture
        print("SUCCESS")
        print(f"DEVICE_ID:{otp_session.device_id}")
        print(f"SESSION_FILE:otp.bin")

        sys.exit(0)

    except ConfigException as e:
        print(f"ERROR: Configuration error - {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
