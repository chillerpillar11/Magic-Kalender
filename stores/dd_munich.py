import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
import re

TZ = ZoneInfo("Europe/Berlin")

WIDGET_URL = "https://www.dd-munich.de/event-list"

# ---------------------------------------------------------
# Modern/RCQ Filter (Premodern ausgeschlossen!)
# ---------------------------------------------------------
def is_modern_or_rcq(title: str) -> bool:
    title = title.lower()

    if "premodern" in title:
        return False

    include = [
        "modern",
        "rcq",
        "regional championship qualifier",
        "qualifier",
    ]

    exclude = [
        "commander",
        "edh",
        "draft",
        "sealed",
        "prerelease",
        "pre-release",
        "standard",
        "pauper",
        "booster",
        "casual",
        "painting",
        "workshop",
        "warhammer",
        "40k",
        "age of sigmar",
        "pokémon",
        "pokemon",
        "lorcana",
        "yu-gi-oh",
        "yugioh",
        "flesh and blood",
        "fab",
        "one piece",
        "star wars",
        "spearwars",
        "spear wars",
        "spearhead",
        "tabletop",
        "boardgame",
        "brettspiel",
    ]

    if any(x in title for x in exclude):
        return False

    return any(x in title for x in include)


# ---------------------------------------------------------
# Datum/Uhrzeit aus Detailseite extrahieren
# ---------------------------------------------------------
def parse_date_range(text: str):
    # Beispiel: "20. März 2026, 18:30 – 23:00"
    m = re.match(r"(\d{1,2})\. (\w+) (\d{4}), (\d{1,2}:\d{2})", text)
    if not m:
        return None, None

    day = int(m.group(1))
    month_name = m.group(2).lower()
    year = int(m.group(3))
    start_time = m.group(4)

    MONTHS = {
        "januar": 1, "februar": 2, "märz": 3, "april": 4, "mai": 5, "juni": 6,
        "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11, "dezember": 12
    }

    if month_name not in MONTHS:
        return None, None

    month = MONTHS[month_name]

    hour, minute = map(int, start_time.split(":"))
    start = datetime(year, month, day, hour, minute, tzinfo=TZ)

    # Endzeit extrahieren
    m2 = re.search(r"– (\d{1,2}:\d{2})", text)
    if m2:
        end_hour, end_minute = map(int, m2.group(1).split(":"))
        end = datetime(year, month, day, end_hour, end_minute, tzinfo=TZ)
    else:
        end = start.replace(hour=start.hour + 3)

    return start, end


# ---------------------------------------------------------
# Alle Event-URLs aus dem Widget extrahieren
# ---------------------------------------------------------
def fetch_event_urls():
    print("\n--- DEBUG: Widget laden ---")
    print(f"  → Lade {WIDGET_URL}")

    resp = requests.get(WIDGET_URL, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    urls = []
    for a in soup.select('[data-hook="title"]'):
        href = a.get("href")
        if href and href.startswith("/event-details/"):
            full_url = "https://www.dd-munich.de" + href
            urls.append(full_url)

    print(f"Gefundene Event-URLs: {len(urls)}")
    return urls


# ---------------------------------------------------------
# Detailseite scrapen
# ---------------------------------------------------------
def fetch_event_details(url):
    print(f"    → Lade Detailseite: {url}")

    resp = requests.get(url, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    title_el = soup.select_one('[data-hook="title"]')
    date_el = soup.select_one('[data-hook="date"]')
    desc_el = soup.select_one('[data-hook="description"]')

    if not title_el or not date_el:
        print("      ✗ Titel oder Datum fehlt")
        return None

    title = title_el.get_text(strip=True)
    date_text = date_el.get_text(strip=True)
    description = desc_el.get_text(strip=True) if desc_el else ""

    start, end = parse_date_range(date_text)
    if not start:
        print("      ✗ Datum konnte nicht geparst werden")
        return None

    return {
        "title": title,
        "start": start,
        "end": end,
        "location": "Deck & Dice Munich",
        "url": url,
        "description": description,
    }


# ---------------------------------------------------------
# Hauptfunktion
# ---------------------------------------------------------
def fetch_dd_munich_events():
    print("Hole Events von Deck & Dice / DD Munich...")

    urls = fetch_event_urls()
    final = []

    print("\n--- DEBUG: Detailseiten-Parsing ---")

    for url in urls:
        ev = fetch_event_details(url)
        if not ev:
            continue

        print(f"  → Prüfe: {ev['title']}")

        if not is_modern_or_rcq(ev["title"]):
            print("    ✗ kein Modern/RCQ")
            continue

        print("    ✓ Modern-Event übernommen")
        final.append(ev)

    print(f"\n--- DEBUG: FINAL ---")
    print(f"Gesamt Modern/RCQ Events: {len(final)}")
    for ev in final:
        print(f"  ✓ {ev['title']} @ {ev['start']}")

    return final
