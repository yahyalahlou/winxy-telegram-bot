from oddsapi_wrapper import get_filtered_matches
from winxylogic import calculate_winxy_confidence
from telegram_sender import send_telegram_alert

print("🧠 DEBUG: Starting scan")

# 🔍 TEMP: Use raw OddsAPI call for debugging
from oddsapi_wrapper import fetch_raw_odds_data
matches = fetch_raw_odds_data()

print(f"🧠 DEBUG: Raw matches pulled: {len(matches)}")

# 🔁 Show details
for match in matches:
    print("📝 Match data:", match)

# ❌ Skip logic and Telegram sending for now
