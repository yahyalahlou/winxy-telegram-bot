import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def scrape_rotowire_nba_injuries():
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    url = "https://www.rotowire.com/basketball/nba-lineups.php"

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "lxml")

        injury_data = []

        for section in soup.select(".lineup.is-nba"):
            team_name = section.select_one(".lineup__team").text.strip()
            status_tag = section.select_one(".lineup__status")
            status = status_tag.text.strip() if status_tag else "Unknown"

            injury_data.append({
                "team": team_name,
                "status": status
            })

        return injury_data

    except Exception as e:
        return [{"error": str(e)}]
