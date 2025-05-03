import os
import requests
import logging
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from winxylogic import calculate_winxy_confidence
from oddsapi_wrapper import get_filtered_matches  # External API wrapper (with fallback safety)
from telegram_sender import send_telegram_alert  # Modular sender

# Setup logging
logging.basicConfig(level=logging.INFO)

# Env vars
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Google Sheets config
SHEET_NAME = "WinxyBot - Bet Feed"
WORKSHEET_NAME = "Sheet1"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("winxybot-gsheetaccess-cee2b3cd0651.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

def safe_get(d, keys):
    for k in keys:
        if isinstance(d, list):
            if isinstance(k, int) and k < len(d):
                d = d[k]
            else:
                return None
        elif isinstance(d, dict):
            d = d.get(k)
        else:
            return None
    return d

# Main logic
def run_bot():
    matches = get_filtered_matches()
    now = datetime.utcnow()
    rows = sheet.get_all_records()

    for match in matches:
        team1 = safe_get(match, ["bookmakers", 0, "markets", 0, "outcomes", 0, "name"])
        team2 = safe_get(match, ["bookmakers", 0, "markets", 0, "outcomes", 1, "name"])
        odds1 = safe_get(match, ["bookmakers", 0, "markets", 0, "outcomes", 0, "price"])
        odds2 = safe_get(match, ["bookmakers", 0, "markets", 0, "outcomes", 1, "price"])
        start_time = match.get("commence_time", "N/A")
        sport = match.get("sport_key", "")

        confidence = calculate_winxy_confidence(match)

        if confidence >= 80:
            alert_exists = any(row for row in rows if row["Team/Player 1 (Name)"] == team1 and row["Match Time"] == start_time)
            if alert_exists:
                continue

            row = [
                sport, "Auto-Push", f"Back {team1}", confidence, start_time, "", team1, odds1, team2, odds2, "oddsapi+web", "Yes", "FALSE"
            ]
            sheet.append_row(row)
            send_telegram_alert(BOT_TOKEN, CHAT_ID, row)

if __name__ == "__main__":
    run_bot()
