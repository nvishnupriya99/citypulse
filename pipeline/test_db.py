from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

db_url = os.getenv("DATABASE_URL")
print("DB URL:", db_url)

connection = psycopg2.connect(db_url)
cursor = connection.cursor()

cursor.execute("""
    INSERT INTO places (city_id, category_id, osm_type, osm_id, name, geom, hours_policy)
    VALUES (1, 1, 'node', 999999, 'Test Cafe',
            ST_SetSRID(ST_MakePoint(13.405, 52.52), 4326)::geography,
            'unknown') ON CONFLICT (osm_type, osm_id) DO UPDATE
SET name = EXCLUDED.name,
    geom = EXCLUDED.geom,
    last_seen_at = now()
""")
connection.commit()
print("Inserted")

cursor.close()
connection.close()


