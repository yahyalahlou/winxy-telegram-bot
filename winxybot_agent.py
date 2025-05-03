import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from winxylogic import calculate_winxy_confidence
from scraper_flashscore import fetch_flashscore_matches
from scraper_sofascore import fetch_sofascore_matches
from scraper_espn import scrape_espn
from scraper_rotowire import scrape_rotowire_nba_injuries
from scraper_tennis_elo import fetch_tennis_elo
import os
import time

SHEET_NAME = "WinxyBot - Bet Feed"
WORKSHEET_NAME = "Sheet1"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("winxybot-gsheetaccess-cee2b3cd0651.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

# Sample OddsAPI Pull (you can expand this)
def fetch_oddsapi_matches():
    key = os.getenv("ODDS_API_KEY")
    url = f"https://api.the-odds-api.com/v4/sports/tennis/odds/?regions=us&markets=h2h&oddsFormat=decimal&apiKey={key}"
    try:
        res = requests.get(url)
        return res.json()
    except Exception as e:
        print("OddsAPI error:", e)
        return []

# Trigger all scraper modules and logic
odds_matches = fetch_oddsapi_matches()
flash_matches = fetch_flashscore_matches()
sofa_matches = fetch_sofascore_matches()
espn_insights = scrape_espn()
rotowire_risks = scrape_rotowire_nba_injuries()

# Now process each match
for match in odds_matches:
    team_1 = match['bookmakers'][0]['markets'][0]['outcomes'][0]['name']
    team_2 = match['bookmakers'][0]['markets'][0]['outcomes'][1]['name']
    odds_1 = match['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
    odds_2 = match['bookmakers'][0]['markets'][0]['outcomes'][1]['price']
    match_time = match['commence_time']

    bet_data = {
        "odds": min(odds_1, odds_2),
        "flashscore_form": ["W", "L", "W"],  # replace later with lookup from flash_matches
        "sofascore_matchup": {"rating_diff": 2.0},  # mock data for now
        "injuries": [],  # can cross-check from rotowire_risks
        "tennis_elo": fetch_tennis_elo(team_1),
        "expert_picks": len([p for p in espn_insights if team_1.lower() in p['title'].lower()])
    }

    confidence = calculate_winxy_confidence(bet_data)
    if confidence >= 80:
        sheet.append_row([
            "Tennis", "Pre-match", f"{team_1} to win",
            f"{confidence}%", match_time, "None",
            team_1, odds_1, team_2, odds_2,
            "WinxyLogic", "Yes", ""
        ])

    time.sleep(1.5)  # space out API requests safely
