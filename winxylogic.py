def calculate_winxy_confidence(scraped_data=None, **kwargs):
    if scraped_data is None:
        scraped_data = {}

    # Base score
    confidence = 50

    # Adjust score based on available scraped data
    if scraped_data.get("momentum") == "strong":
        confidence += 15
    if scraped_data.get("injury") == "none":
        confidence += 20
    if scraped_data.get("fatigue") == "low":
        confidence += 10

    return min(confidence, 100)
