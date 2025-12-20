# PSA OTP Flow - Detailed Flow Diagram

## Overview

This document describes the complete end-to-end flow of the PSA OTP (One-Time Password) system.

## Flow Diagrams

### 1. Initial Setup Flow (Activation)

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       │ 1. Request SMS via PSA App
       ▼
┌─────────────────────┐
│   PSA Mobile App    │
└──────┬──────────────┘
       │
       │ 2. Request SMS Code
       ▼
┌─────────────────────┐
│   PSA API Server    │
└──────┬──────────────┘
       │
       │ 3. Send SMS Code
       ▼
┌─────────────┐
│    User     │ (receives SMS on phone)
└──────┬──────┘
       │
       │ 4. Enter SMS Code + PIN
       ▼
┌─────────────────────┐
│  OTP Setup Script   │
│  new_otp_session()  │
└──────┬──────────────┘
       │
       │ 5. POST /iwws/MAC?action=ActionSetup
       │    - mode: activate
       │    - code: <sms_code>
       │    - macid: bb8e981582b0f31353108fb020bead1c
       ▼
┌─────────────────────┐
│  OTP.MPSA.COM       │
│  InWebo Server      │
└──────┬──────────────┘
       │
       │ 6. Return XML with encrypted keys
       │    - Kiw (encrypted key)
       │    - Kfact (factory key)
       │    - pinmode
       ▼
┌─────────────────────┐
│  OTP Setup Script   │
│  activation_start() │
└──────┬──────────────┘
       │
       │ 7. Decrypt Kiw using Kfact (OAEP)
       │    Initialize cipher
       ▼
┌─────────────────────┐
│  Crypto Operations  │
│  - Generate KMA     │
│  - Encrypt PIN      │
│  - Generate R0,R1,R2│
└──────┬──────────────┘
       │
       │ 8. POST /iwws/MAC?action=ActionFinalize
       │    - mode: activate
       │    - Kma: <encrypted>
       │    - pin: <encrypted>
       │    - R0, R1, R2: <hashes>
       ▼
┌─────────────────────┐
│  OTP.MPSA.COM       │
│  InWebo Server      │
└──────┬──────────────┘
       │
       │ 9. Return sync data (K0, K1, etc.)
       ▼
┌─────────────────────┐
│  Data Sync          │
│  IWData.synchro()   │
└──────┬──────────────┘
       │
       │ 10. May request MS (Master Secret) setup
       │     if ms_n > 0
       ▼
┌─────────────────────┐
│  MS Setup           │
│  - Generate random  │
│  - Encrypt with AES │
│  - Store secval     │
└──────┬──────────────┘
       │
       │ 11. Save session to otp.bin
       ▼
┌─────────────────────┐
│  pickle.dump()      │
│  otp.bin created    │
└─────────────────────┘
```

### 2. OTP Code Generation Flow

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       │ 1. Request OTP Code
       ▼
┌─────────────────────┐
│  OTP Generator      │
│  get_otp_code()     │
└──────┬──────────────┘
       │
       │ 2. Load session from otp.bin
       ▼
┌─────────────────────┐
│  pickle.load()      │
│  Restore Otp object │
└──────┬──────────────┘
       │
       │ 3. POST /iwws/MAC?action=ActionSetup
       │    - mode: otp
       │    - sid: <security_id>
       ▼
┌─────────────────────┐
│  OTP.MPSA.COM       │
│  InWebo Server      │
└──────┬──────────────┘
       │
       │ 4. Return challenge
       ▼
┌─────────────────────┐
│  Challenge Handler  │
│  - Store challenge  │
└──────┬──────────────┘
       │
       │ 5. Calculate response hashes
       │    R0 = SHA256(challenge; K0; serial)
       │    R1 = SHA256(challenge; K0; K1)
       │    R2 = SHA256(challenge; K0; PIN)
       ▼
┌─────────────────────┐
│  Hash Computation   │
│  get_r()            │
└──────┬──────────────┘
       │
       │ 6. POST /iwws/MAC?action=ActionFinalize
       │    - mode: otp
       │    - R0, R1, R2: <hashes>
       ▼
┌─────────────────────┐
│  OTP.MPSA.COM       │
│  InWebo Server      │
└──────┬──────────────┘
       │
       │ 7. Return defi (counter)
       │    May include 'J' flag (requires second request)
       ▼
┌─────────────────────┐
│  Response Handler   │
│  Check for OTP_TWICE│
└──────┬──────────────┘
       │
       │ 8. If J flag present, repeat steps 3-7
       │    Otherwise continue
       ▼
┌─────────────────────┐
│  OTP Calculation    │
│  _get_otp_code()    │
└──────┬──────────────┘
       │
       │ 9. Generate OTP:
       │    password = K1 + ":" + defi + ":" + secval
       │    hash = SHA256(password)
       │    number = (hash[0:4] & 0xFFFFFF) * 1024 + (hash[4:8] & 1023)
       │    otp = base36(number)
       ▼
┌─────────────────────┐
│  Base36 Conversion  │
│  number_to_base36() │
└──────┬──────────────┘
       │
       │ 10. Return 6-character OTP code
       ▼
┌─────────────┐
│    User     │ (receives: e.g., "a3k9m2")
└─────────────┘
```

## Detailed Component Interactions

