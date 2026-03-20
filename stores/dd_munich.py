import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Berlin")

def fetch_deck_and_dice_events():
    print("Hole Events von Deck and Dice...")

    url = "https://www.dd-munich.de/event-list"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print("Fehler bei Deck and Dice:", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    events = []

    for item in soup.select("div[data-hook='event-item']"):
        title_el = item.select_one("h3")
        date_el = item.select_one("time")

        if not title_el or not date_el:
            continue

        title = title_el.get_text(strip=True)
        date_str = date_el.get("datetime")

        try:
            start = datetime.fromisoformat(date_str).replace(tzinfo=TZ)
        except:
            continue

        end = start + timedelta(hours=3)

        events.append({
            "title": title,
            "start": start,
            "end": end,
            "location": "Deck & Dice München",
            "url": url,
            "description": "",
        })

    print(f"Deck & Dice Events gefunden: {len(events)}")
    return events
