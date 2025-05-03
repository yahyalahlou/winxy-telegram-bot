import logging
from oddsapi_wrapper import fetch_raw_odds_data
from winxylogic import calculate_winxy_confidence
from telegram_sender import send_telegram_alert

logging.basicConfig(level=logging.INFO)

def run_agent():
    logging.info("🔍 DEBUG: Starting scan")
    try:
        raw_matches = fetch_raw_odds_data()
        logging.info(f"✅ {len(raw_matches)} raw matches fetched from OddsAPI")

        for match in raw_matches:
            team_1 = match['bookmakers'][0]['markets'][0]['outcomes'][0]['name']
            team_2 = match['bookmakers'][0]['markets'][0]['outcomes'][1]['name']
            odds_1 = match['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
            odds_2 = match['bookmakers'][0]['markets'][0]['outcomes'][1]['price']
            sport_title = match['sport_title']
            commence_time = match['commence_time']

            scraped_data = {
    "momentum": "strong",
    "injury": "none",
    "fatigue": "low"
}

confidence_score = calculate_winxy_confidence(
    scraped_data=scraped_data,
    team_1=team_1,
    team_2=team_2
)


            if confidence_score >= 80:
                message = (
                    f"📢 *NEW BET ALERT*\n"
                    f"🏆 Sport: {sport_title}\n"
                    f"👥 Match: {team_1} vs {team_2}\n"
                    f"📈 Confidence: {confidence_score}%\n"
                    f"🕒 Match Time: {commence_time}\n"
                    f"💡 Reason: {reason}\n"
                    f"💰 Odds: {team_1} ({odds_1}) vs {team_2} ({odds_2})"
                )
                send_telegram_alert(message)
            else:
                logging.info(f"⚠️ Skipping low-confidence match ({confidence_score}%)")

    except Exception as e:
        logging.error(f"💥 Critical failure during agent run: {e}")

if __name__ == "__main__":
    run_agent()
