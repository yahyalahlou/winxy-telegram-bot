import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import os
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SHEET_NAME = "WinxyBot - Bet Feed"
WORKSHEET_NAME = "Sheet1"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("winxybot-gsheetaccess-cee2b3cd0651.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

def send_alerts():
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

# 🔁 Main infinite loop for automation
while True:
    try:
        send_alerts()
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(60)  # ⏱️ Wait 60 seconds before checking again
