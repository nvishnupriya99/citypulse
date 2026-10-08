from dotenv import load_dotenv
import os
import time
import psycopg2
import requests

print("1. Starting script")

load_dotenv()
db_url = os.getenv("DATABASE_URL")

print("2. Connecting to database")
connection = psycopg2.connect(db_url)
cursor = connection.cursor()
print("3. Connected to database")

cursor.execute("""
    SELECT id, min_lat, min_lon, max_lat, max_lon
    FROM cities
    WHERE slug = 'berlin'
""")
city_id, min_lat, min_lon, max_lat, max_lon = cursor.fetchone()
print("4. Berlin:", city_id, min_lat, min_lon, max_lat, max_lon)

cursor.execute("SELECT id FROM categories WHERE slug = 'cafe'")
category_id = cursor.fetchone()[0]
print("5. Cafe category ID:", category_id)

query = f"""
[out:json][timeout:180];
nwr["amenity"="cafe"]({min_lat},{min_lon},{max_lat},{max_lon});
out center;
"""

url = "https://overpass-api.de/api/interpreter"
headers = {"User-Agent": "CityPulse/1.0"}

print("6. Sending request to Overpass")

for attempt in range(3):
    response = requests.post(url, data=query, headers=headers, timeout=200)
    if response.status_code == 200:
        break
    print(f"   Attempt {attempt + 1} failed with {response.status_code}, retrying...")
    time.sleep(10)

response.raise_for_status()
data = response.json()

print("7. Number of cafes:", len(data["elements"]))
print("8. Starting database insert")

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
    """, (
        city_id, category_id, osm_type, osm_id, name,
        lon, lat, opening_hours_raw, hours_policy
    ))

connection.commit()
print("9. Insert committed")

cursor.close()
connection.close()
print("10. Done")