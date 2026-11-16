from dotenv import load_dotenv
import os
import time
import psycopg2
import requests

load_dotenv()
db_url = os.getenv("DATABASE_URL")

connection = psycopg2.connect(db_url)
cursor = connection.cursor()
print("1. Connected to database")

cursor.execute("""
    SELECT id, min_lat, min_lon, max_lat, max_lon
    FROM cities
    WHERE slug = 'berlin'
""")
city_id, min_lat, min_lon, max_lat, max_lon = cursor.fetchone()

cursor.execute("SELECT id FROM categories WHERE slug = 'cafe'")
category_id = cursor.fetchone()[0]
print("2. Berlin:", city_id, "| cafe category:", category_id)

query = f"""
[out:json][timeout:180];
nwr["amenity"="cafe"]({min_lat},{min_lon},{max_lat},{max_lon});
out center;
"""

url = "https://overpass-api.de/api/interpreter"
headers = {"User-Agent": "CityPulse/1.0"}
bbox_text = f"{min_lat},{min_lon},{max_lat},{max_lon}"

cursor.execute("""
    INSERT INTO ingest_runs (city_id, category_id, source, bbox, status)
    VALUES (%s, %s, 'overpass', %s, 'running')
    RETURNING id
""", (city_id, category_id, bbox_text))
run_id = cursor.fetchone()[0]
connection.commit()
print("3. Ingestion run started:", run_id)

try:
    print("4. Sending request to Overpass")

    for attempt in range(3):
        response = requests.post(url, data=query, headers=headers, timeout=200)
        if response.status_code == 200:
            break
        print(f"   Attempt {attempt + 1} failed with {response.status_code}, retrying...")
        time.sleep(10)

    response.raise_for_status()
    data = response.json()

    places_found = len(data["elements"])
    places_inserted = 0
    places_updated = 0
    print("5. Elements returned:", places_found)

    for element in data["elements"]:

        if element["type"] == "node":
            lat = element["lat"]
            lon = element["lon"]
        else:
            lat = element["center"]["lat"]
            lon = element["center"]["lon"]

        osm_type = element["type"]
        osm_id = element["id"]

        tags = element.get("tags", {})
        name = tags.get("name")
        opening_hours_raw = tags.get("opening_hours")

        if opening_hours_raw:
            hours_policy = "parsed"
        else:
            hours_policy = "unknown"

        cursor.execute("""
            INSERT INTO places (
                city_id, category_id, osm_type, osm_id, name,
                geom, opening_hours_raw, hours_policy
            )
            VALUES (
                %s, %s, %s, %s, %s,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                %s, %s
            )
            ON CONFLICT (osm_type, osm_id) DO UPDATE
            SET name = EXCLUDED.name,
                geom = EXCLUDED.geom,
                opening_hours_raw = EXCLUDED.opening_hours_raw,
                hours_policy = EXCLUDED.hours_policy,
                last_seen_at = now()
            RETURNING (xmax = 0) AS was_inserted
        """, (
            city_id, category_id, osm_type, osm_id, name,
            lon, lat, opening_hours_raw, hours_policy
        ))

        if cursor.fetchone()[0]:
            places_inserted += 1
        else:
            places_updated += 1

    connection.commit()

    cursor.execute("""
        UPDATE ingest_runs
        SET status = 'success',
            finished_at = now(),
            places_found = %s,
            places_inserted = %s,
            places_updated = %s
        WHERE id = %s
    """, (places_found, places_inserted, places_updated, run_id))
    connection.commit()

    print(f"6. Done. Found {places_found}, inserted {places_inserted}, updated {places_updated}")

except Exception as error:
    connection.rollback()

    cursor.execute("""
        UPDATE ingest_runs
        SET status = 'failed',
            finished_at = now(),
            error_message = %s
        WHERE id = %s
    """, (str(error), run_id))
    connection.commit()

    print("FAILED:", error)
    raise

finally:
    cursor.close()
    connection.close()