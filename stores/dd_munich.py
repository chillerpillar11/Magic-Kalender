import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

TZ = ZoneInfo("Europe/Berlin")

MONTHS_DE = {
    "januar": 1, "februar": 2, "märz": 3, "april": 4, "mai": 5, "juni": 6,
    "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11, "dezember": 12
}

def fetch_dd_list_view_events(soup, url):
    events = []

    for li in soup.select('li[data-hook^="calendar-event-list-item"]'):
        title_el = li.select_one('[data-hook^="event-title"]')
        time_el = li.select_one('[data-hook^="event-time"]')

        if not title_el or not time_el:
            continue

        title = title_el.get_text(strip=True)
        time_text = time_el.get_text(strip=True)

        print("DEBUG DD LIST TITLE:", repr(title))
        print("DEBUG DD LIST TIME:", repr(time_text))

        # Datum aus data-hook extrahieren
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", li.get("data-hook", ""))
        if not m:
            continue

        year, month, day = map(int, m.groups())
        base_date = datetime(year, month, day, tzinfo=TZ)

        # Zeit normalisieren
        time_text = time_text.replace(".", ":")
        if "uhr" in time_text.lower():
            time_text = time_text.lower().replace("uhr", "").strip() + ":00"

        try:
            hour, minute = map(int, time_text.split(":"))
        except Exception as e:
            print("DEBUG DD LIST PARSE ERROR:", repr(time_text), e)
            continue

        start = base_date.replace(hour=hour, minute=minute)
        end = start + timedelta(hours=3)

        events.append({
            "title": title,
            "start": start,
            "end": end,
            "location": "Deck & Dice Munich",
            "url": url,
            "description": "",
        })

    return events


def fetch_dd_munich_events():
    print("Hole Events von Deck & Dice / DD Munich...")

    url = "https://www.dd-munich.de/event-list"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print("Fehler bei DD Munich:", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    # 1) Monatsansicht (Standard, Commander, Workshops)
    events = []

    for cell in soup.select('[data-hook^="calendar-cell-"]'):
        aria = cell.get("aria-label", "")
        data_hook = cell.get("data-hook", "")

        m = re.search(r"calendar-cell-(\d{4})-(\d{2})-(\d{2})T", data_hook)
        if not m:
            continue

        year = int(m.group(1))

        m2 = re.match(r"\s*(\d{1,2})\.\s+([A-Za-zäöüÄÖÜ]+)", aria)
        if not m2:
            continue

        day = int(m2.group(1))
        month_name = m2.group(2).lower()

        if month_name not in MONTHS_DE:
            continue

        month = MONTHS_DE[month_name]
        base_date = datetime(year, month, day, tzinfo=TZ)

        time_nodes = cell.select("div.B11jYK")
        title_nodes = cell.select("div.OyuNR8")

        for t_node, title_node in zip(time_nodes, title_nodes):
            time_text = t_node.get_text(strip=True)
            title = title_node.get_text(strip=True)

            print("DEBUG DD MONTH TITLE:", repr(title))
            print("DEBUG DD MONTH TIME:", repr(time_text))

            time_text = time_text.replace(".", ":")

            if "uhr" in time_text.lower():
                time_text = time_text.lower().replace("uhr", "").strip() + ":00"

            try:
                hour, minute = map(int, time_text.split(":"))
            except:
                print("DEBUG DD MONTH PARSE ERROR:", repr(time_text))
                continue

            start = base_date.replace(hour=hour, minute=minute)
            end = start + timedelta(hours=3)

            events.append({
                "title": title,
                "start": start,
                "end": end,
                "location": "Deck & Dice Munich",
                "url": url,
                "description": "",
            })

    # 2) Listenansicht (Modern!)
    list_events = fetch_dd_list_view_events(soup, url)

    all_events = events + list_events

    print(f"DD Munich Events gefunden: {len(all_events)}")
    return all_events
