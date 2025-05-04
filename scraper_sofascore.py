import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def scrape_sofascore_data():
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    try:
        url = "https://www.sofascore.com/"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        matches = []
        for event in soup.find_all("a", class_="event__match"):
            match_info = event.get_text(separator=" ", strip=True)
            matches.append(match_info)

        return {"matches": matches}

    except Exception as e:
        print(f"[sofascore scraper] ERROR: {e}")
        return {}
