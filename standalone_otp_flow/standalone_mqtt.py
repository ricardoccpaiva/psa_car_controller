#!/usr/bin/env python3
"""
PSA MQTT - Standalone Connection Script

A simple, standalone script to connect to PSA MQTT server and control your vehicle.

Usage:
    python standalone_mqtt.py

Requirements:
    pip install paho-mqtt requests pycryptodomex

Certificates:
    Uses system default CA certificates (no custom certs needed)
"""

import json
import logging
import sys
import time
from datetime import datetime
from uuid import uuid4

# Check dependencies
try:
    import paho.mqtt.client as mqtt
    import requests
except ModuleNotFoundError as e:
    print(f"✗ Missing dependency: {e.name}")
    print("\nInstall dependencies:")
    print("  pip install paho-mqtt requests pycryptodomex")
    sys.exit(1)

# Try to import OTP functions
try:
    from otp import load_otp, save_otp
    HAS_OTP = True
except (ModuleNotFoundError, ImportError):
    HAS_OTP = False

# Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# PSA MQTT CONFIGURATION
# ============================================================================

MQTT_SERVER = "mwa.mpsa.com"
MQTT_PORT = 8885
MQTT_KEEPALIVE = 60

# Topic templates
MQTT_REQ_TOPIC = "psa/RemoteServices/from/cid/{customer_id}{command}"
MQTT_RESP_TOPIC = "psa/RemoteServices/to/cid/{customer_id}/#"
MQTT_EVENT_TOPIC = "psa/RemoteServices/events/MPHRTServices/{vin}"

# API endpoint for remote token
REMOTE_TOKEN_URL = "https://api.groupe-psa.com/connectedcar/v4/virtualkey/remoteaccess/token"

# Date formats
PSA_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
PSA_CORRELATION_DATE_FORMAT = "%Y%m%d%H%M%S%f"

# Brand/realm info for MQTT customer ID conversion
BRAND_CODES = {
    "clientsB2CPeugeot": "AP",
    "clientsB2CCitroen": "AC",
    "clientsB2CDS": "AC",
    "clientsB2COpel": "OV",
    "clientsB2CVauxhall": "OV"
}

# ============================================================================
# GLOBAL STATE
# ============================================================================

# Connection state
mqtt_client = None
connected = False
remote_access_token = None

# Configuration
config = {
    "client_id": None,
    "customer_id": None,
    "realm": None,
    "vin": None,
    "oauth_access_token": None,
    "mqtt_customer_id": None
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_mqtt_customer_id(customer_id, realm):
    """
    Convert customer ID to MQTT format
    Example: AP-ABC123-DEF456 -> APABC123DEF456
    """
    # Get brand code for this realm
    brand_code = BRAND_CODES.get(realm, customer_id[:2])
    # Remove hyphens from customer ID and replace prefix
    mqtt_id = customer_id.replace("-", "")
    # Replace first 2 chars with brand code
    return brand_code + mqtt_id[2:]


def generate_correlation_id():
    """Generate unique correlation ID for MQTT messages"""
    date_str = datetime.utcnow().strftime(PSA_CORRELATION_DATE_FORMAT)[:-3]
    uuid_str = str(uuid4()).replace("-", "")
    return uuid_str + date_str


def generate_otp_code():
    """Generate OTP code from saved session"""
    if not HAS_OTP:
        logger.warning("OTP module not available")
        return None

    try:
        otp_session = load_otp("otp.bin")
        if not otp_session:
            logger.error("No OTP session found. Run: python example_usage.py setup")
            return None

        code = otp_session.get_otp_code()
        save_otp(otp_session)
        logger.info(f"✓ Generated OTP code: {code}")
        return code
    except Exception as e:
        logger.error(f"Failed to generate OTP: {e}")
        return None


def get_remote_access_token(client_id, realm, oauth_token, otp_code):
    """
    Exchange OTP code for remote access token

    Args:
        client_id: PSA client ID
        realm: PSA realm (e.g., clientsB2CPeugeot)
        oauth_token: OAuth access token
        otp_code: OTP code (6 characters)

    Returns:
        dict with 'access_token' and 'refresh_token', or None on error
    """
    logger.info("Exchanging OTP for remote access token...")

    url = f"{REMOTE_TOKEN_URL}?client_id={client_id}"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "x-introspect-realm": realm,
        "accept": "application/hal+json",
        "User-Agent": "okhttp/4.8.0",
    }
    payload = {
        "grant_type": "password",
        "password": otp_code
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "access_token" in data:
            logger.info("✓ Remote access token obtained")
            return data
        else:
            logger.error(f"✗ Failed: {data}")
            return None

    except requests.RequestException as e:
        logger.error(f"✗ Request failed: {e}")
        return None


def refresh_remote_token(client_id, realm, oauth_token, refresh_token):
    """
    Refresh remote access token using refresh token

    Returns:
        dict with new tokens, or None on error
    """
    logger.info("Refreshing remote access token...")

    url = f"{REMOTE_TOKEN_URL}?client_id={client_id}"
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "x-introspect-realm": realm,
        "accept": "application/hal+json",
        "User-Agent": "okhttp/4.8.0",
    }
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "access_token" in data:
            logger.info("✓ Token refreshed")
            return data
        else:
            logger.error(f"✗ Refresh failed: {data}")
            return None

    except requests.RequestException as e:
        logger.error(f"✗ Refresh request failed: {e}")
        return None


