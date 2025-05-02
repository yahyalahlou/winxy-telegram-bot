# winxybot_agent.py — LIVE SPORTS + GPT FILTERED

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import openai
import os
import requests

# === SETUP GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("winxybot-gsheetaccess-cee2b3cd0651.json", scope)
client = gspread.authorize(creds)
sheet = client.open("WinxyBot - Bet Feed").worksheet("Sheet1")

# === OPENAI SETUP ===
openai.api_key = os.getenv("OPENAI_API_KEY")

# === ODDS API SETUP ===
odds_api_key = os.getenv("SPORTS_API_KEY")
odds_url = "https://api.the-odds-api.com/v4/sports/upcoming/odds"

# === FETCH MATCHES FROM THE ODDS API ===
def get_live_matches():
    params = {
        "apiKey": odds_api_key,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "decimal",
        "dateFormat": "iso"
    }
    try:
        response = requests.get(odds_url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERROR] Failed to fetch matches: {e}")
        return []

# === ASK GPT TO FILTER BETS ===
def ask_gpt_if_bettable(match_data):
    prompt = f"""
    Match: {match_data['home_team']} vs {match_data['away_team']}
    Odds: {match_data['home_odds']} vs {match_data['away_odds']}
    League: {match_data['sport']}
    Starts at: {match_data['commence_time']}

    Context: Bookmaker odds, market sentiment, and performance trends assumed.

    Should we bet on the favorite (lower odds)? YES or NO.
    Include confidence % and 1-sentence reasoning.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] GPT failed: {e}")
        return None

# === CHECK FOR DUPLICATES ===
def is_duplicate(bet):
    existing_bets = sheet.col_values(4)
    return bet in existing_bets

# === PUSH BET TO SHEET ===
def push_bet_to_sheet(bet_text, match_data, confidence):
    row = [
        "TRUE",
        match_data["sport"],
        match_data["bookmaker"],
        bet_text,
        confidence,
        "Yes",
        match_data["commence_time"],
        "",
        "Auto-approved via GPT & Odds API",
        match_data["home_team"],
        match_data["home_odds"],
        match_data["away_team"],
        match_data["away_odds"],
        "WinxyBot GPT-4",
        "Yes"
    ]
    sheet.append_row(row, value_input_option="USER_ENTERED")
    print(f"[ADDED] Bet inserted: {bet_text}")

# === MAIN ===
if __name__ == "__main__":
    print("[INFO] WinxyBot LIVE Agent started...")
    games = get_live_matches()

    for game in games:
        if not game.get("bookmakers"):
            continue

        bookmaker = game["bookmakers"][0]
        outcomes = bookmaker["markets"][0]["outcomes"]

        if len(outcomes) < 2:
            continue

        home_team = outcomes[0]["name"]
        home_odds = outcomes[0]["price"]
        away_team = outcomes[1]["name"]
        away_odds = outcomes[1]["price"]

        match_data = {
            "home_team": home_team,
            "home_odds": home_odds,
            "away_team": away_team,
            "away_odds": away_odds,
            "sport": game["sport_key"],
            "commence_time": game["commence_time"],
            "bookmaker": bookmaker["title"]
        }

        result = ask_gpt_if_bettable(match_data)
        if result and result.startswith("YES"):
            confidence = ''.join([c for c in result if c.isdigit()])[:2]
            bet_text = f"{home_team} to Win"
            if not is_duplicate(bet_text):
                push_bet_to_sheet(bet_text, match_data, confidence)
            else:
                print(f"[SKIPPED] Duplicate: {bet_text}")
        else:
            print(f"[REJECTED] {home_team} vs {away_team} | GPT said: {result}")

    print("[INFO] WinxyBot LIVE Agent finished.")
