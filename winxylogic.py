def calculate_winxy_confidence(scraped_data, team_1=None, team_2=None):
    # Example logic, customize for your needs
    confidence = 50  # base score
    if scraped_data.get("momentum") == "strong":
        confidence += 15
    if scraped_data.get("injury") == "none":
        confidence += 20
    if scraped_data.get("fatigue") == "low":
        confidence += 10

    return min(confidence, 100)
