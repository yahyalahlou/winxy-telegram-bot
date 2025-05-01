import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Telegram config
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Google Sheets config
SHEET_NAME = "WinxyBot - Bet Feed"
WORKSHEET_NAME = "Sheet1"  # adjust if named differently

def send_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

def check_new_bets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("your-google-credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
    data = sheet.get_all_records()

    for idx, row in enumerate(data, start=2):  # row 2 = index 0
        if str(row["Active"]).lower() == "true" and str(row["Alert Sent?"]).lower() != "true":
            msg = f"📢 <b>{row['Sport']} - {row['Category']}</b>\n"
            msg += f"🔮 <b>{row['Bet']}</b>\n"
            msg += f"✅ Confidence: {row['Confidence %']}%\n"
            msg += f"🕒 Match Time: {row['Match Time']}\n"
            msg += f"🧠 Notes: {row['Risk Notes']}"
            send_message(msg)

            # Mark as sent in sheet
            sheet.update_cell(idx, 8, "TRUE")  # column H = Alert Sent?

if __name__ == "__main__":
    check_new_bets()
