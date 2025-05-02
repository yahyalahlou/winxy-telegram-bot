import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os

# Setup Telegram bot credentials
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Google Sheet details
SHEET_NAME = "WinxyBot - Bet Feed"
WORKSHEET_NAME = "Sheet1"

# Load Google credentials from file
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("winxybot-gsheetaccess-90658a4ae6f6.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

# Fetch all rows
rows = sheet.get_all_records()

# Process each row
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
        sheet.update_cell(idx, 8, "TRUE")  # Update 'Alert Sent?' to TRUE
