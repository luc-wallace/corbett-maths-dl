import time
from requests_html import HTMLSession
import os
from threading import Thread

session = HTMLSession()
r = session.get("https://corbettmaths.com/5-a-day/gcse/")

links = {}

for el in r.html.find(".entry-content p"):
    try:
        int(el.text[0])
    except (ValueError, IndexError):
        continue

    month = el.text.split()[1].strip()
    if month not in links:
        links[month] = []

    day = {}
    for link in el.absolute_links:
        if "Higher-Plus" in link:
            day["HP"] = link
        elif "Higher" in link:
            day["H"] = link
        elif "FP" in link:
            day["FP"] = link
    links[month].append(day)


def fetch_month(month, days):
    try:
        os.mkdir(month)
    except FileExistsError:
        pass

    for i, day in enumerate(days):
        for diff, link in day.items():
            while True:
                pdf = session.get(link)
                if pdf.status_code == 429:
                    print("Rate limited, waiting...")
                    time.sleep(0.5)
                    continue
                filename = f"./{month}/{str(i+1).zfill(2)}-{month[:3]}-{diff}.pdf"
                with open(filename, "wb") as f:
                    f.write(pdf.content)
                    print(f"Wrote {filename}")
                break


for month, days in links.items():
    Thread(target=fetch_month, args=(month, days)).start()
    print(f"Started {month} thread")
