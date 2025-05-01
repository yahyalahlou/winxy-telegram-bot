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
creds = ServiceAccountCredentials.from_json_keyfile_name("geometric-timer-458515-r2-de9b78fd102c.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

# Send message to Telegram
def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

# Process new bets
def check_new_bets():
    data = sheet.get_all_records()
    for idx, row in enumerate(data, start=2):  # Start from second row
        if str(row.get("Active", "")).lower() == "true" and str(row.get("Alert Sent?", "")).lower() != "true":
            msg = f"📢 <b>{row['Sport']} - {row['Category']}</b>\n"
            msg += f"🔮 <b>{row['Bet']}</b>\n"
            msg += f"✅ Confidence: {row['Confidence %']}%\n"
            msg += f"🕒 Match Time: {row['Match Time']}\n"
            msg += f"📊 Odds: {row['Team 1']} ({row['Odds 1']}) vs {row['Team 2']} ({row['Odds 2']})\n"
            msg += f"🧠 Notes: {row['Risk Notes']}\n"
            send_message(msg)

            # Mark as sent in sheet (column H = 8th col)
            sheet.update_cell(idx, 8, "TRUE")

# Entry point
if __name__ == "__main__":
    check_new_bets()
