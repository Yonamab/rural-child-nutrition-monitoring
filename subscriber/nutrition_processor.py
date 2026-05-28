import json
import os

import paho.mqtt.client as mqtt
import pymysql
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "child/nutrition")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "nutrition_raw_db")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "raw_messages")

MARIADB_HOST = os.getenv("MARIADB_HOST", "localhost")
MARIADB_PORT = int(os.getenv("MARIADB_PORT", 3306))
MARIADB_DATABASE = os.getenv("MARIADB_DATABASE", "nutrition_db")
MARIADB_USER = os.getenv("MARIADB_USER", "nutrition_user")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD", "nutrition_pass")


mongo_client = MongoClient(MONGODB_URI)
mongo_db = mongo_client[MONGODB_DATABASE]
mongo_collection = mongo_db[MONGODB_COLLECTION]


def get_mariadb_connection():
    connection = pymysql.connect(
        host=MARIADB_HOST,
        port=MARIADB_PORT,
        user=MARIADB_USER,
        password=MARIADB_PASSWORD,
        database=MARIADB_DATABASE,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

    return connection


def generate_alerts(data):
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


def save_to_mongodb(data, alerts):
    document = data.copy()
    document["alerts"] = alerts

    result = mongo_collection.insert_one(document)

    print(f"Saved raw message to MongoDB with document ID: {result.inserted_id}")


def save_to_mariadb(data, alerts):
    connection = get_mariadb_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO villages (village_id, village_name)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE village_name = VALUES(village_name)
                """,
                (data["village_id"], data["village_name"])
            )

            cursor.execute(
                """
                INSERT INTO clinics (clinic_id, clinic_name)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE clinic_name = VALUES(clinic_name)
                """,
                (data["clinic_id"], f"Clinic_{data['clinic_id']}")
            )

            cursor.execute(
                """
                INSERT INTO health_workers (health_worker_id, health_worker_name, clinic_id)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    health_worker_name = VALUES(health_worker_name),
                    clinic_id = VALUES(clinic_id)
                """,
                (
                    data["health_worker_id"],
                    f"HealthWorker_{data['health_worker_id']}",
                    data["clinic_id"]
                )
            )

            cursor.execute(
                """
                INSERT INTO children (child_id, name, age_months, gender, village_id)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    age_months = VALUES(age_months),
                    gender = VALUES(gender),
                    village_id = VALUES(village_id)
                """,
                (
                    data["child_id"],
                    data["name"],
                    data["age_months"],
                    data["gender"],
                    data["village_id"]
                )
            )

            symptoms_text = ",".join(data.get("symptoms", []))

            cursor.execute(
                """
                INSERT INTO measurements (
                    child_id,
                    weight_kg,
                    height_cm,
                    muac_cm,
                    feeding_frequency,
                    symptoms,
                    clinic_id,
                    health_worker_id,
                    measured_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data["child_id"],
                    data["weight_kg"],
                    data["height_cm"],
                    data["muac_cm"],
                    data["feeding_frequency"],
                    symptoms_text,
                    data["clinic_id"],
                    data["health_worker_id"],
                    data["timestamp"]
                )
            )

            for alert in alerts:
                cursor.execute(
                    """
                    INSERT INTO alerts (
                        child_id,
                        alert_type,
                        alert_message,
                        severity,
                        created_at
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        data["child_id"],
                        alert["alert_type"],
                        alert["alert_message"],
                        alert["severity"],
                        data["timestamp"]
                    )
                )

        connection.commit()
        print("Saved structured data to MariaDB.")

    except Exception as error:
        connection.rollback()
        print(f"MariaDB error: {error}")

    finally:
        connection.close()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to MQTT broker successfully.")
        print(f"Subscribing to topic: {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect. Reason code: {reason_code}")


def on_message(client, userdata, message):
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

        save_to_mongodb(data, alerts)
        save_to_mariadb(data, alerts)

    except json.JSONDecodeError:
        print("Error: received message is not valid JSON.")
    except Exception as error:
        print(f"Error while processing message: {error}")


def main():
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