#!/usr/bin/env python3
"""
PSA Vehicle Status Monitor via MQTT

This script connects to PSA MQTT and monitors vehicle status in real-time.

Usage:
    python mqtt_vehicle_monitor.py <remote_access_token> <customer_id> <vin>

Example:
    python mqtt_vehicle_monitor.py \
        'eyJhbGc...' \
        'APACNT200001549013' \
        'VF3XXXXXXXXXXXXXXX'

What it does:
- Subscribes to vehicle event and response topics
- Displays all messages received (status updates, command responses)
- Can optionally send wakeup command to request current status
"""

import sys
import json
import time
from datetime import datetime
from uuid import uuid4

try:
    import paho.mqtt.client as mqtt
except ModuleNotFoundError:
    print("✗ Error: paho-mqtt not installed")
    print("  Install with: pip install paho-mqtt")
    sys.exit(1)

# MQTT Configuration
MQTT_SERVER = "mwa.mpsa.com"
MQTT_PORT = 8885
MQTT_RESP_TOPIC = "psa/RemoteServices/to/cid/"
MQTT_EVENT_TOPIC = "psa/RemoteServices/events/MPHRTServices/"
MQTT_REQ_TOPIC = "psa/RemoteServices/from/cid/"

# Formats for PSA dates
PSA_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
PSA_CORRELATION_DATE_FORMAT = "%Y%m%d%H%M%S%f"


def generate_correlation_id():
    """Generate PSA correlation ID"""
    date = datetime.utcnow()
    date_str = date.strftime(PSA_CORRELATION_DATE_FORMAT)[:-3]
    uuid_str = str(uuid4()).replace("-", "")
    return uuid_str + date_str


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print(f"✓ Connected to {MQTT_SERVER}:{MQTT_PORT}")

        customer_id = userdata['customer_id']
        vin = userdata['vin']

        # Subscribe to response topic
        resp_topic = f"{MQTT_RESP_TOPIC}{customer_id}/#"
        client.subscribe(resp_topic)
        print(f"✓ Subscribed to: {resp_topic}")

        # Subscribe to event topic
        event_topic = f"{MQTT_EVENT_TOPIC}{vin}/#"
        client.subscribe(event_topic)
        print(f"✓ Subscribed to: {event_topic}")

        print("\n" + "=" * 70)
        print("Monitoring vehicle status... (Press Ctrl+C to exit)")
        print("=" * 70)
        print("\nType 'wakeup' and press Enter to request current status")
        print()
    else:
        print(f"✗ Connection failed with code {rc}")
        if rc == 5:
            print("  → Authentication failed (check your remote access token)")


def on_disconnect(client, userdata, rc):
    """Callback when disconnected"""
    if rc != 0:
        print(f"\n⚠  Disconnected unexpectedly (code: {rc})")
        if rc == 1:
            print("  → Token expired - generate a new remote access token")


def on_message(client, userdata, msg):
    """Callback when message received"""
    print("\n" + "─" * 70)
    print(f"📨 Message received at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Topic: {msg.topic}")
    print("─" * 70)

    try:
        data = json.loads(msg.payload)

        # Pretty print the message
        if msg.topic.startswith(MQTT_RESP_TOPIC):
            print("Type: RESPONSE")
            if "return_code" in data:
                code = data["return_code"]
                if code == "0":
                    print(f"Status: ✓ SUCCESS (code {code})")
                else:
                    reason = data.get("reason", "Unknown")
                    print(f"Status: ✗ ERROR (code {code}): {reason}")
            print(f"\nData:\n{json.dumps(data, indent=2)}")

        elif msg.topic.startswith(MQTT_EVENT_TOPIC):
            print("Type: EVENT (Vehicle Status Update)")

            # Extract charging state
            if "charging_state" in data:
                charging = data["charging_state"]
                print("\n🔋 Charging State:")
                for key, value in charging.items():
                    print(f"  {key}: {value}")

            # Extract preconditioning state
            if "precond_state" in data:
                precond = data["precond_state"]
                print("\n🌡️  Preconditioning State:")
                for key, value in precond.items():
                    if key != "programs":
                        print(f"  {key}: {value}")

            # Extract VIN
            if "vin" in data:
                print(f"\n🚗 VIN: {data['vin']}")

            print(f"\n📄 Full Data:\n{json.dumps(data, indent=2)}")

        else:
            print(f"Data:\n{json.dumps(data, indent=2)}")

    except json.JSONDecodeError:
        print(f"Raw payload: {msg.payload}")

    print("─" * 70)


def send_wakeup(client, remote_token, customer_id, vin):
    """Send wakeup command to request vehicle status"""
    print("\n📤 Sending wakeup command to vehicle...")

    topic = f"{MQTT_REQ_TOPIC}{customer_id}/VehCharge/state"

    message = {
        "access_token": remote_token,
        "customer_id": customer_id,
        "correlation_id": generate_correlation_id(),
        "req_date": datetime.utcnow().strftime(PSA_DATE_FORMAT),
        "vin": vin,
        "req_parameters": {
            "action": "state"
        }
    }

    client.publish(topic, json.dumps(message))
    print(f"✓ Published to: {topic}")
    print(f"  (waiting for response...)")


def main():
    if len(sys.argv) != 4:
        print("Usage: python mqtt_vehicle_monitor.py <remote_access_token> <customer_id> <vin>")
        print("\nExample:")
        print("  python mqtt_vehicle_monitor.py \\")
        print("    'eyJhbGc...' \\")
        print("    'APACNT200001549013' \\")
        print("    'VF3XXXXXXXXXXXXXXX'")
        print("\nGet remote_access_token using:")
        print("  python get_remote_token_for_mqtt.py <oauth_token> <client_id> <realm>")
        sys.exit(1)

    remote_token = sys.argv[1]
    customer_id = sys.argv[2]
    vin = sys.argv[3]

    print("=" * 70)
    print("PSA Vehicle Status Monitor")
    print("=" * 70)
    print(f"Customer ID: {customer_id}")
    print(f"VIN: {vin}")
    print(f"Token: {remote_token[:20]}...")
    print()

    # Create MQTT client
    client = mqtt.Client(
        client_id=None,  # Auto-generate
        clean_session=True,
        protocol=mqtt.MQTTv311,
        userdata={
            'customer_id': customer_id,
            'vin': vin,
            'remote_token': remote_token
        }
    )

    # Set callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Set username/password
    client.username_pw_set("IMA_OAUTH_ACCESS_TOKEN", remote_token)

    # Enable TLS
    client.tls_set_context()

    # Connect
    print(f"Connecting to {MQTT_SERVER}:{MQTT_PORT}...")
    try:
        client.connect(MQTT_SERVER, MQTT_PORT, 60)
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)

    # Start loop in background
    client.loop_start()

    try:
        # Wait for user input
        while True:
            user_input = input()
            if user_input.strip().lower() == 'wakeup':
                send_wakeup(client, remote_token, customer_id, vin)
            elif user_input.strip().lower() == 'quit':
                break
            else:
                print("Commands: 'wakeup' to request status, 'quit' to exit")

    except KeyboardInterrupt:
        print("\n\n✓ Shutting down...")

    finally:
        client.loop_stop()
        client.disconnect()
        print("✓ Disconnected")


if __name__ == "__main__":
    main()
