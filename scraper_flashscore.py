import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging
from time import sleep
from random import randint

ua = UserAgent()
headers = {
    "User-Agent": ua.random,
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

# Flashscore mirror (default EN version – avoid redirects)
FLASHSCORE_BASE = "https://www.flashscore.com"

TARGET_PATHS = {
    "tennis": "/tennis/",
    "basketball": "/basketball/",
    "baseball": "/baseball/"
}

def fetch_flashscore_matches():
    scraped_matches = []

    for sport, path in TARGET_PATHS.items():
        try:
            url = FLASHSCORE_BASE + path
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 403:
                logging.warning(f"[FlashScore:{sport}] Blocked: 403 Forbidden at {url}")
                continue
            res.raise_for_status()

            soup = BeautifulSoup(res.text, "lxml")
            matches = soup.select(".event__match")  # Generic match selector

            for match in matches:
                team_1 = match.select_one(".event__participant--home")
                team_2 = match.select_one(".event__participant--away")
                match_time = match.select_one(".event__time")

                if not team_1 or not team_2:
                    continue

                scraped_matches.append({
                    "sport": sport,
                    "team_1": team_1.text.strip(),
                    "team_2": team_2.text.strip(),
                    "match_time": match_time.text.strip() if match_time else "N/A",
                    "source": "flashscore"
                })

            sleep(randint(2, 5))  # Delay between requests

        except Exception as err:
            logging.warning(f"[FlashScore:{sport}] Scrape failed: {err}")
            continue

    return scraped_matches


# Local testing (optional in production)
if __name__ == "__main__":
    matches = fetch_flashscore_matches()
    for match in matches:
        print(match)
