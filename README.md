# Rural Child Nutrition and Growth Monitoring System

## 1. Project Overview

The **Rural Child Nutrition and Growth Monitoring System** is an educational IoT and database prototype designed to collect, process, and store child nutrition data from rural communities.

The system simulates child growth and nutrition measurements that may be collected by rural health workers, clinics, or connected devices. A Python MQTT publisher generates simulated child nutrition records and sends them to an MQTT broker. A Python subscriber receives the messages, applies simple nutrition alert rules, and stores the processed data in three different database systems:

- **MariaDB** for structured relational data
- **MongoDB** for raw JSON message storage
- **Neo4j** for graph-based relationships

> **Disclaimer:** This project is not a medical diagnosis system. The data and alert rules are simplified and intended only for academic, database, and IoT learning purposes.

---

## 2. Technologies Used

### Core Technologies

- Python 3
- MQTT
- Eclipse Mosquitto
- Docker
- Docker Compose
- MariaDB
- MongoDB
- Neo4j
- Git and GitHub
- VS Code

### Python Libraries

- `paho-mqtt`
- `pymysql`
- `pymongo`
- `neo4j`
- `python-dotenv`
- `pandas`

---

## 3. System Architecture

The system follows a simple publish-subscribe architecture using MQTT.

```text
Python Publisher
    |
    | MQTT message
    v
Mosquitto MQTT Broker
    |
    | MQTT subscription
    v
Python Subscriber
    |
    |----> MongoDB: raw JSON messages
    |----> MariaDB: structured relational data
    |----> Neo4j: graph relationships
```

### Architecture Description

1. The **publisher** generates simulated child nutrition data.
2. The data is sent to the **Mosquitto MQTT broker** using the topic `child/nutrition`.
3. The **subscriber** listens for incoming MQTT messages.
4. The subscriber processes each message and applies nutrition alert rules.
5. The processed data is stored in MariaDB, MongoDB, and Neo4j.

---

## 4. MQTT Message Format

The publisher sends child nutrition data as a JSON message.

### Example Message

```json
{
  "child_id": "C001",
  "name": "Child_001",
  "age_months": 24,
  "gender": "F",
  "village_id": "V001",
  "village_name": "Village_A",
  "weight_kg": 9.8,
  "height_cm": 82,
  "muac_cm": 11.2,
  "feeding_frequency": 2,
  "symptoms": ["diarrhea", "loss_of_appetite"],
  "clinic_id": "CL001",
  "health_worker_id": "HW001",
  "timestamp": "2026-01-20 10:30:00"
}
```

### MQTT Topic

```text
child/nutrition
```

---

## 5. Nutrition Alert Rules

The subscriber applies simple rule-based logic to identify possible nutrition risks.

| Condition | Alert |
|---|---|
| `MUAC < 11.5` | Severe Nutrition Risk |
| `MUAC >= 11.5 and MUAC < 12.5` | Moderate Nutrition Risk |
| `feeding_frequency < 3` | Low Feeding Frequency |
| `diarrhea` and `MUAC < 12.5` | Priority Follow-up |
| No rule matched | Normal |

> These rules are simplified for demonstration purposes and should not be used for real medical decisions.

---

## 6. Database Design

This project stores the same incoming data in three different database systems to demonstrate relational, document-based, and graph-based data modeling.

---

### 6.1 MariaDB

MariaDB stores structured relational data.

#### Main Tables

- `villages`
- `clinics`
- `health_workers`
- `children`
- `measurements`
- `alerts`

MariaDB is used to organize data into related tables and support SQL-based queries.

---

### 6.2 MongoDB

MongoDB stores the raw MQTT JSON messages exactly as they are received.

#### Database

```text
nutrition_raw_db
```

#### Collection

```text
raw_messages
```

MongoDB is useful for preserving the original incoming message format and supporting flexible document storage.

---

### 6.3 Neo4j

Neo4j stores relationships between children, villages, health workers, clinics, measurements, nutrition statuses, and alerts.

#### Graph Relationships

```text
Child LIVES_IN Village
Child SCREENED_BY HealthWorker
HealthWorker WORKS_AT Clinic
Child HAS_MEASUREMENT GrowthMeasurement
GrowthMeasurement INDICATES NutritionStatus
NutritionStatus TRIGGERS Alert
```

