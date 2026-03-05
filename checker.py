import requests
from bs4 import BeautifulSoup
import json
import smtplib
import os
from email.mime.text import MIMEText
from datetime import datetime

SEEN_FILE = "seen_listings.json"
URL = "https://kerebyudlejning.dk/"

EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_TO = os.environ["EMAIL_TO"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

def load_seen():
    try:
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def send_email(new_listings):
    body = "New listings found on Kereby:\n\n" + "\n\n".join(new_listings)
    msg = MIMEText(body)
    msg["Subject"] = f"🏠 {len(new_listings)} new listing(s) on Kereby!"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
    print("Email sent!")

def check_listings():
    print(f"[{datetime.now()}] Checking listings...")
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    # ⚠️ UPDATE THIS with the CSS class you found in Step 1
    listings = soup.select(".rental-card")
    print(f"Found {len(listings)} listings")

    current = {}
    for l in listings:
        title = l.get_text(strip=True)[:120]
        link_tag = l.find("a")
        link = link_tag["href"] if link_tag else ""
        key = title + link
        current[key] = f"{title}\n{link}"

    seen = load_seen()
    new = {k: v for k, v in current.items() if k not in seen}

    if new:
        print(f"→ {len(new)} new listing(s) found!")
        send_email(list(new.values()))
    else:
        print("→ No new listings.")

    save_seen(set(current.keys()))

check_listings()
