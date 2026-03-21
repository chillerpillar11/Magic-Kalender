import requests

url = "https://mtgoupdate.com"
headers = {"User-Agent": "Mozilla/5.0"}

resp = requests.get(url, headers=headers, timeout=20)
resp.raise_for_status()

with open("mtgo_raw.html", "w", encoding="utf-8") as f:
    f.write(resp.text)

print("Dump gespeichert als mtgo_raw.html")
