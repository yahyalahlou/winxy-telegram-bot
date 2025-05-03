import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime
import logging

ua = UserAgent()
headers = {"User-Agent": ua.random}

SOFASCORE_URL = "https://www.sofascore.com"
TARGET_SPORTS = ["tennis", "baseball", "basketball"]

def fetch_sofascore_matches():
    scraped_matches = []

    for sport in TARGET_SPORTS:
        url = f"{SOFASCORE_URL}/{sport}/today"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "lxml")

            # Simplified: Grab event blocks (adjust based on structure)
            events = soup.find_all("a", class_="event__match")
            for e in events:
                teams = e.text.strip().split("\n")
                match_time = e.get("href", "").split("/")[-1]
                scraped_matches.append({
                    "sport": sport,
                    "teams": teams,
                    "match_id": match_time,
                    "source": "sofascore"
                })
        except Exception as err:
            logging.warning(f"[SofaScore:{sport}] Scrape failed: {err}")
            continue

    return scraped_matches

if __name__ == "__main__":
    matches = fetch_sofascore_matches()
    for m in matches:
        print(m)
