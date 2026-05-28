import json
import os

import paho.mqtt.client as mqtt
import pymysql
from dotenv import load_dotenv
from pymongo import MongoClient
from neo4j import GraphDatabase


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

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j_password")


mongo_client = MongoClient(MONGODB_URI)
mongo_db = mongo_client[MONGODB_DATABASE]
mongo_collection = mongo_db[MONGODB_COLLECTION]

neo4j_driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)


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


def save_to_neo4j(data, alerts):
    measurement_id = f"M-{data['child_id']}-{data['timestamp'].replace(' ', '-').replace(':', '')}"

    with neo4j_driver.session() as session:
        session.execute_write(create_graph_data, data, alerts, measurement_id)

    print("Saved graph data to Neo4j.")


def create_graph_data(tx, data, alerts, measurement_id):
    query = """
    MERGE (v:Village {village_id: $village_id})
    SET v.village_name = $village_name

    MERGE (cl:Clinic {clinic_id: $clinic_id})
    SET cl.clinic_name = $clinic_name

    MERGE (hw:HealthWorker {health_worker_id: $health_worker_id})
    SET hw.health_worker_name = $health_worker_name

    MERGE (c:Child {child_id: $child_id})
    SET c.name = $name,
        c.age_months = $age_months,
        c.gender = $gender

    MERGE (c)-[:LIVES_IN]->(v)
    MERGE (c)-[:SCREENED_BY]->(hw)
    MERGE (hw)-[:WORKS_AT]->(cl)

    MERGE (m:GrowthMeasurement {measurement_id: $measurement_id})
    SET m.weight_kg = $weight_kg,
        m.height_cm = $height_cm,
        m.muac_cm = $muac_cm,
        m.feeding_frequency = $feeding_frequency,
        m.symptoms = $symptoms,
        m.timestamp = $timestamp

    MERGE (c)-[:HAS_MEASUREMENT]->(m)
    """

    tx.run(
        query,
        village_id=data["village_id"],
        village_name=data["village_name"],
        clinic_id=data["clinic_id"],
        clinic_name=f"Clinic_{data['clinic_id']}",
        health_worker_id=data["health_worker_id"],
        health_worker_name=f"HealthWorker_{data['health_worker_id']}",
        child_id=data["child_id"],
        name=data["name"],
        age_months=data["age_months"],
        gender=data["gender"],
        measurement_id=measurement_id,
        weight_kg=data["weight_kg"],
        height_cm=data["height_cm"],
        muac_cm=data["muac_cm"],
        feeding_frequency=data["feeding_frequency"],
        symptoms=",".join(data.get("symptoms", [])),
        timestamp=data["timestamp"]
    )

    for index, alert in enumerate(alerts, start=1):
        alert_id = f"A-{measurement_id}-{index}"

        alert_query = """
        MATCH (m:GrowthMeasurement {measurement_id: $measurement_id})

        MERGE (s:NutritionStatus {status_name: $status_name})

        MERGE (a:Alert {alert_id: $alert_id})
        SET a.alert_type = $alert_type,
            a.alert_message = $alert_message,
            a.severity = $severity,
            a.created_at = $created_at

        MERGE (m)-[:INDICATES]->(s)
        MERGE (s)-[:TRIGGERS]->(a)
        """

        tx.run(
            alert_query,
            measurement_id=measurement_id,
            status_name=alert["alert_type"],
            alert_id=alert_id,
            alert_type=alert["alert_type"],
            alert_message=alert["alert_message"],
            severity=alert["severity"],
            created_at=data["timestamp"]
        )


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
        save_to_neo4j(data, alerts)

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