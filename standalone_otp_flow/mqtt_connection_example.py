#!/usr/bin/env python3
"""
PSA MQTT Connection Example

This script shows how to connect to the PSA MQTT server and send commands to your vehicle.

Flow:
1. Generate OTP code (using standalone_otp_flow)
2. Exchange OTP for remote access token
3. Connect to MQTT server
4. Send commands to vehicle

Requirements:
    pip install paho-mqtt requests pycryptodomex
"""

import json
import logging
import sys
from datetime import datetime
from uuid import uuid4

try:
    import paho.mqtt.client as mqtt
    import requests
except ModuleNotFoundError as e:
    print(f"✗ Error: Missing required dependency: {e.name}")
    print("\nPlease install dependencies:")
    print("  pip install paho-mqtt requests")
    sys.exit(1)

# Try to import OTP functions
try:
    from otp import load_otp
    HAS_OTP = True
except (ModuleNotFoundError, ImportError):
    HAS_OTP = False
    print("⚠  Warning: OTP module not found. You'll need to provide OTP code manually.")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# PSA MQTT Configuration
MQTT_SERVER = "mwa.mpsa.com"
MQTT_PORT = 8885
MQTT_RESP_TOPIC = "psa/RemoteServices/to/cid/"
MQTT_EVENT_TOPIC = "psa/RemoteServices/events/MPHRTServices/"
MQTT_REQ_TOPIC = "psa/RemoteServices/from/cid/"

# PSA API Configuration
REMOTE_TOKEN_URL = "https://api.groupe-psa.com/connectedcar/v4/virtualkey/remoteaccess/token"
PSA_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
PSA_CORRELATION_DATE_FORMAT = "%Y%m%d%H%M%S%f"

# Brand Configuration
REALM_INFO = {
    "clientsB2CPeugeot": {
        "brand_code": "AP",
        "app_name": "MyPeugeot"
    },
    "clientsB2CCitroen": {
        "brand_code": "AC",
        "app_name": "MyCitroen"
    },
    "clientsB2CDS": {
        "brand_code": "AC",  # DS uses same as Citroen
        "app_name": "MyDS"
    },
    "clientsB2COpel": {
        "brand_code": "OV",
        "app_name": "MyOpel"
    },
    "clientsB2CVauxhall": {
        "brand_code": "OV",  # Vauxhall uses same as Opel
        "app_name": "MyVauxhall"
    }
}


