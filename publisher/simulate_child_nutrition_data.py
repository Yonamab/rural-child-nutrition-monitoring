import json
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os


load_dotenv()


MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "child/nutrition")


def create_child_message(child_number):


    child_id = f"C{child_number:03d}"

    villages = [
        ("V001", "Village_A"),
        ("V002", "Village_B"),
        ("V003", "Village_C")
    ]

    clinics = ["CL001", "CL002"]
    health_workers = ["HW001", "HW002", "HW003"]

    possible_symptoms = [
        "diarrhea",
        "fever",
        "vomiting",
        "loss_of_appetite",
        "none"
    ]

    village_id, village_name = random.choice(villages)

    symptoms = random.sample(possible_symptoms, random.randint(1, 2))

    if "none" in symptoms and len(symptoms) > 1:
        symptoms = ["none"]

    message = {
        "child_id": child_id,
        "name": f"Child_{child_number:03d}",
        "age_months": random.randint(6, 59),
        "gender": random.choice(["M", "F"]),
        "village_id": village_id,
        "village_name": village_name,
        "weight_kg": round(random.uniform(5.0, 18.0), 1),
        "height_cm": round(random.uniform(55.0, 110.0), 1),
        "muac_cm": round(random.uniform(10.0, 15.0), 1),
        "feeding_frequency": random.randint(1, 5),
        "symptoms": symptoms,
        "clinic_id": random.choice(clinics),
        "health_worker_id": random.choice(health_workers),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return message


def main():

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    print("Connecting to MQTT broker...")
    client.connect(MQTT_HOST, MQTT_PORT, 60)

    print(f"Connected to MQTT broker at {MQTT_HOST}:{MQTT_PORT}")
    print(f"Publishing messages to topic: {MQTT_TOPIC}")

    for child_number in range(1, 11):
        message = create_child_message(child_number)

        json_message = json.dumps(message)

        client.publish(MQTT_TOPIC, json_message)

        print(f"Published message {child_number}:")
        print(json_message)
        print("-" * 60)

        time.sleep(2)

    client.disconnect()
    print("Finished publishing messages.")


if __name__ == "__main__":
    main()