import json

with open("datasets/trains.json", "r", encoding="utf-8") as f:
    data = json.load(f)

limits = {
    "number": 20,
    "return_train": 20,
    "type": 50,
    "zone": 20,
    "name": 150,
}

found = False

for feature in data["features"]:
    p = feature.get("properties", {})

    for field, limit in limits.items():
        value = str(p.get(field) or "")

        if len(value) > limit:
            found = True
            print(f"{field}: {len(value)} -> {value}")

if not found:
    print("No values exceed the configured limits.")