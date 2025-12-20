# PSA Car Controller - Standalone OTP Flow

This directory contains the extracted OTP (One-Time Password) flow implementation for PSA car authentication.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run interactive example
python example_usage.py

# Or use direct commands:
python example_usage.py setup      # First time setup
python example_usage.py generate   # Generate OTP code
python example_usage.py info       # View session info
```

## Overview

The PSA OTP flow is used to generate one-time passwords for authenticating remote control commands to PSA vehicles (Peugeot, Citroën, DS, Opel, Vauxhall).

## Flow Description

### 1. Initial Setup (Activation)
```
User → Request SMS Code → PSA Server
PSA Server → Send SMS Code → User
User → Provide SMS Code + PIN → Activation Process
Activation → Generate Keys & Save Session → otp.bin
```

### 2. OTP Generation
```
Load Session → Request OTP → PSA Server
PSA Server → Send Challenge → OTP Process
OTP Process → Generate Code → Return 6-character code
```

## Components

### Core Files

1. **otp.py** - Main OTP implementation
   - `Otp` class: Handles the complete OTP flow
   - `new_otp_session()`: Creates a new OTP session with SMS code and PIN
   - `get_otp_code()`: Generates a one-time password
   - `save_otp()`: Saves session to disk
   - `load_otp()`: Loads session from disk

2. **load.py** - Data structure for OTP session
   - `IWData` class: Manages OTP session data
   - Handles synchronization with PSA servers

3. **tokenizer.py** - String tokenization utility
   - `Tokenizer` class: Parses delimited token strings

4. **oaep.py** - Custom OAEP encryption
   - `MyOAEP` class: Modified RSA-OAEP cipher for PSA compatibility
   - Required for decryption of server responses

## Usage Example

### First Time Setup

```python
from otp import new_otp_session, save_otp

# User receives SMS code from PSA
sms_code = "123456"  # Code received via SMS
pin_code = "1234"    # User's chosen PIN

# Create new OTP session
otp_session = new_otp_session(sms_code, pin_code)
if otp_session:
    print("OTP session activated successfully!")
    save_otp(otp_session, "otp.bin")
else:
    print("Failed to activate OTP session")
```

### Generating OTP Codes

```python
from otp import load_otp

# Load existing session
otp_session = load_otp("otp.bin")
if otp_session:
    # Generate OTP code
    code = otp_session.get_otp_code()
    print(f"OTP Code: {code}")
else:
    print("No saved session found. Please run setup first.")
```

### Complete End-to-End Example

```python
from otp import Otp, new_otp_session, load_otp, save_otp
import os

def setup_otp():
    """First-time OTP setup"""
    print("=== PSA OTP Setup ===")

    # Step 1: User provides SMS code and PIN
    sms_code = input("Enter SMS code received from PSA: ")
    pin_code = input("Enter your PIN code: ")

    # Step 2: Create and activate OTP session
    print("Activating OTP session...")
    otp_session = new_otp_session(sms_code, pin_code)

    if otp_session:
        save_otp(otp_session, "otp.bin")
        print("✓ OTP session activated and saved!")
        return True
    else:
        print("✗ Failed to activate OTP session")
        return False

def generate_otp():
    """Generate an OTP code from saved session"""
    print("=== Generate OTP Code ===")

    # Load saved session
    otp_session = load_otp("otp.bin")
    if not otp_session:
        print("✗ No saved session found. Run setup first.")
        return None

    # Generate OTP code
    print("Generating OTP code...")
    try:
        code = otp_session.get_otp_code()
        print(f"✓ OTP Code: {code}")

        # Save updated session (counter incremented)
        save_otp(otp_session, "otp.bin")
        return code
    except Exception as e:
        print(f"✗ Failed to generate OTP: {e}")
        return None

def main():
    if not os.path.exists("otp.bin"):
        # First time - setup required
        if setup_otp():
            print("\nSetup complete! You can now generate OTP codes.")
    else:
        # Generate OTP code
        generate_otp()

if __name__ == "__main__":
    main()
```

## Technical Details

### OTP Algorithm

1. **Activation Flow**:
   - Send activation request with SMS code
   - Receive encrypted keys (Kiw, Kfact) from server
   - Decrypt keys using OAEP
   - Generate device keys (K0, K1)
   - Complete synchronization with server

2. **OTP Generation Flow**:
   - Send OTP request to server
   - Receive challenge from server
   - Compute response hashes (R0, R1, R2)
   - Receive defi (counter) from server
   - Generate OTP: `SHA256(K1 + ":" + defi + ":" + secval)`
   - Convert hash to base36 format

### Security

- Uses RSA-OAEP encryption with SHA256
- AES-ECB encryption for key storage
- Device-specific keys tied to device_id
- OTP codes are time-limited and single-use

### Dependencies

```
pycryptodomex>=3.9.0
requests>=2.25.0
```

### Configuration

- **OTP Server**: `https://otp.mpsa.com`
- **InWebo Access ID**: `bb8e981582b0f31353108fb020bead1c` (PSA-specific)
- **Config File**: `otp.bin` (pickled session data)

## API Reference

### Class: `Otp`

#### Methods

- `__init__(inwebo_access_id, device_id=None)`
  - Initialize OTP instance
  - `inwebo_access_id`: PSA InWebo service ID
  - `device_id`: Unique device identifier (auto-generated if not provided)

- `get_otp_code()` → str
  - Generate a one-time password
  - Returns: 6-character base36 OTP code
  - Raises: `ConfigException` if session invalid

#### Static Methods

- `new_otp_session(sms_code, pin_code, old_session=None)` → Otp
  - Create new OTP session
  - `sms_code`: SMS code received from PSA
  - `pin_code`: User's PIN code
  - `old_session`: Optional existing session to preserve device_id
  - Returns: Activated Otp instance or None

- `load_otp(filename="otp.bin")` → Otp
  - Load saved OTP session
  - Returns: Otp instance or None

- `save_otp(otp_instance, filename="otp.bin")`
  - Save OTP session to disk

## Error Handling

### Common Errors

1. **ConfigException**: Invalid or expired OTP session
   - Solution: Re-run activation with new SMS code

2. **ValueError**: Bad response from server
   - Solution: Check network connection and retry

3. **FileNotFoundError**: No saved session
   - Solution: Run initial setup to create session

## Notes

- OTP codes are rate-limited (6 codes per 24 hours by PSA)
- Each OTP code can only be used once
- Session data includes encryption keys - keep `otp.bin` secure
- The device_id should remain constant for a given installation

## Integration

This OTP flow is part of the larger PSA Car Controller system. It's used to:
1. Authenticate remote control commands (lock/unlock, climate, etc.)
2. Generate access tokens for MQTT communication
3. Establish secure sessions with PSA servers

For integration with the full system, see the main PSA Car Controller documentation.
