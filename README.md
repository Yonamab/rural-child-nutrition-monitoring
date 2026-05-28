# Rural Child Nutrition and Growth Monitoring System

## Project Overview

This project is an educational prototype for collecting, processing, and storing child nutrition data using MQTT, Python, Docker, MariaDB, MongoDB, and Neo4j.

The system simulates child nutrition measurements from rural communities. A Python MQTT publisher generates fake child nutrition data and sends it to a Mosquitto MQTT broker. A Python subscriber receives the data, applies simple nutrition alert rules, and stores the results in three different database platforms.

This project is for academic purposes only. It is not a real medical diagnosis system.

## Technologies Used

- Python 3
- MQTT
- Eclipse Mosquitto
- Docker and Docker Compose
- MariaDB
- MongoDB
- Neo4j
- Git and GitHub
- VS Code

Python libraries:

- paho-mqtt
- pymysql
- pymongo
- neo4j
- python-dotenv
- pandas

## System Architecture

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

## MQTT Message Example

The publisher sends child nutrition data to this MQTT topic:

```text
child/nutrition
```

Example message:

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

## Alert Rules

The Python subscriber applies these simple alert rules:

| Condition | Alert |
|---|---|
| MUAC < 11.5 | Severe Nutrition Risk |
| MUAC >= 11.5 and MUAC < 12.5 | Moderate Nutrition Risk |
| feeding_frequency < 3 | Low Feeding Frequency |
| diarrhea and MUAC < 12.5 | Priority Follow-up |
| no rule matched | Normal |

## Database Usage

### MariaDB

MariaDB stores structured relational data in tables:

- villages
- clinics
- health_workers
- children
- measurements
- alerts

### MongoDB

MongoDB stores the raw MQTT JSON messages.

Database:

```text
nutrition_raw_db
```

Collection:

```text
raw_messages
```

### Neo4j

Neo4j stores graph relationships between children, villages, clinics, health workers, measurements, nutrition statuses, and alerts.

Graph relationships:

```text
Child LIVES_IN Village
Child SCREENED_BY HealthWorker
HealthWorker WORKS_AT Clinic
Child HAS_MEASUREMENT GrowthMeasurement
GrowthMeasurement INDICATES NutritionStatus
NutritionStatus TRIGGERS Alert
```

## Project Structure

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

## Setup Instructions

Clone the repository:

```bash
git clone <your-repository-url>
cd rural-child-nutrition-monitoring
```

Create the `.env` file:

```bash
cp .env.example .env
```

Start the Docker containers:

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

Create the MariaDB tables:

```bash
docker exec -i nutrition_mariadb mariadb -u root -proot_pass < database/mariadb_schema.sql
```

Create the Neo4j constraints:

```bash
docker exec -i nutrition_neo4j cypher-shell -u neo4j -p neo4j_password < database/neo4j_constraints.cypher
```

Create and activate the Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the System

Start the subscriber in one terminal:

```bash
source venv/bin/activate
python subscriber/nutrition_processor.py
```

Start the publisher in another terminal:

```bash
source venv/bin/activate
python publisher/simulate_child_nutrition_data.py
```

The publisher sends simulated child nutrition messages through MQTT. The subscriber receives the messages, generates alerts, and stores the data in MariaDB, MongoDB, and Neo4j.

## Testing the Databases

### MariaDB

```bash
docker exec -it nutrition_mariadb mariadb -u root -proot_pass
```

```sql
USE nutrition_db;
SELECT * FROM children;
SELECT * FROM measurements;
SELECT * FROM alerts;
EXIT;
```

### MongoDB

```bash
docker exec -it nutrition_mongodb mongosh
```

```javascript
use nutrition_raw_db
db.raw_messages.findOne()
db.raw_messages.countDocuments()
exit
```

### Neo4j

Open Neo4j Browser:

```text
http://localhost:7474
```

Login:

```text
Username: neo4j
Password: neo4j_password
```

Run:

```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 50;
```

## Screenshots

Project screenshots are stored in the `screenshots/` folder and include Docker containers, publisher output, subscriber output, MariaDB query results, MongoDB stored documents, Neo4j graph visualization, and the GitHub repository page.

## Limitations

- The data is simulated.
- The alert rules are simplified.
- The system is not a real medical diagnosis tool.
- Authentication is basic because this is a local academic prototype.

## Future Work

Possible improvements include:

- Adding a web dashboard
- Adding manual data entry for health workers
- Improving authentication and security
- Adding larger performance tests
- Connecting to real IoT devices or mobile data collection tools

## Author

Name: Yonathan Abaineh Munshea  
GitHub Username: Yonamab