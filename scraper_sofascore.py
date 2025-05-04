import os
import logging
from winxylogic import calculate_winxy_confidence
from telegram_sender import send_telegram_alert
from oddsapi_wrapper import fetch_raw_odds_data

from scraper_espn import scrape_espn_data
from scraper_flashscore import scrape_flashscore_data
from scraper_rotowire import scrape_rotowire_data
from scraper_sofascore import scrape_sofascore_data
from scraper_tennis_elo import scrape_tennis_elo_data

logging.basicConfig(level=logging.INFO)

SENT_ALERTS_FILE = "sent_alerts.txt"

def was_alert_sent(match_id):
    if not os.path.exists(SENT_ALERTS_FILE):
        return False
    with open(SENT_ALERTS_FILE, "r") as file:
        return match_id in file.read()

def mark_alert_sent(match_id):
    with open(SENT_ALERTS_FILE, "a") as file:
        file.write(match_id + "\n")

def run_agent():
    logging.info("🔍 DEBUG: Starting scan")
    try:
        raw_matches = fetch_raw_odds_data()
        logging.info(f"✅ {len(raw_matches)} raw matches fetched from OddsAPI")

        scraped_data_sources = [
            scrape_espn_data,
            scrape_flashscore_data,
            scrape_rotowire_data,
            scrape_sofascore_data,
            scrape_tennis_elo_data
        ]

        for match in raw_matches:
            match_id = match.get("id")
            if was_alert_sent(match_id):
                continue

            try:
                bookmakers = match.get("bookmakers", [])
                if not bookmakers or not bookmakers[0].get("markets"):
                    raise ValueError("Missing bookmakers or markets")

                outcomes = bookmakers[0]["markets"][0].get("outcomes", [])
                if len(outcomes) < 2:
                    raise ValueError("Not enough outcomes")

                team_1 = outcomes[0]["name"]
                team_2 = outcomes[1]["name"]
                odds_1 = outcomes[0]["price"]
                odds_2 = outcomes[1]["price"]
                sport_title = match.get("sport_title", "Unknown")
                commence_time = match.get("commence_time", "Unknown")
                category = match.get("competition", {}).get("name", "N/A")

                scraped_data = {}
                for scrape_func in scraped_data_sources:
                    scraped_data.update(scrape_func(team_1, team_2, sport_title))

                confidence_score = calculate_winxy_confidence(
                    scraped_data=scraped_data,
                    team_1=team_1,
                    team_2=team_2,
                    odds_1=odds_1,
                    odds_2=odds_2,
                    sport=sport_title
                )

                if confidence_score >= 80:
                    message = (
                        f"📢 NEW BET ALERT\n"
                        f"🏆 Sport: {sport_title}\n"
                        f"📂 Category: {category}\n"
                        f"📝 Bet: {team_1} to Win\n"
                        f"👤 Team/Player 1: {team_1} (Odds: {odds_1})\n"
                        f"👤 Team/Player 2: {team_2} (Odds: {odds_2})\n"
                        f"💯 Confidence: {confidence_score}%\n"
                        f"🕒 Match Time: {commence_time}\n"
                        f"⚠️ Risk Notes: {scraped_data.get('injury', 'N/A').capitalize()} lineup\n"
                        f"📡 Source: WinxyBot\n"
                        f"🧩 Parlay OK?: YES"
                    )
                    send_telegram_alert(message)
                    mark_alert_sent(match_id)

            except Exception as inner_err:
                logging.error(f"⚠️ Error processing match: {inner_err}")

    except Exception as e:
        logging.error(f"❌ Agent run failed: {e}")

if __name__ == "__main__":
    run_agent()
