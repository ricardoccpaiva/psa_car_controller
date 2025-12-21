#!/usr/bin/env python3
"""
PSA OTP Generate - Standalone Script

Generates OTP code from existing OTP session.
Requires otp.bin file (created by otp_setup.py).

Usage:
    python otp_generate.py [session_file]

Example:
    python otp_generate.py
    python otp_generate.py otp.bin
    python otp_generate.py /path/to/otp.bin

Output:
    Prints OTP code (6 characters) on success
    Prints "ERROR: <message>" on failure
    Exit code 0 on success, 1 on failure
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from otp import load_otp, save_otp, ConfigException
except ImportError as e:
    print(f"ERROR: Missing OTP module - {e}", file=sys.stderr)
    sys.exit(1)


def main():
    """Main entry point"""
    # Get session file path
    if len(sys.argv) > 1:
        session_file = sys.argv[1]
    else:
        session_file = "otp.bin"

    # Check if file exists
    if not os.path.exists(session_file):
        print(f"ERROR: Session file not found: {session_file}", file=sys.stderr)
        print("Run otp_setup.py first to create OTP session", file=sys.stderr)
        sys.exit(1)

    # Load OTP session
    try:
        otp_session = load_otp(session_file)

        if otp_session is None:
            print("ERROR: Failed to load OTP session", file=sys.stderr)
            print("Session file may be corrupted", file=sys.stderr)
            sys.exit(1)

        # Generate OTP code
        otp_code = otp_session.get_otp_code()

        if otp_code is None:
            print("ERROR: Failed to generate OTP code", file=sys.stderr)
            sys.exit(1)

        # Save updated session (counter incremented)
        save_otp(otp_session, session_file)

        # Success - output OTP code for Elixir to capture
        print(otp_code)

        sys.exit(0)

    except ConfigException as e:
        print(f"ERROR: Configuration error - {e}", file=sys.stderr)
        print("Your session may have expired. Run otp_setup.py again.", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
