#!/usr/bin/env python3
"""
PSA OTP Flow - Test/Demo Script

This script demonstrates the OTP flow API without requiring actual SMS codes.
It shows the structure and usage patterns.

Note: This will not work with fake data - it's for demonstration purposes only.
"""

from otp import Otp, new_otp_session, load_otp, save_otp, ConfigException


def demo_flow_structure():
    """
    Demonstrate the OTP flow structure without making actual API calls
    """
    print("=" * 70)
    print("PSA OTP Flow - API Demonstration")
    print("=" * 70)
    print()

    print("1. ACTIVATION FLOW")
    print("-" * 70)
    print("""
    When you receive an SMS code from PSA, the activation flow is:

    Step 1: Create OTP session with SMS code and PIN
    -------
    from otp import new_otp_session

    sms_code = "123456"  # Received via SMS
    pin_code = "1234"    # Your chosen PIN

    otp_session = new_otp_session(sms_code, pin_code)

    Step 2: Behind the scenes, this performs:
    -------
    a) POST to otp.mpsa.com/iwws/MAC
       action=ActionSetup, mode=activate, code=SMS_CODE

    b) Server returns encrypted keys (Kiw, Kfact)

    c) Decrypt Kiw using RSA-OAEP with Kfact

    d) Generate device-specific keys:
       - KMA = SHA256(PIN + serial)[0:32]
       - Encrypt PIN with RSA-OAEP
       - Calculate R0, R1, R2 hashes

    e) POST to otp.mpsa.com/iwws/MAC
       action=ActionFinalize, mode=activate
       with Kma, encrypted PIN, and R0/R1/R2

    f) Server returns session data (K0, K1, etc.)

    g) May perform MS (Master Secret) exchange if required

    h) Session saved to otp.bin

    Step 3: Save session (done automatically)
    -------
    save_otp(otp_session, "otp.bin")
    """)

    print("\n2. OTP GENERATION FLOW")
    print("-" * 70)
    print("""
    Once activated, generate OTP codes:

    Step 1: Load saved session
    -------
    from otp import load_otp

    otp_session = load_otp("otp.bin")

    Step 2: Generate OTP code
    -------
    otp_code = otp_session.get_otp_code()
    # Returns: e.g., "a3k9m2"

    Step 3: Behind the scenes, this performs:
    -------
    a) POST to otp.mpsa.com/iwws/MAC
       action=ActionSetup, mode=otp, sid=security_id

    b) Server returns challenge

    c) Calculate response hashes:
       R0 = SHA256(challenge + K0 + serial)
       R1 = SHA256(challenge + K0 + K1)
       R2 = SHA256(challenge + K0 + PIN)

    d) POST to otp.mpsa.com/iwws/MAC
       action=ActionFinalize, mode=otp, R0, R1, R2

    e) Server returns defi (counter)
       May require second request if 'J' flag present

    f) Generate OTP:
       password = K1 + ":" + defi + ":" + secval
       hash = SHA256(password)
       number = (hash[0:4] & 0xFFFFFF) * 1024 + (hash[4:8] & 1023)
       otp = base36(number)  # 6 characters

    Step 4: Save updated session
    -------
    save_otp(otp_session, "otp.bin")
    """)

    print("\n3. DATA STRUCTURES")
    print("-" * 70)
    print("""
    The OTP session object contains:

    Otp Object:
    -----------
    - device_id      : Unique device identifier (hex)
    - iwalea         : Random authentication value (hex)
    - macid          : InWebo Access ID (PSA-specific)
    - Kiw            : InWebo encryption key (decrypted)
    - Kfact          : Factory key
    - cipher         : RSA-OAEP cipher instance
    - codepin        : User's PIN code
    - mode           : activate/otp/ms
    - challenge      : Server challenge (for OTP generation)
    - defi           : OTP counter
    - data           : IWData session information

    IWData Object:
    --------------
    - iwid           : Session ID
    - iwK0           : Session key 0
    - iwK1           : Session key 1
    - iwsecid        : Security ID (for OTP requests)
    - iwsecval       : Security value (AES encrypted)
    - iwTsync        : Last synchronization timestamp
    """)

    print("\n4. CRYPTOGRAPHIC OPERATIONS")
    print("-" * 70)
    print("""
    Encryption schemes used:

    RSA-OAEP (Server → Client):
    ---------------------------
    - Algorithm: OAEP with SHA256
    - Modulus length: 1024 bits (128 bytes)
    - Exponent: 0x11 (17)
    - Used for decrypting: Kiw, ms_key

    AES-ECB (Client ↔ Server):
    --------------------------
    - Key: KMA (16 bytes)
    - Mode: ECB (no IV)
    - Used for: K0, K1, secval encryption

    SHA256 Hashing:
    ---------------
    - KMA derivation: SHA256(PIN + serial)[0:32]
    - Response hashes: SHA256(challenge + keys)
    - OTP generation: SHA256(K1 + defi + secval)
    - K1 derivation: SHA256(K1_base + dK1)[0:32]
    """)

    print("\n5. ERROR HANDLING")
    print("-" * 70)
    print("""
    Common errors and solutions:

    ConfigException:
    ----------------
    - Cause: Invalid or expired OTP session
    - Solution: Re-run activation with new SMS code

    FileNotFoundError:
    ------------------
    - Cause: No saved session (otp.bin not found)
    - Solution: Run initial setup

    ValueError (Bad response):
    --------------------------
    - Cause: Network error or invalid server response
    - Solution: Check connection and retry

    Rate Limit:
    -----------
    - PSA limit: 6 OTP codes per 24 hours
    - Enforced: Server-side
    - Solution: Wait 24 hours or use existing codes
    """)

    print("\n6. SECURITY NOTES")
    print("-" * 70)
    print("""
    Important security considerations:

    Session Storage:
    ----------------
    - otp.bin contains sensitive encryption keys
    - File should be protected (chmod 600)
    - Do not share or commit to version control

    PIN Security:
    -------------
    - PIN never sent in plain text
    - Used only for key derivation (KMA)
    - Should be strong and memorable

    Device Binding:
    ---------------
    - device_id uniquely identifies this installation
    - Changing it requires new activation
    - Keep device_id consistent

    OTP Usage:
    ----------
    - Each OTP can only be used once
    - Counter (defi) increments each generation
    - Server validates and invalidates after use
    """)

    print("\n" + "=" * 70)
    print("End of API Demonstration")
    print("=" * 70)
    print()
    print("To use this for real:")
    print("1. Request SMS code from PSA mobile app")
    print("2. Run: python example_usage.py setup")
    print("3. Enter SMS code and PIN when prompted")
    print("4. Generate OTPs with: python example_usage.py generate")
    print()


