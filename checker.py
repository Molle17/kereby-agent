import json
import smtplib
import os
from email.mime.text import MIMEText
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

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
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
    print("Email sent!")

def check_listings():
    print(f"[{datetime.now()}] Checking listings...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle")
        content = page.content()
        browser.close()

    soup = BeautifulSoup(content, "html.parser")
    listings = soup.select(".rental-card")
    print(f"Found {len(listings)} listings")

    current = {}
    for l in listings:
        title = l.get_text(strip=True)[:120]
        link = l.get("href", "")
        if not link.startswith("http"):
            link = "https://kerebyudlejning.dk" + link
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
