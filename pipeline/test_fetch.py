import requests

url = "https://overpass-api.de/api/interpreter"
headers = {"User-Agent": "CityPulse/0.1 (student project)"}

query = """
[out:json][timeout:80];
nwr["amenity"="cafe"](52.3383,13.0884,52.6755,13.7611);
out center 200;
"""

response = requests.post(url, data=query, headers=headers)
data = response.json()
for element in data["elements"]:
    if "lat" in element:
        lat = element["lat"]
        lon = element["lon"]
    else:
        lat = element["center"]["lat"]
        lon = element["center"]["lon"]

    print(element["type"], element["id"], lat, lon, element["tags"].get("name"))