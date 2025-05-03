import time
from oddsapi_wrapper import get_filtered_matches  # External API wrapper (with fallback safety)
from winxylogic import calculate_winxy_confidence  # Custom scoring engine
from telegram_sender import send_telegram_alert  # Modular sender


def main():
    print("WinxyBot Agent starting scan...")
    matches = get_filtered_matches()
    print("DEBUG: Filtered matches →", matches)

    enriched = []
    for match in matches:
        confidence = calculate_winxy_confidence(match)
        match["confidence"] = confidence
        enriched.append(match)

    # FINAL FILTER — send only high-confidence matches (80%+)
    for m in enriched:
        if m["confidence"] >= 80:
            print("📢 Sending match to Telegram →", m)
            send_telegram_alert(m)
        else:
            print(f"Skipping low-confidence match: {m['confidence']}%")


if __name__ == "__main__":
    while True:
        main()
        time.sleep(5 * 60 * 60)  # Wait 5 hours
