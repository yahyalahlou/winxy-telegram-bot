# winxybot_agent.py — LIVE GPT FILTERED EVERY 5 HOURS

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import openai
import os
import requests
import time

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
        chat_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return chat_response.choices[0].message.content.strip()
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

# === MAIN LOOP (EVERY 5 HOURS) ===
if __name__ == "__main__":
    while True:
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

        print("[INFO] Sleeping for 5 hours...\n")
        time.sleep(18000)  # 5 hours in seconds
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SHEET_NAME = "WinxyBot - Bet Feed"
WORKSHEET_NAME = "Sheet1"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("winxybot-gsheetaccess-cee2b3cd0651.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

rows = sheet.get_all_records()

for idx, row in enumerate(rows, start=2):
    if str(row["Active"]).upper() == "TRUE" and str(row["Alert Sent?"]).upper() != "TRUE":
        message = (
            f"📢 *NEW BET ALERT*\n"
            f"🏆 Sport: {row['Sport']}\n"
            f"📂 Category: {row['Category']}\n"
            f"📝 Bet: {row['Bet']}\n"
            f"💯 Confidence: {row['Confidence %']}%\n"
            f"🕒 Match Time: {row['Match Time']}\n"
            f"⚠️ Risk Notes: {row['Risk Notes']}\n"
            f"👤 Team/Player 1: {row['Team/Player 1 (Name)']} (Odds: {row['Team/Player 1 (Odds)']})\n"
            f"👤 Team/Player 2: {row['Team/Player 2 (Name)']} (Odds: {row['Team/Player 2 (Odds)']})\n"
            f"📡 Source: {row['Source Trigger']}\n"
            f"🧩 Parlay OK?: {row['Parlay OK?']}"
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }

        requests.post(url, json=payload)
        sheet.update_cell(idx, 8, "TRUE")
