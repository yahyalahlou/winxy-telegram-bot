def calculate_winxy_confidence(scraped_data=None, team_1=None, team_2=None, odds_1=None, odds_2=None, sport=None):
    if scraped_data is None:
        scraped_data = {}

    confidence = 50  # Base confidence

    # Boosts from scraped factors
    if scraped_data.get("momentum") == "strong":
        confidence += 15
    if scraped_data.get("injury") == "none":
        confidence += 20
    if scraped_data.get("fatigue") == "low":
        confidence += 10

    # Odds-based factor
    try:
        implied_1 = 100 / float(odds_1)
        implied_2 = 100 / float(odds_2)
        spread = abs(implied_1 - implied_2)
        confidence += min(spread, 10)
    except:
        confidence += 0

    return min(confidence, 100)