class PSAMQTTClient:
    """
    PSA MQTT Client for vehicle remote control

    This client handles:
    - OTP code generation
    - Remote access token exchange
    - MQTT connection and authentication
    - Command sending to vehicle
    """

    def __init__(self, client_id, customer_id, realm, vin, oauth_access_token):
        """
        Initialize PSA MQTT Client

        Args:
            client_id: PSA API client ID
            customer_id: PSA customer ID (e.g., "AP-XXXXXX")
            realm: PSA realm (e.g., "clientsB2CPeugeot")
            vin: Vehicle Identification Number
            oauth_access_token: OAuth access token for API calls
        """
        self.client_id = client_id
        self.customer_id = customer_id
        self.realm = realm
        self.vin = vin
        self.oauth_access_token = oauth_access_token

        # Get MQTT customer ID (brand-specific format)
        brand_code = customer_id[:2]
        mqtt_brand_code = REALM_INFO.get(realm, {}).get("brand_code", brand_code)
        self.mqtt_customer_id = mqtt_brand_code + customer_id[2:]

        # Remote access token (for MQTT auth)
        self.remote_access_token = None
        self.remote_refresh_token = None

        # MQTT client
        self.mqtt_client = None
        self.connected = False

        logger.info(f"Initialized PSA MQTT Client for {self.vin}")
        logger.info(f"Customer ID: {self.customer_id}")
        logger.info(f"MQTT Customer ID: {self.mqtt_customer_id}")

    def get_remote_access_token_with_otp(self, otp_code):
        """
        Exchange OTP code for remote access token

        Args:
            otp_code: 6-character OTP code (from standalone_otp_flow)

        Returns:
            dict with access_token and refresh_token, or None on error
        """
        logger.info("Exchanging OTP code for remote access token...")

        url = f"{REMOTE_TOKEN_URL}?client_id={self.client_id}"
        headers = {
            "Authorization": f"Bearer {self.oauth_access_token}",
            "x-introspect-realm": self.realm,
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
                self.remote_access_token = data["access_token"]
                self.remote_refresh_token = data.get("refresh_token")
                logger.info("✓ Remote access token obtained successfully")
                logger.debug(f"Access token: {self.remote_access_token[:20]}...")
                return data
            else:
                logger.error(f"✗ Failed to get remote access token: {data}")
                return None

        except requests.RequestException as e:
            logger.error(f"✗ Request failed: {e}")
            return None

    def refresh_remote_access_token(self):
        """
        Refresh remote access token using refresh token

        Returns:
            True if successful, False otherwise
        """
        if not self.remote_refresh_token:
            logger.error("No remote refresh token available")
            return False

        logger.info("Refreshing remote access token...")

        url = f"{REMOTE_TOKEN_URL}?client_id={self.client_id}"
        headers = {
            "Authorization": f"Bearer {self.oauth_access_token}",
            "x-introspect-realm": self.realm,
            "accept": "application/hal+json",
            "User-Agent": "okhttp/4.8.0",
        }
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.remote_refresh_token
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "access_token" in data:
                self.remote_access_token = data["access_token"]
                if "refresh_token" in data:
                    self.remote_refresh_token = data["refresh_token"]
                logger.info("✓ Remote access token refreshed")
                return True
            else:
                logger.error(f"✗ Failed to refresh: {data}")
                return False

        except requests.RequestException as e:
            logger.error(f"✗ Refresh failed: {e}")
            return False

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("✓ Connected to MQTT server")
            self.connected = True

            # Subscribe to response and event topics
            resp_topic = f"{MQTT_RESP_TOPIC}{self.mqtt_customer_id}/#"
            event_topic = f"{MQTT_EVENT_TOPIC}{self.vin}"

            client.subscribe(resp_topic)
            client.subscribe(event_topic)

            logger.info(f"✓ Subscribed to: {resp_topic}")
            logger.info(f"✓ Subscribed to: {event_topic}")
        else:
            logger.error(f"✗ MQTT connection failed with code {rc}")
            self.connected = False

    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        logger.warning(f"Disconnected from MQTT server (code: {rc})")
        self.connected = False

    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        logger.info(f"Message received on {msg.topic}")

        try:
            data = json.loads(msg.payload.decode())
            logger.info(f"Payload: {json.dumps(data, indent=2)}")

            # Check for response codes
            if "return_code" in data:
                if data["return_code"] == "0":
                    logger.info("✓ Command successful")
                elif data["return_code"] == "400":
                    logger.warning("Token expired, need to refresh")
                else:
                    logger.error(f"✗ Command failed: {data.get('return_code')} - {data.get('reason', 'Unknown')}")
        except json.JSONDecodeError:
            logger.error(f"Failed to decode message: {msg.payload}")

    def connect_mqtt(self):
        """
        Connect to PSA MQTT server

        Returns:
            True if connected, False otherwise
        """
        if not self.remote_access_token:
            logger.error("No remote access token. Please get one first using get_remote_access_token_with_otp()")
            return False

        logger.info(f"Connecting to MQTT server: {MQTT_SERVER}:{MQTT_PORT}")

        # Create MQTT client
        self.mqtt_client = mqtt.Client(
            client_id=f"psa-{self.customer_id}",
            clean_session=True,
            protocol=mqtt.MQTTv311
        )

        # Set callbacks
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        self.mqtt_client.on_message = self._on_message

        # Set authentication (username is always "IMA_OAUTH_ACCESS_TOKEN")
        self.mqtt_client.username_pw_set("IMA_OAUTH_ACCESS_TOKEN", self.remote_access_token)

        # Enable TLS
        self.mqtt_client.tls_set()

        try:
            # Connect to server
            self.mqtt_client.connect(MQTT_SERVER, MQTT_PORT, 60)

            # Start network loop
            self.mqtt_client.loop_start()

            # Wait a bit for connection
            import time
            time.sleep(2)

            return self.connected

        except Exception as e:
            logger.error(f"✗ MQTT connection failed: {e}")
            return False

    def disconnect_mqtt(self):
        """Disconnect from MQTT server"""
        if self.mqtt_client:
            logger.info("Disconnecting from MQTT...")
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            self.connected = False

    def _generate_correlation_id(self):
        """Generate correlation ID for MQTT request"""
        date = datetime.utcnow()
        date_str = date.strftime(PSA_CORRELATION_DATE_FORMAT)[:-3]
        uuid_str = str(uuid4()).replace("-", "")
        return uuid_str + date_str

    def send_command(self, command, parameters):
        """
        Send command to vehicle via MQTT

        Args:
            command: Command endpoint (e.g., "/VehCharge", "/Doors", "/Horn")
            parameters: Command parameters (dict)

        Returns:
            True if sent, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to MQTT. Call connect_mqtt() first.")
            return False

        # Build MQTT topic
        topic = f"{MQTT_REQ_TOPIC}{self.mqtt_customer_id}{command}"

        # Build message
        message = {
            "access_token": self.remote_access_token,
            "customer_id": self.mqtt_customer_id,
            "correlation_id": self._generate_correlation_id(),
            "req_date": datetime.utcnow().strftime(PSA_DATE_FORMAT),
            "vin": self.vin,
            "req_parameters": parameters
        }

        # Publish message
        logger.info(f"Sending command to: {topic}")
        logger.info(f"Parameters: {parameters}")

        result = self.mqtt_client.publish(topic, json.dumps(message))

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("✓ Command sent successfully")
            return True
        else:
            logger.error(f"✗ Failed to send command (code: {result.rc})")
            return False

    # Convenience methods for common commands

    def charge_now(self):
        """Start charging immediately"""
        return self.send_command("/VehCharge", {
            "program": {"hour": 0, "minute": 0},
            "type": "immediate"
        })

    def charge_delayed(self, hour, minute):
        """Set delayed charging"""
        return self.send_command("/VehCharge", {
            "program": {"hour": hour, "minute": minute},
            "type": "delayed"
        })

    def lock_doors(self):
        """Lock vehicle doors"""
        return self.send_command("/Doors", {"action": "lock"})

    def unlock_doors(self):
        """Unlock vehicle doors"""
        return self.send_command("/Doors", {"action": "unlock"})

    def horn(self, count=3):
        """Activate horn"""
        return self.send_command("/Horn", {
            "nb_horn": count,
            "action": "activate"
        })

    def lights(self, duration=60):
        """Activate lights (duration in seconds)"""
        return self.send_command("/Lights", {
            "action": "activate",
            "duration": duration
        })

    def preconditioning(self, activate=True):
        """Activate/deactivate preconditioning"""
        return self.send_command("/ThermalPrecond", {
            "asap": "activate" if activate else "deactivate",
            "programs": {
                "program1": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
                "program2": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
                "program3": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0},
                "program4": {"day": [0, 0, 0, 0, 0, 0, 0], "hour": 34, "minute": 7, "on": 0}
            }
        })

    def wakeup(self):
        """Wake up vehicle (get charge status)"""
        return self.send_command("/VehCharge/state", {"action": "state"})


def main():
    """Example usage"""
    print("=" * 70)
    print("PSA MQTT Connection Example")
    print("=" * 70)
    print()

    # Step 1: Configuration
    print("Step 1: Configuration")
    print("-" * 70)

    # You need to provide these values
    CLIENT_ID = input("Enter your PSA client ID: ").strip()
    CUSTOMER_ID = input("Enter your customer ID (e.g., AP-XXXXXX): ").strip()
    REALM = input("Enter realm (e.g., clientsB2CPeugeot): ").strip()
    VIN = input("Enter your vehicle VIN: ").strip()
    OAUTH_ACCESS_TOKEN = input("Enter your OAuth access token: ").strip()

    print()

    # Step 2: Get OTP code
    print("Step 2: Get OTP Code")
    print("-" * 70)

    otp_code = None
    if HAS_OTP:
        print("Checking for saved OTP session...")
        otp_session = load_otp("otp.bin")
        if otp_session:
            try:
                otp_code = otp_session.get_otp_code()
                print(f"✓ OTP Code generated: {otp_code}")
            except Exception as e:
                print(f"✗ Failed to generate OTP: {e}")

    if not otp_code:
        otp_code = input("Enter OTP code manually: ").strip()

    print()

    # Step 3: Create MQTT client
    print("Step 3: Initialize MQTT Client")
    print("-" * 70)

    client = PSAMQTTClient(
        client_id=CLIENT_ID,
        customer_id=CUSTOMER_ID,
        realm=REALM,
        vin=VIN,
        oauth_access_token=OAUTH_ACCESS_TOKEN
    )

    print()

    # Step 4: Get remote access token
    print("Step 4: Get Remote Access Token")
    print("-" * 70)

    result = client.get_remote_access_token_with_otp(otp_code)
    if not result:
        print("✗ Failed to get remote access token")
        return

    print()

    # Step 5: Connect to MQTT
    print("Step 5: Connect to MQTT Server")
    print("-" * 70)

    if not client.connect_mqtt():
        print("✗ Failed to connect to MQTT")
        return

    print()

    # Step 6: Send commands
    print("Step 6: Send Commands")
    print("-" * 70)
    print("Available commands:")
    print("  1. Charge now")
    print("  2. Lock doors")
    print("  3. Unlock doors")
    print("  4. Horn")
    print("  5. Lights")
    print("  6. Wakeup")
    print("  0. Exit")
    print()

    import time

    while True:
        choice = input("Enter command number (0-6): ").strip()

        if choice == "0":
            break
        elif choice == "1":
            client.charge_now()
        elif choice == "2":
            client.lock_doors()
        elif choice == "3":
            client.unlock_doors()
        elif choice == "4":
            client.horn()
        elif choice == "5":
            client.lights()
        elif choice == "6":
            client.wakeup()
        else:
            print("Invalid choice")

        # Wait for response
        time.sleep(2)
        print()

    # Cleanup
    client.disconnect_mqtt()
    print("\nDisconnected. Goodbye!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠  Interrupted by user")
        sys.exit(0)