def show_code_examples():
    """Show practical code examples"""
    print("\n" + "=" * 70)
    print("CODE EXAMPLES")
    print("=" * 70)

    print("""
Example 1: First Time Setup
----------------------------
from otp import new_otp_session, save_otp

# Get SMS code from PSA
sms_code = input("Enter SMS code: ")
pin_code = input("Enter PIN: ")

# Activate session
session = new_otp_session(sms_code, pin_code)
if session:
    save_otp(session, "otp.bin")
    print("Setup complete!")
else:
    print("Setup failed!")


Example 2: Generate OTP Code
-----------------------------
from otp import load_otp, save_otp

# Load session
session = load_otp("otp.bin")
if not session:
    print("No session found - run setup first")
    exit(1)

# Generate OTP
try:
    code = session.get_otp_code()
    print(f"OTP Code: {code}")

    # Save updated session
    save_otp(session, "otp.bin")
except Exception as e:
    print(f"Error: {e}")


Example 3: Error Handling
--------------------------
from otp import load_otp, ConfigException

session = load_otp("otp.bin")
if session:
    try:
        code = session.get_otp_code()
        print(f"OTP: {code}")
    except ConfigException as e:
        print(f"Session expired: {e}")
        print("Please run setup again")
    except Exception as e:
        print(f"Unexpected error: {e}")
else:
    print("No saved session")


Example 4: Session Info
------------------------
from otp import load_otp

session = load_otp("otp.bin")
if session:
    print(f"Device ID: {session.device_id}")
    print(f"InWebo ID: {session.macid}")
    print(f"OTP Count: {session.otp_count}")
    print(f"Session ID: {session.data.iwid}")


Example 5: Custom Device ID
----------------------------
from otp import Otp, save_otp

# Use specific device ID (for migration/backup)
old_device_id = "a1b2c3d4e5f6g7h8"

session = Otp(
    inwebo_access_id="bb8e981582b0f31353108fb020bead1c",
    device_id=old_device_id
)
session.smsCode = "123456"
session.codepin = "1234"

if session.activation_start():
    session.activation_finalyze()
    save_otp(session, "otp.bin")
    """)

    print("=" * 70)


if __name__ == "__main__":
    demo_flow_structure()
    show_code_examples()

    print("\nFor a working example, use: python example_usage.py")
    print("For detailed flow diagrams, see: FLOW_DIAGRAM.md")
    print("For complete documentation, see: README.md")
