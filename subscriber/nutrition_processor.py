import json
import os

import paho.mqtt.client as mqtt
from dotenv import load_dotenv


# Load settings from the .env file
load_dotenv()

# MQTT settings
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "child/nutrition")


def generate_alerts(data):
    """
    Check one child nutrition message and return a list of alerts.

    The input data is a Python dictionary created from the MQTT JSON message.
    The output is a list of alert dictionaries.
    """

    alerts = []

    child_id = data.get("child_id")
    muac_cm = float(data.get("muac_cm", 0))
    feeding_frequency = int(data.get("feeding_frequency", 0))
    symptoms = data.get("symptoms", [])

    if muac_cm < 11.5:
        alerts.append({
            "alert_type": "Severe Nutrition Risk",
            "alert_message": f"Child {child_id} has MUAC {muac_cm} cm, which is below 11.5 cm.",
            "severity": "High"
        })

    elif 11.5 <= muac_cm < 12.5:
        alerts.append({
            "alert_type": "Moderate Nutrition Risk",
            "alert_message": f"Child {child_id} has MUAC {muac_cm} cm, which is between 11.5 and 12.5 cm.",
            "severity": "Medium"
        })

    if feeding_frequency < 3:
        alerts.append({
            "alert_type": "Low Feeding Frequency",
            "alert_message": f"Child {child_id} has feeding frequency of {feeding_frequency} times per day.",
            "severity": "Medium"
        })

    if "diarrhea" in symptoms and muac_cm < 12.5:
        alerts.append({
            "alert_type": "Priority Follow-up",
            "alert_message": f"Child {child_id} has diarrhea and MUAC {muac_cm} cm, requiring follow-up.",
            "severity": "High"
        })

    if len(alerts) == 0:
        alerts.append({
            "alert_type": "Normal",
            "alert_message": f"Child {child_id} does not match the current nutrition risk rules.",
            "severity": "Low"
        })

    return alerts


def on_connect(client, userdata, flags, reason_code, properties):
    """
    This function runs automatically when the subscriber connects to MQTT.
    """

    if reason_code == 0:
        print("Connected to MQTT broker successfully.")
        print(f"Subscribing to topic: {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect. Reason code: {reason_code}")


def on_message(client, userdata, message):
    """
    This function runs automatically every time an MQTT message arrives.
    """

    print("\nNew MQTT message received.")
    print(f"Topic: {message.topic}")

    message_text = message.payload.decode("utf-8")
    print(f"Raw message: {message_text}")

    try:
        data = json.loads(message_text)
        print("Converted JSON into Python dictionary:")
        print(data)

        alerts = generate_alerts(data)

        print("Generated alerts:")
        for alert in alerts:
            print(f"- {alert['alert_type']} | Severity: {alert['severity']}")
            print(f"  {alert['alert_message']}")

    except json.JSONDecodeError:
        print("Error: received message is not valid JSON.")


def main():
    """
    Main program:
    create MQTT subscriber, connect to broker, and wait for messages.
    """

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    client.on_connect = on_connect
    client.on_message = on_message

    print("Starting nutrition subscriber...")
    print(f"Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}")

    client.connect(MQTT_HOST, MQTT_PORT, 60)

    print("Waiting for messages. Press CTRL + C to stop.")
    client.loop_forever()


if __name__ == "__main__":
    main()