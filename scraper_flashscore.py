import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def fetch_flashscore_matches():
    ua = UserAgent()
    headers = {"User-Agent": ua.random}
    url = "https://www.flashscore.com/"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "lxml")

        matches = []
        for match in soup.select(".event__match"):
            teams = match.select(".event__participant")
            if len(teams) == 2:
                match_time = match.select_one(".event__time")
                matches.append({
                    "team_1": teams[0].text.strip(),
                    "team_2": teams[1].text.strip(),
                    "time": match_time.text.strip() if match_time else "N/A"
                })

        return matches

    except Exception as e:
        print("Flashscore Scraper Error:", e)
        return []
