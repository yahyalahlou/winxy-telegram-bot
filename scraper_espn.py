import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def scrape_espn_data():
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    url = "https://www.espn.com/betting/"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    picks = []

    # Look for articles or headlines with betting picks
    for headline in soup.find_all("a", href=True):
        text = headline.get_text(strip=True)
        if any(kw in text.lower() for kw in ["pick", "prediction", "bet"]):
            href = headline['href']
            full_url = f"https://www.espn.com{href}" if href.startswith("/") else href
            picks.append({
                "source": "ESPN",
                "title": text,
                "url": full_url
            })

    return picks