### Activation Sequence

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│   User   │   │   Otp    │   │  Server  │   │  IWData  │
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │
     │ SMS+PIN      │              │              │
     ├─────────────>│              │              │
     │              │ ActionSetup  │              │
     │              ├─────────────>│              │
     │              │   Kiw,Kfact  │              │
     │              │<─────────────┤              │
     │              │              │              │
     │              │ init(Kiw,Kfact)             │
     │              ├──────────────┼─────────────>│
     │              │              │              │
     │              │ActionFinalize│              │
     │              ├─────────────>│              │
     │              │  Sync Data   │              │
     │              │<─────────────┤              │
     │              │              │              │
     │              │   synchro()  │              │
     │              ├──────────────┼─────────────>│
     │              │              │              │
     │   Success    │              │              │
     │<─────────────┤              │              │
```

### OTP Generation Sequence

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│   User   │   │   Otp    │   │  Server  │   │ Crypto   │
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │
     │ Get OTP      │              │              │
     ├─────────────>│              │              │
     │              │ ActionSetup  │              │
     │              ├─────────────>│              │
     │              │  Challenge   │              │
     │              │<─────────────┤              │
     │              │              │              │
     │              │  get_r()     │              │
     │              ├──────────────┼─────────────>│
     │              │              │    R0,R1,R2  │
     │              │<─────────────┼──────────────┤
     │              │              │              │
     │              │ActionFinalize│              │
     │              ├─────────────>│              │
     │              │    defi      │              │
     │              │<─────────────┤              │
     │              │              │              │
     │              │_get_otp_code()              │
     │              ├──────────────┼─────────────>│
     │              │              │  OTP Code    │
     │              │<─────────────┼──────────────┤
     │   OTP Code   │              │              │
     │<─────────────┤              │              │
```

## Key Data Structures

### OTP Session (otp.bin)

```
Otp Object
├── Device Identification
│   ├── device_id: Random hex (16 chars)
│   ├── iwalea: Random hex (32 chars)
│   └── macid: InWebo Access ID
│
├── Encryption Keys
│   ├── Kiw: InWebo key (decrypted)
│   ├── Kfact: Factory key
│   ├── cipher: RSA-OAEP cipher instance
│   └── pinmode: PIN mode setting
│
├── Session Data (IWData)
│   ├── iwid: Session ID
│   ├── iwK0: Session key 0
│   ├── iwK1: Session key 1
│   ├── iwsecid: Security ID
│   ├── iwsecval: Security value (AES encrypted)
│   └── iwTsync: Last sync timestamp
│
└── Runtime State
    ├── mode: activate/otp/ms
    ├── challenge: Server challenge
    ├── defi: OTP counter
    └── otp_count: Number of OTPs generated
```

## Cryptographic Operations

### Key Derivation

```
1. KMA (Key Management Authentication)
   KMA = SHA256(PIN + ";" + serial)[0:32]
   serial = device_id + "/_/" + iwalea

2. Response Hashes
   R0 = SHA256(challenge + ";" + K0 + ";" + serial)
   R1 = SHA256(challenge + ";" + K0 + ";" + K1)
   R2 = SHA256(challenge + ";" + K0 + ";" + PIN)

3. OTP Calculation
   password = K1 + ":" + defi + ":" + secval
   hash = SHA256(password)
   value = (hash[0:4] & 0xFFFFFF) * 1024 + (hash[4:8] & 1023)
   otp = base36(value)
```

### Encryption Schemes

```
1. RSA-OAEP (Server → Client)
   - Algorithm: OAEP with SHA256
   - Used for: Kiw, ms_key decryption
   - Modified: Uses e=0x11 instead of standard e=65537

2. AES-ECB (Client ↔ Server)
   - Key: KMA (32 hex chars = 16 bytes)
   - Used for: K0, K1, secval encryption
   - Mode: ECB (no IV)

3. SHA256 Hashing
   - Used for: KMA, R0/R1/R2, OTP generation, K1 derivation
```

## Error Handling

### Common Error Paths

```
Setup Errors:
├── Invalid SMS Code
│   └── Server returns err != "OK"
├── Invalid PIN
│   └── Encryption fails
├── Network Error
│   └── Timeout or connection refused
└── Server Error
    └── Server returns error in XML

Generation Errors:
├── No Session
│   └── otp.bin not found
├── Expired Session
│   └── ConfigException raised
├── Invalid Session
│   └── Decryption/unpickle fails
└── Rate Limit
    └── 6 OTPs per 24 hours exceeded
```

## Security Considerations

1. **Session Storage**: otp.bin contains sensitive keys
   - Stored as pickled Python object
   - No additional encryption
   - Should be kept secure

2. **PIN Protection**: PIN is only sent encrypted
   - Never transmitted in plain text
   - Used to derive KMA for AES encryption

3. **Device Binding**: device_id ties session to device
   - Random on first setup
   - Should remain constant
   - Changing it requires new activation

4. **Rate Limiting**: Built into PSA servers
   - 6 OTP codes per 24 hours
   - Enforced server-side
   - No client-side bypass

5. **OTP Lifetime**: Each OTP is single-use
   - Counter (defi) increments each time
   - Server validates and invalidates after use

## Integration Points

### With PSA Car Controller

```
RemoteClient.get_otp_code()
    ↓
Otp.get_otp_code()
    ↓
Used for remote_access_token
    ↓
MQTT authentication
    ↓
Vehicle remote control
```

### Standalone Usage

```
Direct API:
    new_otp_session() → Setup
    load_otp() → Load session
    Otp.get_otp_code() → Generate
    save_otp() → Persist
```
