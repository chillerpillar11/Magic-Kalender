import requests
from datetime import datetime
from zoneinfo import ZoneInfo


TZ = ZoneInfo("Europe/Berlin")


def fetch_funtainment_events():
    url = "https://www.funtainment.de/api/events"  # deine bestehende URL hier
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    events = []
    for item in data:
        # Passe diese Keys an deine bestehende Struktur an
        start = datetime.fromisoformat(item["start"]).replace(tzinfo=TZ)
        end = datetime.fromisoformat(item["end"]).replace(tzinfo=TZ)

        events.append(
            {
                "title": item["title"],
                "start": start,
                "end": end,
                "location": "Funtainment",
                "url": item.get("url", "https://www.funtainment.de"),
                "description": item.get("description", ""),
            }
        )

    print(f"Funtainment Events gefunden: {len(events)}")
    return events