Neo4j is used to explore connected data and visualize relationships in a graph format.

---

## 7. Project Structure

```text
rural-child-nutrition-monitoring/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
├── mqtt/
│   └── mosquitto.conf
├── publisher/
│   └── simulate_child_nutrition_data.py
├── subscriber/
│   └── nutrition_processor.py
├── database/
│   ├── mariadb_schema.sql
│   ├── neo4j_constraints.cypher
│   └── sample_queries.md
├── docs/
├── screenshots/
└── report/
```

---

## 8. Setup Instructions

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd rural-child-nutrition-monitoring
```

---

### Step 2: Create the Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

Update the `.env` file if required.

---

### Step 3: Start Docker Containers

Start all services using Docker Compose:

```bash
docker compose up -d
```

Check that the containers are running:

```bash
docker ps
```

Expected containers:

```text
nutrition_mosquitto
nutrition_mariadb
nutrition_mongodb
nutrition_neo4j
```

---

### Step 4: Create MariaDB Tables

Run the MariaDB schema file:

```bash
docker exec -i nutrition_mariadb mariadb -u root -proot_pass < database/mariadb_schema.sql
```

---

### Step 5: Create Neo4j Constraints

Run the Neo4j constraints file:

```bash
docker exec -i nutrition_neo4j cypher-shell -u neo4j -p neo4j_password < database/neo4j_constraints.cypher
```

---

### Step 6: Create a Python Virtual Environment

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## 9. Running the System

Open two terminal windows.

---

### Terminal 1: Start the Subscriber

```bash
source venv/bin/activate
python subscriber/nutrition_processor.py
```

The subscriber connects to the MQTT broker, listens for incoming messages, processes the nutrition data, generates alerts, and stores the data in the databases.

---

### Terminal 2: Start the Publisher

```bash
source venv/bin/activate
python publisher/simulate_child_nutrition_data.py
```

The publisher sends simulated child nutrition messages to the MQTT topic:

```text
child/nutrition
```

---

## 10. Testing the Databases

After running the publisher and subscriber, verify that data has been stored correctly.

---

### 10.1 Test MariaDB

Open the MariaDB shell:

```bash
docker exec -it nutrition_mariadb mariadb -u root -proot_pass
```

Run sample queries:

```sql
USE nutrition_db;

SELECT * FROM children;
SELECT * FROM measurements;
SELECT * FROM alerts;

EXIT;
```

---

### 10.2 Test MongoDB

Open the MongoDB shell:

```bash
docker exec -it nutrition_mongodb mongosh
```

Run sample commands:

```javascript
use nutrition_raw_db

db.raw_messages.findOne()
db.raw_messages.countDocuments()

exit
```

---

### 10.3 Test Neo4j

Open Neo4j Browser in your web browser:

```text
http://localhost:7474
```

Login details:

```text
Username: neo4j
Password: neo4j_password
```

Run this sample Cypher query:

```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 50;
```

---

## 11. Screenshots

Project screenshots are stored in the `screenshots/` folder and include Docker containers, MQTT publisher/subscriber output, MariaDB results, MongoDB documents, and Neo4j graph visualization.
---

## 12. Limitations

- The data is simulated and does not come from real medical devices.
- The nutrition alert rules are simplified and are not medical diagnosis rules.
- Authentication and security are simplified for local academic testing.
- The system is intended as an educational prototype.
- The project does not include a user interface or web dashboard.
- The system is not designed for real-world clinical deployment.

---

## 13. Future Work

Possible improvements include:

- Add a manual data entry form for health workers.
- Add a web dashboard for viewing child nutrition records.
- Add charts and analytics for growth monitoring.
- Add stronger authentication and role-based access control.
- Add data validation and error handling.
- Add real IoT sensor integration.
- Add SMS or email alerts for high-risk cases.
- Add automated reports for clinics and health workers.
- Add performance testing with larger datasets.
- Add deployment instructions for cloud environments.

---

## 14. Author

**Name:** Yonathan Abaineh Munshea

---

## 15. License

This project is created for academic and educational purposes.
