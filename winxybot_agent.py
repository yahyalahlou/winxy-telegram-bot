import time
import logging
from oddsapi_wrapper import fetch_raw_odds_data, get_filtered_matches
from winxylogic import calculate_winxy_confidence
from telegram_sender import send_telegram_alert

logging.basicConfig(level=logging.DEBUG)

def main():
    logging.info("🔍 DEBUG: Starting scan")

    try:
        matches = get_filtered_matches()
        logging.info(f"✅ Retrieved {len(matches)} matches")

        for match in matches:
            confidence = calculate_winxy_confidence(match)
            if confidence >= 80:
                logging.info(f"🚀 HIGH CONFIDENCE {confidence}% → {match.get('teams')}")
                send_telegram_alert(match, confidence)
            else:
                logging.info(f"⚠️ Skipping low-confidence match ({confidence}%)")

    except Exception as e:
        logging.exception(f"CRITICAL ERROR during scan: {e}")

if __name__ == "__main__":
    while True:
        main()
        time.sleep(6 * 60 * 60)  # 6 hours between scans
