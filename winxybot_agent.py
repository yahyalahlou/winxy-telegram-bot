import requests
import os

SPORTS_API_KEY = os.getenv("SPORTS_API_KEY")

BASE_URL = "https://api.the-odds-api.com/v4/sports"

# ✅ Fallback-safe: Grab raw upcoming odds

def fetch_raw_odds_data():
    try:
        params = {
            "regions": "us",
            "markets": "h2h",
            "oddsFormat": "decimal",
            "apiKey": SPORTS_API_KEY
        }
        url = f"{BASE_URL}/upcoming/odds"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[OddsAPI] FATAL: Failed to fetch raw odds: {e}")
        return []

# 🧠 Filter matches with custom logic

def get_filtered_matches():
    raw_matches = fetch_raw_odds_data()
    # ⚠️ Temp: Return raw data only
    return raw_matches
