# PATCH: winxybot_agent.py — Updated to handle API and scraping errors safely

import os
import requests
from scraper_flashscore import fetch_flashscore_matches
from scraper_sofascore import fetch_sofascore_matches
from winxylogic import calculate_winxy_confidence  # ensure this file exists

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/upcoming/odds"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_odds():
    try:
        res = requests.get(ODDS_API_URL, params={
            "apiKey": ODDS_API_KEY,
            "regions": "us",
            "markets": "h2h",
            "oddsFormat": "decimal"
        }, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Odds API error: {e}")
        return []


def parse_match_data(raw_match):
    try:
        bookmakers = raw_match.get("bookmakers", [])
        if not bookmakers:
            return None

        market = bookmakers[0].get("markets", [])[0]
        outcomes = market.get("outcomes", [])
        if len(outcomes) < 2:
            return None

        team_1 = outcomes[0]["name"]
        team_2 = outcomes[1]["name"]
        odds_1 = outcomes[0]["price"]
        odds_2 = outcomes[1]["price"]

        return {
            "sport": raw_match.get("sport_key"),
            "teams": [team_1, team_2],
            "odds": [odds_1, odds_2],
            "commence_time": raw_match.get("commence_time")
        }
    except Exception as err:
        print(f"Error parsing match data: {err}")
        return None


def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram error: {e}")


if __name__ == "__main__":
    raw_matches = fetch_odds()
    web_matches = fetch_flashscore_matches() + fetch_sofascore_matches()

    for raw in raw_matches:
        parsed = parse_match_data(raw)
        if not parsed:
            continue

        confidence = calculate_winxy_confidence(parsed, web_matches)
        if confidence >= 80:
            msg = f"*BET ALERT*\n{parsed['teams'][0]} vs {parsed['teams'][1]}\nConfidence: {confidence}%\nOdds: {parsed['odds']}\nTime: {parsed['commence_time']}"
            send_telegram(msg)
