def calculate_winxy_confidence(scraped_data, team_1, team_2, odds_1, odds_2, sport):
    """
    Calculate a win confidence score based on scraped context and odds.
    """
    confidence = 50  # base score

    # Adjust for injuries
    injury = scraped_data.get("injury", "none")
    if injury == "none":
        confidence += 15
    elif injury == "minor":
        confidence += 5
    elif injury == "severe":
        confidence -= 20

    # Adjust for momentum
    momentum = scraped_data.get("momentum", "neutral")
    if momentum == "strong":
        confidence += 15
    elif momentum == "weak":
        confidence -= 10

    # Adjust for fatigue
    fatigue = scraped_data.get("fatigue", "medium")
    if fatigue == "low":
        confidence += 10
    elif fatigue == "high":
        confidence -= 10

    # Odds-based modifier (underdog boost or risk normalization)
    try:
        odds_ratio = float(odds_2) / float(odds_1)
        if odds_ratio < 1.1:
            confidence += 5
        elif odds_ratio > 1.5:
            confidence -= 10
    except Exception:
        pass

    # Clamp confidence
    return max(0, min(confidence, 100))
