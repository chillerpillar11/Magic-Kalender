import requests
from bs4 import BeautifulSoup
from datetime import datetime
from ics import Calendar, Event

print("Script gestartet")


# ---------------------------------------------------------
# BB-SPIELE
# ---------------------------------------------------------
def fetch_bbspiele_events():
    print("Hole Events von BB-Spiele...")

    url = "https://www.bb-spiele.de/events?categories=0196a9a7d19270a89170491be8392535&p=1"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, headers=headers)
    except Exception as e:
        print("Fehler bei BB-Spiele:", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    events = []

    cards = soup.select(".events-card")

    for card in cards:
        # Titel
        title_el = card.select_one(".netzp-events-title")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)

        # Datum + Uhrzeit
        date_el = card.select_one(".icon-calendar + span")
        if not date_el:
            continue

        raw = date_el.get_text(strip=True)
        # Beispiel: "Sa., 04.04.26, 11:00 - 18:00"
        parts = raw.split(",")
        if len(parts) < 3:
            continue

        date_str = parts[1].strip()  # "04.04.26"
        time_str = parts[2].strip().split("-")[0].strip()  # "11:00"

        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%y %H:%M")
        except:
            continue

        # Ort
        loc_el = card.select_one(".icon-marker + b")
        location = loc_el.get_text(strip=True) if loc_el else "BB-Spiele"

        # Beschreibung
        desc_el = card.select_one(".card-text.lead")
        description = desc_el.get_text(strip=True) if desc_el else "Event von BB-Spiele"

        e = Event()
        e.name = title
        e.begin = dt
        e.location = location
        e.description = description

        events.append(e)

    print(f"BB-Spiele Events gefunden: {len(events)}")
    return events


# ---------------------------------------------------------
# FUNTANIMENT
# ---------------------------------------------------------
def fetch_funtainment_events():
    print("Hole Events von Funtainment...")

    url = "https://www.funtainment.de/b2c-shop/tickets?categories=0197f53c9a997cbe8574b9211c0c8eaf&p=1"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, headers=headers)
    except Exception as e:
        print("Fehler bei Funtainment:", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    events = []

    cards = soup.select(".events-card")

    for card in cards:
        title_el = card.select_one(".netzp-events-title")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)

        date_el = card.select_one(".icon-calendar + span")
        if not date_el:
            continue

        raw = date_el.get_text(strip=True)
        parts = raw.split(",")
        if len(parts) < 3:
            continue

        date_str = parts[1].strip()
        time_str = parts[2].strip().split("-")[0].strip()

        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%y %H:%M")
        except:
            continue

        loc_el = card.select_one(".icon-marker + b")
        location = loc_el.get_text(strip=True) if loc_el else "Funtainment München"

        desc_el = card.select_one(".card-text.lead")
        description = desc_el.get_text(strip=True) if desc_el else "Event von Funtainment"

        e = Event()
        e.name = title
        e.begin = dt
        e.location = location
        e.description = description

        events.append(e)

    print(f"Funtainment Events gefunden: {len(events)}")
    return events


# ---------------------------------------------------------
# DD MUNICH
# ---------------------------------------------------------
def fetch_ddmunich_events():
    print("Hole Events von Deck & Dice / DD Munich...")

    url = "https://www.dd-munich.de/event-list"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, headers=headers)
    except Exception as e:
        print("Fehler bei DD Munich:", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    events = []

    # Alle Kalenderzellen
    cells = soup.select("[data-hook^='calendar-cell-']")

    for cell in cells:
        data_hook = cell.get("data-hook")
        if not data_hook:
            continue

        # Beispiel: calendar-cell-2026-02-22T23:00:00.000Z
        try:
            iso = data_hook.replace("calendar-cell-", "")
            date = datetime.fromisoformat(iso.replace("Z", ""))
        except:
            continue

        # Events in der Zelle
        items = cell.select(".x336W1")

        for item in items:
            time_el = item.select_one(".B11jYK")
            title_el = item.select_one(".OyuNR8")

            if not time_el or not title_el:
                continue

            time_str = time_el.get_text(strip=True)
            title = title_el.get_text(strip=True)

            # Datum + Uhrzeit kombinieren
            try:
                dt = datetime.strptime(
                    f"{date.strftime('%Y-%m-%d')} {time_str}",
                    "%Y-%m-%d %H:%M"
                )
            except:
                continue

            e = Event()
            e.name = title
            e.begin = dt
            e.location = "Deck & Dice / DD Munich"
            e.description = "Event von Deck & Dice / DD Munich"

            events.append(e)

    print(f"DD Munich Events gefunden: {len(events)}")
    return events


# ---------------------------------------------------------
# GENERATE ICS
# ---------------------------------------------------------
def generate_ics():
    print("Erzeuge Kalender...")

    cal = Calendar()

    bb = fetch_bbspiele_events()
    ft = fetch_funtainment_events()
    dd = fetch_ddmunich_events()

    all_events = bb + ft + dd

    print("Gesamtanzahl Events:", len(all_events))

    for e in all_events:
        cal.events.add(e)

    print("Schreibe magic.ics...")
    with open("magic.ics", "w", encoding="utf-8") as f:
        f.writelines(cal)

    print("Fertig! Datei erzeugt.")


if __name__ == "__main__":
    generate_ics()