# ============================================================================
# MQTT CALLBACKS
# ============================================================================

def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    global connected

    if rc == 0:
        logger.info("✓ Connected to MQTT server")
        connected = True

        # Subscribe to response and event topics
        resp_topic = MQTT_RESP_TOPIC.format(customer_id=config["mqtt_customer_id"])
        event_topic = MQTT_EVENT_TOPIC.format(vin=config["vin"])

        client.subscribe(resp_topic)
        client.subscribe(event_topic)

        logger.info(f"✓ Subscribed to: {resp_topic}")
        logger.info(f"✓ Subscribed to: {event_topic}")
    else:
        logger.error(f"✗ MQTT connection failed (code: {rc})")
        connected = False


def on_disconnect(client, userdata, rc):
    """Callback when disconnected from MQTT broker"""
    global connected
    logger.warning(f"Disconnected from MQTT (code: {rc})")
    connected = False


def on_message(client, userdata, msg):
    """Callback when message received from MQTT broker"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Message received on: {msg.topic}")

    try:
        data = json.loads(msg.payload.decode())
        logger.info(f"Payload:\n{json.dumps(data, indent=2)}")

        # Check return code
        if "return_code" in data:
            code = data["return_code"]
            if code == "0":
                logger.info("✓ Command successful")
            elif code == "400":
                logger.warning("⚠ Token expired - need to refresh")
            else:
                reason = data.get("reason", "Unknown error")
                logger.error(f"✗ Command failed: {code} - {reason}")

    except json.JSONDecodeError:
        logger.error(f"Failed to decode: {msg.payload}")

    logger.info(f"{'='*60}\n")


# ============================================================================
# MQTT CONNECTION
# ============================================================================

def connect_mqtt(remote_token):
    """
    Connect to PSA MQTT server

    Args:
        remote_token: Remote access token for authentication

    Returns:
        True if connected, False otherwise
    """
    global mqtt_client, connected, remote_access_token

    remote_access_token = remote_token

    logger.info(f"Connecting to {MQTT_SERVER}:{MQTT_PORT}...")

    # Create MQTT client
    mqtt_client = mqtt.Client(
        client_id=f"psa-{config['customer_id']}",
        clean_session=True,
        protocol=mqtt.MQTTv311
    )

    # Set callbacks
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message

    # Set authentication
    # Username is ALWAYS "IMA_OAUTH_ACCESS_TOKEN"
    # Password is the remote access token
    mqtt_client.username_pw_set("IMA_OAUTH_ACCESS_TOKEN", remote_token)

    # Enable TLS (uses system default CA certificates)
    mqtt_client.tls_set()

    try:
        # Connect to broker
        mqtt_client.connect(MQTT_SERVER, MQTT_PORT, MQTT_KEEPALIVE)

        # Start network loop in background
        mqtt_client.loop_start()

        # Wait for connection
        time.sleep(2)

        return connected

    except Exception as e:
        logger.error(f"✗ Connection failed: {e}")
        return False


def disconnect_mqtt():
    """Disconnect from MQTT server"""
    global mqtt_client, connected

    if mqtt_client:
        logger.info("Disconnecting from MQTT...")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        connected = False


# ============================================================================
# SEND COMMANDS
# ============================================================================

def send_command(command, parameters):
    """
    Send command to vehicle via MQTT

    Args:
        command: Command endpoint (e.g., "/VehCharge", "/Doors")
        parameters: Command parameters (dict)

    Returns:
        True if sent, False otherwise
    """
    global mqtt_client, connected, remote_access_token

    if not connected:
        logger.error("Not connected to MQTT")
        return False

    # Build topic
    topic = MQTT_REQ_TOPIC.format(
        customer_id=config["mqtt_customer_id"],
        command=command
    )

    # Build message
    message = {
        "access_token": remote_access_token,
        "customer_id": config["mqtt_customer_id"],
        "correlation_id": generate_correlation_id(),
        "req_date": datetime.utcnow().strftime(PSA_DATE_FORMAT),
        "vin": config["vin"],
        "req_parameters": parameters
    }

    # Send message
    logger.info(f"\nSending command: {command}")
    logger.info(f"Parameters: {parameters}")

    result = mqtt_client.publish(topic, json.dumps(message))

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        logger.info("✓ Command sent")
        return True
    else:
        logger.error(f"✗ Failed to send (code: {result.rc})")
        return False


# ============================================================================
# CONVENIENCE COMMAND FUNCTIONS
# ============================================================================

def charge_now():
    """Start charging immediately"""
    return send_command("/VehCharge", {
        "program": {"hour": 0, "minute": 0},
        "type": "immediate"
    })


def charge_delayed(hour, minute):
    """Set delayed charging"""
    return send_command("/VehCharge", {
        "program": {"hour": hour, "minute": minute},
        "type": "delayed"
    })


def lock_doors():
    """Lock vehicle doors"""
    return send_command("/Doors", {"action": "lock"})


def unlock_doors():
    """Unlock vehicle doors"""
    return send_command("/Doors", {"action": "unlock"})


def horn(count=3):
    """Activate horn"""
    return send_command("/Horn", {
        "nb_horn": count,
        "action": "activate"
    })


def lights(duration=60):
    """Activate lights (seconds)"""
    return send_command("/Lights", {
        "action": "activate",
        "duration": duration
    })


def wakeup():
    """Wake up vehicle (get status)"""
    return send_command("/VehCharge/state", {"action": "state"})


def preconditioning(activate=True):
    """Activate/deactivate preconditioning"""
    return send_command("/ThermalPrecond", {
        "asap": "activate" if activate else "deactivate",
        "programs": {
            "program1": {"day": [0]*7, "hour": 34, "minute": 7, "on": 0},
            "program2": {"day": [0]*7, "hour": 34, "minute": 7, "on": 0},
            "program3": {"day": [0]*7, "hour": 34, "minute": 7, "on": 0},
            "program4": {"day": [0]*7, "hour": 34, "minute": 7, "on": 0}
        }
    })


# ============================================================================
# MAIN PROGRAM
# ============================================================================

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def get_configuration():
    """Get configuration from user"""
    print_header("PSA MQTT Connection - Configuration")

    print("Enter your PSA account details:\n")

    config["client_id"] = input("Client ID: ").strip()
    config["customer_id"] = input("Customer ID (e.g., AP-XXXXXX): ").strip()
    config["realm"] = input("Realm (e.g., clientsB2CPeugeot): ").strip()
    config["vin"] = input("Vehicle VIN: ").strip()
    config["oauth_access_token"] = input("OAuth Access Token: ").strip()

    # Calculate MQTT customer ID
    config["mqtt_customer_id"] = get_mqtt_customer_id(
        config["customer_id"],
        config["realm"]
    )

    print(f"\n✓ MQTT Customer ID: {config['mqtt_customer_id']}")


def get_otp():
    """Get OTP code (auto-generate or manual entry)"""
    print_header("OTP Code")

    otp_code = None

    # Try to auto-generate
    if HAS_OTP:
        print("Checking for saved OTP session...")
        otp_code = generate_otp_code()

    # Manual entry if needed
    if not otp_code:
        print("\nManual OTP entry required.")
        print("To generate OTP automatically, run: python example_usage.py generate\n")
        otp_code = input("Enter OTP code: ").strip()

    return otp_code


def setup_connection():
    """Set up MQTT connection"""
    print_header("Remote Access Token")

    # Get OTP code
    otp_code = get_otp()
    if not otp_code:
        logger.error("No OTP code provided")
        return False

    # Exchange OTP for remote token
    token_data = get_remote_access_token(
        config["client_id"],
        config["realm"],
        config["oauth_access_token"],
        otp_code
    )

    if not token_data or "access_token" not in token_data:
        logger.error("Failed to get remote access token")
        return False

    remote_token = token_data["access_token"]

    # Connect to MQTT
    print_header("MQTT Connection")

    if not connect_mqtt(remote_token):
        logger.error("Failed to connect to MQTT")
        return False

    return True


def command_menu():
    """Interactive command menu"""
    print_header("Vehicle Commands")

    commands = {
        "1": ("Charge now", charge_now),
        "2": ("Charge delayed", lambda: charge_delayed(
            int(input("Hour (0-23): ")),
            int(input("Minute (0-59): "))
        )),
        "3": ("Lock doors", lock_doors),
        "4": ("Unlock doors", unlock_doors),
        "5": ("Horn", horn),
        "6": ("Lights", lights),
        "7": ("Preconditioning ON", lambda: preconditioning(True)),
        "8": ("Preconditioning OFF", lambda: preconditioning(False)),
        "9": ("Wakeup (get status)", wakeup),
        "0": ("Exit", None)
    }

    while True:
        print("\nAvailable commands:")
        for key, (name, _) in commands.items():
            print(f"  {key}. {name}")

        choice = input("\nEnter command number: ").strip()

        if choice == "0":
            break

        if choice in commands:
            _, func = commands[choice]
            if func:
                try:
                    func()
                    # Wait for response
                    time.sleep(2)
                except Exception as e:
                    logger.error(f"Command failed: {e}")
        else:
            print("Invalid choice")


def main():
    """Main program"""
    print("=" * 70)
    print("  PSA MQTT Connection - Standalone Script")
    print("=" * 70)
    print("\nThis script connects to PSA MQTT server to control your vehicle.")
    print("Uses system default CA certificates (no custom certs needed).\n")

    try:
        # Step 1: Get configuration
        get_configuration()

        # Step 2: Setup connection
        if not setup_connection():
            return 1

        # Step 3: Command menu
        command_menu()

        # Cleanup
        disconnect_mqtt()
        print("\n✓ Disconnected. Goodbye!")
        return 0

    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        disconnect_mqtt()
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        disconnect_mqtt()
        return 1


if __name__ == "__main__":
    sys.exit(main())
