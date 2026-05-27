CREATE CONSTRAINT child_id_unique IF NOT EXISTS
FOR (c:Child)
REQUIRE c.child_id IS UNIQUE;

CREATE CONSTRAINT village_id_unique IF NOT EXISTS
FOR (v:Village)
REQUIRE v.village_id IS UNIQUE;

CREATE CONSTRAINT clinic_id_unique IF NOT EXISTS
FOR (cl:Clinic)
REQUIRE cl.clinic_id IS UNIQUE;

CREATE CONSTRAINT health_worker_id_unique IF NOT EXISTS
FOR (hw:HealthWorker)
REQUIRE hw.health_worker_id IS UNIQUE;

CREATE CONSTRAINT measurement_id_unique IF NOT EXISTS
FOR (m:GrowthMeasurement)
REQUIRE m.measurement_id IS UNIQUE;

CREATE CONSTRAINT status_name_unique IF NOT EXISTS
FOR (s:NutritionStatus)
REQUIRE s.status_name IS UNIQUE;

CREATE CONSTRAINT alert_id_unique IF NOT EXISTS
FOR (a:Alert)
REQUIRE a.alert_id IS UNIQUE;