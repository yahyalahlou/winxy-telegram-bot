import os
import requests
import logging

API_KEY = os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4/sports"

TARGET_MARKETS = ["h2h", "totals", "spreads"]
TARGET_REGIONS = "us"
ODDS_FORMAT = "decimal"

def get_filtered_matches(sport="upcoming", min_confidence=75):
    url = f"{BASE_URL}/{sport}/odds"
    params = {
        "apiKey": API_KEY,
        "markets": ",".join(TARGET_MARKETS),
        "regions": TARGET_REGIONS,
        "oddsFormat": ODDS_FORMAT
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        matches = res.json()

        safe_matches = []
        for match in matches:
            try:
                if not match.get("bookmakers"):
                    continue
                team_1 = match["bookmakers"][0]["markets"][0]["outcomes"][0]["name"]
                team_2 = match["bookmakers"][0]["markets"][0]["outcomes"][1]["name"]

                safe_matches.append({
                    "teams": [team_1, team_2],
                    "commence_time": match["commence_time"],
                    "sport_key": match.get("sport_key"),
                    "confidence": 78,  # Placeholder, replace with WinxyLogic later
                    "source": "oddsapi"
                })
            except Exception as err:
                logging.warning(f"[OddsAPI] Match skipped: {err}")
                continue

        return [m for m in safe_matches if m["confidence"] >= min_confidence]

    except Exception as e:
        logging.error(f"[OddsAPI] Failed to fetch: {e}")
        return []
