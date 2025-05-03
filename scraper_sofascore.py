import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime
import logging
from time import sleep
from random import randint

# Setup headers with randomized User-Agent
ua = UserAgent()
headers = {
    "User-Agent": ua.random,
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

# Constants
SOFASCORE_URL = "https://www.sofascore.com"
TARGET_SPORTS = ["tennis", "baseball", "basketball"]

def fetch_sofascore_matches():
    scraped_matches = []

    for sport in TARGET_SPORTS:
        url = f"{SOFASCORE_URL}/{sport}/today"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 403:
                logging.warning(f"[SofaScore:{sport}] Scrape failed: 403 Forbidden - likely blocked")
                continue
            res.raise_for_status()

            soup = BeautifulSoup(res.text, "lxml")

            # Scrape links to match events (adjust selector if layout changes)
            events = soup.select("a[href*='/match/']")  # Sofascore match links
            for e in events:
                title = e.get("title", "") or e.text.strip()
                href = e.get("href", "")
                if not href:
                    continue

                match_time = href.strip("/").split("/")[-1]
                scraped_matches.append({
                    "sport": sport,
                    "match_url": f"{SOFASCORE_URL}{href}",
                    "title": title,
                    "match_id": match_time,
                    "source": "sofascore"
                })

            sleep(randint(2, 5))  # Add delay to avoid detection

        except Exception as err:
            logging.warning(f"[SofaScore:{sport}] Scrape failed: {err}")
            continue

    return scraped_matches


# For testing only – safe to leave or remove in Render
if __name__ == "__main__":
    matches = fetch_sofascore_matches()
    for m in matches:
        print(m)
