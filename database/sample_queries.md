# Sample Database Queries

This file contains useful queries for testing the Rural Child Nutrition and Growth Monitoring System.

---

## 1. MariaDB Queries

Enter MariaDB:

```bash
docker exec -it nutrition_mariadb mariadb -u root -proot_pass
```

Select the project database:

```sql
USE nutrition_db;
```

Show all tables:

```sql
SHOW TABLES;
```

View villages:

```sql
SELECT * FROM villages;
```

View children:

```sql
SELECT * FROM children;
```

View measurements:

```sql
SELECT * FROM measurements;
```

View alerts:

```sql
SELECT * FROM alerts;
```

Find severe nutrition risk alerts:

```sql
SELECT child_id, alert_type, severity, created_at
FROM alerts
WHERE alert_type = 'Severe Nutrition Risk';
```

Find children with MUAC below 11.5 cm:

```sql
SELECT child_id, muac_cm, measured_at
FROM measurements
WHERE muac_cm < 11.5;
```

Count alerts by severity:

```sql
SELECT severity, COUNT(*) AS total_alerts
FROM alerts
GROUP BY severity;
```

Count measurements per village:

```sql
SELECT v.village_name, COUNT(m.measurement_id) AS total_measurements
FROM villages v
JOIN children c ON v.village_id = c.village_id
JOIN measurements m ON c.child_id = m.child_id
GROUP BY v.village_name;
```

Find children with low feeding frequency:

```sql
SELECT child_id, feeding_frequency, measured_at
FROM measurements
WHERE feeding_frequency < 3;
```

Exit MariaDB:

```sql
EXIT;
```

---

## 2. MongoDB Queries

Enter MongoDB shell:

```bash
docker exec -it nutrition_mongodb mongosh
```

Show databases:

```javascript
show dbs
```

Use the project database:

```javascript
use nutrition_raw_db
```

Show collections:

```javascript
show collections
```

View all raw MQTT messages:

```javascript
db.raw_messages.find().pretty()
```

View one raw MQTT message:

```javascript
db.raw_messages.findOne()
```

Count all raw messages:

```javascript
db.raw_messages.countDocuments()
```

Find messages with severe nutrition risk:

```javascript
db.raw_messages.find({
  "alerts.alert_type": "Severe Nutrition Risk"
}).pretty()
```

Find children with MUAC below 11.5:

```javascript
db.raw_messages.find({
  "muac_cm": { "$lt": 11.5 }
}).pretty()
```

Find children with diarrhea:

```javascript
db.raw_messages.find({
  "symptoms": "diarrhea"
}).pretty()
```

Find messages from Village_A:

```javascript
db.raw_messages.find({
  "village_name": "Village_A"
}).pretty()
```

Exit MongoDB shell:

```javascript
exit
```

---

## 3. Neo4j Queries

Open Neo4j Browser:

```text
http://localhost:7474
```

Login:

```text
Username: neo4j
Password: neo4j_password
```

Show graph relationships:

```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 50;
```

Show all children:

```cypher
MATCH (c:Child)
RETURN c;
```

Show children and their villages:

```cypher
MATCH (c:Child)-[:LIVES_IN]->(v:Village)
RETURN c, v;
```

Show health workers and clinics:

```cypher
MATCH (hw:HealthWorker)-[:WORKS_AT]->(cl:Clinic)
RETURN hw, cl;
```

Show children, measurements, statuses, and alerts:

```cypher
MATCH (c:Child)-[:HAS_MEASUREMENT]->(m:GrowthMeasurement)-[:INDICATES]->(s:NutritionStatus)-[:TRIGGERS]->(a:Alert)
RETURN c, m, s, a;
```

Find severe nutrition risk cases:

```cypher
MATCH (c:Child)-[:HAS_MEASUREMENT]->(m:GrowthMeasurement)-[:INDICATES]->(s:NutritionStatus)
WHERE s.status_name = "Severe Nutrition Risk"
RETURN c.child_id, c.name, m.muac_cm, s.status_name;
```

Find priority follow-up cases:

```cypher
MATCH (c:Child)-[:HAS_MEASUREMENT]->(m:GrowthMeasurement)-[:INDICATES]->(s:NutritionStatus)
WHERE s.status_name = "Priority Follow-up"
RETURN c.child_id, c.name, m.symptoms, m.muac_cm, s.status_name;
```

Count children per village:

```cypher
MATCH (c:Child)-[:LIVES_IN]->(v:Village)
RETURN v.village_name, COUNT(c) AS total_children;
```

Count alerts by status:

```cypher
MATCH (m:GrowthMeasurement)-[:INDICATES]->(s:NutritionStatus)
RETURN s.status_name, COUNT(m) AS total_measurements;
```