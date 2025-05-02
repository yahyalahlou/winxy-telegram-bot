# winxybot_agent.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# === STEP 1: Setup Google Sheets Auth ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("winxybot-gsheetaccess-cee2b3cd0651.json", scope)
client = gspread.authorize(creds)

# === STEP 2: Open Google Sheet ===
sheet = client.open("WinxyBot - Bet Feed").worksheet("Sheet1")

# === STEP 3: Define Dummy Researched Bet (Replace with real logic later) ===
def get_winxybot_bets():
    # This should be replaced with real API/live data + logic
    return [{
        "Sport": "Boxing",
        "Category": "Main Event",
        "Bet": "Ryan Garcia to Win",
        "Confidence %": "89",
        "Approved": "Yes",
        "Match Time": "2025-05-03 08:00 GMT+7",
        "Risk Notes": "High favorite, -1100 odds, full form",
        "Team/Player 1 (Name)": "Ryan Garcia",
        "Team/Player 1 (Odds)": "1.09",
        "Team/Player 2 (Name)": "Rolando Romero",
        "Team/Player 2 (Odds)": "8.00",
        "Source Trigger": "ChatGPT auto-analysis",
        "Parlay OK?": "Yes"
    }]

# === STEP 4: Push Bet to Google Sheet ===
def push_to_sheet(bets):
    for bet in bets:
        row = [
            "TRUE",  # Active
            bet["Sport"],
            bet["Category"],
            bet["Bet"],
            bet["Confidence %"],
            bet["Approved"],
            bet["Match Time"],
            "",  # Alert Sent? (blank = false)
            bet["Risk Notes"],
            bet["Team/Player 1 (Name)"],
            bet["Team/Player 1 (Odds)"],
            bet["Team/Player 2 (Name)"],
            bet["Team/Player 2 (Odds)"],
            bet["Source Trigger"],
            bet["Parlay OK?"]
        ]
        sheet.append_row(row, value_input_option="USER_ENTERED")

# === RUN THE WORKFLOW ===
bets = get_winxybot_bets()
push_to_sheet(bets)
